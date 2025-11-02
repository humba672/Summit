from flask import Blueprint, render_template, request, session, jsonify
from flask_login import login_required, current_user
from .. import db
from ..flashcards.vocabModels import setList, terms, userTerms
from fsrs import Scheduler, Card, Rating
from datetime import datetime, timezone, timedelta

scheduler = Scheduler()

flashcards_bp = Blueprint("flashcards", __name__, template_folder="templates")

def create_set(title, description, cards, ID, index=0):
    # Define a list of gradient colors for different sets
    gradients = [
        "linear-gradient(135deg, #5D4037, #8D6E63, #A1887F, #BCAAA4)",
        "linear-gradient(135deg, #1A237E, #303F9F, #3F51B5, #7986CB)",
        "linear-gradient(135deg, #1B5E20, #2E7D32, #388E3C, #66BB6A)",
        "linear-gradient(135deg, #311B92, #512DA8, #673AB7, #9575CD)",
        "linear-gradient(135deg, #B71C1C, #C62828, #E53935, #EF5350)"
    ]
    
    # Use modulo to cycle through gradients if there are more sets than gradients
    gradient = gradients[index % len(gradients)]
    
    # For first set, include the carousel div opening tag
    carousel_start = """       <div class="carousel" id="mountain-carousel">""" if index == 0 else ""
    
    # Return the formatted HTML string
    return carousel_start + f"""
                <div class="mountain-set">
                    <div class="mountain-container">
                        <div class="mountain-shape" style="background: {gradient};">
                            <div class="mountain-content">
                                <h2 class="mountain-title" id="set-title-{index + 1}">{title}</h2>
                                <p class="mountain-description" id="set-desc-{index + 1}">{description}</p>
                                <div class="mountain-stats">
                                    <div class="stat">
                                        <div class="stat-value" id="set-cards-{index + 1}">{cards}</div>
                                        <div class="stat-label">Cards</div>
                                    </div>
                                </div>
                                <button class="btn" onclick="startStudying({ID})">
                                    <i class="fas fa-hiking"></i> Begin Ascent
                                </button>
                            </div>
                        </div>
                    </div>
                </div>"""

@flashcards_bp.route("/flashcards")
def flashcards():
    session['maxDue'] = 0
    session['new'] = []
    session['setid'] = request.args.get('set')
    session['maxNew'] = request.args.get('terms')
    set_instance = setList.query.filter_by(id=session['setid'], author_id=current_user.id).first()
    if not set_instance:
        return "Set not found", 404
    total_cards = terms.query.filter_by(set_list_id=set_instance.id).count()
    return render_template("flashcards.html", 
                         name=set_instance.name,
                         total_cards=total_cards,
                         set_id=session['setid'])

@flashcards_bp.route("/api/flashcards/<int:set_id>/card/<int:index>")
@login_required
def get_card(set_id, index):
    set_instance = setList.query.filter_by(id=set_id, author_id=current_user.id).first()
    if not set_instance:
        return {"error": "Set not found"}, 404
    
    terms_list = terms.query.filter_by(set_list_id=set_instance.id).all()
    if 0 <= index < len(terms_list):
        term = terms_list[index]
        return {
            "front": term.term,
            "back": term.definition,
            "index": index,
            "total": len(terms_list)
        }
    else:
        return {"error": "Card index out of range"}, 404

@login_required
@flashcards_bp.route("/selection")
def selection():
    cat = request.args.get('category')
    sets = setList.query.filter_by(author_id=current_user.id, category=cat).all()
    carousel = ""
    
    # Create carousel HTML for each set
    for i, s in enumerate(sets):
        card_count = terms.query.filter_by(set_list_id=s.id).count()
        carousel += create_set(
            s.name,
            s.description or "No description provided.",
            card_count,
            s.id,
            i  # Pass the index for gradient selection
        )
    
    # Add closing div if there are any sets
    if sets:
        carousel += "\n            </div>"  # Close the carousel div


    return render_template("selection.html", carousel=carousel, subject=cat)

