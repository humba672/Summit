from flask import Flask


def create_app(config_object: object | None = None) -> Flask:
	"""Flask application factory.

	Args:
		config_object: Optional configuration object or mapping. If provided,
			it will be used via `app.config.from_object` or `app.config.from_mapping`.

	Returns:
		Configured Flask application.
	"""
	app = Flask(__name__, instance_relative_config=False)

	# Default config
	app.config.from_mapping(
		SECRET_KEY="dev",
		JSON_SORT_KEYS=False,
	)

	# Apply optional config object
	if config_object is not None:
		# Accept both mapping-like or object-like configs
		try:
			app.config.from_mapping(config_object)
		except Exception:
			app.config.from_object(config_object)

	# Register blueprints (lazy import to avoid circular imports)
	try:
		from .views import main_bp
		from .landing.landing import landing_bp
		
		app.register_blueprint(landing_bp)
		app.register_blueprint(main_bp)
	except Exception:
		# If views/blueprint are not available, register a minimal route
		@app.route("/")
		def _index():
			return "Summit Flask app (factory) - no blueprint registered"

	return app

