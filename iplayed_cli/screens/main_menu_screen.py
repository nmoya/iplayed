from screens.completions_screen import CompletionsScreen
from screens.config_review_screen import ConfigurationRevisionScreen
from screens.generation_screen import GenerationScreen
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header


class MainMenuScreen(Screen):
    CSS = """
    #main-menu-buttons {
        width: 40;
        height: 100%;
        align-horizontal: center;
        padding: 1;
        content-align: center middle;
    }

    #main-menu-buttons Button {
        width: 100%;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("1", "completions", "Manage Completions"),
        ("2", "configurations", "Review configuration"),
        ("3", "content_management", "Content management"),
        ("escape", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button("[1] Manage Completions", id="completions"),
            Button("[2] Review configuration", id="configurations"),
            Button("[3] Content management", id="content_management"),
            id="main-menu-buttons",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "completions":
            self.action_completions()
        elif event.button.id == "configurations":
            self.action_configurations()
        elif event.button.id == "content_management":
            self.action_content_management()

    def action_completions(self) -> None:
        self.app.push_screen(CompletionsScreen())

    def action_configurations(self) -> None:
        self.app.push_screen(ConfigurationRevisionScreen())

    def action_content_management(self) -> None:
        self.app.push_screen(GenerationScreen())

    def action_quit(self) -> None:
        self.app.exit()
