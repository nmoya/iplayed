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
        self.styles.max_height = max(3, len(options) + 2)
        self.styles.max_width = 80

    def is_selected(self, option) -> bool:
        option_ids = [opt.id for opt in self.selected_options]
        return option.id in option_ids

    def compose(self):
        list_height = max(3, len(self.options) + 2)
        selection_list = SelectionList[str](
            *[(option.name, option.name, self.is_selected(option)) for option in self.options],
            id=self.id,
        )
        selection_list.styles.height = list_height
        selection_list.styles.max_height = list_height
        selection_list.styles.width = 70
        selection_list.styles.max_width = 80
        selection_list.styles.min_width = 40
        yield Vertical(
            Static(self.title),
            selection_list,
        )

    def on_mount(self) -> None:
        self.query_one(SelectionList).focus()

    @property
    def selected(self):
        return self.query_one(SelectionList).selected
