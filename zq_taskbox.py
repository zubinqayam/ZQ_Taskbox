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
