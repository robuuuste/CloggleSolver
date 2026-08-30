#!/usr/bin/env python3
"""
scripts/prune_item_defs.py

Prune unwanted keys from per-item JSON files.

Usage examples:
  # Dry-run and show stats, write to data/item_defs_pruned/
  python scripts/prune_item_defs.py --dry-run

  # Actually write pruned files to data/item_defs_pruned/
  python scripts/prune_item_defs.py

  # In-place pruning with backups (.bak)
  python scripts/prune_item_defs.py --in-place

  # Add extra keys to keep
  python scripts/prune_item_defs.py --keep params placeholderId

  # Specify output directory
  python scripts/prune_item_defs.py --out-dir data/item_defs_trimmed
"""
from pathlib import Path
import json
import argparse
import shutil

ROOT = Path(".")
ITEM_DEFS = ROOT / "data" / "item_defs"

DEFAULT_KEEP = {
    "id",
    "name",
    "examine",
    "tradeable",
    "geTradeable",
    "wearPos1",
    "wearPos2",
    "wearPos3",
    "regions",
    "members"
}

def prune_file(path: Path, keep_keys: set[str]) -> tuple[int,int]:
    """Return (keys_removed, original_size - new_size)"""
    data = json.loads(path.read_text(encoding="utf-8"))
    orig_keys = set(data.keys())
    new_data = {k: data[k] for k in orig_keys & keep_keys}
    # Ensure id & name preserved if present
    if "id" in data and "id" not in new_data:
        new_data["id"] = data["id"]
    if "name" in data and "name" not in new_data:
        new_data["name"] = data["name"]
    orig_size = path.stat().st_size
    new_json = json.dumps(new_data, ensure_ascii=False, indent=2)
    new_size = len(new_json.encode("utf-8"))
    keys_removed = len(orig_keys - set(new_data.keys()))
    return keys_removed, orig_size - new_size, new_data

def main(dry_run=True, out_dir=None, in_place=False, keep_extra=()):
    keep = set(DEFAULT_KEEP) | set(keep_extra)
    if out_dir is None and not in_place:
        out_dir = ITEM_DEFS.parent / (ITEM_DEFS.name + "_pruned")
    if out_dir:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in ITEM_DEFS.glob("*.json") if p.stem.isdigit())
    total_files = len(files)
    total_keys_removed = 0
    total_bytes_saved = 0
    changed_files = 0

    for p in files:
        keys_removed, bytes_saved, new_data = prune_file(p, keep)
        if keys_removed > 0:
            changed_files += 1
            total_keys_removed += keys_removed
            total_bytes_saved += max(0, bytes_saved)
            if dry_run:
                continue
            if in_place:
                bak = p.with_suffix(p.suffix + ".bak")
                shutil.copy2(p, bak)
                p.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                out_path = out_dir / p.name
                out_path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            # still copy if writing out-dir and not dry-run, to keep full set
            if not dry_run and out_dir and not in_place:
                out_path = out_dir / p.name
                out_path.write_text(json.dumps(json.loads(p.read_text(encoding="utf-8")), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Files scanned: {total_files}")
    print(f"Files changed: {changed_files}")
    print(f"Total keys removed: {total_keys_removed}")
    print(f"Estimated bytes saved: {total_bytes_saved}")
    if dry_run:
        print("Dry-run: no files were written. Re-run without --dry-run to apply.")
    else:
        if in_place:
            print("Pruned in-place; backups saved with .bak suffix.")
        else:
            print(f"Pruned files written to: {out_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Do not write files (default)")
    ap.add_argument("--apply", action="store_true", help="Write files (opposite of --dry-run)")
    ap.add_argument("--in-place", action="store_true", help="Modify files in place (creates .bak backups)")
    ap.add_argument("--out-dir", type=str, help="Directory to write pruned files")
    ap.add_argument("--keep", nargs="*", default=[], help="Additional keys to keep")
    args = ap.parse_args()
    dry = not args.apply
    main(dry_run=dry, out_dir=args.out_dir, in_place=args.in_place, keep_extra=args.keep)