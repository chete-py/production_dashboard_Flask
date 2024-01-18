import pandas as pd
import gspread
from google.oauth2 import service_account

# Define your Google Sheets credentials JSON file (replace with your own)
credentials_path = 'keys.json'

# Authenticate with Google Sheets using the credentials
credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://spreadsheets.google.com/feeds'])

# Authenticate with Google Sheets using gspread
gc = gspread.authorize(credentials)

# Your Google Sheets URL
url = "https://docs.google.com/spreadsheets/d/1yQXPZ4zdI8aiIzYXzzuAwDS1V_Zg0fWU6OaqZ_VmwB0/edit#gid=0"

# Open the Google Sheets spreadsheet
worksheet_1 = gc.open_by_url(url).worksheet("accounts")
worksheet_2 = gc.open_by_url(url).worksheet("targets")

data = worksheet_1.get_all_values()
    
# Prepare data for Plotly
headers = data[0]
data = data[1:]
newdf = pd.DataFrame(data, columns=headers)


from flask import Flask, render_template

app = Flask(__name__)

df = pd.read_csv('targets.csv')
data = df['MONTH'].to_list()
newdf = df.dropna(subset='TOTAL')
thedf = newdf.loc[newdf['MONTH'] == ' NOVEMBER ']
names = thedf[['TM','TOTAL']]
TARGETS = names.to_dict(orient='records')

print(newdf)

@app.route("/")

def home():
 
    return render_template('home.html', targets=TARGETS)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



    