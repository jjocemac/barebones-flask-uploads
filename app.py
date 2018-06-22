import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    errors = []
    results = {}
    if request.method == "POST":
        # get text that the user has entered
        try:
            text = request.form['text']
            print(text)
        except:
            flash("text submission unsuccessful","danger")
            return redirect(url_for('upload'))
        # save the result to the DB:
        try:
            result = Result(text=text)
            db.session.add(result)
            db.session.commit()
            flash("Text successfully submitted to DB","success")
            return redirect(url_for('upload'))
        except:
            flash("Unable to add item to database","danger")
            return redirect(url_for('upload'))
    return render_template('upload.html', errors=errors)

@app.route('/download')
def download():
    results = Result.query.all()
    return render_template("download.html", results=results)

if __name__ == '__main__':
    app.run()
