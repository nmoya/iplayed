import json
import shutil
from typing import Callable

import config
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


def refresh_all_igdb_games(progress_fn: Callable[[int, int, str], None] | None = None) -> None:
    completions = read_completions_file()
    total = len(completions)

    for i, data in enumerate(completions):
        # Emit a quick pre-update so the UI shows activity immediately
        if progress_fn:
            progress_fn(i, total, f"Refreshing {data.game.name}...")

        message = ""
        try:
            refreshed = get_igdb_game_by_id(data.game.id)
            if refreshed:
                data.game = refreshed
                add_or_update_completion(data)
                message = data.game.name
            else:
                message = f"{data.game.name} ({data.game.id}) not found in IGDB."
        except Exception as e:
            message = f"Error refreshing {data.game.name}: {e}"
        finally:
            # Always advance the progress to i+1 so the bar moves forward
            if progress_fn:
                progress_fn(i + 1, total, message)


# if __name__ == "__main__":
# from rich import print as rprint

# results = HowLongToBeat().search("Hades")
# best_element = max(results, key=lambda element: element.similarity)
# rprint(best_element.game_name)
# rprint(best_element.main_story)
