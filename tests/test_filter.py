from cloggle.filter import filter_items
from cloggle.models import Item


def test_filter_by_category():
    items = [
        Item(
            name="Boss item",
            categories={"bosses"},
        ),
        Item(
            name="Other item",
            categories={"other"},
        ),
    ]

    result = filter_items(
        items,
        category="other",
    )

    assert [item.name for item in result] == ["Other item"]


def test_filter_by_price():
    items = [
        Item(name="Cheap", price=1_000_000),
        Item(name="Middle", price=3_000_000),
        Item(name="Expensive", price=10_000_000),
    ]

    result = filter_items(
        items,
        min_price=2_000_000,
        max_price=5_000_000,
    )

    assert [item.name for item in result] == ["Middle"]


def test_filter_by_source():
    items = [
        Item(
            name="Dragon harpoon",
            sources={"tempoross", "slayer"},
        ),
        Item(
            name="Other item",
            sources={"zulrah"},
        ),
    ]

    result = filter_items(
        items,
        source="slayer",
    )

    assert [item.name for item in result] == ["Dragon harpoon"]