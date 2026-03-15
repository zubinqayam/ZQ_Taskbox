"""
make_spec.py — Generates INNM_Taskbox.spec for PyInstaller >=6 on Windows CI.
Run: python make_spec.py
"""
from pathlib import Path

spec_content = """\
# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 6.x compatible spec (no cipher/block_cipher/win_no_prefer_redirects)
from PyInstaller.building.datastruct import Tree
from kivy_deps import sdl2, glew

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('ui.kv', '.')],
    hiddenimports=[
        'kivy.core.window.window_sdl2',
        'kivy.core.audio.audio_sdl2',
        'kivy.core.image.img_sdl2',
        'kivy.core.text.text_sdl2',
        'kivy.core.clipboard.clipboard_sdl2',
        'storage',
        'innm_controller',
        'zq_feedback',
        'innm_connect',
        'innm_governance',
        'innm_guard',
        'innm_tracker',
        'innm_validater',
        'coordinator',
    ],
    hookspath=[],
    excludes=['tkinter', 'matplotlib', 'scipy', '_pytest', 'unittest'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='INNM_Taskbox',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in sdl2.dep_bins + glew.dep_bins],
    strip=False,
    upx=False,
    name='INNM_Taskbox',
)
"""

Path("INNM_Taskbox.spec").write_text(spec_content, encoding="utf-8")
print("INNM_Taskbox.spec written successfully.")
