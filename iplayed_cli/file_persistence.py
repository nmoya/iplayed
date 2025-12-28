import json
import shutil
from typing import Callable

import config
import utils
from completions_to_markdown import completion_to_markdown, markdown_filename
from data_schema import DataEntry
from igdb import get_igdb_game_by_id
from utils import read_and_validate_json


class CompletionsDatabase:
    def __init__(self):
        self.completions_filepath = "./iplayed_cli/data/completions.json"
        self.completions = self.read_completions_file()

    def read_completions_file(self) -> list[DataEntry]:
        return read_and_validate_json(self.completions_filepath, DataEntry)

    def search(self, query: str) -> list[DataEntry]:
        query = query.strip().lower()
        if query:
            return [c for c in self.completions if query in c.game.name.lower()]
        return self.completions

    def add_or_update_completion(self, data: DataEntry) -> DataEntry:
        for i, entry in enumerate(self.completions):
            if entry.game.id == data.game.id:
                self.completions[i] = data
                break
        else:
            self.completions.append(data)
        self.commit()
        return data

    def delete_completion(self, game_id: int) -> list[DataEntry]:
        self.completions = [entry for entry in self.completions if entry.game.id != game_id]
        self.commit()
        return self.completions

    def commit(self) -> None:
        completions_json = [entry.model_dump(mode="json") for entry in self.completions]
        with open(self.completions_filepath, "w") as f:
            json.dump(completions_json, f, indent=4, ensure_ascii=True)

    def deploy_markdown_files(self, progress_fn: Callable[[int, int, str], None] | None = None) -> None:
        for i, data in enumerate(self.completions):
            if progress_fn:
                progress_fn(i, len(self.completions), data.game.name)
            markdown = completion_to_markdown(data)
            filename = markdown_filename(config.SSG_CONTENT_DIRECTORY, data.game.slug)
            utils.write_markdown(filename, markdown)

        shutil.copyfile(self.completions_filepath, f"{config.SSG_DIRECTORY}/static/completions.json")
        if progress_fn:
            progress_fn(len(self.completions), len(self.completions), "")

    def refresh_all_igdb_games(self, progress_fn: Callable[[int, int, str], None] | None = None) -> None:
        total = len(self.completions)

        for i, data in enumerate(self.completions):
            # Emit a quick pre-update so the UI shows activity immediately
            if progress_fn:
                progress_fn(i, total, f"Refreshing {data.game.name}...")

            message = ""
            try:
                refreshed = get_igdb_game_by_id(data.game.id)
                if refreshed:
                    data.game = refreshed
                    self.add_or_update_completion(data)
                    message = data.game.name
                else:
                    message = f"{data.game.name} ({data.game.id}) not found in IGDB."
            except Exception as e:
                message = f"Error refreshing {data.game.name}: {e}"
            finally:
                # Always advance the progress to i+1 so the bar moves forward
                if progress_fn:
                    progress_fn(i + 1, total, message)


completions_db = CompletionsDatabase()
print(completions_db)

if __name__ == "__main__":
    completions_db.commit()
