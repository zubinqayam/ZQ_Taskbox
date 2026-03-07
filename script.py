
import os
os.makedirs("output/innm-taskbox", exist_ok=True)
os.makedirs("output/innm-taskbox/docs", exist_ok=True)
os.makedirs("output/innm-taskbox/data", exist_ok=True)

COPYRIGHT_HEADER = """\
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

# ============================================================
# 1. LICENSE (Apache 2.0)
# ============================================================
license_txt = """\
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   Copyright © 2026 ZQ AI LOGIC™

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. Please also get in touch
      with us for any clarifications.

   Copyright © 2026 ZQ AI LOGIC™

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# ============================================================
# 2. .gitignore
# ============================================================
gitignore = """\
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
*.egg

# Virtual environments
.venv/
venv/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Kivy
*.kv.pyc

# Buildozer
.buildozer/
bin/

# PyInstaller
*.spec
*.exe

# OS
.DS_Store
Thumbs.db

# Data files (large Excel — use Git LFS or keep local)
data/*.xlsx
data/*.xls
data/*.csv

# INNM local storage
.innm/

# Logs
*.log

# Secrets (never commit)
secure.json
"""

# ============================================================
# 3. storage.py (V2 — JsonStore split)
# ============================================================
storage_py = COPYRIGHT_HEADER + '''\
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
'''

# ============================================================
# 4. types.py
# ============================================================
types_py = COPYRIGHT_HEADER + '''\
"""
types.py — Enums and data types for INNM app.
"""
from enum import Enum


class UserRole(Enum):
    GUEST = "guest"
    PLAYER = "player"
    ADMIN = "admin"


class TaskType(Enum):
    MTD_YTD = "mtd_ytd"
    REFERRAL_TRACKER = "referral_tracker"
    WEEKLY_DECK = "weekly_deck"
    RESEARCH_DAILY = "research_daily"
    CUSTOM = "custom"


class SourceType(Enum):
    CORPORATE_EXCEL = "corporate_excel"
    CSV = "csv"
    SQL = "sql"
    NONE = "none"
    CUSTOM = "custom"


class FeedbackSeverity(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    IMPROVEMENT = "improvement"
    BUG = "bug"
'''

# ============================================================
# 5. coordinator.py
# ============================================================
coordinator_py = COPYRIGHT_HEADER + '''\
"""
coordinator.py — Data router between shared input files and ZQ Taskboxes.
Loads a source once, slices it per-taskbox config, and hands off the slice.
"""
from typing import Any, Dict, Optional
from pathlib import Path

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class Coordinator:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._cache: Dict[str, Any] = {}

    def load_source(self, source_id: str) -> Optional[Any]:
        if source_id in self._cache:
            return self._cache[source_id]

        if source_id == "corporate_excel":
            if not HAS_PANDAS:
                return None
            candidates = [
                f for f in self.base_dir.glob("*.xlsx")
                if not f.name.startswith("~$")
            ]
            if not candidates:
                data_dir = self.base_dir / "data"
                if data_dir.exists():
                    candidates = [
                        f for f in data_dir.glob("*.xlsx")
                        if not f.name.startswith("~$")
                    ]
            if not candidates:
                return None
            df = pd.read_excel(candidates[0])
            self._cache[source_id] = df
            return df

        return None

    def clear_cache(self):
        self._cache.clear()

    def slice_for_taskbox(
        self,
        taskbox_id: str,
        source_obj: Any,
        params: Dict[str, Any],
    ) -> Any:
        if source_obj is None:
            return None
        if not HAS_PANDAS:
            return source_obj

        df = source_obj

        # Boolean mask approach (no .copy() until the end)
        mask = pd.Series(True, index=df.index)

        hospital = params.get("hospital_name")
        if hospital and "Hospital" in df.columns:
            mask &= df["Hospital"].str.contains(hospital, case=False, na=False)

        department = params.get("department")
        if department and "Department" in df.columns:
            mask &= df["Department"].str.contains(department, case=False, na=False)

        doctor = params.get("doctor")
        if doctor and "Doctor" in df.columns:
            mask &= df["Doctor"].str.contains(doctor, case=False, na=False)

        company = params.get("company")
        for col in ["Company", "Corporate", "Employer"]:
            if company and col in df.columns:
                mask &= df[col].str.contains(company, case=False, na=False)
                break

        period = params.get("period", "MTD")
        date_col = None
        for col in df.columns:
            if "date" in col.lower():
                date_col = col
                break

        if date_col:
            dates = pd.to_datetime(df[date_col], errors="coerce")
            today = pd.Timestamp.today()
            if period == "MTD":
                mask &= (dates.dt.month == today.month) & (dates.dt.year == today.year)
            elif period == "YTD":
                mask &= (dates.dt.year == today.year)

        return df.loc[mask]
'''

