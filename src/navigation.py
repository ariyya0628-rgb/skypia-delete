from __future__ import annotations

from config import AppConfig
from utils import first_available_locator, wait_for_any_selector


async def open_product_management(page, config: AppConfig, logger=None) -> None:
    if config.navigation.product_management_url:
        if logger:
            logger.info("商品管理画面をURLで開きます")
        await page.goto(
            config.navigation.product_management_url,
            wait_until="domcontentloaded",
            timeout=config.page_load_timeout_ms,
        )
    else:
        if logger:
            logger.info("商品管理メニューをクリックします")
        link = await first_available_locator(page, config.selectors.product_management_link)
        await link.click()
        await page.wait_for_load_state("domcontentloaded", timeout=config.page_load_timeout_ms)

    await wait_for_any_selector(
        page,
        config.selectors.product_management_ready,
        timeout_ms=config.page_load_timeout_ms,
    )

    if logger:
        logger.info("商品管理画面への遷移を確認しました")