@login_required
@flashcards_bp.route("/flashcards/next-card")
def next_card():
    try:
        set_id = int(session.get("setid"))
    except (TypeError, ValueError):
        return {"error": "Missing or invalid set id in session"}, 400

    try:
        max_new = int(session.get("maxNew") or 0)
    except (TypeError, ValueError):
        max_new = 0

    if "new" not in session or not isinstance(session["new"], list):
        session["new"] = []

    selected_new_ids = set(session["new"])
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(minutes=5)  # review-due tolerance

    query = (
        userTerms.query
        .join(terms, userTerms.term_id == terms.id)
        .filter(
            userTerms.user_id == current_user.id,
            terms.set_list_id == set_id
        )
    ).all()

    review_due = []  # step > 0 and due soon
    new_pool  = []   # step == 0 (brand new / learning start)

    for ut in query:
        card = Card.from_json(ut.card_json)

        if getattr(card, "step", 0) == 0:
            new_pool.append((ut, card))
        else:
            # Only include review cards that are due soon
            if card.due <= cutoff:
                review_due.append((ut, card))

   
    new_due = []
    for ut, card in new_pool:
        if ut.term_id in selected_new_ids:
            new_due.append((ut, card))


    remaining = max(0, max_new - len(selected_new_ids))
    if remaining > 0:
        for ut, card in new_pool:
            if ut.term_id in selected_new_ids:
                continue
            session["new"].append(ut.term_id)
            selected_new_ids.add(ut.term_id)
            new_due.append((ut, card))
            remaining -= 1
            if remaining == 0:
                break

    review_due.sort(key=lambda x: x[1].due)  
    due_cards = review_due + new_due

    if not due_cards:
        current_user.altitude += 10
        db.session.commit()
        return {"message": "No more cards to review right now. Great job!"}, 204

    session["maxDue"] = max(session.get("maxDue", 0), len(due_cards))

    ut, card = due_cards[0]
    term_instance = terms.query.filter_by(id=ut.term_id).first()
    if not term_instance:
        return {"error": "Term not found"}, 404

    return jsonify({
        "card": {
            "front": term_instance.term,
            "back": term_instance.definition,
            "setId": set_id
        },
        "totalCards": session["maxDue"],
        "masteredCards": session["maxDue"] - len(due_cards),
        "currentCardID": ut.term_id
    })

    user_terms = userTerms.query.filter_by(user_id=current_user.id).all()
    due_cards = []
    for ut in user_terms:
        card = Card.from_json(ut.card_json)
        if card.due.timestamp() < (datetime.now(timezone.utc).timestamp() + 300):
            if card.step == 0:
                if len(session['new']) < int(session['maxNew']):
                    x = session['new']
                    x.append(ut.term_id)
                    session['new'] = x
                    due_cards.append((ut, card))
                else:
                    continue
            else:
                due_cards.append((ut, card))
    
    for k in session['new']:
        due_cards = [dc for dc in due_cards if dc[0].term_id != k]

    if not due_cards:
        return {'message': "No more cards to review right now. Great job!"}, 204

    if len(due_cards) > session.get('maxDue', 0):
        session['maxDue'] = len(due_cards)

    ut, card = due_cards[0]
    term_instance = terms.query.filter_by(id=ut.term_id).first()
    if not term_instance:
        return {"error": "Term not found"}, 404
    return jsonify({
        'card': {
            'front': term_instance.term,
            'back': term_instance.definition,
            'setId': session['setid']
        },
        'totalCards': session['maxDue'],
        'masteredCards': session['maxDue'] - len(due_cards),
        'currentCardID': ut.term_id
    })
    

@login_required
@flashcards_bp.route("/flashcards/report", methods=["POST"])
def report_progress():
    data = request.get_json()
    diff = data.get("difficulty")
    cardID = data.get("currentCardID")
    user_term = userTerms.query.filter_by(user_id=current_user.id, term_id=cardID).first() if cardID != 0 else userTerms.query.filter_by(user_id=current_user.id, term_id=1).first() 

    Card_data = Card.from_json(user_term.card_json)
    if diff == 0:
        rating = Rating.Again
    elif diff == 1:
        rating = Rating.Hard
    elif diff == 2:
        rating = Rating.Good 
    elif diff == 3:
        rating = Rating.Easy
    
    Card_data, _ = scheduler.review_card(Card_data, rating)
    time = Card_data.due - datetime.now(timezone.utc)
    time = time.total_seconds()
    user_term.card_json = Card_data.to_json()
    db.session.commit()

    return {"time": time}