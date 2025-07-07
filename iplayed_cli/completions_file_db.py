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
    for data in completions:
        played = data["completion"]["played_platforms"]
        platforms = data["game"]["platforms"]
        platform_names = [platform["name"] for platform in platforms]

        mapped = []
        for played_platform in played:
            print("\n\n")
            if played_platform in platform_names:
                platform_ref = platforms[platform_names.index(played_platform)]
                mapped.append({"id": platform_ref["id"], "name": platform_ref["name"]})
            else:
                print(f"Warning: Platform '{played_platform}' not found in game platforms for {data['game']['name']}")
                print("Pick the appropriate:")
                for i, platform in enumerate(platforms):
                    print(f"{i + 1}. {platform['name']}")
                print(f"{len(platforms)+1}. Skip")
                choice = int(input("Enter your choice: ")) - 1
                if choice == len(platforms):
                    continue
                elif 0 <= choice < len(platforms):
                    platform_ref = platforms[choice]
                    mapped.append({"id": platform_ref["id"], "name": platform_ref["name"]})
                else:
                    print("Invalid choice, skipping this platform.")
        data["completion"]["played_platforms"] = mapped

    write_json(completions_filepath, completions)


if __name__ == "__main__":
    migrate()
