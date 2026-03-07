# Copyright © 2026 ZQ AI LOGIC™
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
storage.py — Kivy JsonStore-backed persistent storage for INNM app.
Splits high-frequency UI state from low-frequency secure configuration.
"""
from pathlib import Path
from typing import Any
from kivy.storage.jsonstore import JsonStore

APP_DIR = Path.home() / ".innm"
APP_DIR.mkdir(parents=True, exist_ok=True)

ui_store = JsonStore(str(APP_DIR / "ui_state.json"))
config_store = JsonStore(str(APP_DIR / "secure.json"))

SECURE_KEYS = {
    "innm_api_key",
    "zq_fdk_api_key",
    "zq_fdk_github_token",
    "zq_fdk_repo_owner",
    "zq_fdk_repo_name",
}


def _get_store(key: str) -> JsonStore:
    return config_store if key in SECURE_KEYS else ui_store


def get(key: str, default: Any = None) -> Any:
    store = _get_store(key)
    if store.exists(key):
        return store.get(key).get("value", default)
    return default


def set(key: str, value: Any) -> None:
    store = _get_store(key)
    store.put(key, value=value)


def delete(key: str) -> None:
    store = _get_store(key)
    if store.exists(key):
        store.delete(key)


def keys() -> list:
    return list(ui_store.keys()) + list(config_store.keys())
