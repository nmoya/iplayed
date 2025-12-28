import datetime as dt
import json
from datetime import datetime

import toolz as z


def humanize_hours(hours: float | None) -> str:
    if hours is None:
        return "N/A"

    delta = dt.timedelta(hours=int(hours))
    total_seconds = int(delta.total_seconds())
    hours_part = total_seconds // 3600
    minutes_part = (total_seconds % 3600) // 60

    parts = []
    if hours_part > 0:
        parts.append(f"{hours_part} hour{'s' if hours_part != 1 else ''}")
    if minutes_part > 0:
        parts.append(f"{minutes_part} minute{'s' if minutes_part != 1 else ''}")

    return " and ".join(parts) if parts else "N/A"


def read_json(file_path: str):
    """Read a JSON file and return its content."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(file_path: str, data):
    """Write data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def read_and_validate_json(file_path, model):
    data = read_json(file_path)
    return list(z.map(lambda item: model.model_validate(item), data))


def write_markdown(file_path: str, content: str):
    """Write content to a Markdown file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def to_naive_datetime(dt_obj: dt.datetime | None, default=None) -> dt.datetime:
    default = default or datetime.min.replace(tzinfo=None)
    if dt_obj is None:
        return default
    if hasattr(dt_obj, "tzinfo") and dt_obj.tzinfo is not None:
        return dt_obj.replace(tzinfo=None)
    return dt_obj
