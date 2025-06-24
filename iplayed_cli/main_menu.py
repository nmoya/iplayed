from completions_file_db import read_completions_file
from results_view import ResultItem, ResultsView
from search_view import SearchView
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header


class MainMenu(Screen):
    BINDINGS = [
        ("1", "search", "Search for a game"),
        ("2", "results", "View results"),
        ("3", "build", "Build iplayed from local data"),
        ("escape", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button("1. Search for a game", id="search"),
            Button("2. Results", id="results"),
            Button("3. Build iplayed from local data", id="build"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "search":
            self.action_search()
        elif event.button.id == "results":
            self.action_results()
        elif event.button.id == "build":
            self.action_build()

    def action_search(self) -> None:
        self.app.push_screen(SearchView())

    def action_results(self) -> None:
        self.app.push_screen(
            ResultsView(local=sorted([ResultItem.from_data_entry(entry) for entry in read_completions_file()]))
        )

    def action_build(self) -> None:
        pass

    def action_quit(self) -> None:
        self.app.exit()
