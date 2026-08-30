import json

import pytest

from cloggle.item_defs import apply_item_defs
from cloggle.models import Item


def write_item_def(tmp_path, item_id, **data):
    path = tmp_path / f"{item_id}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "id": item_id,
                **data,
            },
            file,
        )


def test_tradeable_weapon(tmp_path):
    write_item_def(
        tmp_path,
        4151,
        name="Abyssal whip",
        tradeable=True,
        geTradeable=True,
        wearPos1=3,
    )

    items = {
        4151: Item(
            id=4151,
            name="Abyssal whip",
        )
    }

    apply_item_defs(items, tmp_path)

    assert items[4151].tradeable is True
    assert items[4151].equipment_slot == "Weapon"


def test_untradeable_cape(tmp_path):
    write_item_def(
        tmp_path,
        6570,
        name="Fire cape",
        tradeable=False,
        wearPos1=1,
    )

    items = {
        6570: Item(
            id=6570,
            name="Fire cape",
        )
    }

    apply_item_defs(items, tmp_path)

    assert items[6570].tradeable is False
    assert items[6570].equipment_slot == "Cape"


def test_all_equipment_slots(tmp_path):
    expected = {
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

    items = {}

    for wear_pos, expected_slot in expected.items():
        item_id = 10000 + wear_pos

        items[item_id] = Item(
            id=item_id,
            name=f"Item {item_id}",
        )

        (tmp_path / f"{item_id}.json").write_text(
            json.dumps({
                "id": item_id,
                "name": f"Item {item_id}",
                "tradeable": True,
                "wearPos1": wear_pos,
            }),
            encoding="utf-8",
        )

    apply_item_defs(items, tmp_path)

    for wear_pos, expected_slot in expected.items():
        item_id = 10000 + wear_pos
        assert items[item_id].equipment_slot == expected_slot


def test_negative_wearpos_means_no_equipment_slot(tmp_path):
    write_item_def(
        tmp_path,
        995,
        name="Coins",
        tradeable=True,
        wearPos1=-1,
    )

    items = {
        995: Item(
            id=995,
            name="Coins",
        )
    }

    apply_item_defs(items, tmp_path)

    assert items[995].tradeable is True
    assert items[995].equipment_slot is "-"


def test_missing_item_definition(tmp_path):
    items = {
        4151: Item(
            id=4151,
            name="Abyssal whip",
        )
    }

    with pytest.raises(
        FileNotFoundError,
        match="Missing item definition for 4151",
    ):
        apply_item_defs(items, tmp_path)


def test_unknown_wearpos_raises(tmp_path):
    write_item_def(
        tmp_path,
        12345,
        name="Test item",
        tradeable=True,
        wearPos1=99,
    )

    items = {
        12345: Item(
            id=12345,
            name="Test item",
        )
    }

    with pytest.raises(ValueError, match="Unknown wearPos1 99"):
        apply_item_defs(items, tmp_path)

def test_tradeable_is_not_derived_from_price(tmp_path):
    items = {
        123: Item(
            id=123,
            name="Test item",
        )
    }

    (tmp_path / "123.json").write_text(
        json.dumps({
            "id": 123,
            "name": "Test item",
            "tradeable": True,
            "wearPos1": -1,
        }),
        encoding="utf-8",
    )

    apply_item_defs(items, tmp_path)

    assert items[123].tradeable is True

def test_non_tradeable_item(tmp_path):
    items = {
        456: Item(
            id=456,
            name="Test item",
        )
    }

    (tmp_path / "456.json").write_text(
        json.dumps({
            "id": 456,
            "name": "Test item",
            "tradeable": False,
            "wearPos1": -1,
            "cost": 100000,
        }),
        encoding="utf-8",
    )

    apply_item_defs(items, tmp_path)

    assert items[456].tradeable is False