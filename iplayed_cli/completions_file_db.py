import json
import shutil

import config
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


def deploy_markdown_files() -> None:
    completions = read_completions_file()
    for data in completions:
        markdown = completion_to_markdown(data)
        filename = markdown_filename(config.SSG_CONTENT_DIRECTORY, data.game.slug)
        utils.write_markdown(filename, markdown)
    shutil.copyfile(completions_filepath, f"{config.SSG_DIRECTORY}/static/completions.json")


def migrate():
    from utils import read_json, write_json

    completions = read_json(completions_filepath)
    # write_json(completions_filepath, completions)


if __name__ == "__main__":
    migrate()
