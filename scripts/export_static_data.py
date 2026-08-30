"""Export the same fully enriched Item values used by the Python UI for Pages."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cloggle.items import load_items
items = load_items(ROOT / "data/templeosrs", ROOT / "data/ItemPrices.txt", ROOT / "data/item_defs")
payload = [{
    "id": item.id, "name": item.name, "price": item.price,
    "tradeable": item.tradeable, "equipment_slot": item.equipment_slot,
    "categories": sorted(item.categories), "sources": sorted(item.sources), "regions": sorted(item.regions),
} for item in items.values()]
(ROOT / "docs/data/items.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
