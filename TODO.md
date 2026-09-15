# INNM Taskbox V2 TODO

## Current Status

✅ SDL deps retry logic added to build scripts (complete)

## Python Version Issue

⚠️ Kivy deps fail on Python 3.12/3.14 (no sdl2_dev wheel).

- Downgrade to Python 3.11 recommended (confirmed by user).

## Next Steps

1. **Install Python 3.11 + Fresh Venv**
   - Download Python 3.11 from python.org
   - `py -3.11 -m venv .venv311`
   - `.venv311\\Scripts\\activate.bat && pip install kivy[base] -r requirements.txt`

2. **Run Desktop App**
   - `python main.py`
   - Test UI flows

3. **Sample Data**
   - Create data/corporate_excel.xlsx dummy

4. **APK Build (WSL)**
   - `./scripts/build_apk_wsl.sh`

5. **Complete**
   - PR changes
