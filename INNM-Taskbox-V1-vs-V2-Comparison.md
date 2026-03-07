# INNM Taskbox V1 vs V2 Comparison

**Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0**

| Area | V1 | V2 |
|---|---|---|
| Controller | Heuristic substring matching | LLM router + heuristic fallback |
| Storage | Single JSON file | Split JsonStore (ui_state + secure) |
| UI Threading | Synchronous (blocks on heavy tasks) | Async background threads + Clock |
| ZQ Feedback | Synchronous HTTP | Threaded with timeout + error handling |
| Coordinator | df.copy() chains | Boolean masking, cache, temp-file filter |
| Taskbox Registry | Hardcoded | Dynamic JSON registry, hot-reload |
| Packaging | Basic | Buildozer spec v2, PyInstaller ready |
| Security | Keys in flat JSON | Secrets in secure.json, keyring-ready |
