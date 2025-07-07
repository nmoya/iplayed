from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import SelectionList, Static


class CheckboxInput(Widget):
    def __init__(self, title: str, options, selected_options, id="platforms"):
        super().__init__(id=id)
        self.title = title
        self.options = options
        self.selected_options = selected_options
        self.styles.height = "auto"
        self.styles.max_height = max(6, len(options) + 2)

    def compose(self):
        yield Vertical(
            Static(self.title),
            SelectionList[str](
                *[(option.name, option.name, option.name in self.selected_options) for option in self.options],
                id=self.id,
            ),
        )

    def on_mount(self) -> None:
        self.query_one(SelectionList).focus()

    @property
    def selected(self):
        return self.query_one(SelectionList).selected
