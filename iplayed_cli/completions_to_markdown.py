import datetime as dt
import math
import os

from data_schema import DataEntry
from utils import humanize_hours


def render_list_value(key: str, value: list):
    if len(value) > 0:
        if isinstance(value[0], str):
            return f"{key} = {value}"
        return f'{key} = ["{", ".join(value)}"]'
    else:
        return f"{key} = []"


def render_boolean_value(key: str, value: bool):
    if value:
        return f"{key} = true"
    else:
        return f"{key} = false"


def render_value(key: str, value):
    if isinstance(value, list):
        return render_list_value(key, value)
    elif isinstance(value, bool):
        return render_boolean_value(key, value)
    else:
        return f'{key} = "{value}"'


def dict_to_frontmatter(data: dict):
    frontmatter = ["+++"]
    for k, v in data.items():
        if isinstance(v, dict):
            frontmatter.append(f"[{k}]")
            for sub_k, sub_v in v.items():
                frontmatter.append(render_value(sub_k, sub_v))
        else:
            frontmatter.append(render_value(k, v))
    frontmatter.append("+++")
    return "\n".join(frontmatter)


def completion_to_frontmatter(data: DataEntry):
    # +++
    # title = "Blue Prince"
    # date="2024-01-01"
    # updated = 2024-02-01T13:00:00Z
    # [taxonomies]
    # platforms = ["PC"]
    # rating = ["7.5"]
    # genres = ["Puzzle", "Roguelike"]
    # [extra]
    # subtitle = "20 hours - PC"
    # completed_at = 2024-01-01T15:00:00Z
    # +++
    if data.completion.hours_played:
        hours = math.floor(data.completion.hours_played)
        minutes = math.floor((data.completion.hours_played - hours) * 60)
        if minutes > 0:
            hours_played_str = f"{hours} hours and {minutes} minutes"
        else:
            hours_played_str = f"{hours} hours"
    else:
        hours_played_str = ""
    if hours_played_str:
        subtitle = f"{hours_played_str} - {', '.join(data.completion.played_platforms_names)}"
    else:
        subtitle = f"{', '.join(data.completion.played_platforms_names)}"
    frontmatter = {
        "title": data.game.name,
        "description": subtitle,
        "date": data.completion.completed_at.strftime("%Y-%m-%d"),
        "updated": data.completion.completed_at.strftime("%Y-%m-%d"),
        "in_search_index": True,
        "taxonomies": {
            "platforms": [s.lower() for s in data.completion.played_platforms_names],
            "rating": [str(data.completion.rating)] if data.completion.rating else [],
            "genres": [g.name.lower() for g in data.game.genres],
        },
        "extra": {
            "subtitle": subtitle,
            "completed_at": data.completion.completed_at.strftime("%Y-%m-%d"),
            "url_cover_small": data.game.cover.sized_url("t_cover_small") if data.game.cover else None,
            "url_cover_big": data.game.cover.sized_url("t_cover_big") if data.game.cover else None,
        },
    }
    return dict_to_frontmatter(frontmatter)


def completion_to_markdown_body(data: DataEntry):
    #     {{ image(src="https://images.igdb.com/igdb/image/upload/t_cover_big/co4t5o.jpg") }}
    # |              |            |
    # | ------------ | ---------- |
    # | Rating       | 7.5        |
    # | Time played  | 19 hours   |
    # | Platforms    | PC, XBOX   |
    # | Completed at | 2024/01/01 |
    markdown = []
    img = data.game.cover.sized_url() if data.game.cover else None
    if img:
        markdown.append(f'{{{{ image(src="{img}") }}}}\n')

    markdown.append("|              |            |")
    markdown.append("| ------------ | ---------- |")
    if data.completion.rating:
        markdown.append(f"| Rating       | {data.completion.rating} |")
    if data.completion.hours_played:
        hours_played_str = humanize_hours(data.completion.hours_played)
        markdown.append(f"| Time played  | {hours_played_str} |")
    if len(data.completion.played_platforms) > 0:
        markdown.append(f"| Played platforms    | {', '.join(data.completion.played_platforms_names)} |")
    if data.completion.completed_at:
        markdown.append(f"| Completed at | {data.completion.completed_at.strftime('%Y/%m/%d')} |")

    markdown.append("\n\n")

    if len(data.game.dlcs) > 0:
        markdown.append("### Additional Content\n\n")
        for dlc in data.game.dlcs:
            if dlc.id in [d.id for d in data.completion.played_dlcs]:
                markdown.append(f"✅ {dlc.name}\n")
            else:
                markdown.append(f"❌ {dlc.name}\n")

    return "\n".join(markdown)


def completion_to_markdown(completion):
    frontmatter = completion_to_frontmatter(completion)
    body = completion_to_markdown_body(completion)
    return f"{frontmatter}\n{body}"


def markdown_filename(target_dir: str, slug: str):
    return os.path.join(target_dir, f"{slug}.md")