# ============================================================
# 6. zq_taskbox.py
# ============================================================
zq_taskbox_py = COPYRIGHT_HEADER + '''\
"""
zq_taskbox.py — ZQ Taskbox engine layer.
Each Taskbox is a single-purpose worker. It knows ONLY its own task.
"""
from typing import Any, Dict


class ZQTaskbox:
    def __init__(self, taskbox_id: str, task_type: str, config: Dict[str, Any]):
        self.id = taskbox_id
        self.task_type = task_type
        self.config = config
        self.history: list = []

    def run(self, data_slice: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        dispatch = {
            "mtd_ytd": self._run_mtd_ytd,
            "referral_tracker": self._run_referral_tracker,
            "weekly_deck": self._run_weekly_deck,
            "research_daily": self._run_research_daily,
        }
        handler = dispatch.get(self.task_type, self._run_custom)
        result = handler(data_slice, params)
        self.history.append({"params": params, "status": result.get("status")})
        return result

    def _run_mtd_ytd(self, df, params) -> Dict[str, Any]:
        if df is None or (hasattr(df, "empty") and df.empty):
            return {"status": "ok", "summary": "No data for this period.", "details": {}}

        metrics = {}
        rev_cols = [c for c in df.columns if "revenue" in c.lower() or "amount" in c.lower()]
        company_cols = [c for c in df.columns if "company" in c.lower() or "corporate" in c.lower()]
        if rev_cols and company_cols:
            by_company = df.groupby(company_cols[0])[rev_cols[0]].sum().sort_values(ascending=False)
            metrics["top_companies"] = by_company.head(10).to_dict()

        dept_cols = [c for c in df.columns if "department" in c.lower()]
        if rev_cols and dept_cols:
            by_dept = df.groupby(dept_cols[0])[rev_cols[0]].sum().sort_values(ascending=False)
            metrics["revenue_by_department"] = by_dept.to_dict()

        doctor_cols = [c for c in df.columns if "doctor" in c.lower()]
        visit_cols = [c for c in df.columns if "visit" in c.lower() or "footfall" in c.lower()]
        if visit_cols and doctor_cols:
            by_doctor = df.groupby(doctor_cols[0])[visit_cols[0]].sum().sort_values(ascending=False)
            metrics["visits_by_doctor"] = by_doctor.head(20).to_dict()

        summary = (
            f"MTD/YTD: {len(df)} rows, "
            f"{len(metrics.get('top_companies', {}))} companies, "
            f"{len(metrics.get('revenue_by_department', {}))} departments."
        )
        return {"status": "ok", "summary": summary, "details": metrics}

    def _run_referral_tracker(self, df, params) -> Dict[str, Any]:
        if df is None or (hasattr(df, "empty") and df.empty):
            return {"status": "ok", "summary": "No referral data.", "details": {}}
        doctor_cols = [c for c in df.columns if "doctor" in c.lower() or "refer" in c.lower()]
        if not doctor_cols:
            return {"status": "ok", "summary": "No referral columns found.", "details": {}}
        referral_counts = df[doctor_cols[0]].value_counts().head(20).to_dict()
        return {"status": "ok", "summary": f"Referral tracker: {len(referral_counts)} doctors.", "details": {"referrals": referral_counts}}

    def _run_weekly_deck(self, df, params) -> Dict[str, Any]:
        if df is None or (hasattr(df, "empty") and df.empty):
            return {"status": "ok", "summary": "No data for weekly deck.", "details": {}}
        return {"status": "ok", "summary": f"Weekly deck: {len(df)} rows ready.", "details": {"row_count": len(df)}}

    def _run_research_daily(self, df, params) -> Dict[str, Any]:
        return {"status": "ok", "summary": "Research daily: text-based task.", "details": {}}

    def _run_custom(self, df, params) -> Dict[str, Any]:
        row_count = len(df) if df is not None and hasattr(df, "__len__") else 0
        return {"status": "ok", "summary": f"Custom taskbox: {row_count} rows.", "details": {}}
'''

