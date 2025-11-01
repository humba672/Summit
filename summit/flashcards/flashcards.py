from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

import re

flashcards_bp = Blueprint("flashcards", __name__, template_folder="templates")

@flashcards_bp.route("/flashcards")
def flashcards():
    return render_template("flashcards.html")



@flashcards_bp.route('/flashcards/import', methods=['POST'])
def import_flashcards():
    """Accept form POST with 'set_name' and 'flashcard_text'.

    This endpoint parses the submitted textarea format (one card per line,
    front | back) and returns a JSON summary. In a full app you'd persist
    to a database and redirect to the set view. For now we return a JSON
    response with counts so the client can show success.
    """
    set_name = request.form.get('set_name', '').strip()
    flashcard_text = request.form.get('flashcard_text', '').strip()

    if not set_name or not flashcard_text:
        return jsonify({'ok': False, 'message': 'Set name and flashcard text are required.'}), 400

    lines = [l.strip() for l in flashcard_text.splitlines() if l.strip()]
    cards = []
    for line in lines:
        parts = [p.strip() for p in re.split(r"\|", line, maxsplit=1)]
        if len(parts) >= 2 and parts[0] and parts[1]:
            cards.append({'front': parts[0], 'back': parts[1]})

    if not cards:
        return jsonify({'ok': False, 'message': 'No valid flashcards found.'}), 400

    # TODO: persist the cards (database). For now just return count.
    return jsonify({'ok': True, 'set_name': set_name, 'imported': len(cards)})