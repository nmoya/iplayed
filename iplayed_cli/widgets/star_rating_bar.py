from textual.containers import Container, Horizontal, Vertical
from textual.events import Key
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class StarRating(Widget):
    class RatingSelected(Message):
        def __init__(self, sender: Widget, rating: int) -> None:
            self.rating = rating
            super().__init__(sender)

    DEFAULT_CSS = """
    StarRating {
        layout: horizontal;
        padding: 1;
        height: auto;
        border: round yellow;
    }

    .star {
        width: 5;
        min-width: 5;
        content-align: center middle;
        color: #666;
        text-style: bold;
    }

    .star.selected {
        color: gold;
    }

    .star.hovered {
        color: yellow;
    }

    StarRating:focus {
        border: round green;
    }

    .star-row {
        margin-top: 1;
    }

    """

    def __init__(self, title: str, rating: int = 0, max_stars: int = 10, id: str = "star_rating") -> None:
        super().__init__(id=id)
        self.title = title
        self.rating = rating
        self.max_stars = max_stars
        self.cursor_index = rating or 0
        self.can_focus = True
        self.styles.height = "auto"
        self.styles.max_height = 8

    def compose(self):
        # for i in range(1, self.max_stars + 1):
        #     yield Static("★", id=f"star-{i}", classes="star")
        yield Vertical(
            Static(self.title),
            Horizontal(
                *[Static("★", id=f"star-{i}", classes="star") for i in range(1, self.max_stars + 1)], classes="star-row"
            ),
        )

    async def on_mount(self) -> None:
        self.update_stars()

    def update_stars(self):
        for i, star in enumerate(self.query(".star"), start=1):
            star.remove_class("hovered")
            if self.has_focus and i <= self.cursor_index:
                star.add_class("hovered")
            else:
                star.remove_class("hovered")

            if i <= self.rating:
                star.add_class("selected")
            else:
                star.remove_class("selected")

    def on_key(self, event: Key) -> None:
        if event.key == "left":
            self.cursor_index = max(0, self.cursor_index - 1)
            self.update_stars()
        elif event.key == "right":
            self.cursor_index = min(self.max_stars, self.cursor_index + 1)
            self.update_stars()
        elif event.key in ("enter", "space"):
            self.rating = self.cursor_index
            self.update_stars()
            self.post_message(self.RatingSelected(self, self.rating))

    def on_focus(self) -> None:
        self.update_stars()

    def on_blur(self) -> None:
        self.update_stars()
