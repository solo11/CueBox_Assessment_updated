import duckdb

# validation beigins
# check 1 - validate if every email in constituents table has an entry in emails table 

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


def validate():

    duckdb.connect('databases.db')
    duckdb.query(f"""create or replace table excluded as ({excluded_rows_query})""")
    duckdb.query("""COPY "excluded" TO 'output/CueBox excluded.csv' (HEADER, DELIMITER ',')""")
    print("Validation file generated")
