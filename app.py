import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import boto3

app = Flask(__name__)
assert "APP_SETTINGS" in os.environ, "APP_SETTINGS environment variable not set"
assert "DATABASE_URL" in os.environ, "DATABASE_URL environment variable not set"
assert "AWS_ACCESS_KEY_ID" in os.environ, "AWS_ACCESS_KEY_ID environment variable not set"
assert "AWS_SECRET_ACCESS_KEY" in os.environ, "AWS_SECRET_ACCESS_KEY environment variable not set"
assert "S3_BUCKET" in os.environ, "S3_BUCKET environment variable not set"
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import Result

def save_file_info_to_db(filename):
    result = Result(filename=filename)
    db.session.add(result)
    db.session.commit()
    return result.id

def upload_file_to_s3(file, filename):
    bucket_name = app.config['S3_BUCKET']
    s3 = boto3.client('s3','eu-west-2')
    s3.upload_fileobj(
        file,
        bucket_name,
        filename,
        ExtraArgs={
            "ACL": "private",
            "ContentType": file.content_type
        }
    )
    return

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/submit-upload-form',methods=['POST'])
def submit_upload_form():
    #Get file name:
    file = request.files['file']
    filename = secure_filename(file.filename)
    #Save the file info to the DB (get back row id):
    try:
        id = save_file_info_to_db(filename)
    except:
        flash("Unable to add file to database","danger")
        return redirect(url_for('upload'))
    #Upload file to S3 bucket:
    filename_in_s3 = str(id)+'_'+filename
    print('test2')
    try:
        upload_file_to_s3(file, filename_in_s3)
    except:
        flash("Unable to upload file to s3 bucket","danger")
        return redirect(url_for('upload'))
    #Return with success:
    flash("File successfully uploaded","success")
    return redirect(url_for('upload'))

@app.route('/download')
def download():
    results = Result.query.all()
    return render_template("download.html", results=results)

@app.route('/download-file/<string:id>', methods=['POST'])
def download_file(id):
    try:
        filename = db.session.query(Result.filename).filter(Result.id == id).one()[0]
    except:
        abort(404)
    if filename is None:
        abort(404)
    filename_in_s3 = str(id)+'_'+filename
    return redirect(url_for('download'))

if __name__ == '__main__':
    app.run()
