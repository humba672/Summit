from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/auth_static",
)

def _credentials_match(email: str, password: str) -> bool:
    """Return True when credentials match a stored or fallback account."""
    stored = session.get("registered_user")
    if stored:
        if (
            email.lower() == stored.get("email", "").lower()
            and password == stored.get("password", "")
        ):
            return True
    return email.lower() == "hackphs" and password == "hackphs"


@auth_bp.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if _credentials_match(email, password):
            session["signed_in"] = True
            session["signed_in_email"] = email or "hackphs"
            flash("Welcome back to Summit.", "success")
            return redirect(url_for("landing.index"))

        flash("We couldn't match those details. Try again or use hackphs / hackphs.", "error")

    return render_template("sign_in.html")


@auth_bp.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        fields = [("Name", name), ("Email", email), ("Password", password)]
        missing = [label for label, value in fields if not value]
        if missing:
            flash(f"Please fill in your {' and '.join(missing)}.", "error")
        else:
            session["registered_user"] = {"name": name, "email": email, "password": password}
            flash("All set! Sign in with your details or try hackphs / hackphs anytime.", "success")
            return redirect(url_for("auth.sign_in"))

    return render_template("sign_up.html")
