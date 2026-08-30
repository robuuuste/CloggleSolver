import json
from pathlib import Path
from urllib.request import Request, urlopen
from .models import Item


BASE_URL = "https://templeosrs.com/api/collection-log"

ENDPOINTS = {
    "items": f"{BASE_URL}/items.php",
    "categories": f"{BASE_URL}/categories.php",
    "category_parameters": f"{BASE_URL}/category_parameters.php",
}


def download_endpoint(name: str, output_path: str | Path) -> None:
    if name not in ENDPOINTS:
        raise ValueError(f"Unknown endpoint: {name}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    request = Request(
        ENDPOINTS[name],
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
        },
    )

    with urlopen(request) as response:
        data = response.read()

    output_path.write_bytes(data)


def load_items(path: str | Path) -> dict[int, str]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        int(item_id): name
        for item_id, name in data["items"].items()
    }


def load_categories(
    path: str | Path,
) -> dict[str, dict[str, list[int]]]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def build_items(
    item_names: dict[int, str],
    categories: dict[str, dict[str, list[int]]],
) -> dict[int, Item]:
    items = {
        item_id: Item(
            id=item_id,
            name=name,
        )
        for item_id, name in item_names.items()
    }

    for category, sources in categories.items():
        for source, item_ids in sources.items():
            for item_id in item_ids:
                if item_id not in items:
                    continue

                items[item_id].categories.add(category)
                items[item_id].sources.add(source)

    return items

def load_collection_log(data_dir: str | Path) -> dict[int, Item]:
    data_dir = Path(data_dir)

    item_names = load_items(
        data_dir / "items.json"
    )

    categories = load_categories(
        data_dir / "categories.json"
    )

    return build_items(
        item_names,
        categories,
    )