from flask import Blueprint, current_app, render_template

landing_bp = Blueprint("main", __name__, template_folder="templates")

@landing_bp.route("/")
def index():
    return render_template("index.html")

@landing_bp.route("/about")
def about():
    return render_template("about.html")