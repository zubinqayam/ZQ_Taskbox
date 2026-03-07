# INNM Taskbox V2

**Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0**

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Kivy UI (main.py + ui.kv)                │
│  ┌─────────────────────┐    ┌──────────────────────────────┐    │
│  │  Master Chatbot      │    │  Tools Panel                 │    │
│  │  (fixed, async)      │    │  • Add Folder / Add Taskbox  │    │
│  │                      │    │  • Folder list (draggable)   │    │
│  │  User ↔ INNM-WOSDS   │    │  • Taskbox list (draggable)  │    │
│  └──────────┬───────────┘    └──────────────────────────────┘    │
│             │                                                    │
│  ┌──────────▼───────────────────────────────────────────┐        │
│  │           INNM-WOSDS Controller (V2)                 │        │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │        │
│  │  │Front Matrix│ │Back Matrix │ │ Top Matrix       │  │        │
│  │  │(LLM router │ │(async data │ │ (supervise       │  │        │
│  │  │ +fallback) │ │ via Coord.)│ │  taskboxes)      │  │        │
│  │  └────────────┘ └─────┬──────┘ └──────────────────┘  │        │
│  │           ┌───────────┘                               │        │
│  │           │  Center I-Box (single AI API key)         │        │
│  └───────────┼───────────────────────────────────────────┘        │
│              │                                                    │
│  ┌───────────▼──────────┐                                        │
│  │    Coordinator        │                                        │
│  │  (Excel/CSV/SQL-ready │                                        │
│  │   slices per taskbox) │                                        │
│  └───────────┬───────────┘                                        │
│              │                                                    │
│  ┌───────────▼──────────────────────────────────────┐            │
│  │       ZQ Taskbox Engine(s)                        │            │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │            │
│  │  │MTD/YTD   │ │Referral  │ │Weekly    │  ...      │            │
│  │  │Worker    │ │Worker    │ │Deck      │           │            │
│  │  └──────────┘ └──────────┘ └──────────┘           │            │
│  └───────────────────────────────────────────────────┘            │
│                                                                   │
│  ┌─────────────────────────────────────────┐  ← FLOATING BUBBLE  │
│  │  ZQ Feedback Note (standalone)          │                      │
│  │  • Own API keyhole                       │                      │
│  │  • Threaded GitHub Issues integration   │                      │
│  └─────────────────────────────────────────┘                      │
└──────────────────────────────────────────────────────────────────┘
```

## Files

| File | Role |
|---|---|
| `storage.py` | Kivy JsonStore — split `ui_state.json` + `secure.json` |
| `types.py` | Enums: UserRole, TaskType, SourceType, FeedbackSeverity |
| `coordinator.py` | Loads Excel, slices data per-taskbox (CSV/SQL ready) |
| `zq_taskbox.py` | Engine workers — each knows only its own task |
| `innm_controller.py` | INNM-WOSDS: LLM router + heuristic fallback + I-Box |
| `zq_feedback.py` | Standalone feedback → GitHub Issues (threaded) |
| `main.py` | Kivy app: async chatbot, tools, drag-drop, ZQ bubble |
| `ui.kv` | Kivy layout |
| `buildozer.spec` | Android APK config (SDK 34) |
| `requirements.txt` | Python dependencies |

## Quick Start

```bash
pip install kivy pandas openpyxl requests
python main.py
```

## Packaging

**Android:**
```bash
pip install buildozer
buildozer android debug
```

**Windows:**
```bash
pip install pyinstaller
pyinstaller --onefile --add-data "ui.kv;." main.py
```

## License

Apache License 2.0 — Copyright © 2026 ZQ AI LOGIC™