# ============================================================
# 7. innm_controller.py (V2 — LLM + heuristic fallback)
# ============================================================
innm_controller_py = COPYRIGHT_HEADER + '''\
"""
innm_controller.py — INNM-WOSDS Central Controller.

Triangular Pyramid architecture:
  - Front Matrix:  AI LLM routing (with heuristic fallback)
  - Back Matrix:   manage data pipelines via Coordinator
  - Top Matrix:    supervise all running Taskboxes
  - Center I-Box:  holds the single AI API key
"""
import json
from typing import Any, Dict, Optional
from pathlib import Path

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import storage as store
from coordinator import Coordinator
from zq_taskbox import ZQTaskbox


class INNMController:
    def __init__(self, base_dir: Path, api_key: str = ""):
        self.base_dir = base_dir
        self.api_key = api_key
        self.coordinator = Coordinator(base_dir)
        self.taskboxes: Dict[str, ZQTaskbox] = {}
        self._load_taskboxes_from_registry()

    def _load_taskboxes_from_registry(self):
        registry = store.get("taskbox_registry", {})
        for tb_id, cfg in registry.items():
            self.taskboxes[tb_id] = ZQTaskbox(
                taskbox_id=cfg["id"],
                task_type=cfg.get("task_type", "custom"),
                config=cfg,
            )

    def reload_taskboxes(self):
        self.taskboxes.clear()
        self._load_taskboxes_from_registry()

    def register_taskbox(
        self,
        tb_id: str,
        project: str,
        task_type: str,
        source_id: str = "corporate_excel",
        params: Optional[Dict] = None,
    ):
        registry = store.get("taskbox_registry", {})
        if tb_id in registry:
            return
        entry = {
            "id": tb_id,
            "project": project,
            "task_type": task_type,
            "source_id": source_id,
            "params": params or {},
        }
        registry[tb_id] = entry
        store.set("taskbox_registry", registry)
        self.taskboxes[tb_id] = ZQTaskbox(
            taskbox_id=entry["id"],
            task_type=entry["task_type"],
            config=entry,
        )

    # ════════════════════════════════════════════════
    # FRONT MATRIX: AI Intent Router
    # ════════════════════════════════════════════════
    def parse_intent(self, text: str) -> Dict[str, Any]:
        llm_intent = self._llm_route_intent(text)
        if llm_intent:
            tb_id = llm_intent.get("taskbox_id")
            if tb_id and tb_id in self.taskboxes:
                base_params = self.taskboxes[tb_id].config.get("params", {})
                llm_intent["params"] = {**base_params, **llm_intent.get("params", {})}
            return llm_intent
        return self._heuristic_route_intent(text)

    def _llm_route_intent(self, text: str) -> Optional[Dict[str, Any]]:
        if not self.api_key or not HAS_REQUESTS:
            return None

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        available_tbs = self.list_taskboxes()
        registry_str = json.dumps(available_tbs, indent=2)

        system_prompt = f"""You are the INNM Front Matrix Intent Router.
Your job is to map the user\'s natural language input to the correct taskbox.

Available Taskboxes:
{registry_str}

Rules:
1. Match the user\'s request to the MOST RELEVANT taskbox_id based on project or task type.
2. Extract any filter parameters mentioned (e.g., "hospital_name", "period": "MTD" or "YTD", "department", "doctor", "company").
3. If the user is just chatting or asking a general question, set taskbox_id to null and action to "chat".

Return a STRICTLY VALID JSON object matching this schema:
{{"taskbox_id": "matched_id_or_null", "action": "update" | "chat", "params": {{"period": "MTD", "hospital_name": "..."}}}}
"""
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }

        try:
            r = _requests.post(url, headers=headers, json=payload, timeout=10)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            intent = json.loads(content)
            if "action" in intent and "params" in intent:
                return intent
            return None
        except Exception:
            return None

    def _heuristic_route_intent(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        for tb_id, tb in self.taskboxes.items():
            project = tb.config.get("project", "").lower()
            task_type = tb.task_type.lower()
            if project in text_lower or task_type in text_lower or tb_id in text_lower:
                return {
                    "taskbox_id": tb_id,
                    "project": tb.config.get("project", ""),
                    "action": "update",
                    "params": tb.config.get("params", {}),
                }
        return {"taskbox_id": None, "action": "chat", "params": {}}

    # ════════════════════════════════════════════════
    # TOP MATRIX: orchestrate intent → coordinator → taskbox
    # ════════════════════════════════════════════════
    def handle_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        tb_id = intent.get("taskbox_id")
        if not tb_id:
            return {"status": "chat", "summary": "No taskbox matched. How can I help?"}

        tb = self.taskboxes.get(tb_id)
        if not tb:
            return {"status": "error", "message": f"Unknown taskbox: {tb_id}"}

        source_id = tb.config.get("source_id", "corporate_excel")
        source_obj = self.coordinator.load_source(source_id)
        params = {**tb.config.get("params", {}), **intent.get("params", {})}
        data_slice = self.coordinator.slice_for_taskbox(tb.id, source_obj, params)
        return tb.run(data_slice, params)

    def process_message(self, text: str) -> str:
        intent = self.parse_intent(text)
        result = self.handle_intent(intent)
        return result.get("summary", result.get("message", "Done."))

    def list_taskboxes(self) -> list:
        return [
            {"id": tb.id, "project": tb.config.get("project"), "type": tb.task_type}
            for tb in self.taskboxes.values()
        ]
'''

