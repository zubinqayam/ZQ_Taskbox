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
Your job is to map the user's natural language input to the correct taskbox.

Available Taskboxes:
{registry_str}

Rules:
1. Match the user's request to the MOST RELEVANT taskbox_id based on project or task type.
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
