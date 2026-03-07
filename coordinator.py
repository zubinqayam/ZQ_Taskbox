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
