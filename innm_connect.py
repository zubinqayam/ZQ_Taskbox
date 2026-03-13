"""
innm_connect.py - CONNECT module for INNM.

Normalizes inbound requests into a predictable envelope before I-Box intake.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class INNMConnect:
    def normalize(self, payload: str, source: str = "chat_ui", channel: str = "default") -> Dict[str, Any]:
        text = (payload or "").strip()
        return {
            "source": source,
            "channel": channel,
            "payload": text,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "content_type": "text/plain",
        }
