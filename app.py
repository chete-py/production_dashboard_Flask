import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import timedelta
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

app.secret_key = 'PfdRs1999@A-402'


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


df = None

@app.route("/")
def index(): 
    return render_template('form.html')

@app.route("/upload_file" , methods=['POST'])
def upload_file():
    global df

    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'
    
    if file:
        file_path = 'uploads/' + file.filename
        file.save(file_path)

        # Store the file path in a session variable
        session['uploaded_file_path'] = file_path

        return redirect(url_for('home'))  # Redirect to the /home route for rendering home.html

@app.route("/home")
def home():
    # Retrieve the uploaded file path from the session
    file_path = session.get('uploaded_file_path', None)

    if file_path:
        df, newdf, week_gp, week_receipted, week_credit, month_gp, month_receipted, month_credit = process_uploaded_file(file_path)
        return render_template('home.html', data=df, week_gp=week_gp, week_receipted=week_receipted, week_credit=week_credit, month_gp=month_gp, month_receipted=month_receipted, month_credit=month_credit)
    else:
        return 'No uploaded file found.'


@app.route("/tms")
def tms():
    #Retrieve the uploaded file path from the session
    file_path = session.get('uploaded_file_path', None)

    if file_path:
        if request.method == 'POST':
            selected_manager = request.form.get('manager')

            # Process the selected manager and filter the data
            df, newdf, week_gp, week_receipted, week_credit, month_gp, month_receipted, month_credit = process_uploaded_file(file_path)
            filtered_data = newdf[newdf['INTERMEDIARY'] == selected_manager]
            data_to_render = filtered_data.to_dict(orient='records')

            return render_template('tms.html', data=data_to_render, week_gp=week_gp, week_receipted=week_receipted, week_credit=week_credit, month_gp=month_gp, month_receipted=month_receipted, month_credit=month_credit)

        else:
            # Initial rendering without manager selection
            df, newdf, week_gp, week_receipted, week_credit, month_gp, month_receipted, month_credit = process_uploaded_file(file_path)
            return render_template('tms.html', data=df, week_gp=week_gp, week_receipted=week_receipted, week_credit=week_credit, month_gp=month_gp, month_receipted=month_receipted, month_credit=month_credit)

    else:
        return 'No uploaded file found..'
        

def process_uploaded_file(file_path):
    
    df = pd.read_excel(file_path, header=6)
    df2 = df[["TRANSACTION DATE", "BRANCH", "INTERMEDIARY TYPE", "INTERMEDIARY", "PRODUCT", "PORTFOLIO MIX", "SALES TYPE", "STAMP DUTY", "SUM INSURED", "GROSS PREMIUM", "NET BALANCE", "RECEIPTS", "TM"]].copy()
    df2.loc[df2['INTERMEDIARY'] == 'GWOKA INSURANCE AGENCY', 'BRANCH'] = 'Head Office'
    # Convert the 'Date' column to datetime format
    df2['TRANSACTION DATE'] = pd.to_datetime(df2['TRANSACTION DATE'] , format='%m/%d/%Y')    
    # Replace all occurrences of 2023 with 1/11/2024
    df2['TRANSACTION DATE'] =  df2['TRANSACTION DATE'].mask( df2['TRANSACTION DATE'].dt.year == 2023, '2024-01-11')
    # Extract the day of the week, month and create new columns
    df2['DayOfWeek'] = df2['TRANSACTION DATE'].dt.day_name()
    df2['MONTH NAME'] = df2['TRANSACTION DATE'].dt.strftime('%B')
    df2['MONTH NAME'] = df2['MONTH NAME'].str.upper()

    # Create a pandas Timestamp object
    most_current_date = df2['TRANSACTION DATE'].max()
    current_date = pd.to_datetime(most_current_date)

    timestamp = pd.Timestamp(current_date)
    current_month = timestamp.strftime('%B')
    current_month_name = current_month.upper()       
    

    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    account_data = worksheet_accounts.get_all_values()
    headers = account_data[0]
    account_data = account_data[1:]
    lastdf = pd.DataFrame(account_data, columns=headers)  # Convert data to a DataFrame
    
    
    jointdf = pd.merge(df2, lastdf, on='INTERMEDIARY', how='left')
    jointdf.loc[jointdf['INTERMEDIARY'].str.contains('REIN', case=False, na=False), 'NEW TM'] = 'REINSURANCE'
    jointdf = jointdf[["TRANSACTION DATE", "BRANCH", "INTERMEDIARY TYPE", "INTERMEDIARY", "PRODUCT", "PORTFOLIO MIX", "SALES TYPE", "SUM INSURED", "GROSS PREMIUM", "NET BALANCE", "RECEIPTS", "NEW TM", "MONTH NAME", "DayOfWeek"]].copy()
    
    newdf = jointdf.dropna(subset='TRANSACTION DATE')

    # THIS MONTH
    this_month = newdf.loc[newdf['MONTH NAME'] == current_month_name].copy()
    month_gp = this_month['GROSS PREMIUM'].sum()   
    month_receipted = this_month['RECEIPTS'].sum()  
    month_credit = this_month['NET BALANCE'].sum()
 
    
    # Get transactions done in the current week
    this_week = newdf.loc[((newdf['TRANSACTION DATE']).dt.date >= start_of_week.date()) & ((newdf['TRANSACTION DATE']).dt.date <= end_of_week.date())].copy()
    week_gp = this_week['GROSS PREMIUM'].sum()   
    week_receipted = this_week['RECEIPTS'].sum() 
    week_credit = this_week['NET BALANCE'].sum()

    unique_manager = newdf['NEW TM'].unique().tolist()

    session['unique_manager'] = unique_manager
    
    df = df2.to_dict(orient='records')
    return df, newdf, week_gp, week_receipted, week_credit, month_gp, month_receipted, month_credit


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



    