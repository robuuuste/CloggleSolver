from cloggle.items import (
    apply_prices,
    build_price_index,
    load_items,
)
from cloggle.models import Item


def test_build_price_index():
    source_prices = {
        "tempoross": {
            "Dragon harpoon": 2_982_336.5,
        },
        "slayer": {
            "Dragon harpoon": 2_982_336.5,
        },
        "barrows_chests": {
            "Ahrim's hood": 100_000.0,
        },
    }

    items = build_price_index(source_prices)

    assert "Dragon harpoon" in items
    assert "Ahrim's hood" in items

    assert items["Dragon harpoon"].price == 2_982_336.5
    assert items["Ahrim's hood"].price == 100_000.0

def test_apply_prices():
    items = {
        21028: Item(
            id=21028,
            name="Dragon harpoon",
        ),
    }

    source_prices = {
        "tempoross": {
            "Dragon harpoon": 2_982_336.5,
        },
    }

    apply_prices(items, source_prices)

    assert items[21028].price == 2_982_336.5

def test_load_real_items():
    items = load_items(
        "data/templeosrs",
        "data/ItemPrices.txt",
        "data/item_defs",
    )

    assert items

    dragon_harpoon = items[21028]

    assert dragon_harpoon.name == "Dragon harpoon"
    assert dragon_harpoon.price is not None

    assert dragon_harpoon.categories == {
        "bosses",
        "other",
    }

    assert dragon_harpoon.sources == {
        "tempoross",
        "slayer",
    }

def test_real_item_definitions():
    items = load_items(
        "data/templeosrs",
        "data/ItemPrices.txt",
        "data/item_defs",
    )

    whip = items[4151]
    assert whip.name == "Abyssal whip"
    # Price data is a checked-in snapshot; keep this assertion aligned with it.
    assert whip.price == 792096.5
    assert whip.tradeable is True
    assert whip.equipment_slot == "Weapon"

    fire_cape = items[6570]
    assert fire_cape.name == "Fire cape"
    assert fire_cape.tradeable is False
    assert fire_cape.equipment_slot == "Cape"
    assert fire_cape.regions == {"Karamja"}
