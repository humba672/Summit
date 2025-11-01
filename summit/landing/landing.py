from flask import Blueprint, render_template

landing_bp = Blueprint("main", __name__, template_folder="templates")

@landing_bp.route("/")
def index():
    return render_template("index.html")

@landing_bp.route("/sign-in")
def sign_in():
    return render_template("sign_in.html")
