#!/usr/bin/env python3
"""
scripts/item_defs_db.py

Usage examples:
  # Build/refresh the DB
  python scripts/item_defs_db.py --build

  # List items missing regions
  python scripts/item_defs_db.py --list-missing

  # Open a specific item's JSON in your editor (or default app on Windows)
  python scripts/item_defs_db.py --open 6570

  # Export a CSV for manual editing
  python scripts/item_defs_db.py --export-csv missing_regions.csv

  # Apply (write) DB 'regions' values back into per-item JSON files
  python scripts/item_defs_db.py --apply
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sqlite3
import json
import argparse
import os
import csv
import subprocess

ROOT = Path(".")
DATA_DIR = ROOT / "data"
ITEM_DEFS_DIR = DATA_DIR / "item_defs"
TEMPLE_ITEMS = DATA_DIR / "templeosrs" / "items.json"
DB_PATH = ITEM_DEFS_DIR / "item_defs.db"

def open_sqlite(path: Path):
    return sqlite3.connect(str(path))

def build_db():
    if not TEMPLE_ITEMS.exists():
        print(f"Missing collection log: {TEMPLE_ITEMS}")
        return 2

    item_names = json.loads(TEMPLE_ITEMS.read_text(encoding="utf-8")).get("items", {})
    conn = open_sqlite(DB_PATH)
    cur = conn.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = OFF;
    BEGIN;
    CREATE TABLE IF NOT EXISTS items (
      id INTEGER PRIMARY KEY,
      name TEXT,
      sources TEXT,
      categories TEXT,
      regions TEXT,
      tradeable INTEGER,
      equipment_slot TEXT,
      path TEXT
    );
    DELETE FROM items;
    """)
    conn.commit()

    from cloggle.templeosrs import load_collection_log

    # mapping for wearPos1 -> name (same as in item_defs.py)
    WEAR_POS_NAMES = {
        0: "Head", 1: "Cape", 2: "Amulet", 3: "Weapon", 4: "Torso",
        5: "Shield", 6: "Arms", 7: "Legs", 8: "Hair", 9: "Hands",
        10: "Boots", 11: "Jaw", 12: "Ring", 13: "Ammo",
    }

    # load collection log items with sources/categories
    collection_items = load_collection_log(DATA_DIR / "templeosrs")  # dict[id, Item]

    for p in sorted(ITEM_DEFS_DIR.glob("*.json")):
        if not p.stem.isdigit():
            continue
        iid = int(p.stem)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue

        # prefer names from the collection log when available
        coll_item = collection_items.get(iid)
        name = (coll_item.name if coll_item else None) or data.get("name")
        sources = ",".join(sorted(coll_item.sources)) if coll_item else ""
        categories = ",".join(sorted(coll_item.categories)) if coll_item else ""

        # derive equipment_slot from wearPos1 if present
        wear_pos = data.get("wearPos1", -1)
        equip = WEAR_POS_NAMES.get(wear_pos)

        regions = data.get("regions", [])
        tradeable = int(bool(data.get("tradeable")))

        cur.execute(
            "INSERT INTO items(id,name,sources,categories,regions,tradeable,equipment_slot,path) VALUES(?,?,?,?,?,?,?,?)",
            (iid, name, sources, categories, json.dumps(regions, ensure_ascii=False), tradeable, equip, str(p))
        )
    conn.commit()
    conn.close()
    print(f"DB written: {DB_PATH}")
    print("Open it with a SQLite browser (DB Browser for SQLite) to query and edit.")

def list_missing(limit=200):
    if not DB_PATH.exists():
        print("DB not found. Run --build first.")
        return 2
    conn = open_sqlite(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id,name,regions,path FROM items WHERE regions IS NULL OR regions = '[]' OR TRIM(regions) = '' ORDER BY id")
    rows = cur.fetchall()
    print(f"Items missing regions: {len(rows)}")
    for r in rows[:limit]:
        print(f"{r[0]}\t{r[1]}\t{r[3]}")
    if len(rows) > limit:
        print(f"... and {len(rows)-limit} more")
    conn.close()

def export_csv(out_path: Path):
    if not DB_PATH.exists():
        print("DB not found. Run --build first.")
        return 2
    conn = open_sqlite(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id,name,sources,regions,path FROM items ORDER BY id")
    with out_path.open("w", newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id","name","sources","regions","path"])
        for id_, name, sources, regions, path in cur:
            w.writerow([id_, name or "", sources or "", regions or "[]", path or ""])
    conn.close()
    print(f"Exported CSV: {out_path}")

def open_json(item_id: int):
    p = ITEM_DEFS_DIR / f"{item_id}.json"
    if not p.exists():
        print(f"No JSON for {item_id}")
        return 2
    # Windows: use os.startfile, else use $EDITOR or open command
    if sys.platform.startswith("win"):
        os.startfile(str(p))
    else:
        editor = os.environ.get("EDITOR")
        if editor:
            subprocess.run([editor, str(p)])
        else:
            # fallback to xdg-open / open
            opener = "xdg-open" if sys.platform.startswith("linux") else "open"
            subprocess.run([opener, str(p)])
    return 0

def apply_back():
    """Write 'regions' column back to per-item JSONs for rows where regions is non-empty."""
    if not DB_PATH.exists():
        print("DB not found. Run --build first.")
        return 2
    conn = open_sqlite(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id,regions,path FROM items")
    changed = 0
    for iid, regions_json, path in cur:
        if not regions_json:
            continue
        try:
            regions = json.loads(regions_json)
        except Exception:
            continue
        p = Path(path)
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        prev = data.get("regions", [])
        if set(prev) != set(regions):
            data["regions"] = sorted(list(regions))
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            changed += 1
    conn.close()
    print(f"Wrote regions back to {changed} files.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--list-missing", action="store_true")
    ap.add_argument("--open", type=int, help="Open item <id>.json in editor")
    ap.add_argument("--export-csv", type=str, help="Export DB to CSV")
    ap.add_argument("--apply", action="store_true", help="Write DB 'regions' back into JSON files")
    args = ap.parse_args()
    if args.build:
        return build_db()
    if args.list_missing:
        return list_missing()
    if args.open:
        return open_json(args.open)
    if args.export_csv:
        return export_csv(Path(args.export_csv))
    if args.apply:
        return apply_back()
    ap.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())