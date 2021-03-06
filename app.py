import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import boto3
from random import randint
import json
import dropbox

app = Flask(__name__)
assert "APP_SETTINGS" in os.environ, "APP_SETTINGS environment variable not set"
assert "DATABASE_URL" in os.environ, "DATABASE_URL environment variable not set"
assert "AWS_ACCESS_KEY_ID" in os.environ, "AWS_ACCESS_KEY_ID environment variable not set"
assert "AWS_SECRET_ACCESS_KEY" in os.environ, "AWS_SECRET_ACCESS_KEY environment variable not set"
assert "S3_BUCKET" in os.environ, "S3_BUCKET environment variable not set"
assert "DROPBOX_KEY" in os.environ, "DROPBOX_KEY environment variable not set"
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import Result, Direct, Dropbox

def save_file_info_to_s3_db(filename):
    result = Result(filename=filename)
    db.session.add(result)
    db.session.commit()
    return result.id

def save_file_info_to_direct_db(filename_orig,filename_s3):
    direct = Direct(filename_orig=filename_orig,filename_s3=filename_s3)
    db.session.add(direct)
    db.session.commit()
    return

def save_file_info_to_dropbox_db(filename):
    dropbox = Dropbox(filename=filename)
    db.session.add(dropbox)
    db.session.commit()
    return dropbox.id

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

def download_file_from_s3(filename):
    bucket_name = app.config['S3_BUCKET']
    s3 = boto3.resource('s3','eu-west-2')
    s3.meta.client.download_file(
        bucket_name,
        filename,
        '/tmp/'+filename
    )
    return

def delete_file_from_s3(filename):
    bucket_name = app.config['S3_BUCKET']
    s3 = boto3.resource('s3','eu-west-2')
    s3.Object(bucket_name,filename).delete()
    return

def upload_file_to_dbx(file,filename):
    dbx = dropbox.Dropbox(app.config['DROPBOX_KEY'])
    response = dbx.files_upload(file.read(),'/'+filename,mute=True)

def download_file_from_dbx(filename):
    dbx = dropbox.Dropbox(app.config['DROPBOX_KEY'])
    response = dbx.files_download_to_file('/tmp/'+filename,'/'+filename)

def delete_file_from_dbx(filename):
    dbx = dropbox.Dropbox(app.config['DROPBOX_KEY'])
    print(filename)
    response = dbx.files_delete('/'+filename)

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
        id = save_file_info_to_s3_db(filename)
    except:
        flash("Unable to add file to database","danger")
        return redirect(url_for('upload'))
    #Upload file to S3 bucket:
    filename_in_s3 = str(id)+'_'+filename
    try:
        upload_file_to_s3(file, filename_in_s3)
    except:
        flash("Unable to upload file","danger")
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
    # Retrieve filename from DB:
    try:
        filename = db.session.query(Result.filename).filter(Result.id == id).one()[0]
    except:
        abort(404)
    if filename is None:
        abort(404)
    filename_in_s3 = str(id)+'_'+filename
    #Try to download the file from S3 bucket to /tmp if it's not already there:
    if not os.path.exists('/tmp/'+filename_in_s3):
        try:
            download_file_from_s3(filename_in_s3)
        except:
            flash("Unable to download file","danger")
            return redirect(url_for('download'))
    #Serve the file to the client:
    if os.path.exists('/tmp/'+filename_in_s3):
        return send_from_directory('/tmp',filename_in_s3,as_attachment=True,attachment_filename=filename)
    else:
        abort(404)

@app.route('/delete-file/<string:id>', methods=['POST'])
def delete_file(id):
    #Delete entry from DB:
    try:
        entry = Result.query.filter_by(id=id).one()
        filename = entry.filename
        db.session.delete(entry)
        db.session.commit()
    except:
        flash("Unable to delete file entry in database","danger")
        return redirect(url_for('download'))
    #Delete file from S3 bucket:
    filename_in_s3 = str(id)+'_'+filename
    try:
        delete_file_from_s3(filename_in_s3)
    except:
        flash("Unable to delete file","danger")
        return redirect(url_for('download'))
    flash("File successfully deleted","success")
    return redirect(url_for('download'))


@app.route('/direct-upload')
def direct_upload():
    return render_template('direct_upload.html')


@app.route('/submit-direct-upload-form',methods=['POST'])
def submit_direct_upload_form():
    #Get S3 filename:
    filename_s3 = request.form['filename_s3']
    #Retrieve original filename
    filename_orig = filename_s3[6:]
    #Save the file info to the DB:
    try:
        save_file_info_to_direct_db(filename_orig,filename_s3)
    except:
        flash("Unable to add file to database","danger")
        return redirect(url_for('direct_upload'))
    #Return with success:
    flash("File successfully uploaded","success")
    return redirect(url_for('direct_upload'))


@app.route('/direct-download')
def direct_download():
    results = Direct.query.all()
    return render_template("direct_download.html", results=results)


