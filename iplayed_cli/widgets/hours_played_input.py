from textual.validation import Number
from textual.widget import Widget
from textual.widgets import Input, Static


class HoursPlayedInput(Widget):
    def __init__(self, id="hours_played", default: float | None = 0, title="🎮 Hours Played"):
        super().__init__(id=id)
        self.default = default
        self.title = title
        self.styles.height = "auto"
        self.styles.max_height = 5

    def compose(self):
        yield Static(self.title)
        yield Input(
            value=str(self.default) if self.default is not None else "",
            id=self.id,
            type="number",
            validators=[
                Number(minimum=0, maximum=9999, failure_description="Hours played must be between 0 and 9999"),
            ],
        )

    @property
    def value(self) -> float:
        try:
            return float(self.query_one(Input).value)
        except ValueError:
            return 0.0
