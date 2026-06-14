from __future__ import annotations

import inspect
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directories() -> None:
    for path in ("input", "output/logs", "output/screenshots"):
        Path(path).mkdir(parents=True, exist_ok=True)


async def first_available_locator(page, selectors: Sequence[str]):
    for selector in selectors:
        locator = page.locator(selector)
        try:
            count = await locator.count()
        except Exception:
            continue
        if count > 0:
            return await first_locator(locator)
    raise LookupError(f"No matching selector found: {', '.join(selectors)}")


async def first_locator(locator):
    first = getattr(locator, "first")
    if callable(first):
        value = first()
        if inspect.isawaitable(value):
            return await value
        return value
    return first


async def wait_for_any_selector(page, selectors: Sequence[str], timeout_ms: int):
    last_error: Exception | None = None
    for selector in selectors:
        try:
            locator = await first_locator(page.locator(selector))
            await locator.wait_for(timeout=timeout_ms)
            return locator
        except Exception as exc:
            last_error = exc
    raise TimeoutError(f"Timed out waiting for selectors: {', '.join(selectors)}") from last_error


async def save_error_screenshot(page, mode: str, detail: str = "error") -> str:
    screenshots_dir = Path("output/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    safe_detail = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in detail)[:60]
    path = screenshots_dir / f"error_{timestamp()}_{mode}_{safe_detail}.png"
    await page.screenshot(path=str(path), full_page=True)
    return str(path)


def unique_non_empty_lines(lines: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for line in lines:
        value = line.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        values.append(value)
    return values
