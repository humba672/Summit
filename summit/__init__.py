from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()


def create_app(config_object: object | None = None) -> Flask:
	app = Flask(__name__, instance_relative_config=False)

	login_manager = LoginManager()
	login_manager.login_view = "auth.login"
	login_manager.init_app(app)

	app.config.from_mapping(
        SECRET_KEY="askdfaksdfjkhafdfshdh",
        SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite",
    )

	db.init_app(app)

	from .auth.userModel import User

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	from .landing.landing import landing_bp	
	from .auth.auth import auth_bp

	app.register_blueprint(auth_bp)
	app.register_blueprint(landing_bp)

	return app

