from flask import Flask


def create_app(config_object: object | None = None) -> Flask:
	app = Flask(__name__, instance_relative_config=False)

	# Default config
	app.config.from_mapping(
		SECRET_KEY="dev",
		JSON_SORT_KEYS=False,
	)

	# Register blueprints (lazy import to avoid circular imports)
	try:
		from .landing.landing import landing_bp
		
		app.register_blueprint(landing_bp)
	except Exception:
		# If views/blueprint are not available, register a minimal route
		@app.route("/")
		def _index():
			return "Summit Flask app (factory) - no blueprint registered"

	return app

