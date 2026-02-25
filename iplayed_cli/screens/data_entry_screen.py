from enum import Enum
from typing import NamedTuple

from data_schema import DataEntry, PersonalCompletion
from file_persistence import completions_db
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static
from widgets.blurb_widget import BlurbWidget
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
        padding: 0;
        margin: 0;
    }

    VerticalScroll {
        padding: 0 1 2 1;
        content-align: left top;
    }

    Vertical > * {
        margin: 0 0 1 0;
        padding: 0;
    }

    VerticalScroll > * {
        margin: 0 0 1 0;
        padding: 0;
    }

    CheckboxInput,
    DatePicker,
    StarRating,
    HoursPlayedInput,
    SelectionList,
    Static,
    Input {
        margin: 0;
        padding: 0;
        max-width: 80;
    }

    TextInput {
        margin: 0;
        padding: 0;
        max-width: 80;
        margin-top: 1;
    }

    CheckboxInput {
        margin-bottom: 2;
    }

    DatePicker {
        margin-top: 1;
        margin-bottom: 1;
        width: 60;
        max-width: 80;
    }

    StarRating {
        width: 60;
        max-width: 80;
    }

    SelectionList {
        min-width: 40;
        max-width: 80;
    }

    .hint {
        color: #777;
        margin: 0 0 1 1;
        padding: 0;
    }

    StarRating .star-row {
        margin-top: 0;
    }

    .button-row {
        margin-top: 0;
        align-horizontal: center;
    }

    Button {
        margin-right: 1;
        min-width: 14;
    }

    .game-title {
        margin: 0 0 1 0;
        padding: 0;
    }
    """
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("p", "focus_platforms", "Focus platforms"),
        ("d", "focus_details", "Focus details"),
        ("l", "focus_dlcs", "Focus DLCs"),
        ("t", "focus_date", "Focus completion date"),
        ("r", "focus_rating", "Focus rating"),
        ("c", "focus_comments", "Focus comments"),
        ("h", "focus_hours", "Focus hours played"),
        ("ctrl+s", "save_and_close", "Save & close"),
        ("ctrl+q", "close_without_saving", "Close without saving"),
    ]

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
        content.append(
            DatePicker(
                title=" 📅 Completion Date",
                default_date=self.data.completion.completed_at,
                id="completion_date",
            )
        )
        content.append(
            StarRating(title="How would you rate this game?", rating=self.data.completion.rating, id="rating")
        )
        content.append(Static("Left/Right to move, Space to confirm", classes="hint"))
        content.append(TextInput(default=self.data.completion.comments, title="Additional Comments", id="comments"))
        content.append(
            BlurbWidget(blurb=self.data.completion.blurb, blurb_author=self.data.completion.blurb_author, id="blurb")
        )
        content.append(
            HoursPlayedInput(
                default=self.data.completion.hours_played, game_name=self.data.game.name, id="hours_played"
            ),
        )
        content.append(Static("Use the HLTB button if you're unsure.", classes="hint"))
        content.append(
            Horizontal(Button("💾 Save", id="save"), Button("🗑️ Delete", id="delete"), classes="button-row"),
        )
        return content

    def compose(self):
        yield Header(name=f"🎮 {self.data.game.name}")
        yield Static(self.data.game.name, classes="game-title")
        yield VerticalScroll(*self.build_form_content())
        yield Footer()

    def on_mount(self) -> None:
        platform = self.query_one("#platforms", CheckboxInput)
        platform.focus()

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
                    blurb=self.query_one("#blurb", BlurbWidget).value["blurb"],
                    blurb_author=self.query_one("#blurb", BlurbWidget).value["blurb_author"],
                    is_favorite=False,
                    rating=rating,
                ),
            )
            completions_db.add_or_update_completion(data_entry)
            self.dismiss(data_entry)
        elif event.button.id == "delete":
            completions_db.delete_completion(self.data.game.id)
            self.dismiss(self.data.game.id)

    def _shortcuts_blocked(self) -> bool:
        """Return True when shortcuts should be ignored (e.g., while typing comments)."""
        try:
            return self.query_one("#comments", Input).has_focus
        except Exception:
            return False

    def action_focus_platforms(self) -> None:
        if self._shortcuts_blocked():
            return
        self.query_one("#platforms", CheckboxInput).focus()

    def action_focus_details(self) -> None:
        if self._shortcuts_blocked():
            return
        self.query_one("#details", CheckboxInput).focus()

    def action_focus_dlcs(self) -> None:
        if self._shortcuts_blocked() or not self.data.game.dlcs:
            return
        self.query_one("#dlcs", CheckboxInput).focus()

    def action_focus_date(self) -> None:
        if self._shortcuts_blocked():
            return
        self.query_one("#completion_date", DatePicker).focus()

    def action_focus_rating(self) -> None:
        if self._shortcuts_blocked():
            return
        self.query_one("#rating", StarRating).focus()

    def action_focus_comments(self) -> None:
        if self._shortcuts_blocked():
            return
        self.query_one("#comments", Input).focus()

    def action_focus_hours(self) -> None:
        if self._shortcuts_blocked():
            return
        self.query_one("#hours_played", Input).focus()

    def action_save_and_close(self) -> None:
        if self._shortcuts_blocked():
            return
        self.on_button_pressed(Button.Pressed(self.query_one("#save", Button)))

    def action_close_without_saving(self) -> None:
        if self._shortcuts_blocked():
            return
        self.app.pop_screen()
