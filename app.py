import pandas as pd
import gspread
from google.oauth2 import service_account
import openpyxl

# Define your Google Sheets credentials JSON file (replace with your own)
credentials_path = 'keys.json'

# Authenticate with Google Sheets using the credentials
credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://spreadsheets.google.com/feeds'])

# Authenticate with Google Sheets using gspread
gc = gspread.authorize(credentials)

# Your Google Sheets URL
url_acc = "https://docs.google.com/spreadsheets/d/1yQXPZ4zdI8aiIzYXzzuAwDS1V_Zg0fWU6OaqZ_VmwB0/edit#gid=0"
url_targ = "https://docs.google.com/spreadsheets/d/1yQXPZ4zdI8aiIzYXzzuAwDS1V_Zg0fWU6OaqZ_VmwB0/edit#gid=1885515628"

# Open the Google Sheets spreadsheet
worksheet_accounts = gc.open_by_url(url_acc).worksheet("accounts")
worksheet_targets = gc.open_by_url(url_targ).worksheet("targets")

data = worksheet_accounts.get_all_values()
    
# Prepare data for Plotly
headers = data[0]
data = data[1:]
newdf = pd.DataFrame(data, columns=headers)
five_rows = newdf.head(5)
TARGETS = five_rows.to_dict(orient='records')


  
df = None


from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index(): 
    return render_template('form.html')

@app.route("/home", methods=['GET', 'POST'])
def home():
    global df
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'
    
    if file:
        file_path = 'uploads/' + file.filename
        file.save(file_path)
        df = process_uploaded_file(file_path)
        return render_template('home.html', data=df, targets=TARGETS)


@app.route("/tms")
def tms():    
    return render_template('tms.html', data=df, targets=TARGETS)


def process_uploaded_file(file_path):
    import pandas as pd
    df = pd.read_excel(file_path)
    return df


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



    