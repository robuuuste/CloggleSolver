import json
from pathlib import Path
from cloggle.models import Item
from cloggle.item_defs import apply_item_defs


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def test_infers_region_from_source(tmp_path):
    d = tmp_path / "item_defs"
    d.mkdir()
    item_id = 123
    _write_json(d / f"{item_id}.json", {"tradeable": True, "wearPos1": -1})
    _write_json(d / "source_regions.json", {"kalphite queen": ["Kharidian Desert"]})
    items = {item_id: Item(id=item_id, name="Test", sources={"kalphite queen"})}
    apply_item_defs(items, d)
    assert "Kharidian Desert" in items[item_id].regions


def test_unions_regions_from_multiple_sources(tmp_path):
    d = tmp_path / "item_defs"
    d.mkdir()
    item_id = 124
    _write_json(d / f"{item_id}.json", {"tradeable": True, "wearPos1": -1})
    _write_json(
        d / "source_regions.json",
        {
            "kalphite queen": ["Kharidian Desert"],
            "smoke devil": ["Wilderness"],
        },
    )
    items = {item_id: Item(id=item_id, name="Multi", sources={"kalphite queen", "smoke devil"})}
    apply_item_defs(items, d)
    assert items[item_id].regions == {"Kharidian Desert", "Wilderness"}