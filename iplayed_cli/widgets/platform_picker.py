from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import SelectionList, Static


class PlatformPicker(Widget):
    def __init__(self, title: str, platforms, played_platforms, id="platforms"):
        super().__init__(id=id)
        self.title = title
        self.platforms = platforms
        self.played_platforms = played_platforms
        self.styles.height = "auto"
        self.styles.max_height = max(6, len(platforms) + 2)

    def compose(self):
        yield Vertical(
            Static(self.title),
            SelectionList[str](
                *[
                    (platform.name, platform.name, platform.name in self.played_platforms)
                    for platform in self.platforms
                ],
                id=self.id,
            ),
        )

    def on_mount(self) -> None:
        self.query_one(SelectionList).focus()

    @property
    def selected(self):
        return self.query_one(SelectionList).selected