# ============================================================
# 8. zq_feedback.py (V2 — timeout + error handling)
# ============================================================
zq_feedback_py = COPYRIGHT_HEADER + '''\
"""
zq_feedback.py — ZQ Feedback Note (standalone).
Observes, reviews, and reports positives/negatives/improvements to GitHub Issues.
Has its own API key (keyhole). Threaded network I/O via main.py.
"""
import json
from typing import Optional
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import storage as store


class ZQFeedbackNote:
    def __init__(self):
        self.api_key: str = store.get("zq_fdk_api_key", "")
        self.github_token: str = store.get("zq_fdk_github_token", "")
        self.repo_owner: str = store.get("zq_fdk_repo_owner", "")
        self.repo_name: str = store.get("zq_fdk_repo_name", "zq-taskbox-feedback")
        self.history: list = store.get("zq_fdk_history", [])

    def set_ai_api_key(self, key: str):
        self.api_key = key
        store.set("zq_fdk_api_key", key)

    def set_github_token(self, token: str):
        self.github_token = token
        store.set("zq_fdk_github_token", token)

    def set_repo(self, owner: str, name: str):
        self.repo_owner = owner
        self.repo_name = name
        store.set("zq_fdk_repo_owner", owner)
        store.set("zq_fdk_repo_name", name)

    def add_feedback(self, text: str, severity: str = "improvement"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "severity": severity,
        }
        self.history.append(entry)
        store.set("zq_fdk_history", self.history)
        return entry

    def get_history(self) -> list:
        return self.history

    def get_history_text(self) -> str:
        lines = []
        for e in self.history:
            ts = e.get("timestamp", "?")[:19]
            sev = e.get("severity", "?")
            txt = e.get("text", "")
            lines.append(f"[{ts}] ({sev}) {txt}")
        return "\\n".join(lines)

    def send_to_github(
        self,
        title: str,
        body: Optional[str] = None,
        labels: Optional[list] = None,
    ) -> dict:
        if not HAS_REQUESTS:
            return {"status": "error", "message": "requests library not installed."}
        if not self.github_token or not self.repo_owner:
            return {"status": "error", "message": "GitHub token or repo not configured."}

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github+json",
        }
        data = {
            "title": title,
            "body": body or self.get_history_text(),
            "labels": labels or ["feedback"],
        }

        try:
            r = requests.post(url, headers=headers, json=data, timeout=10)
            if r.status_code == 201:
                return {"status": "ok", "url": r.json().get("html_url", "")}
            return {"status": "error", "message": f"HTTP {r.status_code}: {r.text}"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Network Error: {str(e)}"}
'''

