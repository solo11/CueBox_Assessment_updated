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

To run the web app locally use the following command
`python -m streamlit run App/app.py `

The webapp will open in `http://localhost:8501/`

