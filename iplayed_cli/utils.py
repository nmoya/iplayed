import json

import toolz as z


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
