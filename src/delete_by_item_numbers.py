from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from config import AppConfig
from logger import DeleteResult, append_delete_result
from safety import ensure_asin_ng_unchecked
from utils import first_available_locator, unique_non_empty_lines, wait_for_any_selector


MODE_NAME = "delete-by-item-numbers"


@dataclass(frozen=True)
class DeleteByItemNumbersSummary:
    total_items: int
    loops: int
    deleted_count: int
    skipped_count: int


def read_item_numbers(path: str | Path = "input/item_numbers.txt") -> list[str]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    return unique_non_empty_lines(file_path.read_text(encoding="utf-8").splitlines())


def chunk_item_numbers(item_numbers: list[str], chunk_size: int) -> list[list[str]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    return [item_numbers[index : index + chunk_size] for index in range(0, len(item_numbers), chunk_size)]


async def delete_by_item_numbers(
    page,
    config: AppConfig,
    item_numbers_path: str | Path = "input/item_numbers.txt",
    csv_path: str | Path = "output/delete_results.csv",
    logger=None,
) -> DeleteByItemNumbersSummary:
    item_numbers = read_item_numbers(item_numbers_path)
    if not item_numbers:
        append_delete_result(
            DeleteResult(
                mode=MODE_NAME,
                loop=0,
                display_count=0,
                deleted_count=0,
                result="finished",
                detail="item_numbers.txt is empty",
            ),
            csv_path=csv_path,
        )
        return DeleteByItemNumbersSummary(total_items=0, loops=0, deleted_count=0, skipped_count=0)

    chunks = chunk_item_numbers(item_numbers, config.item_number_delete_chunk_size)
    total_deleted = 0
    total_skipped = 0

    for loop_index, chunk in enumerate(chunks, start=1):
        if logger:
            logger.info("商品番号指定削除 loop=%s count=%s", loop_index, len(chunk))

        search_input = await first_available_locator(page, config.selectors.item_number_search_input)
        await search_input.fill("\n".join(chunk))

        search_button = await first_available_locator(page, config.selectors.item_number_search_submit)
        await search_button.click()

        result_count = await count_matching_rows(page, config.selectors.item_number_result_row)
        if result_count == 0:
            total_skipped += len(chunk)
            append_delete_result(
                DeleteResult(
                    mode=MODE_NAME,
                    loop=loop_index,
                    display_count=len(chunk),
                    deleted_count=0,
                    result="no_target",
                    detail="search result is empty",
                ),
                csv_path=csv_path,
            )
            continue

        select_all = await first_available_locator(page, config.selectors.item_number_select_all)
        await select_all.click()

        delete_button = await first_available_locator(page, config.selectors.selected_items_delete_button)
        await delete_button.click()

        confirm_button = await first_available_locator(page, config.selectors.delete_confirm_button)
        await ensure_asin_ng_unchecked(page, config.selectors.asin_ng_checkbox)
        await confirm_button.click()

        await wait_for_any_selector(
            page,
            config.selectors.delete_complete,
            timeout_ms=config.delete_complete_timeout_ms,
        )

        deleted_count = min(result_count, len(chunk))
        total_deleted += deleted_count
        append_delete_result(
            DeleteResult(
                mode=MODE_NAME,
                loop=loop_index,
                display_count=len(chunk),
                deleted_count=deleted_count,
                result="success",
                detail="deleted selected items",
            ),
            csv_path=csv_path,
        )

        if config.wait_after_delete_seconds > 0:
            await asyncio.sleep(config.wait_after_delete_seconds)

    return DeleteByItemNumbersSummary(
        total_items=len(item_numbers),
        loops=len(chunks),
        deleted_count=total_deleted,
        skipped_count=total_skipped,
    )


async def count_matching_rows(page, selectors: list[str]) -> int:
    for selector in selectors:
        locator = page.locator(selector)
        try:
            count = await locator.count()
        except Exception:
            continue
        if count > 0:
            return count
    return 0
