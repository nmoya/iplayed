from completions_file_db import add_or_update_completion, delete_completion, deploy_markdown_files
from data_schema import DataEntry, PersonalCompletion
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header
from widgets.date_picker import DatePicker
from widgets.hours_played_input import HoursPlayedInput
from widgets.platform_picker import CheckboxInput
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

    Button {
        margin-right: 1;
    }

    """
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, data: DataEntry):
        super().__init__()
        self.data = data

    def build_form_content(self):
        content = [
            CheckboxInput(
                title="Select the platform(s) you played on",
                options=self.data.game.platforms,
                selected_options=self.data.completion.played_platforms,
                id="platforms",
            )
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
        content.append(HoursPlayedInput(default=self.data.completion.hours_played, id="hours_played"))
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
                    is_favorite=False,
                    rating=rating,
                ),
            )
            add_or_update_completion(data_entry)
            deploy_markdown_files()
            self.dismiss(data_entry)
        elif event.button.id == "delete":
            delete_completion(self.data.game.id)
            deploy_markdown_files()
            self.dismiss(self.data.game.id)
