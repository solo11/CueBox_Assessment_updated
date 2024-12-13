import duckdb

query_2 = """CREATE or replace table tags_api as (SELECT * FROM read_json('https://6719768f7fc4c5ff8f4d84f1.mockapi.io/api/v1/tags'));"""

query = """with s as (select distinct "Patron ID", trim(UNNEST(STRING_SPLIT(tags, ','))) as tag from donation_constituents)

                SELECT tag as "CB Tag Name", count(*) "CB Tag Count" FROM s where tag in (select "name" from tags_api) GROUP BY tag"""



def execute_cb_tags():
    duckdb.connect('databases.db')

    duckdb.query(query_2)
    duckdb.query(f"""create table "CueBox Tags" as({query})""" )
    duckdb.query("""COPY "CueBox Tags" TO 'output/CueBox Tags.csv' (HEADER, DELIMITER ',')""")
    print("CueBox Tags file exported successfully")