"""
innm_governance.py - Phase 1 governance primitives for INNM.

Implements:
- I-Box intake envelope with provenance_id assignment
- Trust score calculation and threshold enforcement
- Append-only local ZQ_AI_LOGIC_LEDGER writer
- Non-repeating error doctrine with signature tracking
"""
from __future__ import annotations

import hashlib
import json
import traceback
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class TrustDecision:
    action: str
    grade: str
    score: float


class INNMGovernance:
    def __init__(self, app_dir: Optional[Path] = None):
        self.app_dir = app_dir or (Path.home() / ".innm")
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.app_dir / "zq_ai_logic_ledger.jsonl"
        self.error_index_path = self.app_dir / "error_signature_index.json"
        self._lock = Lock()

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _sha256(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_intake_envelope(self, payload: str, agent_id: str, source: str) -> Dict[str, Any]:
        ts = self._utc_now()
        payload_hash = self._sha256(payload)
        seed = f"{payload_hash}|{agent_id}|{source}|{ts}|{uuid.uuid4()}"
        provenance_id = self._sha256(seed)
        return {
            "provenance_id": provenance_id,
            "timestamp": ts,
            "agent_id": agent_id,
            "source": source,
            "payload": payload,
            "payload_hash": payload_hash,
            "plane": "I-Box",
        }

    def calculate_trust_score(self, agent_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        profile = agent_profile or {}

        verification_status = float(profile.get("verification_status", 0.8))
        action_success_rate = float(profile.get("action_success_rate", 0.9))
        security_alerts = float(profile.get("security_alerts", 0.0))
        uptime = float(profile.get("uptime", 0.9))
        compliance_score = float(profile.get("compliance_score", 0.85))
        age_history = float(profile.get("age_history", 0.75))
        drift_detection = float(profile.get("drift_detection", 0.9))
        user_feedback = float(profile.get("user_feedback", 0.8))

        security_component = max(0.0, 1.0 - min(security_alerts / 5.0, 1.0))
        drift_component = max(0.0, min(drift_detection, 1.0))

        factors = [
            max(0.0, min(verification_status, 1.0)),
            max(0.0, min(action_success_rate, 1.0)),
            security_component,
            max(0.0, min(uptime, 1.0)),
            max(0.0, min(compliance_score, 1.0)),
            max(0.0, min(age_history, 1.0)),
            drift_component,
            max(0.0, min(user_feedback, 1.0)),
        ]
        weights = [0.25, 0.15, 0.15, 0.15, 0.10, 0.10, 0.05, 0.05]

        score = sum(w * f for w, f in zip(weights, factors))
        score = max(0.0, min(score, 1.0))

        if score >= 0.85:
            grade = "A+"
        elif score >= 0.70:
            grade = "A"
        elif score >= 0.60:
            grade = "B"
        elif score >= 0.50:
            grade = "C"
        elif score >= 0.30:
            grade = "D"
        else:
            grade = "F"

        return {"score": score, "grade": grade, "factors": factors}

    @staticmethod
    def enforce_trust_score(score: float, grade: str) -> TrustDecision:
        if score >= 0.70:
            return TrustDecision(action="allow", grade=grade, score=score)
        if score >= 0.50:
            return TrustDecision(action="jit_approval", grade=grade, score=score)
        if score >= 0.30:
            return TrustDecision(action="warn_monitor", grade=grade, score=score)
        return TrustDecision(action="suspend_block", grade=grade, score=score)

    def append_ledger(self, entry: Dict[str, Any]) -> None:
        line = json.dumps(entry, ensure_ascii=True)
        with self._lock:
            with self.ledger_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def log_event(
        self,
        provenance_id: str,
        agent_id: str,
        action_type: str,
        trust_score: float,
        metadata: Optional[Dict[str, Any]] = None,
        error_signature: Optional[str] = None,
    ) -> None:
        entry = {
            "ledger_id": str(uuid.uuid4()),
            "timestamp": self._utc_now(),
            "provenance_id": provenance_id,
            "agent_id": agent_id,
            "action_type": action_type,
            "trust_score": round(float(trust_score), 4),
            "error_signature": error_signature,
            "metadata": metadata or {},
        }
        self.append_ledger(entry)

    def _load_error_index(self) -> Dict[str, Any]:
        if not self.error_index_path.exists():
            return {}
        try:
            return json.loads(self.error_index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _save_error_index(self, data: Dict[str, Any]) -> None:
        self.error_index_path.write_text(
            json.dumps(data, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

    def encode_error_signature(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_payload = context or {}
        serialized_context = json.dumps(context_payload, sort_keys=True, default=str)
        canonical = "|".join([
            error.__class__.__name__,
            str(error),
            serialized_context,
        ])
        signature = self._sha256(canonical)

        with self._lock:
            index = self._load_error_index()
            now = self._utc_now()
            is_repeat = signature in index
            if is_repeat:
                index[signature]["count"] = int(index[signature].get("count", 1)) + 1
                index[signature]["last_seen"] = now
            else:
                index[signature] = {
                    "count": 1,
                    "first_seen": now,
                    "last_seen": now,
                    "error_type": error.__class__.__name__,
                    "message": str(error),
                }
            self._save_error_index(index)

        return {
            "signature": signature,
            "is_repeat": is_repeat,
            "count": index[signature]["count"],
            "trace": traceback.format_exc(limit=3),
        }
