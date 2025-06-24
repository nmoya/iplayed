from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.validation import Number
from textual.widget import Widget
from textual.widgets import Input, Static


class DatePicker(Widget):
    def __init__(self, title: str, default_date: datetime | None, id: str = "date_picker") -> None:
        super().__init__(id=id)
        self.title = title
        self.default_date = default_date
        self.styles.height = "auto"
        self.styles.max_height = 6

    def compose(self) -> ComposeResult:
        if self.default_date is None:
            day, month, year = "", "", ""
        else:
            day = str(self.default_date.day)
            month = str(self.default_date.month)
            year = str(self.default_date.year)
        yield Vertical(
            Static(self.title),
            Horizontal(
                Input(
                    placeholder="Day",
                    id="day",
                    classes="date-input",
                    value=day,
                    type="integer",
                    validators=[
                        Number(minimum=1, maximum=31, failure_description="Day must be between 1 and 31"),
                    ],
                ),
                Input(
                    placeholder="Month",
                    id="month",
                    classes="date-input",
                    value=month,
                    type="integer",
                    validators=[
                        Number(minimum=1, maximum=12, failure_description="Month must be between 1 and 12"),
                    ],
                ),
                Input(
                    placeholder="Year",
                    id="year",
                    classes="year-input",
                    value=year,
                    type="integer",
                    validators=[
                        Number(minimum=1991, maximum=2080, failure_description="Year must be between 1991 and 2080"),
                    ],
                ),
            ),
        )

    @property
    def value(self) -> datetime | None:
        day_input = self.query_one("#day", Input)
        month_input = self.query_one("#month", Input)
        year_input = self.query_one("#year", Input)

        try:
            day = int(day_input.value)
            month = int(month_input.value)
            year = int(year_input.value)
            return datetime(year, month, day)
        except ValueError:
            return None
