from textual.validation import Number
from textual.widget import Widget
from textual.widgets import Input, Static


class TextInput(Widget):
    def __init__(self, default: str, id="text_input", title=""):
        super().__init__(id=id)
        self.default = default
        self.title = title
        self.styles.height = "auto"
        self.styles.max_height = 5

    def compose(self):
        yield Static(self.title)
        yield Input(
            value=self.default,
            id=self.id,
            type="text",
        )

    @property
    def value(self) -> str:
        return self.query_one(Input).value.strip()
