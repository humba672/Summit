from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .. import db
from ..flashcards.vocabModels import setList, terms, userTerms

flashcards_bp = Blueprint("flashcards", __name__, template_folder="templates")

def create_set(title, description, cards, ID):
    temp = """       <div class="carousel" id="mountain-carousel">
                <div class="mountain-set">
                    <div class="mountain-container">
                        <div class="mountain-shape" style="background: linear-gradient(135deg, #5D4037, #8D6E63, #A1887F, #BCAAA4);">
                            <div class="mountain-content">
                                <h2 class="mountain-title" id="set-title-1">{}</h2>
                                <p class="mountain-description" id="set-desc-1">{}</p>
                                <div class="mountain-stats">
                                    <div class="stat">
                                        <div class="stat-value" id="set-cards-1">{}</div>
                                        <div class="stat-label">Cards</div>
                                    </div>
                                </div>
                                <button class="btn" onclick="startStudying({})">
                                    <i class="fas fa-hiking"></i> Begin Ascent
                                </button>
                            </div>
                        </div>
                    </div>
                </div>"""
    
    return temp.format(title, description, cards, ID)

@flashcards_bp.route("/flashcards")
def flashcards():
    return render_template("flashcards.html")

@login_required
@flashcards_bp.route("/selection")
def selection():
    print(current_user.id)
    sets = setList.query.filter_by(author_id=current_user.id).all()
    carousel = ""
    for s in sets:
        card_count = terms.query.filter_by(set_list_id=s.id).count()
        carousel += create_set(s.name, s.description or "No description provided.", card_count, s.id)
    return render_template("selection.html", carousel=carousel)