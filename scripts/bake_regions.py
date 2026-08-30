#!/usr/bin/env python3
"""
Bake inferred regions into data/item_defs/<id>.json

Usage:
  python scripts/bake_regions.py        # apply changes
  python scripts/bake_regions.py --dry-run   # show what would change
  python scripts/bake_regions.py --report-only # only print items with no regions
"""
from pathlib import Path
import sys
import json
import re
import argparse

# allow running from repo/scripts without installing package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cloggle.templeosrs import load_collection_log

ROOT = Path(".")
DATA_DIR = ROOT / "data"
ITEM_DEFS_DIR = DATA_DIR / "item_defs"
SOURCE_REGIONS_FILE = ITEM_DEFS_DIR / "source_regions.json"


def load_source_regions(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    defaults: dict[str, set[str]] = {}
    patterns: dict[str, list[tuple[re.Pattern, set[str]]]] = {}
    manual: set[str] = set()

    for src, val in raw.items():
        key = src.lower()
        if isinstance(val, list):
            defaults[key] = set(val)
        elif isinstance(val, dict):
            if val.get("mode") == "manual":
                manual.add(key)
                continue
            pats = []
            for pat, regs in val.get("patterns", {}).items():
                pats.append((re.compile(pat, re.I), set(regs)))
            if pats:
                patterns[key] = pats
            if "default" in val:
                defaults[key] = set(val["default"])
        else:
            # unknown type, ignore
            continue

    return defaults, patterns, manual


def infer_regions_for_item(item, per_item_regions, defaults, patterns, manual):
    # item: cloggle.models.Item
    regions = set(per_item_regions or ())
    name = item.name or ""
    for src in item.sources:
        key = src.lower()
        if key in manual:
            continue
        matched = False
        if key in patterns:
            for pat, regs in patterns[key]:
                if pat.search(name):
                    regions.update(regs)
                    matched = True
        if not matched and key in defaults:
            regions.update(defaults[key])
    return regions


def main(dry_run=False, report_only=False):
    if not SOURCE_REGIONS_FILE.exists():
        print(f"Missing {SOURCE_REGIONS_FILE}, aborting.")
        return 2

    defaults, patterns, manual = load_source_regions(SOURCE_REGIONS_FILE)

    items = load_collection_log(DATA_DIR / "templeosrs")  # dict[id, Item]

    changed = []
    no_regions = []

    for item_id, item in items.items():
        path = ITEM_DEFS_DIR / f"{item_id}.json"
        if not path.exists():
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Failed to read {path}: {exc}")
            continue

        per_item = data.get("regions", [])
        override = bool(data.get("regions_override"))

        if override:
            # respect explicit override — still record if none present
            if not per_item:
                no_regions.append((item_id, item.name))
            continue

        inferred = infer_regions_for_item(item, per_item, defaults, patterns, manual)

        if not inferred:
            no_regions.append((item_id, item.name))

        # sort for deterministic output
        inferred_list = sorted(inferred)
        if set(per_item) != set(inferred_list):
            changed.append((path, per_item, inferred_list))
            if not dry_run and not report_only:
                data["regions"] = inferred_list
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # summary
    if report_only:
        print("Items lacking regions (candidates for manual edit):")
        for iid, name in no_regions:
            print(f"{iid}\t{name}")
        return 0

    if dry_run:
        print("Dry run — files that would be changed:")
    else:
        print("Files changed:")

    for path, old, new in changed:
        print(f"- {path}: {len(old)} -> {len(new)} regions")

    print()
    print(f"Items with no inferred regions: {len(no_regions)} (see list)")
    for iid, name in no_regions[:50]:
        print(f"{iid}\t{name}")
    if len(no_regions) > 50:
        print(f"... and {len(no_regions)-50} more")

    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Show changes without writing files")
    p.add_argument("--report-only", action="store_true", help="Only print items with no regions (no writes)")
    args = p.parse_args()
    sys.exit(main(dry_run=args.dry_run, report_only=args.report_only))