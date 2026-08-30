"""Cross-language regression coverage for the browser solver's core behavior."""
import json
import subprocess
from pathlib import Path

from cloggle.comparator import compare
from cloggle.models import Item
from cloggle.solver import filter_candidates


ROOT = Path(__file__).resolve().parents[1]


def _payload(item: Item) -> dict:
    return {
        "id": item.id, "name": item.name, "price": item.price,
        "tradeable": item.tradeable, "equipment_slot": item.equipment_slot,
        "categories": sorted(item.categories), "sources": sorted(item.sources), "regions": sorted(item.regions),
    }


def test_browser_comparator_and_filter_match_python():
    guess = Item(id=1, name="Guess", tradeable=True, price=100, equipment_slot="Head", regions={"A", "B"}, categories={"boss"}, sources={"one"})
    answer = Item(id=2, name="Answer", tradeable=True, price=50, equipment_slot="Body", regions={"B"}, categories={"other"}, sources={"two"})
    unknown = Item(id=3, name="Unknown", tradeable=None, price=None, equipment_slot=None)
    items = [guess, answer, unknown]
    expected = compare(guess, answer)
    completed = subprocess.run(
        ["node", "tests-js/parity-runner.mjs"], cwd=ROOT,
        input=json.dumps({"items": [_payload(item) for item in items], "guessIndex": 0, "answerIndex": 1}),
        text=True, capture_output=True, check=True,
    )
    actual = json.loads(completed.stdout)
    assert actual["feedback"] == {name: value.value for name, value in expected.__dict__.items()}
    assert actual["candidateIds"] == [item.id for item in filter_candidates(items, guess, expected)]
