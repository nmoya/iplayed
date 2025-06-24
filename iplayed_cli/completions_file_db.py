import json

from data_schema import DataEntry
from utils import read_and_validate_json


def read_completions_file() -> list[DataEntry]:
    return read_and_validate_json("./iplayed_cli/data/completions.json", DataEntry)


def add_or_update_completion(data: DataEntry) -> None:
    completions = read_completions_file()
    for i, entry in enumerate(completions):
        if entry.game.id == data.game.id:
            completions[i] = data
            break
    else:
        completions.append(data)

    completions_json = [entry.model_dump(mode="json") for entry in completions]
    with open("./iplayed_cli/data/completions.json", "w") as f:
        json.dump(completions_json, f, indent=4, ensure_ascii=True)


def delete_completion(game_id: int) -> None:
    completions = read_completions_file()
    completions = [entry for entry in completions if entry.game.id != game_id]

    completions_json = [entry.model_dump(mode="json") for entry in completions]
    with open("./iplayed_cli/data/completions.json", "w") as f:
        json.dump(completions_json, f, indent=4, ensure_ascii=True)
