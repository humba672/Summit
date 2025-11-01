from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static", static_url_path="/auth_static")

@auth_bp.route("/sign-in")
def sign_in():
    return render_template("sign_in.html")