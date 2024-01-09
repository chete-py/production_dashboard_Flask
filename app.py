import pandas as pd

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")

def home():
    # df = pd.read_csv('targets.csv')
    # names = df['TM']
    # output = names.to_list()
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



    