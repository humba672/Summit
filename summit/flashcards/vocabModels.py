from .. import db


class setList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<setList {self.name}>"

class terms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(150), unique=True, nullable=False)
    definition = db.Column(db.String(500), nullable=False)
    set_list_id = db.Column(db.Integer, db.ForeignKey('set_list.id'), nullable=False)

    def __repr__(self):
        return f"<terms {self.term}>"

class userTerms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'), nullable=False)
    card_json = db.Column(db.Text)
    
    def __repr__(self):
        return f"<userTerms UserID: {self.user_id}, TermID: {self.term_id}, Progress: {self.progress}>"