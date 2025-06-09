import toolz as z
from rich import print as rprint

import iplayed_cli.utils as utils


def tranform_completion(completion):
    return {
        "game": {
            "id": completion.get("game_id"),
            "name": completion.get("game_name"),
            "slug": z.get_in(["game", "slug"], completion),
            "cover": z.get_in(["game", "cover"], completion),
            "platforms": z.get_in(["game", "platforms"], completion),
            "genres": z.get_in(["game", "genres"], completion),
            "artworks": z.get_in(["game", "artworks"], completion),
            "releases": z.get_in(["game", "releases"], completion),
            "game_modes": z.get_in(["game", "game_modes"], completion),
            "alternative_names": z.get_in(["game", "alternative_names"], completion),
            "parent_game": z.get_in(["game", "parent_game"], completion),
            "rating": z.get_in(["game", "rating"], completion),
            "rating_count": z.get_in(["game", "rating_count"], completion),
            "summary": z.get_in(["game", "summary"], completion),
            "themes": z.get_in(["game", "themes"], completion),
            "dlcs": z.get_in(["game", "dlcs"], completion),
            "keywords": z.get_in(["game", "keywords"], completion),
            "created_at": z.get_in(["game", "created_at", "$date"], completion),
            "updated_at": z.get_in(["game", "updated_at", "$date"], completion),
            "url": z.get_in(["game", "url"], completion),
            "total_rating": z.get_in(["game", "total_rating"], completion),
            "total_rating_count": z.get_in(["game", "total_rating_count"], completion),
            "first_release_date": z.get_in(["game", "first_release_date", "$date"], completion),
            "category": z.get_in(["game", "category"], completion),
            "status": z.get_in(["game", "status"], completion),
            "version_parent": z.get_in(["game", "version_parent"], completion),
        },
        "completion": {
            "completed_at": z.get_in(["completed_at", "$date"], completion),
            "hours_played": completion.get("hours_played"),
            "played_platforms": completion.get("played_platforms", []),
            "is_favorite": completion.get("is_favorite", False),
            "rating": 10 if completion.get("is_favorite", False) else None,
        },
    }


def main():
    data = utils.read_json("./iplayed_cli/iplayed.users.json")[0]
    transformed = list(z.map(tranform_completion, data.get("completions", [])))
    utils.write_json("./iplayed_cli/completions.json", transformed)


if __name__ == "__main__":
    main()
