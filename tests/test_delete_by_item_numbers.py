import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import AppConfig, BrowserConfig, LoginConfig, NavigationConfig, SelectorsConfig
from delete_by_item_numbers import chunk_item_numbers, delete_by_item_numbers, read_item_numbers


class FakeLocator:
    def __init__(self, page, selector, count=1, checked=False):
        self.page = page
        self.selector = selector
        self._count = count
        self.checked = checked

    async def count(self):
        return self._count

    async def first(self):
        return self

    async def fill(self, value):
        self.page.actions.append(("fill", self.selector, value))

    async def click(self):
        self.page.actions.append(("click", self.selector))

    async def wait_for(self, timeout=None):
        self.page.actions.append(("wait_for", self.selector, timeout))

    async def is_checked(self):
        return self.checked

    async def uncheck(self):
        self.checked = False
        self.page.actions.append(("uncheck", self.selector))


class FakePage:
    def __init__(self):
        self.actions = []
        self.counts = {
            "#search": 1,
            "#search-submit": 1,
            "#result-row": 2,
            "#select-all": 1,
            "#delete-selected": 1,
            "#confirm-delete": 1,
            "#delete-complete": 1,
            "#asin-ng": 1,
        }
        self.checked = {"#asin-ng": True}

    def locator(self, selector):
        return FakeLocator(
            self,
            selector,
            count=self.counts.get(selector, 0),
            checked=self.checked.get(selector, False),
        )


def make_config():
    return AppConfig(
        login=LoginConfig(url="https://example.test/login", email="user@example.test", password="secret"),
        navigation=NavigationConfig(product_management_url="", listing_candidates_url=""),
        browser=BrowserConfig(headless=True, slow_mo_ms=0),
        selectors=SelectorsConfig(
            item_number_search_input=["#search"],
            item_number_search_submit=["#search-submit"],
            item_number_result_row=["#result-row"],
            item_number_select_all=["#select-all"],
            selected_items_delete_button=["#delete-selected"],
            delete_confirm_button=["#confirm-delete"],
            delete_complete=["#delete-complete"],
            asin_ng_checkbox=["#asin-ng"],
        ),
        item_number_delete_chunk_size=2,
        wait_after_delete_seconds=0,
    )


class DeleteByItemNumbersTest(unittest.IsolatedAsyncioTestCase):
    def test_read_item_numbers_removes_blanks_spaces_and_duplicates(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "item_numbers.txt"
            path.write_text(" A001 \n\nA002\nA001\n", encoding="utf-8")

            self.assertEqual(read_item_numbers(path), ["A001", "A002"])

    def test_chunk_item_numbers_uses_requested_size(self):
        self.assertEqual(
            chunk_item_numbers(["A001", "A002", "A003"], 2),
            [["A001", "A002"], ["A003"]],
        )

    async def test_delete_by_item_numbers_searches_selects_deletes_and_unchecks_asin_ng(self):
        with TemporaryDirectory() as temp_dir:
            item_path = Path(temp_dir) / "item_numbers.txt"
            csv_path = Path(temp_dir) / "delete_results.csv"
            item_path.write_text("A001\nA002\n", encoding="utf-8")
            page = FakePage()

            summary = await delete_by_item_numbers(
                page,
                make_config(),
                item_numbers_path=item_path,
                csv_path=csv_path,
            )
            csv_text = csv_path.read_text(encoding="utf-8")

        self.assertEqual(summary.total_items, 2)
        self.assertEqual(summary.deleted_count, 2)
        self.assertIn(("fill", "#search", "A001\nA002"), page.actions)
        self.assertIn(("click", "#search-submit"), page.actions)
        self.assertIn(("click", "#select-all"), page.actions)
        self.assertIn(("click", "#delete-selected"), page.actions)
        self.assertIn(("uncheck", "#asin-ng"), page.actions)
        self.assertIn(("click", "#confirm-delete"), page.actions)
        self.assertTrue(csv_text.startswith("datetime,mode,loop"))
        self.assertIn("success", csv_text)


if __name__ == "__main__":
    unittest.main()
