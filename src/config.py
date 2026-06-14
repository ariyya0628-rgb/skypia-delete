from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LoginConfig:
    url: str
    email: str
    password: str


@dataclass(frozen=True)
class NavigationConfig:
    product_management_url: str = ""
    listing_candidates_url: str = ""


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = False
    slow_mo_ms: int = 0


@dataclass(frozen=True)
class SelectorsConfig:
    login_email: list[str] = field(default_factory=list)
    login_password: list[str] = field(default_factory=list)
    login_submit: list[str] = field(default_factory=list)
    login_success: list[str] = field(default_factory=list)
    product_management_link: list[str] = field(default_factory=list)
    product_management_ready: list[str] = field(default_factory=list)
    asin_ng_checkbox: list[str] = field(default_factory=list)
    item_number_search_input: list[str] = field(default_factory=list)
    item_number_search_submit: list[str] = field(default_factory=list)
    item_number_result_row: list[str] = field(default_factory=list)
    item_number_select_all: list[str] = field(default_factory=list)
    selected_items_delete_button: list[str] = field(default_factory=list)
    delete_confirm_button: list[str] = field(default_factory=list)
    delete_complete: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AppConfig:
    login: LoginConfig
    navigation: NavigationConfig
    browser: BrowserConfig
    selectors: SelectorsConfig
    default_display_count: int = 200
    fallback_display_counts: list[int] = field(default_factory=lambda: [100, 50])
    disabled_display_counts: list[int] = field(default_factory=lambda: [500, 1000])
    item_number_delete_chunk_size: int = 50
    item_number_delete_fallback_chunk_sizes: list[int] = field(default_factory=lambda: [30, 10, 1])
    wait_after_delete_seconds: int = 5
    max_retry: int = 2
    page_load_timeout_seconds: int = 60
    search_timeout_seconds: int = 60
    delete_confirm_timeout_seconds: int = 60
    delete_complete_timeout_seconds: int = 120
    restart_browser_every_loops: int = 20
    save_screenshot_on_error: bool = True
    asin_ng_register: bool = False

    @property
    def page_load_timeout_ms(self) -> int:
        return self.page_load_timeout_seconds * 1000

    @property
    def search_timeout_ms(self) -> int:
        return self.search_timeout_seconds * 1000

    @property
    def delete_confirm_timeout_ms(self) -> int:
        return self.delete_confirm_timeout_seconds * 1000

    @property
    def delete_complete_timeout_ms(self) -> int:
        return self.delete_complete_timeout_seconds * 1000


DEFAULT_SELECTORS = {
    "login_email": ["input[name='user[email]']", "input[type='email']", "input[name='email']"],
    "login_password": ["input[name='user[password]']", "input[type='password']", "input[name='password']"],
    "login_submit": ["input[type='submit']", "button[type='submit']", "text=ログイン"],
    "login_success": ["text=商品管理", "text=ログアウト", "text=出品選択"],
    "product_management_link": ["text=商品管理", "a:has-text('商品管理')"],
    "product_management_ready": ["text=商品管理", "text=商品番号", "input[name*='item']"],
    "asin_ng_checkbox": [
        "label:has-text('対象のASINをNG登録する') input[type='checkbox']",
        "input[type='checkbox'][name*='asin']",
    ],
    "item_number_search_input": ["textarea[name*='item']", "textarea[name*='number']", "input[name*='item_number']"],
    "item_number_search_submit": ["button:has-text('検索')", "input[type='submit'][value*='検索']"],
    "item_number_result_row": ["table tbody tr", ".items tbody tr"],
    "item_number_select_all": ["input[type='checkbox'][name*='all']", "thead input[type='checkbox']"],
    "selected_items_delete_button": [
        "button:has-text('選択データを削除')",
        "a:has-text('選択データを削除')",
        "input[type='submit'][value*='削除']",
    ],
    "delete_confirm_button": [
        "button:has-text('選択データを削除')",
        "button:has-text('削除する')",
        "input[type='submit'][value*='削除']",
    ],
    "delete_complete": ["text=削除しました", "text=削除が完了", "text=商品管理"],
}


def load_config(config_path: str | Path = "config.json", env_path: str | Path = ".env") -> AppConfig:
    load_env_file(Path(env_path))
    path = Path(config_path)
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))

    email = os.getenv("SKYPIEA_LOGIN_EMAIL", "").strip()
    password = os.getenv("SKYPIEA_LOGIN_PASSWORD", "").strip()
    if not email or not password:
        raise ValueError("SKYPIEA_LOGIN_EMAIL and SKYPIEA_LOGIN_PASSWORD must be set in .env or environment.")

    selector_data = DEFAULT_SELECTORS | data.get("selectors", {})

    return AppConfig(
        login=LoginConfig(url=str(data.get("login_url", "")).strip(), email=email, password=password),
        navigation=NavigationConfig(
            product_management_url=str(data.get("product_management_url", "")).strip(),
            listing_candidates_url=str(data.get("listing_candidates_url", "")).strip(),
        ),
        browser=BrowserConfig(headless=bool(data.get("headless", False)), slow_mo_ms=int(data.get("slow_mo_ms", 0))),
        selectors=SelectorsConfig(
            login_email=list(selector_data["login_email"]),
            login_password=list(selector_data["login_password"]),
            login_submit=list(selector_data["login_submit"]),
            login_success=list(selector_data["login_success"]),
            product_management_link=list(selector_data["product_management_link"]),
            product_management_ready=list(selector_data["product_management_ready"]),
            asin_ng_checkbox=list(selector_data["asin_ng_checkbox"]),
            item_number_search_input=list(selector_data["item_number_search_input"]),
            item_number_search_submit=list(selector_data["item_number_search_submit"]),
            item_number_result_row=list(selector_data["item_number_result_row"]),
            item_number_select_all=list(selector_data["item_number_select_all"]),
            selected_items_delete_button=list(selector_data["selected_items_delete_button"]),
            delete_confirm_button=list(selector_data["delete_confirm_button"]),
            delete_complete=list(selector_data["delete_complete"]),
        ),
        default_display_count=int(data.get("default_display_count", 200)),
        fallback_display_counts=list(data.get("fallback_display_counts", [100, 50])),
        disabled_display_counts=list(data.get("disabled_display_counts", [500, 1000])),
        item_number_delete_chunk_size=int(data.get("item_number_delete_chunk_size", 50)),
        item_number_delete_fallback_chunk_sizes=list(data.get("item_number_delete_fallback_chunk_sizes", [30, 10, 1])),
        wait_after_delete_seconds=int(data.get("wait_after_delete_seconds", 5)),
        max_retry=int(data.get("max_retry", 2)),
        page_load_timeout_seconds=int(data.get("page_load_timeout_seconds", 60)),
        search_timeout_seconds=int(data.get("search_timeout_seconds", 60)),
        delete_confirm_timeout_seconds=int(data.get("delete_confirm_timeout_seconds", 60)),
        delete_complete_timeout_seconds=int(data.get("delete_complete_timeout_seconds", 120)),
        restart_browser_every_loops=int(data.get("restart_browser_every_loops", 20)),
        save_screenshot_on_error=bool(data.get("save_screenshot_on_error", True)),
        asin_ng_register=bool(data.get("asin_ng_register", False)),
    )


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
