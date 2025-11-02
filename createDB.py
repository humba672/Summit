from summit import db, create_app
from summit.auth.userModel import User
from summit.flashcards.vocabModels import setList, terms, userTerms

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()