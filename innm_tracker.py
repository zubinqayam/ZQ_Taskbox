"""
innm_tracker.py - TRACKER module for INNM.

Provides a thin API for provenance and telemetry event recording.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from innm_governance import INNMGovernance


class INNMTracker:
    def __init__(self, governance: INNMGovernance):
        self.governance = governance

    def record(
        self,
        provenance_id: str,
        agent_id: str,
        action_type: str,
        trust_score: float,
        metadata: Optional[Dict[str, Any]] = None,
        error_signature: Optional[str] = None,
    ) -> None:
        self.governance.log_event(
            provenance_id=provenance_id,
            agent_id=agent_id,
            action_type=action_type,
            trust_score=trust_score,
            metadata=metadata,
            error_signature=error_signature,
        )