@app.route('/direct-download-file/<string:id>', methods=['POST'])
def direct_download_file(id):
    # Retrieve original and s3 filenames from DB:
    try:
        db_entry = Direct.query.filter_by(id=id).first()
        filename_orig = db_entry.filename_orig
        filename_s3 = db_entry.filename_s3
    except:
        abort(404)
    if filename_s3 is None:
        abort(404)
    #Try to download the file from S3 bucket to /tmp if it's not already there:
    if not os.path.exists('/tmp/'+filename_s3):
        try:
            download_file_from_s3(filename_s3)
        except:
            flash("Unable to download file","danger")
            return redirect(url_for('direct-download'))
    #Serve the file to the client:
    if os.path.exists('/tmp/'+filename_s3):
        return send_from_directory('/tmp',filename_s3,as_attachment=True,attachment_filename=filename_orig)
    else:
        abort(404)

@app.route('/direct-delete-file/<string:id>', methods=['POST'])
def direct_delete_file(id):
    #Delete entry from DB:
    try:
        entry = Direct.query.filter_by(id=id).one()
        filename_s3 = entry.filename_s3
        db.session.delete(entry)
        db.session.commit()
    except:
        flash("Unable to delete file entry in database","danger")
        return redirect(url_for('download'))
    #Delete file from S3 bucket:
    try:
        delete_file_from_s3(filename_s3)
    except:
        flash("Unable to delete file","danger")
        return redirect(url_for('direct_download'))
    flash("File successfully deleted","success")
    return redirect(url_for('direct_download'))

@app.route('/sign_s3/')
def sign_s3():
    bucket_name = app.config['S3_BUCKET']
    filename_orig = request.args.get('file_name')
    filename_s3 = str(randint(10000,99999)) + '_' + secure_filename(filename_orig)
    file_type = request.args.get('file_type')

    s3 = boto3.client('s3','eu-west-2')

    presigned_post = s3.generate_presigned_post(
      Bucket = bucket_name,
      Key = filename_s3,
      Fields = {"acl": "private", "Content-Type": file_type},
      Conditions = [
        {"acl": "private"},
        {"Content-Type": file_type}
      ],
      ExpiresIn = 3600
    )

    return json.dumps({
      'data': presigned_post,
      'url': 'https://%s.s3.eu-west-2.amazonaws.com/%s' % (bucket_name, filename_s3)
    })

@app.route('/sign_s3_download/')
def sign_s3_download():
    bucket_name = app.config['S3_BUCKET']
    id = request.args.get('id')
    # Retrieve original and s3 filenames from DB:
    db_entry = Direct.query.filter_by(id=id).first()
    filename_orig = db_entry.filename_orig
    filename_s3 = db_entry.filename_s3
    # Create and return pre-signed url:
    s3 = boto3.client('s3','eu-west-2')
    presigned_url = s3.generate_presigned_url(
      'get_object',
      Params = {'Bucket': bucket_name, 'Key': filename_s3},
      ExpiresIn = 3600
    )
    return json.dumps({
      'url': presigned_url,
    })

@app.route('/dropbox-upload')
def dropbox_upload():
    return render_template('dropbox-upload.html')

@app.route('/submit-dropbox-upload-form',methods=['POST'])
def submit_dropbox_upload_form():
    #Get file name:
    file = request.files['file']
    filename = secure_filename(file.filename)
    #Save the file info to the DB (get back row id):
    try:
        id = save_file_info_to_dropbox_db(filename)
    except:
        flash("Unable to add file to database","danger")
        return redirect(url_for('dropbox_upload'))
    #Upload file to dropbox:
    filename_in_dbx = str(id)+'_'+filename
    try:
        upload_file_to_dbx(file, filename_in_dbx)
    except:
        flash("Unable to upload file","danger")
        return redirect(url_for('dropbox_upload'))
    #Return with success:
    flash("File successfully uploaded","success")
    return redirect(url_for('dropbox_upload'))

@app.route('/dropbox-download')
def dropbox_download():
    results = Dropbox.query.all()
    return render_template("dropbox-download.html", results=results)

@app.route('/dropbox-download-file/<string:id>', methods=['POST'])
def dropbox_download_file(id):
    # Retrieve filename from DB:
    try:
        filename = db.session.query(Dropbox.filename).filter(Dropbox.id == id).one()[0]
    except:
        abort(404)
    if filename is None:
        abort(404)
    filename_in_dbx = str(id)+'_'+filename
    #Try to download the file from dropbox to /tmp if it's not already there:
    if not os.path.exists('/tmp/'+filename_in_dbx):
        try:
            download_file_from_dbx(filename_in_dbx)
        except:
            flash("Unable to download file","danger")
            return redirect(url_for('dropbox_download'))
    #Serve the file to the client:
    if os.path.exists('/tmp/'+filename_in_dbx):
        return send_from_directory('/tmp',filename_in_dbx,as_attachment=True,attachment_filename=filename)
    else:
        abort(404)

@app.route('/dropbox-delete-file/<string:id>', methods=['POST'])
def dropbox_delete_file(id):
    #Delete entry from DB:
    try:
        entry = Dropbox.query.filter_by(id=id).one()
        filename = entry.filename
        db.session.delete(entry)
        db.session.commit()
    except:
        flash("Unable to delete file entry in database","danger")
        return redirect(url_for('dropbox_download'))
    #Delete file from dropbox:
    filename_in_dbx = str(id)+'_'+filename
    try:
        delete_file_from_dbx(filename_in_dbx)
    except:
        flash("Unable to delete file","danger")
        return redirect(url_for('dropbox_download'))
    flash("File successfully deleted","success")
    return redirect(url_for('dropbox_download'))

if __name__ == '__main__':
    app.run()
