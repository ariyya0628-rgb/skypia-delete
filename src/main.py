from __future__ import annotations

import argparse
import asyncio

from config import load_config
from delete_by_item_numbers import delete_by_item_numbers
from logger import DeleteResult, append_delete_result, setup_logger
from login import login
from navigation import open_product_management
from utils import ensure_directories, save_error_screenshot


async def run_login_check() -> None:
    ensure_directories()
    config = load_config()
    logger = setup_logger()

    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright が未インストールです。requirements.md の手順でセットアップしてください。") from exc

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=config.browser.headless,
            slow_mo=config.browser.slow_mo_ms,
        )
        page = await browser.new_page()
        page.set_default_timeout(config.page_load_timeout_ms)
        try:
            await login(page, config, logger=logger)
            await open_product_management(page, config, logger=logger)
            append_delete_result(
                DeleteResult(
                    mode="login-check",
                    loop=1,
                    display_count=0,
                    deleted_count=0,
                    result="success",
                    detail="ログインと商品管理画面への遷移を確認",
                )
            )
        except Exception as exc:
            screenshot = ""
            if config.save_screenshot_on_error:
                screenshot = await save_error_screenshot(page, "login-check")
            append_delete_result(
                DeleteResult(
                    mode="login-check",
                    loop=1,
                    display_count=0,
                    deleted_count=0,
                    result="error",
                    detail=str(exc),
                    screenshot=screenshot,
                )
            )
            logger.exception("ログイン確認に失敗しました")
            raise
        finally:
            await browser.close()


async def run_delete_by_item_numbers() -> None:
    ensure_directories()
    config = load_config()
    logger = setup_logger()

    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is not installed. Install it using requirements.md.") from exc

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=config.browser.headless,
            slow_mo=config.browser.slow_mo_ms,
        )
        page = await browser.new_page()
        page.set_default_timeout(config.page_load_timeout_ms)
        try:
            await login(page, config, logger=logger)
            await open_product_management(page, config, logger=logger)
            summary = await delete_by_item_numbers(page, config, logger=logger)
            logger.info(
                "商品番号指定削除が終了しました total=%s deleted=%s skipped=%s",
                summary.total_items,
                summary.deleted_count,
                summary.skipped_count,
            )
        except Exception as exc:
            screenshot = ""
            if config.save_screenshot_on_error:
                screenshot = await save_error_screenshot(page, "delete-by-item-numbers")
            append_delete_result(
                DeleteResult(
                    mode="delete-by-item-numbers",
                    loop=0,
                    display_count=0,
                    deleted_count=0,
                    result="error",
                    detail=str(exc),
                    screenshot=screenshot,
                )
            )
            logger.exception("商品番号指定削除に失敗しました")
            raise
        finally:
            await browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="スカイピア削除自動化ツール")
    parser.add_argument(
        "--mode",
        choices=[
            "login-check",
            "delete-by-item-numbers",
            "delete-deleted-items",
            "delete-by-item-numbers-and-clean",
            "delete-listing-candidates",
        ],
        default="login-check",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.mode == "login-check":
        await run_login_check()
        return
    if args.mode == "delete-by-item-numbers":
        await run_delete_by_item_numbers()
        return
    raise NotImplementedError(f"{args.mode} は後続ステップで実装します。")


if __name__ == "__main__":
    asyncio.run(main())
