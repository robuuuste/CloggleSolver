from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import Item
from .prices import parse_item_prices
from .templeosrs import load_collection_log
from .item_defs import apply_item_defs


@dataclass
class ItemPrice:
    name: str
    price: float


def build_price_index(
    source_prices: dict[str, dict[str, float]]
) -> dict[str, ItemPrice]:
    items: dict[str, ItemPrice] = {}

    for source_items in source_prices.values():
        for item_name, price in source_items.items():
            if item_name in items:
                if items[item_name].price != price:
                    raise ValueError(
                        f"Conflicting prices for {item_name!r}: "
                        f"{items[item_name].price} vs {price}"
                    )
                continue

            items[item_name] = ItemPrice(
                name=item_name,
                price=price,
            )

    return items


def apply_prices(
    items: dict[int, Item],
    source_prices: dict[str, dict[str, float]],
    *,
    source_priority: Iterable[str] | None = None,
    strict: bool = False,
) -> None:
    """
    Apply prices to `items`.

    - If `strict` is True, conflicts across sources raise via `build_price_index`.
    - Otherwise, prices are applied deterministically:
      * If `source_priority` is provided, it's tried first (in order).
      * Then remaining sources are tried in sorted order.
      * First match wins.
    """
    if strict:
        index = build_price_index(source_prices)
        for item in items.values():
            if item.name in index:
                item.price = index[item.name].price
        return

    # deterministic source order
    all_sources = list(source_prices.keys())
    if source_priority:
        priority = [s for s in source_priority if s in source_prices]
        remaining = [s for s in all_sources if s not in priority]
        ordered = priority + remaining
    else:
        ordered = all_sources

    for item in items.values():
        for src in ordered:
            src_items = source_prices.get(src, {})
            if item.name in src_items:
                item.price = src_items[item.name]
                break


def load_items(
    collection_log_dir: str | Path,
    prices_file: str | Path,
    item_defs_dir: str | Path,
) -> dict[int, Item]:
    items = load_collection_log(collection_log_dir)

    source_prices = parse_item_prices(prices_file)
    apply_prices(items, source_prices)

    apply_item_defs(items, item_defs_dir)

    return items