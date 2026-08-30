#!/usr/bin/env python3
import argparse, json, sys
from cloggle.items import load_items
from cloggle.models import Feedback, Match, PriceRelation
from cloggle.solver import explain_filter

COL_DIR = "data/templeosrs"
PRICES = "data/ItemPrices.txt"
DEFS = "data/item_defs"

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guess", required=True, help="Guess item name (case-insensitive)")
    ap.add_argument("--region", choices=["match","no_match"], default="match")
    ap.add_argument("--price", choices=["lower","equal","higher"], default="equal")
    ap.add_argument("--tradeable", choices=["match","no_match"], default="no_match")
    return ap.parse_args()

def to_match(s):
    return Match.MATCH if s=="match" else Match.NO_MATCH

def main():
    args = parse_args()
    items = load_items(COL_DIR, PRICES, DEFS)
    all_items = list(items.values())
    guess = next((i for i in all_items if i.name and i.name.lower()==args.guess.lower()), None)
    if not guess:
        print("Guess not found:", args.guess)
        sys.exit(2)
    fb = Feedback(
        tradeable=to_match(args.tradeable),
        price=PriceRelation(args.price),
        equipment_slot=Match.NO_MATCH,
        region=to_match(args.region),
        category=Match.NO_MATCH,
        source=Match.NO_MATCH,
        name=Match.NO_MATCH,
    )
    kept, excluded = explain_filter(all_items, guess, fb)
    print("Kept count:", len(kept))
    print()
    target = next((i for i in all_items if i.name and i.name.lower()=="abyssal whip"), None)
    if target:
        if target.id in excluded:
            print("Abyssal whip excluded because:")
            for r in excluded[target.id]:
                print(" -", r)
        else:
            print("Abyssal whip is kept.")
    print()
    # show some kept candidates
    print("Example kept (first 30):")
    for c in kept[:30]:
        print(c.id, c.name, c.regions, c.price)
    # optionally output excluded reasons count
    print()
    print("Excluded count:", len(excluded))

if __name__=="__main__":
    main()