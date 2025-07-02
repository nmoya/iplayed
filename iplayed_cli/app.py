from main_menu import MainMenu
from textual.app import App


class IPlayedCLI(App):
    CSS = """
        Screen {
            padding: 5;
        }
        Vertical {
           align: center middle;
        }
        Button {
            width: 40;
            height: 5;
            color: $text;
            text-align: left;
        }
    """
    TITLE = "iPlayed CLI"

    def on_mount(self) -> None:
        self.theme = "gruvbox"
        super().push_screen(MainMenu())


if __name__ == "__main__":
    IPlayedCLI().run()
