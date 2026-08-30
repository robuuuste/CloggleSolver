import json
from cloggle.templeosrs import (
    build_items,
    load_collection_log,
)


def test_dragon_harpoon_multiple_sources():
    item_names = {
        21028: "Dragon harpoon",
    }

    categories = {
        "bosses": {
            "tempoross": [21028],
        },
        "other": {
            "slayer": [21028],
        },
    }

    items = build_items(item_names, categories)

    dragon_harpoon = items[21028]

    assert dragon_harpoon.name == "Dragon harpoon"

    assert dragon_harpoon.categories == {
        "bosses",
        "other",
    }

    assert dragon_harpoon.sources == {
        "tempoross",
        "slayer",
    }

def test_dragon_harpoon_from_real_data():
    items = load_collection_log("data/templeosrs")

    dragon_harpoon = items[21028]

    assert dragon_harpoon.name == "Dragon harpoon"

    assert dragon_harpoon.categories == {
        "bosses",
        "other",
    }

    assert dragon_harpoon.sources == {
        "tempoross",
        "slayer",
    }