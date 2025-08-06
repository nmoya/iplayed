from completions_file_db import deploy_markdown_files, generate_pixelated_covers
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
                yield Button("Generate All Pixelated Images", id="images")
                yield ProgressBar(id="progress", total=10)
                yield Static("Status", id="status")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        task_id = event.button.id
        if task_id == "markdown":
            await self.run_content_generation()
        elif task_id == "images":
            await self.run_cover_generation()

    def progress_update(self, current: int, total: int, message: str) -> None:
        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(total=total, progress=current)
        status = self.query_one("#status", Static)
        status.update(f"{message} ({current}/{total})")

    async def run_content_generation(self) -> None:
        deploy_markdown_files(self.progress_update)

    async def run_cover_generation(self) -> None:
        generate_pixelated_covers(self.progress_update)
