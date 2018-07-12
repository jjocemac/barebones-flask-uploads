from app import db

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String())

    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Direct(db.Model):
    __tablename__ = 'direct'

    id = db.Column(db.Integer, primary_key=True)
    filename_orig = db.Column(db.String())
    filename_s3 = db.Column(db.String())

    def __init__(self, filename_orig, filename_s3):
        self.filename_orig = filename_orig
        self.filename_s3 = filename_s3

    def __repr__(self):
        return '<id {}>'.format(self.id)
