"""
innm_validater.py - VALIDATER module for INNM.

Enforces baseline schema and input constraints for incoming requests.
"""
from __future__ import annotations

from typing import Any, Dict


class INNMValidater:
    def validate_request(self, normalized: Dict[str, Any]) -> Dict[str, Any]:
        payload = (normalized.get("payload") or "").strip()
        source = (normalized.get("source") or "").strip()

        errors = []
        if not payload:
            errors.append("payload is empty")
        if not source:
            errors.append("source is missing")
        if len(payload) > 8000:
            errors.append("payload length exceeds 8000 characters")

        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "payload_len": len(payload),
        }
