from __future__ import annotations

from collections.abc import Sequence

from utils import first_locator


async def ensure_asin_ng_unchecked(page, selectors: Sequence[str]) -> bool:
    for selector in selectors:
        locator = page.locator(selector)
        try:
            if await locator.count() == 0:
                continue
            checkbox = await first_locator(locator)
            if await checkbox.is_checked():
                await checkbox.uncheck()
                return True
            return False
        except Exception:
            continue
    return False
