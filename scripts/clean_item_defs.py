#!/usr/bin/env python3
"""
Find and optionally delete item_defs/<id>.json files that are not in the collection log.

Usage:
  python scripts/clean_item_defs.py         # dry-run (default)
  python scripts/clean_item_defs.py --delete    # delete matches (prompts)
  python scripts/clean_item_defs.py --delete --yes  # delete without prompt
"""
from pathlib import Path
import json
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ITEM_DEFS = DATA_DIR / "item_defs"
TEMPLE_ITEMS = DATA_DIR / "templeosrs" / "items.json"

def load_collection_item_ids(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k) for k in data.get("items", {}).keys()}

def find_orphan_defs(item_defs_dir: Path, collection_ids: set[int]):
    orphans = []
    for p in item_defs_dir.glob("*.json"):
        name = p.stem
        # skip mapping/metadata files which are not numeric
        if not name.isdigit():
            continue
        if int(name) not in collection_ids:
            orphans.append(p)
    return sorted(orphans)

def main(dry_run=True, delete=False, yes=False):
    if not TEMPLE_ITEMS.exists():
        print(f"Missing collection log: {TEMPLE_ITEMS}")
        return 2

    collection_ids = load_collection_item_ids(TEMPLE_ITEMS)
    orphans = find_orphan_defs(ITEM_DEFS, collection_ids)

    print(f"Found {len(orphans)} orphan item_def files (not in collection log).")
    if orphans:
        for p in orphans[:200]:
            print(p.relative_to(ROOT))
        if len(orphans) > 200:
            print(f"... and {len(orphans)-200} more")

    if delete:
        if dry_run:
            print("Note: --delete implies action; ignoring dry-run flag.")
        if not yes:
            resp = input("Delete these files? Type 'yes' to confirm: ")
            if resp.strip().lower() != "yes":
                print("Aborted.")
                return 0
        for p in orphans:
            try:
                p.unlink()
            except Exception as exc:
                print(f"Failed to delete {p}: {exc}")
        print(f"Deleted {len(orphans)} files.")
    else:
        print("Dry-run (no files deleted). Use --delete to remove them.")

    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--delete", action="store_true", help="Actually delete orphan files")
    ap.add_argument("--yes", action="store_true", help="Auto-confirm deletions")
    args = ap.parse_args()
    sys.exit(main(dry_run=not args.delete, delete=args.delete, yes=args.yes))