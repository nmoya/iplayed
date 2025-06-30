import datetime as dt
from enum import Enum
from re import S

import humanize
from completions_file_db import delete_completion, read_completions_file
from data_entry_view import DataEntryView
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input
from utils import humanize_hours


class SortType(Enum):
    NAME = "name"
    RATING = "rating"
    COMPLETION_DATE = "completion_date"
    HOURS_PLAYED = "hours_played"


class CompletionsView(Screen):
    CSS = """
    .hidden {
        display: none;
    }
    Input {
        dock: top;
        height: 3;
    }
    #completions_table {
        dock: left;
    }
    #remote_results {
        dock: right;
    }

    """
    BINDINGS = [
        ("ctrl+e", "edit_completion", "Edit"),
        ("q", "sort_by_name", "Sort By Name"),
        ("w", "sort_by_hours_played", "Sort By Hours Played"),
        ("e", "sort_by_completion_date", "Sort By Completion Date"),
        ("r", "sort_by_rating", "Sort By Rating"),
        ("ctrl+x", "delete", "Delete"),
        ("ctrl+f", "filter_by_text", "Filter by Game Name"),
        ("escape", "quit", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.completions = read_completions_file()
        self.last_sort_type = SortType.NAME

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Input(placeholder="Filter by game name...", id="filter_input", classes="hidden"),
            Horizontal(DataTable(id="completions_table"), DataTable(id="remote_results")),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#completions_table", DataTable).focus()
        self.action_sort_by_name()

    def refresh_table(self, cursor_row: int | None = None) -> None:
        table = self.query_one("#completions_table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        columns = ["Game", "Hours Played", "Completed at", "Rating", "Played platforms"]
        table.add_columns(*columns)
        for data in self.completions:
            table.add_row(
                data.game.name,
                humanize_hours(data.completion.hours_played),
                humanize.naturaldate(data.completion.completed_at),
                f"{data.completion.rating:.1f}" if data.completion.rating else "N/A",
                ", ".join(data.completion.played_platforms) if data.completion.played_platforms else "N/A",
                key=data.game.id,
            )
        table.cursor_coordinate = Coordinate(
            row=cursor_row if cursor_row is not None else 0,
            column=0,
        )

    def action_sort_by_name(self) -> None:
        self.last_sort_type = SortType.NAME
        self.completions.sort(key=lambda c: c.game.name.lower())
        self.refresh_table()

    def action_sort_by_hours_played(self) -> None:
        self.last_sort_type = SortType.HOURS_PLAYED
        self.completions.sort(key=lambda c: c.completion.hours_played or 0, reverse=True)
        self.refresh_table()

    def action_sort_by_completion_date(self) -> None:
        self.last_sort_type = SortType.COMPLETION_DATE
        self.completions.sort(
            key=lambda c: (c.completion.completed_at.date() if c.completion.completed_at else dt.date.min)
        )
        self.refresh_table()

    def action_sort_by_rating(self) -> None:
        self.last_sort_type = SortType.RATING
        self.completions.sort(key=lambda c: c.completion.rating or 0, reverse=True)
        self.refresh_table()

    def action_delete(self) -> None:
        table = self.query_one("#completions_table", DataTable)
        if not table.has_focus:
            return
        game_id = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
        delete_completion(game_id)
        self.completions = [c for c in self.completions if c.game.id != game_id]
        self.refresh_table(table.cursor_row)

    def reload_completions(self) -> None:
        self.completions = read_completions_file()
        if self.last_sort_type == SortType.NAME:
            self.action_sort_by_name()
        elif self.last_sort_type == SortType.HOURS_PLAYED:
            self.action_sort_by_hours_played()
        elif self.last_sort_type == SortType.COMPLETION_DATE:
            self.action_sort_by_completion_date()
        elif self.last_sort_type == SortType.RATING:
            self.action_sort_by_rating()

    def action_edit_completion(self) -> None:
        table = self.query_one("#completions_table", DataTable)
        if not table.has_focus:
            return
        game_id = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
        data = next((c for c in self.completions if c.game.id == game_id), None)
        if not data:
            return
        self.app.push_screen(DataEntryView(data=data))
        self.reload_completions()

    def apply_filter(self, query: str) -> None:
        query = query.strip().lower()
        if query:
            self.completions = [c for c in read_completions_file() if query in c.game.name.lower()]
            self.refresh_table()
        else:
            self.reload_completions()

    def action_filter_by_text(self) -> None:
        input_widget = self.query_one("#filter_input", Input)
        input_widget.remove_class("hidden")
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.apply_filter(event.value)
        self.query_one("#completions_table", DataTable).focus()

    def action_quit(self) -> None:
        input_widget = self.query_one("#filter_input", Input)
        if not input_widget.has_class("hidden"):
            input_widget.add_class("hidden")
            self.query_one("#completions_table", DataTable).focus()
            return
        else:
            self.app.exit()
