from app import db

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return '<id {}>'.format(self.id)
