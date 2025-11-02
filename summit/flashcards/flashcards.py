from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .. import db
from ..flashcards.vocabModels import setList, terms, userTerms
from fsrs import Scheduler, Card, Rating

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
    setid = request.args.get('set')
    set_instance = setList.query.filter_by(id=setid, author_id=current_user.id).first()
    if not set_instance:
        return "Set not found", 404
    total_cards = terms.query.filter_by(set_list_id=set_instance.id).count()
    return render_template("flashcards.html", 
                         name=set_instance.name,
                         total_cards=total_cards,
                         set_id=setid)

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

@flashcards_bp.route("/flashcards/report", methods=["POST"])
def report_progress():
    data = request.get_json()
    term_id = data.get("cardIndex")