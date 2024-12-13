import streamlit as st
import duckdb
import pandas as pd
import altair as alt
st.set_page_config(page_title="Demo", layout="wide",)
st.title("Demo App")

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Constituents file')
    uploaded_file_constituests = st.file_uploader("Upload Constituents file")
with col2:
    st.subheader('Donation History file')
    uploaded_file_Donation_History = st.file_uploader("Upload Donation History file")
with col3:
    st.subheader('Emails file')
    uploaded_file_Email = st.file_uploader("Upload Emails file")
   

conn = duckdb.connect('temp.db')

if(uploaded_file_constituests and uploaded_file_Donation_History and uploaded_file_Email):
    st.write("Files uploaded")

    donation_constituents = pd.read_csv(uploaded_file_constituests)
    donation_emails = pd.read_csv(uploaded_file_Email)
    donation_history = pd.read_csv(uploaded_file_Donation_History)

    conn.register("upldoaded_data", donation_constituents)
    conn.register("upldoaded_data", donation_emails)
    conn.register("upldoaded_data", donation_history)


    excluded_rows_query = """with check_person_company as (select "Patron ID","Date Entered", case when Company is NULL or Company = '...' or Company = 'None' or Company = 'N/A' or Company = 'Retired' 
    then 'Person'
    ELSE 'Company'
    END AS "CB Constituent Type", Company, "First Name", "Last Name" from donation_constituents),

    check_multiple_entries as (select row_number() over (partition by "Patron ID" order by "Date Entered" desc) as latest_insert, 
    "Patron ID", "Date Entered" from donation_constituents)
  
    select "Patron ID","Date Entered" from donation_constituents where "Primary Email" is not null and "Primary Email" not in (select Email from donation_emails)

    union

    select "Patron ID","Date Entered" from donation_constituents where "Date Entered" is null

    union
    
    select "Patron ID","Date Entered" from check_person_company where "CB Constituent Type" = 'Company' and Company is null

    union

    select "Patron ID","Date Entered" from check_person_company where "CB Constituent Type" = 'Person' and ("First Name" is null or "Last Name" is null)

    union

    select "Patron ID", "Date Entered" from check_multiple_entries where latest_insert != 1
    """

    # Output Table 1
    query_1 = """
    create or replace view donation_constituents_v1 as 
    (
        select row_number() over (partition by "Patron ID" order by "Date Entered" desc) as latest_insert,
        case when Company is NULL or Company = '...' or Company = 'None' or Company = 'N/A' or Company = 'Retired' 
        then 'Person'
        ELSE 'Company'
        END AS "CB Constituent Type", 
        STRFTIME(
            CASE
                WHEN "Date Entered" LIKE '% %,%' THEN STRPTIME("Date Entered", '%b %d, %Y')
                WHEN "Date Entered" LIKE '%/%/% %:%' THEN STRPTIME("Date Entered", '%m/%d/%Y %H:%M')
                WHEN "Date Entered" LIKE '%/%/% %' THEN STRPTIME("Date Entered", '%m/%d/%Y %H:%M')
                WHEN "Date Entered" LIKE '%/%/%' THEN STRPTIME("Date Entered", '%m/%d/%Y') 
                ELSE NULL 
            END,
            '%Y-%m-%d %H:%M' 
        ) AS 'CB Created At',
        CASE
            WHEN Salutation IN ('Mr', 'Mr.') THEN 'Mr.'
            WHEN Salutation IN ('Mrs', 'Mrs.') THEN 'Mrs.'
            WHEN Salutation = 'Ms' THEN 'Ms.'
            WHEN Salutation = 'Dr' THEN 'Dr.'
            ELSE '' 
        END AS 'CB Title',
        CASE
            WHEN Title IS NOT NULL AND Gender IS NOT NULL THEN
                'Job Title: ' || Title || '; Marital Status: ' || Gender
            WHEN Title IS NOT NULL THEN
                'Job Title: ' || Title
            WHEN Gender IS NOT NULL THEN
                'Marital Status: ' || Gender
            ELSE
                ''
        END AS 'CB Background Information',
        CASE when Company is NULL or Company = '...' or Company = 'None' or Company = 'N/A' or Company = 'Retired' 
        then ''
        ELSE Company END as 'CB Company Name',
        * 
        FROM donation_constituents WHERE "Date Entered" is not null
    ) 
    """
    query_2 = """CREATE or replace table tags_api as (SELECT * FROM read_json('https://6719768f7fc4c5ff8f4d84f1.mockapi.io/api/v1/tags'));"""
    query_3 = """
    create or replace table CueBox_Constituents as (
    with final_table as (select "Patron ID" as 'CB Constituent ID', "CB Constituent Type" ,
    "First Name" as 'CB First Name' ,
    "Last Name" as 'CB Last Name',
    "CB Company Name",
    "CB Created At",
    "Primary Email" as 'CB Email 1 (Standardized)',
    NULL as 'CB Email 2 (Standardized)',
    "CB Title",
    "CB Background Information",
    tags
    from donation_constituents_v1 where latest_insert = 1
    and "CB Constituent Type" = 'Person' and "First Name" is not null and "Last Name" is not null

    UNION 

    select "Patron ID" as 'CB Constituent ID', "CB Constituent Type" ,
    "First Name" as 'CB First Name' ,
    "Last Name" as 'CB Last Name',
    "CB Company Name",
    "CB Created At",
        "Primary Email" as 'CB Email 1 (Standardized)',
    NULL as 'CB Email 2 (Standardized)',
    "CB Title",
    "CB Background Information",
    tags
    from donation_constituents_v1 where latest_insert = 1
    and "CB Constituent Type" = 'Company' and Company is not null),

    tags_updated as (with tags_updated_a as (select *, trim(UNNEST(STRING_SPLIT(ifnull(tags,''), ','))) as tag from final_table)

    SELECT DISTINCT 
    a."CB Constituent ID",
    a."CB Constituent Type",
    a."CB First Name",
    a."CB Last Name",
    a."CB Company Name",
    a."CB Created At",
    a."CB Email 1 (Standardized)",
    a."CB Email 2 (Standardized)",
    a."CB Title",
    list(b.mapped_name) as "CB Tags"
    FROM tags_updated_a a 
    LEFT JOIN tags_api b ON b."name" = a.tag
    GROUP by ALL),

    total_donation_calc as (select '$' || cast(sum(CAST(REPLACE(REPLACE("Donation Amount", '$', ''), ',', '') AS INT)) as string) || '.00' as 'CB Lifetime Donation Amount', "Patron ID" 
    from donation_history where Status = 'Paid' GROUP BY "Patron ID"),

    latest_donation as (with latest_donation_a as (select "Patron ID", "Donation Date",
    row_number() OVER (PARTITION BY "Patron ID" ORDER BY "Donation Date" desc) as rn
    from donation_history where Status = 'Paid')
    select * from latest_donation_a where rn = 1)

    select a.*, b."CB Lifetime Donation Amount", c."Donation Date" as 'CB Most Recent Donation Date'
    from tags_updated a 
    left join total_donation_calc b on a."CB Constituent ID" = b."Patron ID"
    left join latest_donation c on a."CB Constituent ID" = c."Patron ID")
    """



    duckdb.query(query_1)
    duckdb.query(query_2)
    duckdb.query(query_3)

    data_c = duckdb.query("select * from CueBox_Constituents").to_df()
    st.divider()
    st.subheader("Output table - CueBox Constituents")
    st.write(data_c)

    # Output table 2

    query = """with s as (select distinct "Patron ID", trim(UNNEST(STRING_SPLIT(tags, ','))) as tag from donation_constituents)

                SELECT tag as "CB Tag Name", count(*) "CB Tag Count" FROM s where tag in (select "name" from tags_api) GROUP BY tag"""

    data = duckdb.query(query).to_df()
    st.divider()
    st.subheader("Output table - CueBox Tags")
    st.write(data)

    data_line = duckdb.query(""" with total_donation_calc as (select '$' || cast(sum(CAST(REPLACE(REPLACE("Donation Amount", '$', ''), ',', '') AS INT)) as string) || '.00' as 'CB Lifetime Donation Amount', "Patron ID" 
    from donation_history where Status = 'Paid' GROUP BY "Patron ID") 
                             select "Patron ID" as ID, "CB Lifetime Donation Amount" as "Total amount" from total_donation_calc order by "CB Lifetime Donation Amount" desc limit 10 """).to_df()
    
    excluded_rows_result = duckdb.query(excluded_rows_query).to_df()

    st.divider()
    st.subheader("Excluded/Filtered out rows")

    st.write(excluded_rows_result)

    st.divider()
    st.subheader("Top total donations")
    st.bar_chart(data=data_line,x="ID", y="Total amount",use_container_width=True)

    # st.write(data_line)