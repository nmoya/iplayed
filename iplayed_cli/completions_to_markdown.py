import math
import os

from data_schema import DataEntry
from utils import read_and_validate_json


def render_list_value(key: str, value: list, prefix: str = ""):
    if len(value) == 0:
        return f"{key} = []"
    if isinstance(value[0], dict):
        lines = []
        table_name = f"{prefix}{key}" if prefix else key
        for item in value:
            lines.append(f"[[{table_name}]]")
            for item_k, item_v in item.items():
                lines.append(render_value(item_k, item_v))
        return "\n".join(lines)
    if isinstance(value[0], str):
        return f"{key} = {value}"
    joined = '", "'.join(str(v) for v in value)
    return f'{key} = ["{joined}"]'


def render_boolean_value(key: str, value: bool):
    return f"{key} = {'true' if value else 'false'}"


def render_value(key: str, value, prefix: str = ""):
    if isinstance(value, list):
        return render_list_value(key, value, prefix=prefix)
    if isinstance(value, bool):
        return render_boolean_value(key, value)
    return f'{key} = "{value}"'


def dict_to_frontmatter(data: dict, prefix: str = ""):
    lines = []
    for k, v in data.items():
        if isinstance(v, dict):
            table_header = f"{prefix}{k}"
            lines.append(f"[{table_header}]")
            lines.extend(dict_to_frontmatter(v, prefix=f"{table_header}."))
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            table_header = f"{prefix}{k}" if prefix else k
            for item in v:
                lines.append(f"[[{table_header}]]")
                for item_k, item_v in item.items():
                    lines.append(render_value(item_k, item_v))
        else:
            lines.append(render_value(k, v, prefix=prefix))
    return lines


def completion_to_frontmatter(data: DataEntry):
    if data.completion.hours_played:
        hours = math.floor(data.completion.hours_played)
        minutes = math.floor((data.completion.hours_played - hours) * 60)
        hours_played_str = f"{hours} hours and {minutes} minutes" if minutes > 0 else f"{hours} hours"
    else:
        hours_played_str = ""

    if hours_played_str:
        subtitle = f"{hours_played_str} - {', '.join(data.completion.played_platforms_names)}"
        playtime = hours_played_str
    else:
        subtitle = f"{', '.join(data.completion.played_platforms_names)}"
        playtime = ""

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
            "flags": [],
        },
        "extra": {
            "subtitle": subtitle,
            "playtime": playtime,
            "completed_at": data.completion.completed_at.strftime("%Y-%m-%d"),
            "url_cover_small": data.game.cover.sized_url("t_cover_small") if data.game.cover else None,
            "url_cover_big": data.game.cover.sized_url("t_cover_big") if data.game.cover else None,
            "all_achievements_unlocked": data.completion.all_achievements_unlocked,
            "backseat_gaming": data.completion.backseat_gaming,
            "comments": data.completion.comments,
            "blurb": data.completion.blurb,
            "blurb_author": data.completion.blurb_author,
        },
    }

    flags = []
    if data.completion.all_achievements_unlocked:
        flags.append("all achievements unlocked")
    if data.completion.backseat_gaming:
        flags.append("backseat mode")
    frontmatter["taxonomies"]["flags"] = flags

    played_dlc_ids = {d.id for d in data.completion.played_dlcs}
    frontmatter["extra"]["additional_content"] = [
        {"name": dlc.name, "completed": dlc.id in played_dlc_ids} for dlc in data.game.dlcs
    ]

    lines = ["+++"] + dict_to_frontmatter(frontmatter) + ["+++"]
    return "\n".join(lines)


def completion_to_markdown_body(data: DataEntry):
    # Additional content now lives in frontmatter (extra.additional_content)
    return ""


def completion_to_markdown(completion):
    frontmatter = completion_to_frontmatter(completion)
    body = completion_to_markdown_body(completion)
    return f"{frontmatter}\n{body}"


def markdown_filename(target_dir: str, slug: str):
    return os.path.join(target_dir, f"{slug}.md")


def generate_markdown_files(completions_path: str, target_dir: str):
    completions = read_and_validate_json(completions_path, DataEntry)
    for completion in completions:
        markdown = completion_to_markdown(completion)
        filename = markdown_filename(target_dir, completion.game.slug)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate markdown files from completions JSON.")
    parser.add_argument(
        "--completions", type=str, default="./iplayed_cli/data/completions.json", help="Path to completions JSON file"
    )
    parser.add_argument(
        "--target-dir", type=str, default="./iplayed_ssg/content/games", help="Directory to output markdown files"
    )
    args = parser.parse_args()

    generate_markdown_files(args.completions, args.target_dir)
