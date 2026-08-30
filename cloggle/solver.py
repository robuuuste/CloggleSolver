from .comparator import compare
from math import inf
from .models import Feedback, Item, Match, PriceRelation


class Solver:
    def __init__(self, candidates: list[Item]):
        self.all_candidates = candidates
        self.candidates = candidates.copy()
        self._recommendation_cache = {}
        self._initial_recommendation_cache = {}
        self._initial_recommendation_cache[2000] = self.recommend_next_guess()

    def apply_feedback(
        self,
        guess: Item,
        feedback: Feedback,
    ) -> None:
        self.candidates = filter_candidates(
            self.candidates,
            guess,
            feedback,
        )
        self._recommendation_cache.clear()

    def recommend_next_guess(self, *, guess_pool=None, answer_pool=None, max_guesses=2000):
        uses_current_candidates = guess_pool is None and answer_pool is None
        if uses_current_candidates and max_guesses in self._recommendation_cache:
            return self._recommendation_cache[max_guesses]

        guesses = guess_pool if guess_pool is not None else self.candidates
        answers = answer_pool if answer_pool is not None else self.candidates

        if not guesses or not answers:
            result = (None, float("inf"))
            if uses_current_candidates:
                self._recommendation_cache[max_guesses] = result
            return result

        if max_guesses is not None and len(guesses) > max_guesses:
            guesses = guesses[:max_guesses]

        # A dangerous guess is a hard item whose source bucket is crowded with other
        # hard items in the same region. That is the actual 15-guess risk pattern:
        # a source with 15 single-source, untradeable, - items is far more
        # likely to kill the run than a larger but less concentrated bucket like
        # miscellaneous. We rank by the local bucket size, not by the total count of
        # hard items in that source globally.
        source_weights = {
            g.id: _hard_bucket_size(g, answers)
            for g in guesses
            if g.id is not None
        }
        if any(weight > 0 for weight in source_weights.values()):
            guesses = sorted(
                guesses,
                key=lambda g: (
                    -(source_weights.get(g.id, 0)),
                    g.name or "",
                ),
            )

        best = None
        best_rank = None

        for g in guesses:
            partitions = {}
            for a in answers:
                fb = compare(g, a)
                key = (
                    fb.tradeable.value,
                    fb.price.value,
                    fb.equipment_slot.value,
                    fb.region.value,
                    fb.category.value,
                    fb.source.value,
                    fb.name.value,
                )
                partitions[key] = partitions.get(key, 0) + 1

            expected = sum((size / len(answers)) * size for size in partitions.values())

            source_weight = source_weights.get(g.id, 0)
            hard_item = _is_hard_guess_item(g)
            rank = (
                0 if source_weight > 0 or hard_item else 1,
                -source_weight,
                0 if hard_item else 1,
                expected,
            )

            if best_rank is None or rank < best_rank:
                best_rank = rank
                best = g

        result = (best, float("inf") if best is None else best_rank[3])
        if uses_current_candidates:
            self._recommendation_cache[max_guesses] = result
        return result

    def reset(self) -> None:
        self.candidates = self.all_candidates.copy()
        self._recommendation_cache = self._initial_recommendation_cache.copy()

def _is_hard_guess_item(item: Item) -> bool:
    return (
        item.tradeable is False
        and item.equipment_slot in (None, "-")
    )


def _hard_bucket_size(item: Item, pool: list[Item]) -> int:
    if len(item.sources) != 1 or not _is_hard_guess_item(item):
        return 0

    source = next(iter(item.sources))
    return sum(
        1
        for candidate in pool
        if candidate.tradeable is False
        and candidate.equipment_slot in (None, "-")
        and len(candidate.sources) == 1
        and source in candidate.sources
        and (
            not item.regions
            or not candidate.regions
            or bool(item.regions & candidate.regions)
        )
        and candidate.name != item.name
    )


def _hard_dead_end_bucket_size(item: Item, pool: list[Item]) -> int:
    return _hard_bucket_size(item, pool)

def _values_overlap(a: set[str], b: set[str]) -> bool:
    return bool(a and b and (a & b))


def _match_bool_field(guess_val, candidate_val, expected: Match) -> bool:
    # If either side is unknown (None), treat as wildcard (don't reject)
    if guess_val is None or candidate_val is None:
        return True
    actual = Match.MATCH if guess_val == candidate_val else Match.NO_MATCH
    return actual == expected


def _match_set_field(guess_set: set[str], candidate_set: set[str], expected: Match) -> bool:
    # If either set is empty, treat as wildcard
    if not guess_set or not candidate_set:
        return True
    actual = Match.MATCH if bool(guess_set & candidate_set) else Match.NO_MATCH
    return actual == expected


