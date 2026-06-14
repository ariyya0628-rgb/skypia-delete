import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import load_config
from safety import ensure_asin_ng_unchecked


class FakeCheckbox:
    def __init__(self, checked):
        self.checked = checked
        self.unchecked = False

    async def is_checked(self):
        return self.checked

    async def uncheck(self):
        self.unchecked = True
        self.checked = False


class FakeLocator:
    def __init__(self, checkbox=None):
        self.checkbox = checkbox

    async def count(self):
        return 1 if self.checkbox else 0

    @property
    def first(self):
        return self.checkbox


class FakePage:
    def __init__(self, checkbox=None):
        self.checkbox = checkbox

    def locator(self, selector):
        return FakeLocator(self.checkbox)


class ConfigSafetyTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._old_email = os.environ.get("SKYPIEA_LOGIN_EMAIL")
        self._old_password = os.environ.get("SKYPIEA_LOGIN_PASSWORD")

    def tearDown(self):
        if self._old_email is None:
            os.environ.pop("SKYPIEA_LOGIN_EMAIL", None)
        else:
            os.environ["SKYPIEA_LOGIN_EMAIL"] = self._old_email
        if self._old_password is None:
            os.environ.pop("SKYPIEA_LOGIN_PASSWORD", None)
        else:
            os.environ["SKYPIEA_LOGIN_PASSWORD"] = self._old_password

    def test_load_config_reads_json_and_env_credentials(self):
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                """
{
  "login_url": "https://example.test/login",
  "product_management_url": "https://example.test/items",
  "headless": true,
  "selectors": {
    "login_email": ["#email"],
    "login_password": ["#password"],
    "login_submit": ["#submit"],
    "login_success": ["text=ok"],
    "product_management_link": ["text=商品管理"],
    "product_management_ready": ["text=商品番号"],
    "asin_ng_checkbox": ["#asin-ng"]
  }
}
""",
                encoding="utf-8",
            )
            os.environ["SKYPIEA_LOGIN_EMAIL"] = "user@example.test"
            os.environ["SKYPIEA_LOGIN_PASSWORD"] = "secret"

            config = load_config(config_path, env_path=Path(temp_dir) / ".env")

        self.assertEqual(config.login.url, "https://example.test/login")
        self.assertEqual(config.login.email, "user@example.test")
        self.assertEqual(config.login.password, "secret")
        self.assertEqual(config.navigation.product_management_url, "https://example.test/items")
        self.assertEqual(config.default_display_count, 200)
        self.assertEqual(config.fallback_display_counts, [100, 50])
        self.assertTrue(config.browser.headless)

    def test_load_config_rejects_missing_credentials(self):
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text('{"login_url":"https://example.test/login"}', encoding="utf-8")
            os.environ.pop("SKYPIEA_LOGIN_EMAIL", None)
            os.environ.pop("SKYPIEA_LOGIN_PASSWORD", None)

            with self.assertRaisesRegex(ValueError, "SKYPIEA_LOGIN_EMAIL"):
                load_config(config_path, env_path=Path(temp_dir) / ".env")

    async def test_ensure_asin_ng_unchecked_removes_existing_check(self):
        checkbox = FakeCheckbox(checked=True)
        page = FakePage(checkbox=checkbox)

        changed = await ensure_asin_ng_unchecked(page, ["#asin-ng"])

        self.assertTrue(changed)
        self.assertTrue(checkbox.unchecked)
        self.assertFalse(checkbox.checked)

    async def test_ensure_asin_ng_unchecked_does_nothing_when_not_checked(self):
        checkbox = FakeCheckbox(checked=False)
        page = FakePage(checkbox=checkbox)

        changed = await ensure_asin_ng_unchecked(page, ["#asin-ng"])

        self.assertFalse(changed)
        self.assertFalse(checkbox.unchecked)


if __name__ == "__main__":
    unittest.main()
