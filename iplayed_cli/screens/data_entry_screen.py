from enum import Enum
from typing import NamedTuple

from data_schema import DataEntry, PersonalCompletion
from file_persistence import completions_db
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header
from widgets.date_picker import DatePicker
from widgets.hours_played_input import HoursPlayedInput
from widgets.platform_picker import CheckboxInput
from widgets.star_rating_bar import StarRating
from widgets.text_input import TextInput

CheckboxOption = NamedTuple("CheckboxOption", [("id", int), ("name", str), ("store_field", str)])


class DetailsCheckboxOption(Enum):
    ALL_ACHIEVEMENTS_UNLOCKED = CheckboxOption(
        id=1, name="All Achievements Unlocked", store_field="all_achievements_unlocked"
    )
    BACKSEAT_GAMING = CheckboxOption(id=2, name="Backseat Gaming", store_field="backseat_gaming")


class DataEntryScreen(Screen):
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

    Button {
        margin-right: 1;
    }
    """
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, data: DataEntry):
        super().__init__()
        self.data = data

    def build_form_content(self):
        details_selected_options = [
            option.value for option in DetailsCheckboxOption if getattr(self.data.completion, option.value.store_field)
        ]
        content = [
            CheckboxInput(
                title="Select the platform(s) you played on",
                options=self.data.game.platforms,
                selected_options=self.data.completion.played_platforms,
                id="platforms",
            ),
            CheckboxInput(
                title="Check the applicable details:",
                options=[v.value for v in DetailsCheckboxOption],
                selected_options=details_selected_options,
                id="details",
            ),
        ]
        if self.data.game.dlcs:
            content.append(
                CheckboxInput(
                    title="Select the additional content you played",
                    options=self.data.game.dlcs,
                    selected_options=self.data.completion.played_dlcs,
                    id="dlcs",
                )
            )
        content.append(DatePicker(title=" 📅 Completion Date", default_date=self.data.completion.completed_at))
        content.append(
            StarRating(title="How would you rate this game?", rating=self.data.completion.rating, id="rating")
        )
        content.append(TextInput(default=self.data.completion.comments, title="Additional Comments", id="comments"))
        content.append(
            HoursPlayedInput(
                default=self.data.completion.hours_played, game_name=self.data.game.name, id="hours_played"
            ),
        )
        content.append(
            Horizontal(Button("💾 Save", id="save"), Button("🗑️ Delete", id="delete"), classes="button-row"),
        )
        return content

    def compose(self):
        yield Header(name=f"🎮 {self.data.game.name}")
        yield VerticalScroll(*self.build_form_content())
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            played_platforms = self.query_one("#platforms", CheckboxInput).selected
            played_dlcs = self.query_one("#dlcs", CheckboxInput).selected if self.data.game.dlcs else []
            details_selections = self.query_one("#details", CheckboxInput).selected
            all_achievements_unlocked = DetailsCheckboxOption.ALL_ACHIEVEMENTS_UNLOCKED.value.name in details_selections
            backseat_gaming = DetailsCheckboxOption.BACKSEAT_GAMING.value.name in details_selections
            date = self.query_one(DatePicker).value
            hours_played = self.query_one(HoursPlayedInput).value
            rating = self.query_one(StarRating).value
            data_entry = DataEntry(
                game=self.data.game,
                completion=PersonalCompletion(
                    completed_at=date,
                    hours_played=hours_played,
                    played_platforms=self.data.selection_refs(self.data.game.platforms, played_platforms),
                    played_dlcs=self.data.selection_refs(self.data.game.dlcs, played_dlcs),
                    all_achievements_unlocked=all_achievements_unlocked,
                    backseat_gaming=backseat_gaming,
                    comments=self.query_one("#comments", TextInput).value,
                    is_favorite=False,
                    rating=rating,
                ),
            )
            completions_db.add_or_update_completion(data_entry)
            completions_db.deploy_markdown_files()
            self.dismiss(data_entry)
        elif event.button.id == "delete":
            completions_db.delete_completion(self.data.game.id)
            completions_db.deploy_markdown_files()
            self.dismiss(self.data.game.id)
