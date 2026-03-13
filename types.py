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

# Use lazy import via __getattr__ to avoid shadowing stdlib 'types' module
# during PyInstaller bundling (circular import guard).

_public = ["UserRole", "TaskType", "SourceType", "FeedbackSeverity"]
__all__ = _public


def __getattr__(name):
    if name in _public:
        import importlib
        _zq = importlib.import_module("zq_types")
        return getattr(_zq, name)
    raise AttributeError(f"module 'types' (shim) has no attribute {name!r}")
