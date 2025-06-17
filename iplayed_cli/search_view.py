from igdb import search_igdb_game
from local_data import search_local_games
from results_view import ResultItem, ResultsView
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static


class SearchView(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self):
        yield Header()
        yield Vertical(Static("🔍 Search for a game"), Input(placeholder="Enter game name", id="game_input"))
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if not name:
            return

        remote_results = await search_igdb_game(name)
        local_results = search_local_games(name)
        local = [ResultItem.from_data_entry(entry) for entry in local_results]
        remote = [ResultItem.from_base_igdb_game(game) for game in remote_results]
        self.app.push_screen(ResultsView(local=sorted(local), remote=sorted(remote)))
