from flask import Blueprint, render_template, redirect, url_for

landing_bp = Blueprint(
    "landing",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/landing_static",
)

@landing_bp.route("/")
def root():
    """Make the sign-in screen the default landing experience."""
    return redirect(url_for("auth.sign_in"))

@landing_bp.route("/home")
@landing_bp.route("/landing")
def index():
    return render_template("index.html")

@landing_bp.route("/about")
def about():
    return render_template("about.html")

@landing_bp.route("/sign-in")
def sign_in():
    return redirect(url_for("auth.sign_in"))

@landing_bp.route("/learn")
def home():
    return render_template("home.html")
