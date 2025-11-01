from flask import Blueprint, jsonify, current_app

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return "Summit Flask app (factory) - blueprint registered"


@main_bp.route("/health")
def health():
    return jsonify(status="ok", name=current_app.import_name)
