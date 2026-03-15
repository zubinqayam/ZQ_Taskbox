"""
make_spec.py — Generates INNM_Taskbox.spec for PyInstaller on Windows CI.
Run: python make_spec.py
"""
from kivy_deps import sdl2, glew
from pathlib import Path

spec_content = """\
# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[*sdl2.dep_bins, *glew.dep_bins],
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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='INNM_Taskbox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in sdl2.dep_bins + glew.dep_bins],
    strip=False,
    upx=False,
    upx_exclude=[],
    name='INNM_Taskbox',
)
"""

Path("INNM_Taskbox.spec").write_text(spec_content, encoding="utf-8")
print("INNM_Taskbox.spec written successfully.")
