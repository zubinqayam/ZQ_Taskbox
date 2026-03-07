# INNM Taskbox V2 — Architecture and Usage Guide

**Copyright © 2026 ZQ AI LOGIC™ — Apache License 2.0**

## Introduction

The INNM Taskbox V2 is a modular, Kivy-based application for hospital, clinic,
and corporate medical data workflows. V2 introduces:

- Asynchronous Kivy core (background threading + Clock callbacks)
- Split JsonStore storage (ui_state.json + secure.json)
- LLM-based Front Matrix intent router with heuristic fallback
- Threaded ZQ Feedback Note with GitHub Issues integration

## Data Flow

1. User types in master chatbot
2. INNM-WOSDS Front Matrix routes intent (LLM or heuristic)
3. Coordinator loads Excel and slices data for the matched Taskbox
4. ZQ Taskbox engine processes slice and returns structured result
5. Result displayed in chatbot via async callback
6. ZQ Feedback Note (standalone) logs QA feedback → GitHub Issues

## V2 Enhancements over V1

- **Async Core**: All heavy processing runs in daemon threads
- **LLM Router**: Replaces naive substring matching
- **Split Storage**: UI state separated from secrets/config
- **Threaded GitHub**: Network I/O never blocks the UI
- **Coordinator**: Boolean masking instead of chained .copy()
