import utils
from data_schema import DataEntry


def search_local_games(name: str) -> list[DataEntry]:
    all_entries: list[DataEntry] = utils.read_and_validate_json("./iplayed_cli/data/completions.json", DataEntry)
    matches = []
    for entry in all_entries:
        if entry.game.name.lower().startswith(name.lower()):
            matches.append(entry)
    return matches
