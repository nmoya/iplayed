import datetime as dt
from enum import Enum

import humanize
from completions_file_db import delete_completion
from data_entry_view import DataEntryView
from data_schema import DataEntry
from textual.coordinate import Coordinate
from textual.widget import Widget
from textual.widgets import DataTable
from utils import humanize_hours


class SortType(Enum):
    NAME = "name"
    RATING = "rating"
    COMPLETION_DATE = "completion_date"
    HOURS_PLAYED = "hours_played"


class GameDataTableBase(Widget):
    can_focus = True
    DEFAULT_CSS = """
    """
    BINDINGS = [
        ("q", "sort_by_name", "Sort By Name"),
        ("ctrl+e", "edit_completion", "Add/Edit"),
        ("z", "edit_completion", "Add/Edit"),
    ]

    def __init__(self, id: str, **kwargs):
        super().__init__(id=id, **kwargs)
        self.data: list[DataEntry] = []
        self.last_sort_type: Enum | None = None
        self.table = DataTable()
        self.table.cursor_type = "row"

    def compose(self):
        yield self.table

    def get_selected_entry(self) -> DataEntry | None:
        if not self.table.row_count:
            return None
        coord = self.table.cursor_coordinate
        if not coord:
            return None
        key = self.table.coordinate_to_cell_key(coord).row_key.value
        return next((d for d in self.data if d.game.id == key), None)

    def load(self, data: list[DataEntry], cursor_row: int = 0) -> None:
        raise NotImplementedError("Subclasses must implement `load()`")

    def action_sort_by_name(self) -> None:
        self.last_sort_type = SortType.NAME
        self.data.sort(key=lambda c: c.game.name.lower())
        self.load(self.data)

    def on_data_entry_view_close(self, data: DataEntry | int | None) -> None:
        if data is None:
            return

        # Game was deleted
        if isinstance(data, int):
            self.data = [c for c in self.data if c.game.id != data]
        # Game was added or edited
        else:
            for idx, entry in enumerate(self.data):
                if entry.game.id == data.game.id:
                    self.data[idx] = data
                break
            else:
                self.data.append(data)

        self.load(self.data)

    def action_edit_completion(self) -> None:
        if not self.table.has_focus:
            return
        game_id = self.table.coordinate_to_cell_key(self.table.cursor_coordinate).row_key.value
        data = next((c for c in self.data if c.game.id == game_id), None)
        if not data:
            return
        self.app.push_screen(DataEntryView(data=data), self.on_data_entry_view_close)

    def focus(self, scroll_visible: bool = True) -> Widget:
        self.table.focus()
        return self


class CompletionsTable(GameDataTableBase):
    BINDINGS = [
        ("w", "sort_by_hours_played", "Sort By Hours Played"),
        ("e", "sort_by_completion_date", "Sort By Completion Date"),
        ("r", "sort_by_rating", "Sort By Rating"),
        ("ctrl+x", "delete", "Delete"),
    ]

    def load(self, data: list[DataEntry], cursor_row: int = 0) -> None:
        self.data = data
        self.table.clear(columns=True)
        self.table.add_columns("Game", "Hours Played", "Completed at", "Rating", "Played platforms")
        for entry in data:
            self.table.add_row(
                entry.game.name,
                humanize_hours(entry.completion.hours_played),
                humanize.naturaldate(entry.completion.completed_at),
                f"{entry.completion.rating:.1f}" if entry.completion.rating else "N/A",
                ", ".join(entry.completion.played_platforms_names) if entry.completion.played_platforms else "N/A",
                key=entry.game.id,
            )
        self.table.cursor_coordinate = Coordinate(row=cursor_row, column=0)

    def action_sort_by_hours_played(self) -> None:
        self.last_sort_type = SortType.HOURS_PLAYED
        self.data.sort(key=lambda c: c.completion.hours_played or 0, reverse=True)
        self.load(self.data)

    def action_sort_by_completion_date(self) -> None:
        self.last_sort_type = SortType.COMPLETION_DATE
        self.data.sort(key=lambda c: (c.completion.completed_at.date() if c.completion.completed_at else dt.date.min))
        self.load(self.data)

    def action_sort_by_rating(self) -> None:
        self.last_sort_type = SortType.RATING
        self.data.sort(key=lambda c: c.completion.rating or 0, reverse=True)
        self.load(self.data)

    def action_delete(self) -> None:
        if not self.table.has_focus:
            return
        game_id = self.table.coordinate_to_cell_key(self.table.cursor_coordinate).row_key.value
        self.data = delete_completion(game_id)
        self.load(self.data, self.table.cursor_row)


class RemoteResultsTable(GameDataTableBase):
    def load(self, data: list[DataEntry], cursor_row: int = 0) -> None:
        self.data = data
        self.table.clear(columns=True)
        self.table.add_columns("Id", "Game", "Platforms")
        for entry in data:
            self.table.add_row(
                str(entry.game.id),
                entry.game.name,
                ", ".join(p.name for p in entry.game.platforms),
                key=entry.game.id,
            )
        self.table.cursor_coordinate = Coordinate(row=cursor_row, column=0)
