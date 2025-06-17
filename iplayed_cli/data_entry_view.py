from data_schema import DataEntry
from star_rating_bar import StarRating
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, RadioButton, RadioSet, SelectionList, Static


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

    """
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, data: DataEntry):
        super().__init__()
        self.data = data

    def compose(self):
        played_platforms = self.data.completion.played_platforms
        yield Header(name=f"🎮 {self.data.game.name}")
        yield VerticalScroll(
            SelectionList[str](
                *[
                    (platform.name, platform.id, platform.name in played_platforms)
                    for platform in self.data.game.platforms
                ],
            ),
            Vertical(
                Static(" 📅 Completion Date"),
                Horizontal(
                    Input(placeholder="Day", id="day", classes="date-input"),
                    Input(placeholder="Month", id="month", classes="date-input"),
                    Input(placeholder="Year", id="year", classes="year-input"),
                ),
            ),
            Vertical(
                Static("🎮 Hours Played"),
                Input(placeholder="e.g. 12.5", id="hours_played"),
            ),
            Vertical(Static("How would you rate this game?"), StarRating(rating=0, id="rating")),
            Horizontal(
                Button("💾 Save", id="save"),
                Button("🗑️ Delete", id="delete"),
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Select the platform(s) you played on"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            pass
        elif event.button.id == "delete":
            pass
