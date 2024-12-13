
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

#### Web App:
The web app is also hosted at: https://cuebox.streamlit.app/


Assusumptions

To run the web app locally use the following command
`python -m streamlit run App/app.py `

The webapp will open in `http://localhost:8501/`

### Assumptions and Decisions made:

 - Gender column: the gender columns is misrepresented, corrected it to Martial status based on the data in the column
 - Assuming that if the primary email of a row is not present in the email file, then the row should be excluded 
 - The data for the output columns primary email 1 and primary email 2 comes from the constituent data file and not the email data file
- The company names a not typical for some rows and, those rows have been excluded
- The patron id 1288 has two entries in the constituent file; the record with the latest 'entered date' is included
- The Salutation specifies one of "Mr.", "Mrs.", "Ms.", "Dr.", or empty string - based on that the rows having the values as ‘Mr. and Mrs’ -have been inserted as empty string.
- Determining the type person/company: The rows having a value in the company column are categorised as company and the rows without them are categorised as person. 
 
 Exclusion criteria - The rows satisfying these conditions were excluded:
 
 - Having `CB Created At` column null/empty
 - Rows having an primary email and the email not present in `Input_Emails.csv`  file
 - Rows categorised as person and having either last name, first name or both as null or empty
 - Rows categorised as company and having company name as null or empty
 - Rows having duplicate entries in the Constituents file, the row with the latest  
`CB Created At` date is included rest of the rows are excluded

#### Questions:

 - Are all the assumptions correct, does anything needs to be changed
 - The email file has multiple entires for a given patron id, does it needs to be handled, and what is the significance/importance of the email file - is it only used the validate the primary email value?
 - How strict can the salutation be -  Ex: Mrs Mr Mr. and Mrs. here clearly the data is valid and correct except for a few variations.
 - The tags are repeating, should it be handled?
 - Does both the output tables use the same source/filtering conditions
 -  How do you determine type person or company?

General questions for example:
- How often is the data updated? 
- What are the downstream applications


