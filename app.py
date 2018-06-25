import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json
import boto3
from random import randint

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
UPLOAD_FOLDER = 'Uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

from models import Result

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        #Get file name
        try:
            newfile = request.files['file']
        except:
            flash("file submission unsuccessful","danger")
            return redirect(url_for('upload'))
        #No selected file
        if newfile.filename == '':
            flash('No file selected','danger')
            return redirect(url_for('upload'))
        #Get fields from web-form
        filename = secure_filename(newfile.filename)
        #Save the result to the DB
        try:
            result = Result(filename=filename)
            db.session.add(result)
            db.session.commit()
            id = result.id
        except:
            flash("Unable to add file to database","danger")
            return redirect(url_for('upload'))
        #Save the file
        try:
            newfile.save(os.path.join(UPLOAD_FOLDER,str(id)+'_'+filename))
            flash("File successfully uploaded","success")
            return redirect(url_for('upload'))
        except:
            flash("Added file to database but unable to save file","danger")
            return redirect(url_for('upload'))
    return render_template('upload.html')

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
    filepath = os.path.join(UPLOAD_FOLDER,id+'_'+filename)
    if os.path.exists(filepath):
        return send_from_directory(UPLOAD_FOLDER,id+'_'+filename,as_attachment=True,attachment_filename=filename)
    else:
        abort(404)

@app.route('/sign_s3/')
def sign_s3():
  S3_BUCKET = os.environ.get('S3_BUCKET')

  file_name = str(randint(100,999)) + request.args.get('file_name')
  file_type = request.args.get('file_type')

  s3 = boto3.client('s3','eu-west-2')

  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "private", "Content-Type": file_type},
    Conditions = [
      {"acl": "private"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.eu-west-2.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })

if __name__ == '__main__':
    app.run()