# ============================================================
# 9. ui.kv
# ============================================================
ui_kv = '''\
# Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0

#:import dp kivy.metrics.dp
#:import DragBehavior kivy.uix.behaviors.drag.DragBehavior

<ZQBubble@DragBehavior+Button>:
    size_hint: None, None
    size: dp(56), dp(56)
    text: "ZQ"
    bold: True
    background_color: 0.2, 0.6, 1, 1
    on_release: app.toggle_zq_panel()
    drag_timeout: 999999
    drag_distance: 5

<DragTemplate@DragBehavior+Button>:
    size_hint_y: None
    height: dp(36)
    drag_timeout: 999999
    drag_distance: 5

<DropWorkspace@BoxLayout>:
    on_touch_up:
        if self.collide_point(*args[1].pos): app.handle_drop(args[1])

<RootUI@FloatLayout>:
    BoxLayout:
        orientation: "horizontal"
        size_hint: 1, 1

        DropWorkspace:
            orientation: "vertical"
            size_hint_x: 0.62
            padding: dp(8)
            spacing: dp(4)

            Label:
                text: "[b]INNM Master Chatbot[/b]"
                markup: True
                size_hint_y: None
                height: dp(28)

            TextInput:
                id: chat_display
                readonly: True
                font_size: "13sp"

            BoxLayout:
                size_hint_y: None
                height: dp(44)
                spacing: dp(4)

                TextInput:
                    id: chat_input
                    hint_text: "Type a message..."
                    multiline: False
                    on_text_validate: app.send_message(self.text); self.text = ""

                Button:
                    text: "Send"
                    size_hint_x: None
                    width: dp(70)
                    on_release: app.send_message(chat_input.text); chat_input.text = ""

        BoxLayout:
            orientation: "vertical"
            size_hint_x: 0.38
            padding: dp(6)
            spacing: dp(6)

            Label:
                text: "[b]Tools[/b]"
                markup: True
                size_hint_y: None
                height: dp(28)

            BoxLayout:
                size_hint_y: None
                height: dp(36)
                spacing: dp(4)
                DragTemplate:
                    text: "New Folder"
                    template_type: "folder"
                DragTemplate:
                    text: "New Taskbox"
                    template_type: "taskbox"

            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(4)
                TextInput:
                    id: new_folder_name
                    hint_text: "Folder name"
                    multiline: False
                Button:
                    text: "Add"
                    size_hint_x: None
                    width: dp(60)
                    on_release:
                        app.add_folder(new_folder_name.text)
                        new_folder_name.text = ""

            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(4)
                TextInput:
                    id: new_taskbox_name
                    hint_text: "Taskbox name"
                    multiline: False
                Button:
                    text: "Add"
                    size_hint_x: None
                    width: dp(60)
                    on_release:
                        app.add_taskbox(new_taskbox_name.text)
                        new_taskbox_name.text = ""

            Label:
                text: "Folders"
                size_hint_y: None
                height: dp(22)
            ScrollView:
                size_hint_y: 0.2
                GridLayout:
                    id: folder_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: dp(34)
                    spacing: dp(3)

            Label:
                text: "Taskboxes"
                size_hint_y: None
                height: dp(22)
            ScrollView:
                size_hint_y: 0.2
                GridLayout:
                    id: taskbox_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: dp(34)
                    spacing: dp(3)

            Button:
                text: "Settings"
                size_hint_y: None
                height: dp(38)
                on_release: app.open_settings_screen()

            Button:
                text: "Profile"
                size_hint_y: None
                height: dp(38)
                on_release: app.open_profile_screen()

    ZQBubble:
        id: zq_bubble
        pos_hint: {"right": 0.98, "y": 0.05}

    BoxLayout:
        id: zq_panel
        orientation: "vertical"
        size_hint: 0.33, 0.55
        pos_hint: {"x": 0.01, "y": 0.02}
        padding: dp(6)
        spacing: dp(4)
        opacity: 0
        disabled: True
        canvas.before:
            Color:
                rgba: 0.08, 0.08, 0.15, 0.92
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "[b]ZQ Feedback Note[/b]"
            markup: True
            size_hint_y: None
            height: dp(26)

        TextInput:
            id: zq_history_display
            readonly: True
            font_size: "12sp"

        TextInput:
            id: zq_input
            hint_text: "+ves / -ves / complaints..."
            size_hint_y: None
            height: dp(60)
            multiline: False

        BoxLayout:
            size_hint_y: None
            height: dp(38)
            spacing: dp(4)
            Button:
                text: "Add"
                on_release:
                    app.add_zq_feedback(zq_input.text)
                    zq_input.text = ""
            Button:
                text: "Send to GitHub"
                on_release: app.send_zq_to_github()
            Button:
                text: "Close"
                on_release: app.toggle_zq_panel()
'''

