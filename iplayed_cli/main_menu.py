from deploy_confirmation import DeployConfirmation
from search_view import SearchView
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header


class MainMenu(Screen):
    BINDINGS = [
        ("1", "search", "Search for a game"),
        ("2", "build", "Build iplayed from local data"),
        ("escape", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button("1. Search for a game", id="search"),
            Button("2. Build iplayed from local data", id="build"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search":
            self.action_search()
        elif event.button.id == "build":
            self.action_build()

    def action_search(self) -> None:
        self.app.push_screen(SearchView())

    def action_build(self) -> None:
        self.app.push_screen(DeployConfirmation())

    def action_quit(self) -> None:
        self.app.exit()
