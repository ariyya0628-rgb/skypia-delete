from __future__ import annotations

from config import AppConfig
from utils import first_available_locator, wait_for_any_selector


async def login(page, config: AppConfig, logger=None) -> None:
    if logger:
        logger.info("ログイン画面を開きます")

    await page.goto(
        config.login.url,
        wait_until="domcontentloaded",
        timeout=config.page_load_timeout_ms,
    )

    email_input = await first_available_locator(page, config.selectors.login_email)
    password_input = await first_available_locator(page, config.selectors.login_password)
    submit_button = await first_available_locator(page, config.selectors.login_submit)

    await email_input.fill(config.login.email)
    await password_input.fill(config.login.password)
    await submit_button.click()

    await wait_for_any_selector(
        page,
        config.selectors.login_success,
        timeout_ms=config.page_load_timeout_ms,
    )

    if logger:
        logger.info("ログインに成功しました")
