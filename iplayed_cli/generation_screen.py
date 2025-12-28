import asyncio
import threading
from typing import Callable

from completions_file_db import deploy_markdown_files, refresh_all_igdb_games
from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ProgressBar, Static


class GenerationScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    class GenerationComplete(Message):
        def __init__(self, task_name: str) -> None:
            self.task_name = task_name
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield Button("Generate All Markdown Files", id="markdown")
                yield Button("Refresh All IGDB Game entries", id="igdb_refresh")
                yield ProgressBar(id="progress", total=10)
                yield Static("Status", id="status")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        task_map = {
            "markdown": deploy_markdown_files,
            "igdb_refresh": refresh_all_igdb_games,
        }
        func = task_map.get(event.button.id)
        if func:
            # Schedule the task so the event handler can return immediately
            # and the UI can process progress updates from the background thread.
            asyncio.create_task(self.run_task(event.button.label, func))

    async def run_task(self, task_name: str, func: Callable[[Callable[[int, int, str], None]], None]) -> None:
        """Run a sync task in a background thread with live progress updates."""

        # Reset progress
        self._update_ui(0, 1, f"Starting {task_name}...")

        def thread_entry():
            func(self.progress_update_safe)

        await asyncio.to_thread(thread_entry)

        self.post_message(self.GenerationComplete(task_name))
        self._update_ui(0, 1, f"{task_name} complete!")

    def progress_update_safe(self, current: int, total: int, message: str) -> None:
        """Thread-safe UI update."""
        if threading.current_thread() is threading.main_thread():
            self._update_ui(current, total, message)
        else:
            self.app.call_from_thread(self._update_ui, current, total, message)

    def _update_ui(self, current: int, total: int, message: str) -> None:
        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(total=total, progress=current)
        status = self.query_one("#status", Static)
        status.update(f"{message} ({current}/{total})")


if __name__ == "__main__":
    print(-9 % 10)
