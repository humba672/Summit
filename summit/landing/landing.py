from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..flashcards.vocabModels import setList, terms, userTerms
from .. import db
from flask_login import login_required, current_user

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

@landing_bp.route("/landing")
def legacy_landing():
    return redirect(url_for("landing.index"), code=301)

@landing_bp.route("/home")
def index():
    return render_template("index.html")

@landing_bp.route("/about")
def about():
    return render_template("about.html")

@landing_bp.route("/sign-in")
def sign_in():
    return redirect(url_for("auth.sign_in"))

@login_required
@landing_bp.route("/learn")
def home():
    return render_template("home.html")

@login_required
@landing_bp.route("/createSet", methods=["POST"])
def create_set():
    set_name = request.form.get("set-name", "Untitled Set").strip()
    set_category = request.form.get("set-category").strip()
    flashcards_data = request.form.get("set-text", "").strip()

    if not flashcards_data:
        flash("Please provide flashcards data to create a set.", "error")
        return redirect(url_for("landing.home"))

    set_instance = setList.query.filter_by(name=set_name, category=set_category, author=current_user.id).first()

    if set_instance:
        flash("Name already in use.", "error")
        return redirect(url_for("landing.home"))

    set_instance = setList(name=set_name, category=set_category, author=current_user.id)
    db.session.add(set_instance)
    
    flashcards = []
    for line in flashcards_data.splitlines():
        if '|' in line:
            term, definition = line.split('|', 1)
        elif '\t' in line:
            term, definition = line.split('\t', 1)
        else:
            continue
        terms_instance = terms(term=term.strip(), definition=definition.strip(), set_list_id=set_instance.id)
        db.session.add(terms_instance)
    db.session.commit()
    if not flashcards:
        flash("No valid flashcards found in the provided data.", "error")
        return redirect(url_for("landing.home"))

    return render_template("flashcards.html", set_name=set_name, flashcards=flashcards)
