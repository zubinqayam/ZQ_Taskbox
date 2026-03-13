"""
innm_guard.py - GUARD module for INNM.

Applies policy checks and trust-based access decisions.
"""
from __future__ import annotations

from typing import Dict, Optional, Set

from innm_governance import TrustDecision


class INNMGuard:
    def __init__(self, allowed_sources: Optional[Set[str]] = None):
        self.allowed_sources = allowed_sources or {"chat_ui", "api", "system"}

    def authorize(self, source: str, decision: TrustDecision) -> Dict[str, str]:
        if source not in self.allowed_sources:
            return {
                "ok": "false",
                "reason": f"source_not_allowed:{source}",
            }

        if decision.action == "suspend_block":
            return {
                "ok": "false",
                "reason": "trust_suspended",
            }

        if decision.action == "jit_approval":
            return {
                "ok": "true",
                "reason": "jit_required",
            }

        return {
            "ok": "true",
            "reason": "allowed",
        }
