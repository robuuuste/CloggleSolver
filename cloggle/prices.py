from pathlib import Path
import re


def parse_item_prices(path: str | Path) -> dict[str, dict[str, float]]:
    """
    Parse Cloggle's ItemPrices.txt.

    Returns:
        {
            "tempoross": {
                "Dragon harpoon": 2982336.5,
                ...
            },
            ...
        }
    """

    data: dict[str, dict[str, float]] = {}
    current_source: str | None = None

    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line:
                continue

            # Source header, e.g.:
            # abyssal_sire:
            if line.endswith(":") and not line.startswith((" ", "\t")):
                current_source = line[:-1]
                data[current_source] = {}
                continue

            if current_source is None:
                continue

            # Item line, e.g.:
            # Abyssal whip: 1297755,
            match = re.match(
                r"^(.*?):\s*(-?\d+(?:\.\d+)?)\s*,?$",
                line,
            )

            if not match:
                continue

            item_name = match.group(1).strip()
            price = float(match.group(2))

            data[current_source][item_name] = price

    return data