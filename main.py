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
main.py — INNM Kivy Application entry point.

Layout:
  - Fixed master chatbot (left)  — talks to INNM-WOSDS controller
  - Tools panel (right)          — folders, taskboxes, settings, profile
  - Floating ZQ Feedback bubble  — standalone feedback chat -> GitHub

Run: python main.py
"""
import uuid
import threading
from pathlib import Path
from datetime import datetime
import os
import sys

# Use ANGLE (DirectX) backend when available to avoid Windows GDI Generic OpenGL 1.1
# Must be set before importing Kivy modules so the selected backend is used at import time.
os.environ.setdefault("KIVY_GL_BACKEND", "angle_sdl2")

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

import storage as store
from innm_controller import INNMController
from zq_feedback import ZQFeedbackNote

# ---- Resolve paths relative to THIS file, not the working directory ----
# When frozen by PyInstaller the data files live in sys._MEIPASS (_internal/).
# In dev mode they sit next to main.py.
_BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)).resolve()
_KV_FILE  = str(_BASE_DIR / "ui.kv")


class DraggableToolItem(DragBehavior, Button):
    def __init__(self, item_id, item_type, **kw):
        super().__init__(**kw)
        self.item_id      = item_id
        self.item_type    = item_type
        self.drag_timeout = 999999
        self.drag_distance = 5


class INNMApp(App):

    def build(self):
        self.title = "INNM Taskbox"
        api_key = store.get("innm_api_key", "")
        self.controller = INNMController(base_dir=_BASE_DIR, api_key=api_key)
        self.feedback    = ZQFeedbackNote()
        self.folders     = store.get("folders", [])
        self.taskboxes_ui = store.get("taskboxes_ui", [])

        # Build the UI tree from the .kv file
        root = Builder.load_file(_KV_FILE)

        # Defer list rendering until after the widget tree is fully attached
        Clock.schedule_once(lambda dt: self._render_lists(), 0)

        return root  # <-- Kivy sets self.root from this return value

    # ================================================
    # BACKGROUND TASK HELPER
    # ================================================
    def run_in_background(self, target_func, callback, *args, **kwargs):
        def thread_worker():
            try:
                result = target_func(*args, **kwargs)
                Clock.schedule_once(lambda dt: callback(result, None), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt, err=e: callback(None, err), 0)
        threading.Thread(target=thread_worker, daemon=True).start()

    # ================================================
    # MASTER CHATBOT (async)
    # ================================================
    def send_message(self, text):
        text = (text or "").strip()
        if not text:
            return
        disp = self.root.ids.chat_display
        disp.text += f"\n\nYou: {text}"
        disp.text += f"\nINNM: ⏳ Thinking..."

        def on_innm_reply(reply, error):
            disp.text = disp.text.replace("\nINNM: ⏳ Thinking...", "")
            if error:
                disp.text += f"\nINNM: ⚠️ Error: {str(error)}"
            else:
                disp.text += f"\nINNM: {reply}"

        self.run_in_background(self.controller.process_message, on_innm_reply, text)

    # ================================================
    # FOLDERS
    # ================================================
    def add_folder(self, name):
        name = (name or "").strip()
        if not name:
            return
        entry = {"id": str(uuid.uuid4()), "name": name, "children": []}
        self.folders.append(entry)
        store.set("folders", self.folders)
        self._render_lists()
        self._show_in_chat(f"Folder created: {name}")

    def open_folder(self, fid):
        f = next((x for x in self.folders if x["id"] == fid), None)
        if not f:
            return
        self.root.ids.chat_display.text += f"\n\n[Folder: {f['name']}] opened."

    # ================================================
    # TASKBOXES
    # ================================================
    def add_taskbox(self, name):
        name = (name or "").strip()
        if not name:
            return
        tb_id = name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8]
        entry = {"id": tb_id, "name": name, "task_type": "custom", "source_id": "corporate_excel"}
        self.taskboxes_ui.append(entry)
        store.set("taskboxes_ui", self.taskboxes_ui)
        self.controller.register_taskbox(
            tb_id=tb_id,
            project=name,
            task_type="custom",
            source_id="corporate_excel",
        )
        self._render_lists()
        self._show_in_chat(f"Taskbox created: {name} (id={tb_id})")

    def open_taskbox(self, tid):
        t = next((x for x in self.taskboxes_ui if x["id"] == tid), None)
        if not t:
            return
        self.root.ids.chat_display.text += f"\n\n[Taskbox: {t['name']}] opened."

    # ================================================
    # RENDER LISTS
    # ================================================
    def _render_lists(self):
        if self.root is None:
            return
        fl = self.root.ids.get("folder_list")
        tl = self.root.ids.get("taskbox_list")
        if fl is None or tl is None:
            return
        fl.clear_widgets()
        tl.clear_widgets()
        for f in self.folders:
            btn = DraggableToolItem(
                item_id=f["id"],
                item_type="folder",
                text=f["name"],
                size_hint_y=None,
                height=34,
            )
            btn.bind(on_release=lambda inst, fid=f["id"]: self.open_folder(fid))
            fl.add_widget(btn)
        for t in self.taskboxes_ui:
            btn = DraggableToolItem(
                item_id=t["id"],
                item_type="taskbox",
                text=t["name"],
                size_hint_y=None,
                height=34,
            )
            btn.bind(on_release=lambda inst, tid=t["id"]: self.open_taskbox(tid))
            tl.add_widget(btn)

    # ================================================
    # DRAG & DROP
    # ================================================
    def handle_drop(self, touch):
        widget = touch.grab_current
        if isinstance(widget, DraggableToolItem):
            if widget.item_type == "folder":
                self.open_folder(widget.item_id)
            elif widget.item_type == "taskbox":
                self.open_taskbox(widget.item_id)
            return
        if hasattr(widget, "template_type"):
            if widget.template_type == "folder":
                self._prompt_name("New Folder", self.add_folder)
            elif widget.template_type == "taskbox":
                self._prompt_name("New Taskbox", self.add_taskbox)

    def _prompt_name(self, title, callback):
        content = BoxLayout(orientation="vertical", spacing=5, padding=5)
        ti = TextInput(multiline=False)
        btns = BoxLayout(size_hint_y=None, height=40, spacing=5)
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.3))
        ok_btn     = Button(text="OK")
        cancel_btn = Button(text="Cancel")

        def on_ok(*_):
            if ti.text.strip():
                callback(ti.text.strip())
            popup.dismiss()

        ok_btn.bind(on_release=on_ok)
        cancel_btn.bind(on_release=lambda *_: popup.dismiss())
        btns.add_widget(ok_btn)
        btns.add_widget(cancel_btn)
        content.add_widget(ti)
        content.add_widget(btns)
        popup.open()

    # ================================================
    # ZQ FEEDBACK NOTE (async GitHub)
    # ================================================
    def toggle_zq_panel(self):
        panel = self.root.ids.zq_panel
        if panel.disabled:
            panel.disabled = False
            panel.opacity  = 1
            self.root.ids.zq_history_display.text = self.feedback.get_history_text()
        else:
            panel.disabled = True
            panel.opacity  = 0

    def add_zq_feedback(self, text):
        text = (text or "").strip()
        if not text:
            return
        self.feedback.add_feedback(text)
        self.root.ids.zq_history_display.text = self.feedback.get_history_text()

    def send_zq_to_github(self):
        self._show_in_chat("⏳ Sending feedback to GitHub...")

        def on_github_reply(result, error):
            disp = self.root.ids.chat_display
            disp.text = disp.text.replace("\nSystem: ⏳ Sending feedback to GitHub...", "")
            if error:
                self._show_in_chat(f"GitHub send failed: {str(error)}")
            elif result.get("status") == "ok":
                self._show_in_chat(f"Feedback sent to GitHub: {result.get('url', '')}")
            else:
                self._show_in_chat(f"GitHub send failed: {result.get('message', '')}")

        title = "ZQ Feedback Session — " + datetime.now().strftime("%Y-%m-%d %H:%M")
        self.run_in_background(self.feedback.send_to_github, on_github_reply, title=title)

    # ================================================
    # SETTINGS / PROFILE
    # ================================================
    def open_settings_screen(self):
        self._show_in_chat("Settings screen — configure INNM API key and preferences.")

    def open_profile_screen(self):
        self._show_in_chat("Profile screen — user info and role management.")

    # ================================================
    # HELPERS
    # ================================================
    def _show_in_chat(self, text):
        if self.root is not None:
            self.root.ids.chat_display.text += f"\nSystem: {text}"


if __name__ == "__main__":
    INNMApp().run()
