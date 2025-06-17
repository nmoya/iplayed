from functools import total_ordering
from typing import Any

from data_entry_view import DataEntryView
from data_schema import BaseIGDBGame, DataEntry, PersonalCompletion
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


@total_ordering
class ResultItem:
    def __init__(self, name: str, data: Any):
        self.name = name
        self.data = data

    def __lt__(self, other: "ResultItem") -> bool:
        if not isinstance(other, ResultItem):
            return NotImplemented
        return self.name < other.name

    @staticmethod
    def from_data_entry(entry: DataEntry) -> "ResultItem":
        return ResultItem(name=entry.game.name, data=entry)

    @staticmethod
    def from_base_igdb_game(game: BaseIGDBGame) -> "ResultItem":
        return ResultItem(name=game.name, data=game)


class ResultsView(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, local: list[ResultItem] = None, remote: list[ResultItem] = None):
        super().__init__()
        self.local_results = local or []
        self.remote_results = remote or []

    def compose(self):
        yield Header()
        yield Horizontal(
            VerticalScroll(
                Static("Local Results", id="local_results_header"),
                *[Button(label=result.name, id=f"btn_local_{i}") for i, result in enumerate(self.local_results)],
                id="results_list_local",
            ),
            VerticalScroll(
                Static("Remote Results", id="remote_results_header"),
                *[Button(label=result.name, id=f"btn_remote_{i}") for i, result in enumerate(self.remote_results)],
                id="results_list_remote",
            ),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id is None:
            return
        # btn_id format: btn_local_{i} or btn_remote_{i}
        parts = btn_id.split("_")
        if len(parts) == 3:
            source, idx = parts[1], int(parts[2])
            if source == "local":
                data = self.local_results[idx].data
            elif source == "remote":
                igdb_game = self.remote_results[idx].data
                data = DataEntry(
                    game=igdb_game,
                    completion=PersonalCompletion(
                        completed_at=None,
                        hours_played=None,
                        played_platforms=[],
                        is_favorite=False,
                        rating=None,
                    ),
                )
            else:
                return
            self.app.push_screen(DataEntryView(data=data))
