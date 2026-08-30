from .models import Item, Feedback, Match, PriceRelation


def values_match(
    guess: set[str],
    answer: set[str],
) -> bool:
    return bool(guess & answer)


def compare(guess: Item, answer: Item) -> Feedback:
# Price relation: if either price is missing, treat as EQUAL (no information)
    if guess.price is None or answer.price is None:
        price = PriceRelation.EQUAL
    else:
        if guess.price == answer.price:
            price = PriceRelation.EQUAL
        elif answer.price < guess.price:
            price = PriceRelation.LOWER
        else:
            price = PriceRelation.HIGHER

    return Feedback(
    tradeable=(
        Match.MATCH
        if guess.tradeable == answer.tradeable
        else Match.NO_MATCH
    ),

    price=price,

    equipment_slot=(
        Match.MATCH
        if (
            guess.equipment_slot is not None
            and answer.equipment_slot is not None
            and guess.equipment_slot == answer.equipment_slot
        )
        else Match.NO_MATCH
    ),

    region=(
        Match.MATCH
        if values_match(guess.regions, answer.regions)
        else Match.NO_MATCH
    ),

    category=(
        Match.MATCH
        if values_match(guess.categories, answer.categories)
        else Match.NO_MATCH
    ),

    source=(
        Match.MATCH
        if values_match(guess.sources, answer.sources)
        else Match.NO_MATCH
    ),

    name=(
        Match.MATCH
        if guess.name == answer.name
        else Match.NO_MATCH
    ),
)