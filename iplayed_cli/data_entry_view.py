import datetime

from completions_file_db import add_or_update_completion, delete_completion
from data_schema import DataEntry, PersonalCompletion
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static
from widgets.date_picker import DatePicker
from widgets.hours_played_input import HoursPlayedInput
from widgets.platform_picker import PlatformPicker
from widgets.star_rating_bar import StarRating


class DataEntryView(Screen):
    CSS = """
    .date-input {
        width: 15;
    }

    .year-input {
        width: 30;
    }

    Horizontal {
        align-horizontal: left;
    }

    Vertical {
        padding-bottom: 1;
    }

    .button-row {
        margin-top: 1;
    }

    """
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, data: DataEntry):
        super().__init__()
        self.data = data

    def compose(self):
        yield Header(name=f"🎮 {self.data.game.name}")
        yield VerticalScroll(
            PlatformPicker(
                title="Select the platform(s) you played on",
                platforms=self.data.game.platforms,
                played_platforms=self.data.completion.played_platforms,
                id="platforms",
            ),
            DatePicker(title=" 📅 Completion Date", default_date=self.data.completion.completed_at),
            StarRating(title="How would you rate this game?", rating=self.data.completion.rating, id="rating"),
            HoursPlayedInput(),
            Horizontal(Button("💾 Save", id="save"), Button("🗑️ Delete", id="delete"), classes="button-row"),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(PlatformPicker).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            played_platforms = self.query_one(PlatformPicker).selected
            date = self.query_one(DatePicker).value
            hours_played = self.query_one(HoursPlayedInput).value
            rating = self.query_one(StarRating).value
            data_entry = DataEntry(
                game=self.data.game,
                completion=PersonalCompletion(
                    completed_at=date,
                    hours_played=hours_played,
                    played_platforms=played_platforms,
                    is_favorite=False,
                    rating=rating,
                ),
            )
            add_or_update_completion(data_entry)
            self.app.pop_screen()
        elif event.button.id == "delete":
            delete_completion(self.data.game.id)
            self.app.pop_screen()
