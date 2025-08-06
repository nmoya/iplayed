import json
import os
import shutil
from typing import Callable

import config
import pixelate
import utils
from completions_to_markdown import completion_to_markdown, markdown_filename
from data_schema import DataEntry
from utils import read_and_validate_json

completions_filepath = "./iplayed_cli/data/completions.json"


def read_completions_file() -> list[DataEntry]:
    return read_and_validate_json(completions_filepath, DataEntry)


def add_or_update_completion(data: DataEntry) -> None:
    completions = read_completions_file()
    for i, entry in enumerate(completions):
        if entry.game.id == data.game.id:
            completions[i] = data
            break
    else:
        completions.append(data)

    completions_json = [entry.model_dump(mode="json") for entry in completions]
    with open(completions_filepath, "w") as f:
        json.dump(completions_json, f, indent=4, ensure_ascii=True)


def delete_completion(game_id: int) -> list[DataEntry]:
    completions = read_completions_file()
    completions = [entry for entry in completions if entry.game.id != game_id]

    completions_json = [entry.model_dump(mode="json") for entry in completions]
    with open(completions_filepath, "w") as f:
        json.dump(completions_json, f, indent=4, ensure_ascii=True)
    return completions


def deploy_markdown_files(progress_fn: Callable[[int, int, str], None] | None = None) -> None:
    completions = read_completions_file()
    for i, data in enumerate(completions):
        if progress_fn:
            progress_fn(i, len(completions), data.game.name)
        markdown = completion_to_markdown(data)
        filename = markdown_filename(config.SSG_CONTENT_DIRECTORY, data.game.slug)
        utils.write_markdown(filename, markdown)

    shutil.copyfile(completions_filepath, f"{config.SSG_DIRECTORY}/static/completions.json")
    if progress_fn:
        progress_fn(len(completions), len(completions), "")


def generate_pixelated_covers(progress_fn: Callable[[int, int, str], None] | None = None) -> None:
    completions = read_completions_file()
    for i, data in enumerate(completions):
        print(f"Generating cover for {data.game.name} ({i + 1}/{len(completions)})")
        if progress_fn:
            progress_fn(i, len(completions), data.game.name)
        filename = f"{config.SSG_PIXELATED_COVERS_DIRECTORY}/{data.game.slug}.png"
        if not data.game.cover:
            continue
        if os.path.exists(filename):
            continue
        original = pixelate.download_image(data.game.cover.sized_url("t_cover_big"))
        pixelation = pixelate.apply_pixelation(original, 0.5)
        pixelate.save_image(pixelation, filename)

    if progress_fn:
        progress_fn(len(completions), len(completions), "")


def migrate():
    from utils import read_json, write_json

    completions = read_json(completions_filepath)
    # write_json(completions_filepath, completions)


if __name__ == "__main__":
    generate_pixelated_covers(None)
