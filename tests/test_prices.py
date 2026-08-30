import importlib
import sys
from pathlib import Path

from cloggle.prices import parse_item_prices


def test_parse_item_prices(tmp_path):
    content = """\
abyssal_sire:
  Abyssal whip: 1297755,
  Abyssal dagger: 1989491.5,
aerial_fishing:
  Fish sack: 0,
  Golden tench: 0,
"""

    file = tmp_path / "ItemPrices.txt"
    file.write_text(content, encoding="utf-8")

    data = parse_item_prices(file)

    assert data["abyssal_sire"]["Abyssal whip"] == 1_297_755
    assert data["abyssal_sire"]["Abyssal dagger"] == 1_989_491.5

    assert data["aerial_fishing"]["Fish sack"] == 0
    assert data["aerial_fishing"]["Golden tench"] == 0


def test_app_refreshes_prices_on_startup(monkeypatch, tmp_path):
    calls = []

    def fake_download(output_path, **kwargs):
        calls.append(("download", str(output_path)))
        Path(output_path).write_text("", encoding="utf-8")

    def fake_load_items(collection_log_dir, prices_file, item_defs_dir):
        calls.append(("load", prices_file))
        return {}

    monkeypatch.setattr("cloggle.download.download_item_prices", fake_download)
    monkeypatch.setattr("cloggle.items.load_items", fake_load_items)
    # app.py uses a relative price path; keep this startup test from touching the
    # checked-in price source used by the real-data tests.
    (tmp_path / "data").mkdir()
    monkeypatch.chdir(tmp_path)

    sys.modules.pop("ui.app", None)
    importlib.import_module("ui.app")

    assert calls[0] == ("download", "data/ItemPrices.txt")
    assert calls[1] == ("load", "data/ItemPrices.txt")