# ============================================================
# 10. main.py (V2 — async background execution)
# ============================================================
main_py = COPYRIGHT_HEADER + '''\
"""
main.py — INNM Kivy Application entry point.

Layout:
  - Fixed master chatbot (left) — talks to INNM-WOSDS controller
  - Tools panel (right)         — folders, taskboxes, settings, profile
  - Floating ZQ Feedback bubble — standalone feedback chat -> GitHub

Run: python main.py
"""
import uuid
import threading
from pathlib import Path
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

import storage as store
from innm_controller import INNMController
from zq_feedback import ZQFeedbackNote


class DraggableToolItem(DragBehavior, Button):
    def __init__(self, item_id, item_type, **kw):
        super().__init__(**kw)
        self.item_id = item_id
        self.item_type = item_type
        self.drag_timeout = 999999
        self.drag_distance = 5


class INNMApp(App):
    def build(self):
        self.title = "INNM Taskbox"
        base_dir = Path(".").resolve()
        api_key = store.get("innm_api_key", "")
        self.controller = INNMController(base_dir=base_dir, api_key=api_key)
        self.feedback = ZQFeedbackNote()
        self.folders = store.get("folders", [])
        self.taskboxes_ui = store.get("taskboxes_ui", [])
        self.root = Builder.load_file("ui.kv")
        self._render_lists()
        return self.root

    # ════════════════════════════════════════════════
    # BACKGROUND TASK HELPER
    # ════════════════════════════════════════════════
    def run_in_background(self, target_func, callback, *args, **kwargs):
        def thread_worker():
            try:
                result = target_func(*args, **kwargs)
                Clock.schedule_once(lambda dt: callback(result, None), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: callback(None, e), 0)
        threading.Thread(target=thread_worker, daemon=True).start()

    # ════════════════════════════════════════════════
    # MASTER CHATBOT (async)
    # ════════════════════════════════════════════════
    def send_message(self, text):
        text = (text or "").strip()
        if not text:
            return
        disp = self.root.ids.chat_display
        disp.text += f"\\n\\nYou: {text}"
        disp.text += f"\\nINNM: ⏳ Thinking..."

        def on_innm_reply(reply, error):
            disp.text = disp.text.replace("\\nINNM: ⏳ Thinking...", "")
            if error:
                disp.text += f"\\nINNM: ⚠️ Error: {str(error)}"
            else:
                disp.text += f"\\nINNM: {reply}"

        self.run_in_background(self.controller.process_message, on_innm_reply, text)

    # ════════════════════════════════════════════════
    # FOLDERS
    # ════════════════════════════════════════════════
    def add_folder(self, name):
        name = (name or "").strip()
        if not name:
            return
        entry = {"id": str(uuid.uuid4()), "name": name, "children": []}
        self.folders.append(entry)
        store.set("folders", self.folders)
        self._render_lists()
        self._show_in_chat(f"Folder created: {name}")

    def open_folder(self, fid):
        f = next((x for x in self.folders if x["id"] == fid), None)
        if not f:
            return
        self.root.ids.chat_display.text += f"\\n\\n[Folder: {f[\'name\']}] opened."

    # ════════════════════════════════════════════════
    # TASKBOXES
    # ════════════════════════════════════════════════
    def add_taskbox(self, name):
        name = (name or "").strip()
        if not name:
            return
        tb_id = name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8]
        entry = {"id": tb_id, "name": name, "task_type": "custom", "source_id": "corporate_excel"}
        self.taskboxes_ui.append(entry)
        store.set("taskboxes_ui", self.taskboxes_ui)
        self.controller.register_taskbox(
            tb_id=tb_id, project=name, task_type="custom", source_id="corporate_excel",
        )
        self._render_lists()
        self._show_in_chat(f"Taskbox created: {name} (id={tb_id})")

    def open_taskbox(self, tid):
        t = next((x for x in self.taskboxes_ui if x["id"] == tid), None)
        if not t:
            return
        self.root.ids.chat_display.text += f"\\n\\n[Taskbox: {t[\'name\']}] opened."

    # ════════════════════════════════════════════════
    # RENDER LISTS
    # ════════════════════════════════════════════════
    def _render_lists(self):
        fl = self.root.ids.folder_list
        tl = self.root.ids.taskbox_list
        fl.clear_widgets()
        tl.clear_widgets()
        for f in self.folders:
            btn = DraggableToolItem(
                item_id=f["id"], item_type="folder",
                text=f["name"], size_hint_y=None, height=34,
            )
            btn.bind(on_release=lambda inst, fid=f["id"]: self.open_folder(fid))
            fl.add_widget(btn)
        for t in self.taskboxes_ui:
            btn = DraggableToolItem(
                item_id=t["id"], item_type="taskbox",
                text=t["name"], size_hint_y=None, height=34,
            )
            btn.bind(on_release=lambda inst, tid=t["id"]: self.open_taskbox(tid))
            tl.add_widget(btn)

    # ════════════════════════════════════════════════
    # DRAG & DROP
    # ════════════════════════════════════════════════
    def handle_drop(self, touch):
        widget = touch.grab_current
        if isinstance(widget, DraggableToolItem):
            if widget.item_type == "folder":
                self.open_folder(widget.item_id)
            elif widget.item_type == "taskbox":
                self.open_taskbox(widget.item_id)
            return
        if hasattr(widget, "template_type"):
            if widget.template_type == "folder":
                self._prompt_name("New Folder", self.add_folder)
            elif widget.template_type == "taskbox":
                self._prompt_name("New Taskbox", self.add_taskbox)

    def _prompt_name(self, title, callback):
        content = BoxLayout(orientation="vertical", spacing=5, padding=5)
        ti = TextInput(multiline=False)
        btns = BoxLayout(size_hint_y=None, height=40, spacing=5)
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.3))
        ok_btn = Button(text="OK")
        cancel_btn = Button(text="Cancel")
        def on_ok(*_):
            if ti.text.strip():
                callback(ti.text.strip())
            popup.dismiss()
        ok_btn.bind(on_release=on_ok)
        cancel_btn.bind(on_release=lambda *_: popup.dismiss())
        btns.add_widget(ok_btn)
        btns.add_widget(cancel_btn)
        content.add_widget(ti)
        content.add_widget(btns)
        popup.open()

    # ════════════════════════════════════════════════
    # ZQ FEEDBACK NOTE (async GitHub)
    # ════════════════════════════════════════════════
    def toggle_zq_panel(self):
        panel = self.root.ids.zq_panel
        if panel.disabled:
            panel.disabled = False
            panel.opacity = 1
            self.root.ids.zq_history_display.text = self.feedback.get_history_text()
        else:
            panel.disabled = True
            panel.opacity = 0

    def add_zq_feedback(self, text):
        text = (text or "").strip()
        if not text:
            return
        self.feedback.add_feedback(text)
        self.root.ids.zq_history_display.text = self.feedback.get_history_text()

    def send_zq_to_github(self):
        self._show_in_chat("⏳ Sending feedback to GitHub...")

        def on_github_reply(result, error):
            disp = self.root.ids.chat_display
            disp.text = disp.text.replace("\\nSystem: ⏳ Sending feedback to GitHub...", "")
            if error:
                self._show_in_chat(f"GitHub send failed: {str(error)}")
            elif result.get("status") == "ok":
                self._show_in_chat(f"Feedback sent to GitHub: {result.get(\'url\', \'\')}")
            else:
                self._show_in_chat(f"GitHub send failed: {result.get(\'message\', \'\')}")

        title = "ZQ Feedback Session — " + datetime.now().strftime("%Y-%m-%d %H:%M")
        self.run_in_background(self.feedback.send_to_github, on_github_reply, title=title)

    # ════════════════════════════════════════════════
    # SETTINGS / PROFILE (stubs)
    # ════════════════════════════════════════════════
    def open_settings_screen(self):
        self._show_in_chat("Settings screen — configure INNM API key and preferences.")

    def open_profile_screen(self):
        self._show_in_chat("Profile screen — user info and role management.")

    # ════════════════════════════════════════════════
    # HELPERS
    # ════════════════════════════════════════════════
    def _show_in_chat(self, text):
        self.root.ids.chat_display.text += f"\\nSystem: {text}"


if __name__ == "__main__":
    INNMApp().run()
'''

