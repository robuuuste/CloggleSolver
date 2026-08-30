from cloggle.items import apply_prices, build_price_index
from cloggle.models import Item
import pytest


def test_apply_prices_deterministic_by_priority():
    items = {
        1: Item(id=1, name="Foo"),
        2: Item(id=2, name="Bar"),
    }
    source_prices = {
        "a": {"Foo": 10.0},
        "b": {"Foo": 11.0, "Bar": 20.0},
    }

    # without priority: uses sorted source order -> 'a' before 'b'
    apply_prices(items, source_prices)
    assert items[1].price == 10.0
    assert items[2].price == 20.0

    # with explicit priority preferring 'b'
    items = {k: Item(id=v.id, name=v.name) for k, v in items.items()}
    apply_prices(items, source_prices, source_priority=["b"])
    assert items[1].price == 11.0
    assert items[2].price == 20.0


def test_build_price_index_conflict_raises():
    source_prices = {
        "a": {"Foo": 10.0},
        "b": {"Foo": 11.0},
    }
    with pytest.raises(ValueError):
        build_price_index(source_prices)