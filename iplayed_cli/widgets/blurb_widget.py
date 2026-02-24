from textual.widget import Widget
from widgets.text_input import TextInput


class BlurbWidget(Widget):
    def __init__(self, blurb: str = "", blurb_author: str = "", id: str = "blurb", **kwargs):
        super().__init__(id=id, **kwargs)
        self._blurb = blurb
        self._blurb_author = blurb_author
        self.styles.height = "auto"

    def compose(self):
        yield TextInput(default=self._blurb, title="Blurb", id=f"{self.id}-blurb")
        yield TextInput(default=self._blurb_author, title="Blurb Author", id=f"{self.id}-author")

    @property
    def value(self) -> dict:
        blurb = self.query_one(f"#{self.id}-blurb", TextInput).value
        blurb_author = self.query_one(f"#{self.id}-author", TextInput).value
        return {"blurb": blurb, "blurb_author": blurb_author}
