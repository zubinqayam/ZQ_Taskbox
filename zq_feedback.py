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

KEYHOLE PRIORITY ORDER (token resolution):
  1. Environment variable:  ZQ_GITHUB_TOKEN  (set in PowerShell / .env)
  2. Kivy persistent store:  zq_fdk_github_token
  3. Empty string (no-op — shows error)

Usage (one-time setup in PowerShell before running app):
  $env:ZQ_GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
  python main.py
"""
import os
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
        # Keyhole: env var takes priority over stored value
        self.github_token: str = (
            os.environ.get("ZQ_GITHUB_TOKEN", "")
            or store.get("zq_fdk_github_token", "")
        )
        self.repo_owner: str = store.get("zq_fdk_repo_owner", "zubinqayam")
        self.repo_name: str  = store.get("zq_fdk_repo_name",  "ZQ_Taskbox")
        self.history: list   = store.get("zq_fdk_history",    [])

    # ───────────────────────────────────────────────────────
    # KEYHOLE SETTERS
    # ───────────────────────────────────────────────────────
    def set_ai_api_key(self, key: str):
        self.api_key = key
        store.set("zq_fdk_api_key", key)

    def set_github_token(self, token: str):
        """Override keyhole token at runtime (also persists to store)."""
        self.github_token = token
        store.set("zq_fdk_github_token", token)

    def set_repo(self, owner: str, name: str):
        self.repo_owner = owner
        self.repo_name  = name
        store.set("zq_fdk_repo_owner", owner)
        store.set("zq_fdk_repo_name",  name)

    # ───────────────────────────────────────────────────────
    # FEEDBACK STORE
    # ───────────────────────────────────────────────────────
    def add_feedback(self, text: str, severity: str = "improvement"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text":      text,
            "severity":  severity,
        }
        self.history.append(entry)
        store.set("zq_fdk_history", self.history)
        return entry

    def get_history(self) -> list:
        return self.history

    def get_history_text(self) -> str:
        lines = []
        for e in self.history:
            ts  = e.get("timestamp", "?")[:19]
            sev = e.get("severity",  "?")
            txt = e.get("text",      "")
            lines.append(f"[{ts}] ({sev}) {txt}")
        return "\n".join(lines)

    def clear_history(self):
        self.history = []
        store.set("zq_fdk_history", [])

    # ───────────────────────────────────────────────────────
    # GITHUB ISSUE SENDER (triggers the branch pipeline)
    # ───────────────────────────────────────────────────────
    def send_to_github(
        self,
        title:  str,
        body:   Optional[str]  = None,
        labels: Optional[list] = None,
    ) -> dict:
        if not HAS_REQUESTS:
            return {"status": "error", "message": "requests library not installed."}

        # Re-check env var at send time (in case set after __init__)
        token = (
            os.environ.get("ZQ_GITHUB_TOKEN", "")
            or self.github_token
        )
        if not token or not self.repo_owner:
            return {
                "status":  "error",
                "message": (
                    "GitHub token missing. "
                    "Set $env:ZQ_GITHUB_TOKEN in PowerShell before launching."
                ),
            }

        url     = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
        headers = {
            "Authorization": f"token {token}",
            "Accept":        "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        # Label MUST be 'feedback' — this is what triggers the branch workflow
        issue_labels = labels or ["feedback"]
        data = {
            "title":  title,
            "body":   body or self._build_github_body(),
            "labels": issue_labels,
        }
        try:
            r = requests.post(url, headers=headers, json=data, timeout=15)
            if r.status_code == 201:
                issue_url = r.json().get("html_url", "")
                issue_num = r.json().get("number", "?")
                self.clear_history()  # Reset after successful send
                return {
                    "status":     "ok",
                    "url":        issue_url,
                    "issue_num":  issue_num,
                    "message":    f"Issue #{issue_num} created. Branch pipeline triggered.",
                }
            return {"status": "error", "message": f"HTTP {r.status_code}: {r.text[:200]}"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Network Error: {str(e)}"}

    def _build_github_body(self) -> str:
        """Build a rich Markdown body for the GitHub Issue."""
        lines = [
            "## ZQ Feedback Session",
            "**App:** INNM Taskbox v2.0.0",
            f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M')} (Sohar, OM)",
            "",
            "### Entries",
            "```",
            self.get_history_text() or "(no entries)",
            "```",
            "",
            "---",
            "*Auto-generated by ZQ Feedback Pipeline. "
            "This issue will trigger an enhancement workbranch.*",
        ]
        return "\n".join(lines)
