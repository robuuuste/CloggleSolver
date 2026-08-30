import json
from pathlib import Path

from .models import Item


WEAR_POS_NAMES = {
    0: "Head",
    1: "Cape",
    2: "Amulet",
    3: "Weapon",
    4: "Torso",
    5: "Shield",
    6: "Arms",
    7: "Legs",
    8: "Hair",
    9: "Hands",
    10: "Boots",
    11: "Jaw",
    12: "Ring",
    13: "Ammo",
}


def apply_item_defs(
    items: dict[int, Item],
    item_defs_dir: str | Path,
    *,
    missing_ok: bool = False,
) -> None:
    """
    Apply per-item definitions.

    - `missing_ok`: if True, missing item-id JSONs are skipped with a warning instead of raising.
    """
    item_defs_dir = Path(item_defs_dir)

    # Optional source->regions mapping file (placed alongside per-item JSONs)
    source_regions_path = item_defs_dir / "source_regions.json"
    source_regions: dict[str, set[str]] = {}
    if source_regions_path.exists():
        with source_regions_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        # support three mapping modes (list default, dict with patterns/default, mode: "manual")
        # Normalize simple list mappings to sets. Complex pattern handling is left to scripts.
        for k, v in raw.items():
            if isinstance(v, list):
                source_regions[k.lower()] = set(v)
            elif isinstance(v, dict):
                # prefer explicit 'default' key when present
                if "default" in v and isinstance(v["default"], list):
                    source_regions[k.lower()] = set(v["default"])
                # else ignore at runtime (patterns handled by bake scripts)
    for item_id, item in items.items():
        path = item_defs_dir / f"{item_id}.json"

        if not path.exists():
            if missing_ok:
                # skip silently but leave item fields as-is
                continue
            raise FileNotFoundError(
                f"Missing item definition for {item_id} ({item.name!r})"
            )

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        item.tradeable = data.get("tradeable")

        wear_pos = data.get("wearPos1", -1)
        if wear_pos >= 0:
            if wear_pos not in WEAR_POS_NAMES:
                raise ValueError(f"Unknown wearPos1 {wear_pos}")
            item.equipment_slot = WEAR_POS_NAMES[wear_pos]
        else:
            # Explicitly mark items that cannot be equipped so they behave like other slots
            item.equipment_slot = "-"

        # Merge regions: explicit per-item regions + regions inferred from sources
        regions: set[str] = set()
        per_item = data.get("regions")
        if per_item:
            regions.update(per_item)

        for src in item.sources:
            mapped = source_regions.get(src.lower())
            if mapped:
                regions.update(mapped)

        if regions:
            item.regions = regions