# ============================================================
# 11. requirements.txt
# ============================================================
requirements_txt = """\
kivy>=2.3.0
pandas>=2.0.0
openpyxl>=3.1.0
requests>=2.28.0
"""

# ============================================================
# 12. buildozer.spec
# ============================================================
buildozer_spec = """\
[app]
title = INNM Taskbox
package.name = innmtaskbox
package.domain = org.zqailogic
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,xlsx
version = 2.0.0

requirements = python3,kivy,pandas,openpyxl,requests

orientation = portrait
fullscreen = 0

android.api = 34
android.sdk = 34
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
"""

# ============================================================
# 13. README.md
# ============================================================
readme_md = """\
# INNM Taskbox V2

**Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0**

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Kivy UI (main.py + ui.kv)                │
│  ┌─────────────────────┐    ┌──────────────────────────────┐    │
│  │  Master Chatbot      │    │  Tools Panel                 │    │
│  │  (fixed, async)      │    │  • Add Folder / Add Taskbox  │    │
│  │                      │    │  • Folder list (draggable)   │    │
│  │  User ↔ INNM-WOSDS   │    │  • Taskbox list (draggable)  │    │
│  └──────────┬───────────┘    └──────────────────────────────┘    │
│             │                                                    │
│  ┌──────────▼───────────────────────────────────────────┐        │
│  │           INNM-WOSDS Controller (V2)                 │        │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │        │
│  │  │Front Matrix│ │Back Matrix │ │ Top Matrix       │  │        │
│  │  │(LLM router │ │(async data │ │ (supervise       │  │        │
│  │  │ +fallback) │ │ via Coord.)│ │  taskboxes)      │  │        │
│  │  └────────────┘ └─────┬──────┘ └──────────────────┘  │        │
│  │           ┌───────────┘                               │        │
│  │           │  Center I-Box (single AI API key)         │        │
│  └───────────┼───────────────────────────────────────────┘        │
│              │                                                    │
│  ┌───────────▼──────────┐                                        │
│  │    Coordinator        │                                        │
│  │  (Excel/CSV/SQL-ready │                                        │
│  │   slices per taskbox) │                                        │
│  └───────────┬───────────┘                                        │
│              │                                                    │
│  ┌───────────▼──────────────────────────────────────┐            │
│  │       ZQ Taskbox Engine(s)                        │            │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │            │
│  │  │MTD/YTD   │ │Referral  │ │Weekly    │  ...      │            │
│  │  │Worker    │ │Worker    │ │Deck      │           │            │
│  │  └──────────┘ └──────────┘ └──────────┘           │            │
│  └───────────────────────────────────────────────────┘            │
│                                                                   │
│  ┌─────────────────────────────────────────┐  ← FLOATING BUBBLE  │
│  │  ZQ Feedback Note (standalone)          │                      │
│  │  • Own API keyhole                       │                      │
│  │  • Threaded GitHub Issues integration   │                      │
│  └─────────────────────────────────────────┘                      │
└──────────────────────────────────────────────────────────────────┘
```

## Files

| File | Role |
|---|---|
| `storage.py` | Kivy JsonStore — split `ui_state.json` + `secure.json` |
| `types.py` | Enums: UserRole, TaskType, SourceType, FeedbackSeverity |
| `coordinator.py` | Loads Excel, slices data per-taskbox (CSV/SQL ready) |
| `zq_taskbox.py` | Engine workers — each knows only its own task |
| `innm_controller.py` | INNM-WOSDS: LLM router + heuristic fallback + I-Box |
| `zq_feedback.py` | Standalone feedback → GitHub Issues (threaded) |
| `main.py` | Kivy app: async chatbot, tools, drag-drop, ZQ bubble |
| `ui.kv` | Kivy layout |
| `buildozer.spec` | Android APK config (SDK 34) |
| `requirements.txt` | Python dependencies |

## Quick Start

```bash
pip install kivy pandas openpyxl requests
python main.py
```

## Packaging

**Android:**
```bash
pip install buildozer
buildozer android debug
```

**Windows:**
```bash
pip install pyinstaller
pyinstaller --onefile --add-data "ui.kv;." main.py
```

## License

Apache License 2.0 — Copyright © 2026 ZQ AI LOGIC™
"""

