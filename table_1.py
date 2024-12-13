import duckdb

# The below query populates the intermediate table with the data transformation
# Adding 'CB Constituent Type' Column
# Date formating for "Date Entered" Column
# Adding "CB Title" Column
# Adding "CB Background Information" Column
# Filters the rows where "Date Entered" column is null

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
query_2 = """CREATE table tags_api as (SELECT * FROM read_json('https://6719768f7fc4c5ff8f4d84f1.mockapi.io/api/v1/tags'));"""
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
list(b.mapped_name) as "CB Tags",
a."CB Background Information"
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

def execute_cb_constituents():
  duckdb.connect('databases.db')

  duckdb.query(query_1)
  duckdb.query(query_2)
  duckdb.query(query_3)

  duckdb.sql("select * from CueBox_Constituents").show()
  duckdb.query("""COPY "CueBox_Constituents" TO 'output/CueBox Constituents.csv' (HEADER, DELIMITER ',')""")
  print("CueBox Constituents file exported successfully")