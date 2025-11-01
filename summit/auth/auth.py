from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/sign-in")
def sign_in():
    return render_template("sign_in.html")