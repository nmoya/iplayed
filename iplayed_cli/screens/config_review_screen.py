import config
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from widgets.text_input import TextInput


class ConfigurationRevisionScreen(Screen):
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
            TextInput(title="Content directory", default=config.SSG_CONTENT_DIRECTORY, id="content_dir", disabled=True),
            TextInput(
                title="Static site generator directory", default=config.SSG_DIRECTORY, id="ssg_dir", disabled=True
            ),
            Static(
                "This will build the static site generator with the current local data. "
                "It will read the completions file and generate markdown files for each game. "
                "It will also copy the completions file to the static site generator directory. "
                "Modify values in .env file",
            ),
            Horizontal(Button("Confirm", id="confirm")),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.app.pop_screen()
