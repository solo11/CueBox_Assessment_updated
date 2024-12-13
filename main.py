import duckdb
from table_1 import execute_cb_constituents
from table_2 import execute_cb_tags
from validation import validate

# Creating tables from CSV files
def create_tables():
    duckdb.sql("create or replace table donation_constituents as (select * from './input/Input_Constituents.csv' )")
    duckdb.sql("create or replace  table donation_emails as (select * from './input/Input_Emails.csv' )") 
    duckdb.sql("create or replace  table donation_history as (select * from './input/Input_Donation_History.csv' )")

if __name__ == "__main__":
    duckdb.connect('databases.db')
    create_tables()
    validate()
    execute_cb_constituents()
    execute_cb_tags()
    