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
types.py — DEPRECATED shim. Import from zq_types instead.
Kept for backward compatibility only.
"""
# Re-export everything from zq_types so legacy imports keep working
from zq_types import UserRole, TaskType, SourceType, FeedbackSeverity

__all__ = ["UserRole", "TaskType", "SourceType", "FeedbackSeverity"]
