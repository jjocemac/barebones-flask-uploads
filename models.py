from app import db

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String())

    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return '<id {}>'.format(self.id)