def _match_price(guess_price, candidate_price, expected: PriceRelation) -> bool:
    # If either price missing, treat as wildcard
    if guess_price is None or candidate_price is None:
        return True

    if guess_price == candidate_price:
        actual = PriceRelation.EQUAL
    elif candidate_price < guess_price:
        actual = PriceRelation.LOWER
    else:
        actual = PriceRelation.HIGHER

    return actual == expected


def filter_candidates(
    candidates: list[Item],
    guess: Item,
    feedback: Feedback,
) -> list[Item]:
    """
    Return candidates that could produce the given feedback
    when compared against the guess, treating unknown/missing item
    fields as wildcards (do not reject on those fields).
    """
    result = []
    for candidate in candidates:
        if not _match_bool_field(guess.tradeable, candidate.tradeable, feedback.tradeable):
            continue

        if not _match_price(guess.price, candidate.price, feedback.price):
            continue

        if not _match_bool_field(guess.equipment_slot, candidate.equipment_slot, feedback.equipment_slot):
            continue

        if not _match_set_field(guess.regions, candidate.regions, feedback.region):
            continue

        if not _match_set_field(guess.categories, candidate.categories, feedback.category):
            continue

        if not _match_set_field(guess.sources, candidate.sources, feedback.source):
            continue

        # Name is explicit: if guess or candidate name missing, treat as wildcard
        if guess.name is None or candidate.name is None:
            name_ok = True
        else:
            name_ok = (Match.MATCH if guess.name == candidate.name else Match.NO_MATCH) == feedback.name

        if not name_ok:
            continue

        result.append(candidate)

    return result

def explain_candidate(guess: Item, candidate: Item, feedback: Feedback) -> list[str]:
    """
    Return an empty list if candidate would be kept for the given feedback,
    otherwise return a list of human-readable reasons why it was rejected.
    """
    reasons: list[str] = []

    # tradeable
    if guess.tradeable is not None and candidate.tradeable is not None:
        actual = Match.MATCH if guess.tradeable == candidate.tradeable else Match.NO_MATCH
        if actual != feedback.tradeable:
            reasons.append(f"tradeable: guess={guess.tradeable} candidate={candidate.tradeable} -> expected {feedback.tradeable}")

    # price
    if guess.price is not None and candidate.price is not None:
        if guess.price == candidate.price:
            actual_price = PriceRelation.EQUAL
        elif candidate.price < guess.price:
            actual_price = PriceRelation.LOWER
        else:
            actual_price = PriceRelation.HIGHER
        if actual_price != feedback.price:
            reasons.append(f"price: guess={guess.price} candidate={candidate.price} -> {actual_price} != {feedback.price}")

    # equipment_slot
    if guess.equipment_slot is not None and candidate.equipment_slot is not None:
        actual = Match.MATCH if guess.equipment_slot == candidate.equipment_slot else Match.NO_MATCH
        if actual != feedback.equipment_slot:
            reasons.append(f"equipment_slot: guess={guess.equipment_slot} candidate={candidate.equipment_slot} -> expected {feedback.equipment_slot}")

    # regions
    if guess.regions and candidate.regions:
        actual = Match.MATCH if bool(guess.regions & candidate.regions) else Match.NO_MATCH
        if actual != feedback.region:
            reasons.append(f"regions: guess={guess.regions} candidate={candidate.regions} -> expected {feedback.region}")

    # categories
    if guess.categories and candidate.categories:
        actual = Match.MATCH if bool(guess.categories & candidate.categories) else Match.NO_MATCH
        if actual != feedback.category:
            reasons.append(f"categories: guess={guess.categories} candidate={candidate.categories} -> expected {feedback.category}")

    # sources
    if guess.sources and candidate.sources:
        actual = Match.MATCH if bool(guess.sources & candidate.sources) else Match.NO_MATCH
        if actual != feedback.source:
            reasons.append(f"sources: guess={guess.sources} candidate={candidate.sources} -> expected {feedback.source}")

    # name
    if guess.name is not None and candidate.name is not None:
        actual = Match.MATCH if guess.name == candidate.name else Match.NO_MATCH
        if actual != feedback.name:
            reasons.append(f"name: guess={guess.name!r} candidate={candidate.name!r} -> expected {feedback.name}")

    return reasons


def explain_filter(candidates: list[Item], guess: Item, feedback: Feedback) -> tuple[list[Item], dict[int, list[str]]]:
    """
    Returns (kept_candidates, excluded_reasons) where excluded_reasons maps candidate.id -> reasons list.
    """
    kept = []
    excluded: dict[int, list[str]] = {}
    for c in candidates:
        reasons = explain_candidate(guess, c, feedback)
        if reasons:
            excluded[c.id] = reasons
        else:
            kept.append(c)
    return kept, excluded