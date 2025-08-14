import json
import os
import shutil
from typing import Callable

import config
import pixelate
import utils
from completions_to_markdown import completion_to_markdown, markdown_filename
from data_schema import DataEntry
from igdb import get_igdb_game_by_id
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


def refresh_igdb_game(data: DataEntry) -> DataEntry:
    game = get_igdb_game_by_id(data.game.id)
    if game:
        data.game = game
    else:
        print(f"Game {data.game.name} ({data.game.id}) not found in IGDB.")
    return data


def refresh_all_igdb_games(progress_fn: Callable[[int, int, str], None] | None = None) -> None:
    completions = read_completions_file()
    for i, data in enumerate(completions):
        data = refresh_igdb_game(data)
        add_or_update_completion(data)
        if progress_fn:
            progress_fn(i, len(completions), data.game.name)


# if __name__ == "__main__":
# from rich import print as rprint

# results = HowLongToBeat().search("Hades")
# best_element = max(results, key=lambda element: element.similarity)
# rprint(best_element.game_name)
# rprint(best_element.main_story)

# generate_pixelated_covers(None)
