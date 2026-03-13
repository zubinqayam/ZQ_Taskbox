# INNM Taskbox V2

## License Notice

Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0

## Architecture

```text
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

| File                 | Role                                                    |
| -------------------- | ------------------------------------------------------- |
| `storage.py`         | Kivy JsonStore — split `ui_state.json` + `secure.json`  |
| `zq_types.py`        | Enums: UserRole, TaskType, SourceType, FeedbackSeverity |
| `coordinator.py`     | Loads Excel, slices data per-taskbox (CSV/SQL ready)    |
| `zq_taskbox.py`      | Engine workers — each knows only its own task           |
| `innm_controller.py` | INNM-WOSDS: LLM router + heuristic fallback + I-Box     |
| `zq_feedback.py`     | Standalone feedback → GitHub Issues (threaded)          |
| `main.py`            | Kivy app: async chatbot, tools, drag-drop, ZQ bubble    |
| `ui.kv`              | Kivy layout                                             |
| `buildozer.spec`     | Android APK config (SDK 34)                             |
| `requirements.txt`   | Python dependencies                                     |

## Quick Start

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "kivy[base]" --pre --extra-index-url https://kivy.org/downloads/simple/
python -m pip install pandas openpyxl requests pyinstaller
$env:ZQ_GITHUB_TOKEN = "ghp_your_token_here"
python main.py
```

Notes:

- Python 3.12 is the working Windows path for Kivy in this repo.
- The app expects `ZQ_GITHUB_TOKEN` when sending feedback issues to GitHub.

## Packaging

**Android:**

```bash
pip install buildozer
buildozer android debug
```

**Windows:**

```powershell
python -m PyInstaller --onefile --windowed --name INNM_Taskbox --add-data "ui.kv;." main.py
```

## Governance Phase 1

Implemented in the current codebase:

- Intake envelope + provenance assignment (I-Box): `innm_governance.py`
- Trust score evaluation + threshold enforcement: `innm_governance.py`
- Append-only local ledger (`ZQ_AI_LOGIC_LEDGER`): `~/.innm/zq_ai_logic_ledger.jsonl`
- Non-Repeating Error Doctrine signature index: `~/.innm/error_signature_index.json`

Controller integration path:

- `INNMController.process_message(...)` now executes intake, trust gate, ledger logging, and doctrine-compliant error encoding.

## License

Apache License 2.0 — Copyright © 2026 ZQ AI LOGIC™
