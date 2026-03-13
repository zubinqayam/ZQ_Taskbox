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
zq_types.py — Enums and data types for INNM app.
Renamed from types.py to avoid shadowing Python stdlib types module.
"""
from enum import Enum


class UserRole(Enum):
    GUEST = "guest"
    PLAYER = "player"
    ADMIN = "admin"


class TaskType(Enum):
    MTD_YTD = "mtd_ytd"
    REFERRAL_TRACKER = "referral_tracker"
    WEEKLY_DECK = "weekly_deck"
    RESEARCH_DAILY = "research_daily"
    CUSTOM = "custom"


class SourceType(Enum):
    CORPORATE_EXCEL = "corporate_excel"
    CSV = "csv"
    SQL = "sql"
    NONE = "none"
    CUSTOM = "custom"


class FeedbackSeverity(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    IMPROVEMENT = "improvement"
    BUG = "bug"
