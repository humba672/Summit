from summit import db, create_app
from summit.auth.userModel import User

app = create_app()

with app.app_context():
    db.create_all()