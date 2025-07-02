from completions_file_db import read_completions_file
from data_schema import DataEntry
from igdb import search_igdb_game
from rich.console import Console
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input
from widgets.game_data_table import CompletionsTable, RemoteResultsTable

console = Console()


class CompletionsView(Screen):
    CSS = """
    .hidden {
        display: none;
    }
    Input {
        dock: top;
        height: 3;
    }
    Vertical {
       border: solid red;
    }

    Input {
        border: solid blue;
    }
    Horizontal {
        height: 1fr;
    }
    #completions, #remote {
        width: 1fr;
        border: solid green;
    }

    """
    BINDINGS = [
        ("ctrl+f", "filter_by_text", "Filter by Game Name"),
        ("f", "filter_by_text", "Filter by Game Name"),
        ("escape", "quit", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.completions = read_completions_file()
        self.last_search_results = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Input(placeholder="Filter by game name...", id="filter_input", classes="hidden"),
            Horizontal(CompletionsTable(id="completions"), RemoteResultsTable(id="remote", classes="hidden")),
        )
        yield Footer()

    def on_mount(self) -> None:
        completions = self.completions_table()
        completions.load(self.completions)
        completions.action_sort_by_name()
        self.call_after_refresh(completions.focus)

    def completions_table(self) -> CompletionsTable:
        return self.query_one("#completions", CompletionsTable)

    def remote_table(self) -> RemoteResultsTable:
        return self.query_one("#remote", RemoteResultsTable)

    def local_search(self, query: str) -> None:
        query = query.strip().lower()
        if query:
            self.completions = [c for c in read_completions_file() if query in c.game.name.lower()]
        else:
            self.completions = read_completions_file()
        table = self.completions_table()
        table.load(self.completions)

    def action_filter_by_text(self) -> None:
        input_widget = self.query_one("#filter_input", Input)
        input_widget.remove_class("hidden")
        input_widget.focus()

    async def remote_search(self, query: str) -> None:
        if len(query) == 0:
            return
        remote_results = await search_igdb_game(query)
        remote = [DataEntry.from_base_igdb_game(game) for game in remote_results]
        self.last_search_results = remote
        table = self.remote_table()
        table.remove_class("hidden")
        table.load(remote)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if len(query) == 0:
            self.remote_table().add_class("hidden")
            self.last_search_results = []
        self.local_search(query)
        await self.remote_search(query)
        self.completions_table().focus()

    def action_quit(self) -> None:
        input_widget = self.query_one("#filter_input", Input)
        if not input_widget.has_class("hidden"):
            input_widget.add_class("hidden")
            self.completions_table().focus()
            return
        else:
            self.app.pop_screen()
