from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

flashcards_bp = Blueprint("flashcards", __name__, template_folder="templates")

@flashcards_bp.route("/flashcards")
def flashcards():
    return render_template("flashcards.html")

@flashcards_bp.route("/selection")
def selection():
    return render_template("selection.html")