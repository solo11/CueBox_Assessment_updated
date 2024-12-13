
# CueBox Assessment

Input csv files taken from: [google sheets file](https://docs.google.com/spreadsheets/d/1JO-oZ64DNJUQdsZwa0pwVNM29m0_-7fp8kb7wFG1jas/edit?gid=1098870409#gid=1098870409)

#### The repo has two parts:

 1. Python app
 2. Streamlit Web App

#### Python App

To run the python app, use the following commands

 - install the required packages
   `pip install -r requirements.txt` 
 - run the app
 `python main.py`

`/input`  path contains the input CSV files
   
The program will generate the output files in the `/output` folder

    
   #### Naming conventions for the input files:
  - `Input_Constituents.csv` - constituents fIle
 - `Input_Donation_History.csv` - donation history fIle
- `Input_Emails.csv` - emails fIle
#### Naming conventions for the output files:
-   `CueBox Constituents.csv` - constituents fIle
 - `CueBox Tags.csv` - tags count fIle
- `CueBox excluded.csv` - filtered/excluded rows fIle

#### Validation:
The program also generates an excluded rows file  `CueBox excluded.csv`, which included all the rows that were filtered out at every stage of the process. This is used to validate the output generated.

#### Web App:
The web app is also hosted at: https://cuebox.streamlit.app/

To run the web app locally use the following command
`python -m streamlit run App/app.py `

The webapp will open in `http://localhost:8501/`

### Assumptions and Decisions made:

- ID Column: The `Patron ID` is unique, and instead of generating a new ID column, the `Patron ID` is used. This approach also helps in maintaining standardized data ID across the system.
 - Gender column: the gender columns is misrepresented, corrected it to Martial status based on the data in the column
 - Assuming that if the primary email of a row is not present in the email file, then the row should be excluded 
 - The data for the output columns primary email 1 and primary email 2 comes from the constituent data file and not the email data file
- The company names a not typical for some rows and, those rows have been excluded
- The patron id 1288 has two entries in the constituent file; the record with the latest 'entered date' is included
- The Salutation specifies one of "Mr.", "Mrs.", "Ms.", "Dr.", or empty string - based on that the rows having the values as ‘Mr. and Mrs’ -have been inserted as empty string.
- Determining the type person/company: The rows having a value in the company column are categorised as company and the rows without them are categorised as person.
- For background informantion column - some values for marital status are `unknown` or `NULL` , I've not made any changes to these values and let them flow.
 
 Exclusion criteria - The rows satisfying these conditions were excluded:
 
 - Having `CB Created At` column null/empty
 - Rows having an primary email and the email not present in `Input_Emails.csv`  file
 - Rows categorised as person and having either last name, first name or both as null or empty
 - Rows categorised as company and having company name as null or empty
 - Rows having duplicate entries in the Constituents file, the row with the latest  
`CB Created At` date is included rest of the rows are excluded

#### Questions:
 - Can the Patron ID column be used as unique id as it's unique across the table.
 - Assumptions: Are all the assumptions correct, or do any need to be adjusted?
 - Email File Handling: The email file has multiple entries for a given Patron ID. How should this be handled, and what is its significance? Is the email file solely used to validate primary email values?
 - Salutation Standardization: How strict can the salutation be -  Ex: `Mrs Mr Mr. and Mrs.` here clearly the data is valid and correct except for a few variations.
 - Repeating Tags: Should repeating tags in the tags file be handled, and if so, how?
 - Output Filtering: Do both output tables `CueBox Constituents.csv and CueBox Tags.csv` use the same source data and filtering conditions?
- Type Determination: How should the Type column `Person or Company` be determined consistently?
- How to handle `unknown and null` values in marital status

General questions for example:
- How often is the data updated? 
- What are the downstream applications

#### Use of AI tools:
AI tools have been used to support repetative tasks, it has been in two places in this project - to generate case statement conditions for Salutation column and for Date column standardisation 

#### Use of AI Tools:
AI tools have been used to support repetitive tasks in this project. Specifically, they were applied in two areas:
Generating case statement conditions for standardizing the `Salutation` column and `Date` column

  


