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
  - Fixed master chatbot (left) — talks to INNM-WOSDS controller
  - Tools panel (right)         — folders, taskboxes, settings, profile
  - Floating ZQ bubble          — toggles slide-in Feedback Drawer (right)
  - Feedback Drawer             — dual-channel AI chat -> isolated memory -> GitHub

Run: python main.py
"""
import copy
import uuid
import threading
from pathlib import Path
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import BooleanProperty
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

import storage as store
from innm_controller import INNMController
from zq_feedback import ZQFeedbackNote


# ════════════════════════════════════════════════
# ISOLATED MEMORY BANKS (per-channel context)
# ════════════════════════════════════════════════
class ZQMemoryBanks:
    """Maintains isolated conversation history for each named channel."""

    ALLOWED_CHANNELS = frozenset({"main", "feedback"})

    def __init__(self):
        self.banks = {"main": [], "feedback": []}

    def add_message(self, channel: str, role: str, content: str):
        if channel not in self.ALLOWED_CHANNELS:
            raise ValueError(
                f"Unknown channel {channel!r}. Allowed: {sorted(self.ALLOWED_CHANNELS)}"
            )
        self.banks[channel].append({"role": role, "content": content})

    def get_history(self, channel: str) -> list:
        return copy.deepcopy(self.banks.get(channel, []))

    def clear_memory(self, channel: str):
        if channel in self.banks:
            self.banks[channel] = []


class DraggableToolItem(DragBehavior, Button):
    def __init__(self, item_id, item_type, **kw):
        super().__init__(**kw)
        self.item_id = item_id
        self.item_type = item_type
        self.drag_timeout = 999999
        self.drag_distance = 5


class INNMApp(App):
    # Animation constants for the feedback drawer
    _DRAWER_HIDDEN_RIGHT = 1.5   # off-screen to the right (matches ui.kv initial pos)
    _DRAWER_VISIBLE_RIGHT = 1.0  # flush with right edge of window
    _DRAWER_ANIM_DURATION = 0.3

    # Kivy observable property — KV can bind size_hint to this
    drawer_open = BooleanProperty(False)

    def build(self):
        self.title = "INNM Taskbox"
        base_dir = Path(".").resolve()
        api_key = store.get("innm_api_key", "")
        self.controller = INNMController(base_dir=base_dir, api_key=api_key)
        self.feedback = ZQFeedbackNote()
        self.memory_banks = ZQMemoryBanks()
        self.folders = store.get("folders", [])
        self.taskboxes_ui = store.get("taskboxes_ui", [])
        self.root = Builder.load_file("ui.kv")
        self._render_lists()
        return self.root

    # ════════════════════════════════════════════════
    # BACKGROUND TASK HELPER
    # ════════════════════════════════════════════════
    def run_in_background(self, target_func, callback, *args, **kwargs):
        def thread_worker():
            try:
                result = target_func(*args, **kwargs)
                Clock.schedule_once(lambda dt: callback(result, None), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: callback(None, e), 0)
        threading.Thread(target=thread_worker, daemon=True).start()

    # ════════════════════════════════════════════════
    # MASTER CHATBOT — channel="main" (async)
    # ════════════════════════════════════════════════
    def send_message(self, text, channel="main"):
        """Send *text* through *channel* ("main" or "feedback").

        The message is stored in the corresponding ZQMemoryBanks bank, routed
        to the INNM controller for an AI reply, and the result is appended to
        the channel's history TextInput widget.
        """
        text = (text or "").strip()
        if not text:
            return
        self.memory_banks.add_message(channel, "user", text)
        if channel == "main":
            disp = self.root.ids.chat_display
            prefix = "INNM"
        else:
            disp = self.root.ids.feedback_history_display
            prefix = "ZQ"
        disp.text += f"\n\nYou: {text}"
        placeholder_token = uuid.uuid4().hex
        placeholder = f"\n{prefix}: ⏳ Thinking... [{placeholder_token}]"
        disp.text += placeholder

        def on_innm_reply(reply, error):
            # Remove only this request's placeholder instance
            disp.text = disp.text.replace(placeholder, "", 1)
            if error:
                msg = f"⚠️ Error: {str(error)}"
            else:
                msg = reply
            self.memory_banks.add_message(channel, "assistant", msg)
            disp.text += f"\n{prefix}: {msg}"

        self.run_in_background(self.controller.process_message, on_innm_reply, text)

    # ════════════════════════════════════════════════
    # FOLDERS
    # ════════════════════════════════════════════════
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

    # ════════════════════════════════════════════════
    # TASKBOXES
    # ════════════════════════════════════════════════
    def add_taskbox(self, name):
        name = (name or "").strip()
        if not name:
            return
        tb_id = name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8]
        entry = {"id": tb_id, "name": name, "task_type": "custom", "source_id": "corporate_excel"}
        self.taskboxes_ui.append(entry)
        store.set("taskboxes_ui", self.taskboxes_ui)
        self.controller.register_taskbox(
            tb_id=tb_id, project=name, task_type="custom", source_id="corporate_excel",
        )
        self._render_lists()
        self._show_in_chat(f"Taskbox created: {name} (id={tb_id})")

    def open_taskbox(self, tid):
        t = next((x for x in self.taskboxes_ui if x["id"] == tid), None)
        if not t:
            return
        self.root.ids.chat_display.text += f"\n\n[Taskbox: {t['name']}] opened."

    # ════════════════════════════════════════════════
    # RENDER LISTS
    # ════════════════════════════════════════════════
    def _render_lists(self):
        fl = self.root.ids.folder_list
        tl = self.root.ids.taskbox_list
        fl.clear_widgets()
        tl.clear_widgets()
        for f in self.folders:
            btn = DraggableToolItem(
                item_id=f["id"], item_type="folder",
                text=f["name"], size_hint_y=None, height=34,
            )
            btn.bind(on_release=lambda inst, fid=f["id"]: self.open_folder(fid))
            fl.add_widget(btn)
        for t in self.taskboxes_ui:
            btn = DraggableToolItem(
                item_id=t["id"], item_type="taskbox",
                text=t["name"], size_hint_y=None, height=34,
            )
            btn.bind(on_release=lambda inst, tid=t["id"]: self.open_taskbox(tid))
            tl.add_widget(btn)

    # ════════════════════════════════════════════════
    # DRAG & DROP
    # ════════════════════════════════════════════════
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
        ok_btn = Button(text="OK")
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

    # ════════════════════════════════════════════════
    # FEEDBACK DRAWER — channel="feedback"
    # ════════════════════════════════════════════════
    def toggle_feedback_drawer(self):
        """Slide the feedback drawer in/out using Animation."""
        drawer = self.root.ids.feedback_drawer
        if not self.drawer_open:
            anim = Animation(
                pos_hint={"right": self._DRAWER_VISIBLE_RIGHT, "top": 1},
                duration=self._DRAWER_ANIM_DURATION,
                t="out_quad",
            )
            anim.start(drawer)
            self.drawer_open = True
            self.root.ids.feedback_history_display.text = self._get_feedback_history_text()
        else:
            anim = Animation(
                pos_hint={"right": self._DRAWER_HIDDEN_RIGHT, "top": 1},
                duration=self._DRAWER_ANIM_DURATION,
                t="in_quad",
            )
            anim.start(drawer)
            self.drawer_open = False

    def send_feedback_message(self, text):
        """Route a message through the feedback channel."""
        self.send_message(text, channel="feedback")

    def inject_feedback_to_github(self):
        """Send feedback channel history to GitHub via zq_feedback.py."""
        history = self.memory_banks.get_history("feedback")
        if not history:
            self._show_in_chat("No feedback to inject.")
            return
        self.feedback.clear_history()
        for msg in history:
            # Only user-authored messages are forwarded to GitHub; AI responses
            # are context-only and not included in the submitted feedback report.
            if msg["role"] == "user":
                self.feedback.add_feedback(msg["content"])
        self._show_in_chat("⏳ Injecting feedback to GitHub...")

        def on_github_reply(result, error):
            chat = self.root.ids.chat_display
            chat.text = chat.text.replace("\nSystem: ⏳ Injecting feedback to GitHub...", "")
            if error:
                self._show_in_chat(f"GitHub inject failed: {str(error)}")
            elif result.get("status") == "ok":
                self._show_in_chat(f"Feedback injected to GitHub: {result.get('url', '')}")
                self.memory_banks.clear_memory("feedback")
                self.root.ids.feedback_history_display.text = ""
            else:
                self._show_in_chat(f"GitHub inject failed: {result.get('message', '')}")

        title = "ZQ Feedback Session — " + datetime.now().strftime("%Y-%m-%d %H:%M")
        self.run_in_background(self.feedback.send_to_github, on_github_reply, title=title)

    def _get_feedback_history_text(self) -> str:
        history = self.memory_banks.get_history("feedback")
        lines = []
        for msg in history:
            role = "You" if msg["role"] == "user" else "ZQ"
            lines.append(f"{role}: {msg['content']}")
        return "\n\n".join(lines)

    # ════════════════════════════════════════════════
    # LEGACY ZQ PANEL DELEGATES (backward-compat)
    # ════════════════════════════════════════════════
    def toggle_zq_panel(self):
        self.toggle_feedback_drawer()

    def add_zq_feedback(self, text):
        self.send_feedback_message(text)

    def send_zq_to_github(self):
        self.inject_feedback_to_github()

    # ════════════════════════════════════════════════
    # SETTINGS / PROFILE (stubs)
    # ════════════════════════════════════════════════
    def open_settings_screen(self):
        self._show_in_chat("Settings screen — configure INNM API key and preferences.")

    def open_profile_screen(self):
        self._show_in_chat("Profile screen — user info and role management.")

    # ════════════════════════════════════════════════
    # HELPERS
    # ════════════════════════════════════════════════
    def _show_in_chat(self, text):
        self.root.ids.chat_display.text += f"\nSystem: {text}"


if __name__ == "__main__":
    INNMApp().run()
