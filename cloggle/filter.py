from .models import Item


def filter_items(
    items: list[Item],
    *,
    category: str | None = None,
    source: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[Item]:
    result = items

    if category is not None:
        result = [
            item
            for item in result
            if category in item.categories
        ]

    if source is not None:
        result = [
            item
            for item in result
            if source in item.sources
        ]

    if min_price is not None:
        result = [
            item
            for item in result
            if item.price is not None
            and item.price >= min_price
        ]

    if max_price is not None:
        result = [
            item
            for item in result
            if item.price is not None
            and item.price <= max_price
        ]

    return result