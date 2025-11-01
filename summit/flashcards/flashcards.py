from flask import Blueprint, render_template

flashcards_bp = Blueprint("flashcards", __name__, template_folder="templates")

@flashcards_bp.route("/flashcards")
def flashcards():
    return render_template("flashcards.html")