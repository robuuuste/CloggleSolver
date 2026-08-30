from cloggle.comparator import compare
from cloggle.models import Item, Match, PriceRelation


def test_ranger_boots_against_armadyl_helmet():
    ranger_boots = Item(
        name="Ranger boots",
        tradeable=True,
        price=32_124_144,
        equipment_slot="feet",
        regions={"Varies"},
        categories={"Clues"},
        sources={"medium_treasure_trails"},
    )

    armadyl_helmet = Item(
        name="Armadyl helmet",
        tradeable=True,
        price=5_000_000,
        equipment_slot="head",
        regions={"Troll Country"},
        categories={"Bosses"},
        sources={"Kree'arra"},
    )

    feedback = compare(ranger_boots, armadyl_helmet)

    assert feedback.tradeable == Match.MATCH
    assert feedback.price == PriceRelation.LOWER
    assert feedback.equipment_slot == Match.NO_MATCH
    assert feedback.region == Match.NO_MATCH
    assert feedback.category == Match.NO_MATCH
    assert feedback.source == Match.NO_MATCH
    assert feedback.name == Match.NO_MATCH


def test_multiple_values():
    abyssal_whip = Item(
        name="Abyssal whip",
        tradeable=True,
        price=2_000_000,
        equipment_slot="weapon",
        regions={"Other Planes", "Varies"},
        categories={"Bosses", "Other"},
        sources={"Abyssal Sire", "Slayer"},
    )

    chromium_ingot = Item(
        name="Chromium Ingot",
        tradeable=True,
        price=1_000_000,
        equipment_slot="Not Equippable",
        regions={"Other Planes", "Wilderness"},
        categories={"Bosses"},
        sources={"Leviathan"},
    )

    feedback = compare(abyssal_whip, chromium_ingot)

    assert feedback.tradeable == Match.MATCH
    assert feedback.price == PriceRelation.LOWER
    assert feedback.equipment_slot == Match.NO_MATCH
    assert feedback.region == Match.MATCH
    assert feedback.category == Match.MATCH
    assert feedback.source == Match.NO_MATCH
    assert feedback.name == Match.NO_MATCH

def test_multiple_values_partial_overlap():
    guess = Item(
        name="Guess",
        categories={"Bosses", "Other"},
        sources={"Abyssal Sire", "Slayer"},
    )

    answer = Item(
        name="Answer",
        categories={"Bosses"},
        sources={"Kree'arra"},
    )

    feedback = compare(guess, answer)

    assert feedback.category == Match.MATCH
    assert feedback.source == Match.NO_MATCH

def test_multiple_values_no_overlap():
    guess = Item(
        name="Guess",
        categories={"Bosses", "Other"},
        sources={"Abyssal Sire", "Slayer"},
    )

    answer = Item(
        name="Answer",
        categories={"Raids"},
        sources={"Zulrah"},
    )

    feedback = compare(guess, answer)

    assert feedback.category == Match.NO_MATCH
    assert feedback.source == Match.NO_MATCH