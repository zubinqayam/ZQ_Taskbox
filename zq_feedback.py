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
        return "\n".join(lines)

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
