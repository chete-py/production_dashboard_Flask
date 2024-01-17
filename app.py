import pandas as pd


from flask import Flask, render_template

app = Flask(__name__)

df = pd.read_csv('targets.csv')
data = df['MONTH'].to_list()
newdf = df.dropna(subset='TOTAL')
thedf = newdf.loc[newdf['MONTH'] == ' NOVEMBER ']
names = thedf[['TM','TOTAL']]
TARGETS = names.to_dict(orient='records')



@app.route("/")

def home():
 
    return render_template('home.html', targets=TARGETS)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



    