# ============================================================
# 14. docs/INNM-Taskbox-V2-Architecture.md
# ============================================================
v2_arch_md = """\
# INNM Taskbox V2 — Architecture and Usage Guide

**Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0**

## Introduction

The INNM Taskbox V2 is a modular, Kivy-based application for hospital, clinic,
and corporate medical data workflows. V2 introduces:

- Asynchronous Kivy core (background threading + Clock callbacks)
- Split JsonStore storage (ui_state.json + secure.json)
- LLM-based Front Matrix intent router with heuristic fallback
- Threaded ZQ Feedback Note with GitHub Issues integration

## Data Flow

1. User types in master chatbot
2. INNM-WOSDS Front Matrix routes intent (LLM or heuristic)
3. Coordinator loads Excel and slices data for the matched Taskbox
4. ZQ Taskbox engine processes slice and returns structured result
5. Result displayed in chatbot via async callback
6. ZQ Feedback Note (standalone) logs QA feedback → GitHub Issues

## V2 Enhancements over V1

- **Async Core**: All heavy processing runs in daemon threads
- **LLM Router**: Replaces naive substring matching
- **Split Storage**: UI state separated from secrets/config
- **Threaded GitHub**: Network I/O never blocks the UI
- **Coordinator**: Boolean masking instead of chained .copy()
"""

# ============================================================
# 15. docs/INNM-Taskbox-V1-vs-V2-Comparison.md
# ============================================================
v1_v2_md = """\
# INNM Taskbox V1 vs V2 Comparison

**Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0**

| Area | V1 | V2 |
|---|---|---|
| Controller | Heuristic substring matching | LLM router + heuristic fallback |
| Storage | Single JSON file | Split JsonStore (ui_state + secure) |
| UI Threading | Synchronous (blocks on heavy tasks) | Async background threads + Clock |
| ZQ Feedback | Synchronous HTTP | Threaded with timeout + error handling |
| Coordinator | df.copy() chains | Boolean masking, cache, temp-file filter |
| Taskbox Registry | Hardcoded | Dynamic JSON registry, hot-reload |
| Packaging | Basic | Buildozer spec v2, PyInstaller ready |
| Security | Keys in flat JSON | Secrets in secure.json, keyring-ready |
"""

# ============================================================
# 16. data/.gitkeep (placeholder so Git tracks the folder)
# ============================================================
gitkeep = ""

# ── Write all files ──
files = {
    "output/innm-taskbox/LICENSE": license_txt,
    "output/innm-taskbox/.gitignore": gitignore,
    "output/innm-taskbox/storage.py": storage_py,
    "output/innm-taskbox/types.py": types_py,
    "output/innm-taskbox/coordinator.py": coordinator_py,
    "output/innm-taskbox/zq_taskbox.py": zq_taskbox_py,
    "output/innm-taskbox/innm_controller.py": innm_controller_py,
    "output/innm-taskbox/zq_feedback.py": zq_feedback_py,
    "output/innm-taskbox/ui.kv": ui_kv,
    "output/innm-taskbox/main.py": main_py,
    "output/innm-taskbox/requirements.txt": requirements_txt,
    "output/innm-taskbox/buildozer.spec": buildozer_spec,
    "output/innm-taskbox/README.md": readme_md,
    "output/innm-taskbox/docs/INNM-Taskbox-V2-Architecture.md": v2_arch_md,
    "output/innm-taskbox/docs/INNM-Taskbox-V1-vs-V2-Comparison.md": v1_v2_md,
    "output/innm-taskbox/data/.gitkeep": gitkeep,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Total files written: {len(files)}")
for p in sorted(files.keys()):
    print(f"  {p}")
