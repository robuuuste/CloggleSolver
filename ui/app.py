from flask import Flask, render_template, request, redirect, url_for, flash
from cloggle import download as price_download
from cloggle import items as items_module
from cloggle.solver import Solver
from cloggle.models import Feedback, Match, PriceRelation, Item

COLLECTION_DIR = "data/templeosrs"
PRICES_FILE = "data/ItemPrices.txt"
ITEM_DEFS_DIR = "data/item_defs"

app = Flask(__name__)
app.secret_key = "dev"


def refresh_prices() -> None:
    try:
        price_download.download_item_prices(PRICES_FILE)
    except RuntimeError:
        pass


def format_price(value):
    if value is None:
        return "?"
    rounded = int(round(float(value)))
    return f"{rounded:,}"


app.jinja_env.globals["format_price"] = format_price

refresh_prices()
items_map = items_module.load_items(COLLECTION_DIR, PRICES_FILE, ITEM_DEFS_DIR)
all_items = list(items_map.values())
solver = Solver(all_items)


def parse_feedback_from_form(form):
    def is_match(name: str) -> bool:
        return "match" in form.getlist(name)

    def to_match_value(name: str):
        return Match.MATCH if is_match(name) else Match.NO_MATCH

    tradeable = to_match_value("tradeable")
    price_val = form.get("price")
    price = PriceRelation(price_val) if price_val in {p.value for p in PriceRelation} else PriceRelation.EQUAL
    equipment_slot = to_match_value("equipment_slot")
    region = to_match_value("region")
    category = to_match_value("category")
    source = to_match_value("source")
    name = to_match_value("name")

    return Feedback(
        tradeable=tradeable,
        price=price,
        equipment_slot=equipment_slot,
        region=region,
        category=category,
        source=source,
        name=name,
    )


@app.route("/", methods=["GET"])
def index():
    names = [i.name for i in all_items if i.name]
    requested_suggestion = (request.args.get("suggestion") or "").strip()
    reset_feedback = request.args.get("reset") == "1"
    best, score = solver.recommend_next_guess()
    suggested_name = best.name if best is not None else None
    return render_template(
        "index.html",
        candidates=solver.candidates,
        count=len(solver.candidates),
        names=names,
        suggestion=requested_suggestion or suggested_name,
        suggestion_score=score,
        reset_feedback=reset_feedback,
    )


@app.route("/guess", methods=["POST"])
def guess():
    guess_name = request.form.get("guess_name", "").strip()
    if not guess_name:
        flash("Please enter a guess name.")
        return redirect(url_for("index"))

    guess_item = next((i for i in all_items if i.name and i.name.lower() == guess_name.lower()), None)
    if not guess_item:
        flash(f"Unknown item: {guess_name}")
        return redirect(url_for("index"))

    feedback = parse_feedback_from_form(request.form)
    solver.apply_feedback(guess_item, feedback)
    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    solver.reset()
    return redirect(url_for("index", reset=1))


if __name__ == "__main__":
    app.run(debug=True)