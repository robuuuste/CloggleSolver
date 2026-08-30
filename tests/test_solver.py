from cloggle.comparator import compare
from cloggle.models import Item
from cloggle.solver import Solver


def test_solver_multiple_guesses():
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

    dragon_boots = Item(
        name="Dragon boots",
        tradeable=True,
        price=200_000,
        equipment_slot="feet",
        regions={"Troll Country"},
        categories={"Other"},
        sources={"Slayer"},
    )

    solver = Solver([
        ranger_boots,
        armadyl_helmet,
        dragon_boots,
    ])

    # First guess: Ranger boots.
    feedback = compare(ranger_boots, armadyl_helmet)

    solver.apply_feedback(
        ranger_boots,
        feedback,
    )

    assert armadyl_helmet in solver.candidates
    assert ranger_boots not in solver.candidates
    assert dragon_boots not in solver.candidates

    # Second guess: Armadyl helmet.
    feedback = compare(armadyl_helmet, armadyl_helmet)

    solver.apply_feedback(
        armadyl_helmet,
        feedback,
    )

    assert solver.candidates == [armadyl_helmet]


def test_solver_caches_recommendation_until_candidates_change():
    first = Item(name="First", tradeable=True, price=10, equipment_slot="head")
    second = Item(name="Second", tradeable=True, price=20, equipment_slot="body")
    solver = Solver([first, second])

    first_result = solver.recommend_next_guess()
    second_result = solver.recommend_next_guess()

    assert first_result is second_result
    assert solver._recommendation_cache[2000] == first_result

    solver.apply_feedback(first, compare(first, second))

    assert solver._recommendation_cache == {}

    solver.reset()

    assert solver._recommendation_cache[2000] == first_result


def test_solver_prioritizes_sources_with_many_hard_items():
    tombs_source = "tombs_of_amascut"
    rift_source = "guardians_of_the_rift"
    misc_source = "miscellaneous"

    tombs_items = [
        Item(
            name=f"Tombs item {idx}",
            tradeable=False,
            equipment_slot=None,
            regions={"Kharidian Desert"},
            categories={"Bosses"},
            sources={tombs_source},
        )
        for idx in range(15)
    ]

    rift_items = [
        Item(
            name=f"Rift item {idx}",
            tradeable=False,
            equipment_slot="-",
            regions={"Kourend"},
            categories={"Bosses"},
            sources={rift_source},
        )
        for idx in range(9)
    ]

    misc_items = [
        Item(
            name=f"Misc item {idx}",
            tradeable=False,
            equipment_slot="-",
            regions={"Varies"},
            categories={"Other"},
            sources={misc_source},
        )
        for idx in range(14)
    ]

    safe_item = Item(
        name="Easy guess",
        tradeable=True,
        price=10,
        equipment_slot="head",
        regions={"Lumbridge"},
        categories={"Other"},
        sources={"easy_source"},
    )

    solver = Solver(tombs_items + rift_items + misc_items + [safe_item])
    guess, _ = solver.recommend_next_guess(
        guess_pool=solver.candidates,
        answer_pool=solver.candidates,
    )

    assert guess is not None
    assert tombs_source in guess.sources
    assert guess.name.startswith("Tombs item")