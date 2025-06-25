import shutil

import utils
from completions_file_db import completions_filepath, read_completions_file
from completions_to_markdown import completion_to_markdown, markdown_filename
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ProgressBar, Static
from widgets.text_input import TextInput


class DeployConfirmation(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]
    CSS = """
    TextInput{
        margin-top: 1;
        margin-bottom: 1;
    }

    Button {
        margin-right: 1;
    }
    """

    def compose(self):
        yield Header()
        yield VerticalScroll(
            TextInput(title="Content directory", default="./iplayed_ssg/content/games", id="content_dir"),
            TextInput(title="Static site generator directory", default="./iplayed_ssg", id="ssg_dir"),
            Static(
                "This will build the static site generator with the current local data. "
                "It will read the completions file and generate markdown files for each game. "
                "It will also copy the completions file to the static site generator directory."
            ),
            Horizontal(Button("Confirm", id="confirm"), Button("Cancel", id="cancel")),
            ProgressBar(show_percentage=True, show_bar=False),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            content_dir = self.query_one("#content_dir").value.strip()
            ssg_dir = self.query_one("#ssg_dir").value.strip()
            completions = read_completions_file()
            progress_bar = self.query_one(ProgressBar)
            progress_bar.show_bar = True
            progress_bar.total = len(completions)
            for data in completions:
                markdown = completion_to_markdown(data)
                filename = markdown_filename(content_dir, data.game.slug)
                utils.write_markdown(filename, markdown)
                progress_bar.advance(1)
            shutil.copyfile(completions_filepath, f"{ssg_dir}/static/completions.json")
            self.app.pop_screen()
        elif event.button.id == "cancel":
            self.app.pop_screen()
