#!/usr/bin/env python3
"""
Annotate pruned item_defs JSONs with collection-log `sources` and `categories`.

Usage:
  # Dry-run show changes (default)
  python scripts/annotate_pruned_defs.py

  # Apply changes in-place (writes to files, creates .bak backups)
  python scripts/annotate_pruned_defs.py --apply --in-place

  # Write annotated files to output directory
  python scripts/annotate_pruned_defs.py --apply --out-dir data/item_defs_annotated

Options:
  --src-dir PATH   Directory to read JSONs from (default: data/item_defs_pruned)
  --apply          Write changes (default: dry-run)
  --in-place       Modify files in place (requires --apply). Creates .bak backups.
"""
from pathlib import Path
import sys
import json
import argparse
import shutil

# allow importing cloggle when running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cloggle.templeosrs import load_collection_log

ROOT = Path(".")
DATA_DIR = ROOT / "data"
DEFAULT_SRC_DIR = DATA_DIR / "item_defs_pruned"
TEMPLE_DIR = DATA_DIR / "templeosrs"

def load_collection_items():
    return load_collection_log(TEMPLE_DIR)

def annotate(src_dir: Path, out_dir: Path | None, apply: bool, in_place: bool):
    coll = load_collection_items()  # dict[id, Item]
    src_dir = Path(src_dir)
    if not src_dir.exists():
        print(f"Source dir not found: {src_dir}")
        return 2

    files = sorted(p for p in src_dir.glob("*.json") if p.stem.isdigit())
    changed = []
    for p in files:
        data = json.loads(p.read_text(encoding="utf-8"))
        iid = int(p.stem)
        coll_item = coll.get(iid)

        coll_sources = set(s for s in (coll_item.sources if coll_item else set()))
        coll_cats = set(c for c in (coll_item.categories if coll_item else set()))

        existing_sources = set(data.get("sources", []))
        existing_cats = set(data.get("categories", []))

        new_sources = sorted(existing_sources | coll_sources)
        new_cats = sorted(existing_cats | coll_cats)

        if new_sources == sorted(existing_sources) and new_cats == sorted(existing_cats):
            continue

        changed.append((p, new_sources, new_cats))

        if apply:
            if in_place:
                bak = p.with_suffix(p.suffix + ".bak")
                shutil.copy2(p, bak)
                data["sources"] = new_sources
                data["categories"] = new_cats
                p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                assert out_dir is not None
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / p.name
                data["sources"] = new_sources
                data["categories"] = new_cats
                out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # summary
    if not changed:
        print("No files require annotation.")
        return 0

    if apply:
        action = "Updated"
    else:
        action = "Would update (dry-run):"
    print(f"{action} {len(changed)} files:")
    for p, s, c in changed[:200]:
        print(f"{p}: sources={s or []}, categories={c or []}")
    if len(changed) > 200:
        print(f"... and {len(changed)-200} more")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-dir", type=str, default=str(DEFAULT_SRC_DIR))
    ap.add_argument("--out-dir", type=str)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--in-place", action="store_true", help="Modify files in place (creates .bak backups)")
    args = ap.parse_args()
    if args.in_place and not args.apply:
        print("--in-place requires --apply")
        return 2
    out_dir = Path(args.out_dir) if args.out_dir else None
    return annotate(Path(args.src_dir), out_dir, args.apply, args.in_place)

if __name__ == "__main__":
    raise SystemExit(main())