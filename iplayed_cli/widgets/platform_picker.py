from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import SelectionList, Static


class CheckboxInput(Widget):
    def __init__(self, title: str, options, selected_options, id="platforms"):
        super().__init__(id=id)
        self.title = title
        self.options = options  # need to have attr id and name
        self.selected_options = selected_options  # need to have attr id at mininum
        self.styles.height = "auto"
        self.styles.max_height = max(12, len(options) + 2)

    def is_selected(self, option) -> bool:
        option_ids = [opt.id for opt in self.selected_options]
        return option.id in option_ids

    def compose(self):
        yield Vertical(
            Static(self.title),
            SelectionList[str](
                *[(option.name, option.name, self.is_selected(option)) for option in self.options],
                id=self.id,
            ),
        )

    def on_mount(self) -> None:
        self.query_one(SelectionList).focus()

    @property
    def selected(self):
        return self.query_one(SelectionList).selected
