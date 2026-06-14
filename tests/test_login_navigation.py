import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import AppConfig, BrowserConfig, LoginConfig, NavigationConfig, SelectorsConfig
from login import login
from navigation import open_product_management


class FakeLocator:
    def __init__(self, page, selector, count=1):
        self.page = page
        self.selector = selector
        self._count = count

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


class FakePage:
    def __init__(self, unavailable_selectors=None):
        self.actions = []
        self.unavailable_selectors = set(unavailable_selectors or [])

    async def goto(self, url, wait_until=None, timeout=None):
        self.actions.append(("goto", url, wait_until, timeout))

    def locator(self, selector):
        count = 0 if selector in self.unavailable_selectors else 1
        return FakeLocator(self, selector, count=count)

    async def wait_for_load_state(self, state, timeout=None):
        self.actions.append(("wait_for_load_state", state, timeout))


def make_config(product_management_url=""):
    return AppConfig(
        login=LoginConfig(
            url="https://example.test/login",
            email="user@example.test",
            password="secret",
        ),
        navigation=NavigationConfig(
            product_management_url=product_management_url,
            listing_candidates_url="",
        ),
        browser=BrowserConfig(headless=True, slow_mo_ms=0),
        selectors=SelectorsConfig(
            login_email=["#email"],
            login_password=["#password"],
            login_submit=["#submit"],
            login_success=["text=商品管理"],
            product_management_link=["text=商品管理"],
            product_management_ready=["text=商品番号"],
            asin_ng_checkbox=["#asin-ng"],
        ),
    )


class LoginNavigationTest(unittest.IsolatedAsyncioTestCase):
    async def test_login_fills_credentials_and_waits_for_success_marker(self):
        page = FakePage()
        config = make_config()

        await login(page, config)

        self.assertIn(("goto", "https://example.test/login", "domcontentloaded", 60000), page.actions)
        self.assertIn(("fill", "#email", "user@example.test"), page.actions)
        self.assertIn(("fill", "#password", "secret"), page.actions)
        self.assertIn(("click", "#submit"), page.actions)
        self.assertIn(("wait_for", "text=商品管理", 60000), page.actions)

    async def test_open_product_management_uses_direct_url_when_configured(self):
        page = FakePage()
        config = make_config(product_management_url="https://example.test/items")

        await open_product_management(page, config)

        self.assertIn(("goto", "https://example.test/items", "domcontentloaded", 60000), page.actions)
        self.assertIn(("wait_for", "text=商品番号", 60000), page.actions)

    async def test_open_product_management_clicks_menu_when_url_is_not_configured(self):
        page = FakePage()
        config = make_config(product_management_url="")

        await open_product_management(page, config)

        self.assertIn(("click", "text=商品管理"), page.actions)
        self.assertIn(("wait_for_load_state", "domcontentloaded", 60000), page.actions)
        self.assertIn(("wait_for", "text=商品番号", 60000), page.actions)


if __name__ == "__main__":
    unittest.main()
