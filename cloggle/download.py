from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import time


ITEM_PRICES_URL = (
    "https://raw.githubusercontent.com/eX-C0n/Cloggle/refs/heads/main/ItemPrices.txt"
)


def download_item_prices(output_path: str | Path, *, timeout: int = 10, retries: int = 2, backoff: float = 1.0) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    request = Request(
        ITEM_PRICES_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
        },
    )

    last_exc = None
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                data = response.read()
            output_path.write_bytes(data)
            return
        except (HTTPError, URLError, TimeoutError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
                continue
            raise RuntimeError(f"Failed to download item prices: {exc}") from exc