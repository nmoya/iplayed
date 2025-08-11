from howlongtobeatpy import HowLongToBeat
from textual.containers import Horizontal
from textual.validation import Number
from textual.widget import Widget
from textual.widgets import Button, Input, Static


class HoursPlayedInput(Widget):
    def __init__(
        self,
        id="hours_played",
        default: float | None = 0,
        title="🎮 Hours Played",
        game_name: str | None = None,
        **kwargs,
    ):
        super().__init__(id=id, **kwargs)
        self.default = default
        self.title = title
        self.styles.height = "auto"
        self.styles.max_height = 5
        self.game_name = game_name

    def compose(self):
        yield Static(self.title)
        input_field = Input(
            value=str(self.default) if self.default is not None else "",
            id=self.id,
            type="number",
            validators=[
                Number(minimum=0, maximum=9999, failure_description="Hours played must be between 0 and 9999"),
            ],
        )
        input_field.styles.width = 20
        button = Button("From HLTB", id="default_hours")
        button.styles.height = 3
        row = Horizontal(input_field, button)
        row.styles.width = "100%"
        row.styles.gap = 1
        yield row

    @property
    def value(self) -> float:
        try:
            return float(self.query_one(Input).value)
        except ValueError:
            return 0.0

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "default_hours":
            if not self.game_name:
                return
            client = HowLongToBeat()
            result = client.search(self.game_name)
            if not result:
                return
            best = max(result, key=lambda x: x.similarity)
            if best:
                self.query_one(Input).value = str(best.main_story)
