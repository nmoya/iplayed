import asyncio
import json
import time
from functools import cmp_to_key, partial
from urllib.parse import urlencode

import config
import httpx
from data_schema import BaseIGDBGame, BaseIGDBSearchResults


def levenshtein_distance(str1, str2):
    m, n = len(str1), len(str2)

    # Create a table to store results of subproblems
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill dp[][] in a bottom-up manner
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j  # If first string is empty, insert all characters of second string
            elif j == 0:
                dp[i][j] = i  # If second string is empty, insert all characters of first string
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j], dp[i - 1][j - 1])  # Insert  # Remove  # Replace

    return dp[m][n]


def compute_rank(query: str, game: BaseIGDBGame) -> int:
    if query.lower() == game.name.lower():
        return 0

    rank = 100 - levenshtein_distance(query.lower(), game.name.lower())

    if game.summary is not None:
        rank -= 1
    if game.rating is not None:
        rank -= 1
    if game.rating_count is not None:
        rank -= 1

    if len(game.dlcs) > 0:
        rank -= 1
    return rank


def compare(query: str, game1: BaseIGDBGame, game2: BaseIGDBGame) -> int:
    rank1 = compute_rank(query, game1)
    rank2 = compute_rank(query, game2)
    if rank1 < rank2:
        return -1
    elif rank1 > rank2:
        return 1

    if game1.rating_count is not None and game2.rating_count is None:
        return -1
    elif game1.rating_count is None and game2.rating_count is not None:
        return 1
    if game1.rating_count is not None and game2.rating_count is not None:
        if game1.rating_count < game2.rating_count:
            return -1
        elif game1.rating_count > game2.rating_count:
            return 1

    return 0


class IGDBClient:
    def __init__(self, client_id, client_secret):
        self.base_url = "https://api.igdb.com/v4"
        self.auth_url = "https://id.twitch.tv/oauth2/token"
        self.client_id = client_id
        self.client_secret = client_secret
        self.accept = "application/json"
        self.auth = None
        self.base_payload = """fields id, game_type, game_status, created_at, first_release_date, name, slug, summary, total_rating, total_rating_count, updated_at, url,
    cover.*, platforms.*, platforms.platform_logo.*, artworks.*, release_dates.*, screenshots.*,
    keywords.*,
    game_modes.*,
    genres.*,
    parent_game.id, parent_game.name,
    version_parent.id, version_parent.name,
    themes.*,
    dlcs.name, dlcs.id;
    """

    def payload_for_search(self, query: str, limit: int, offset: int) -> str:
        return self.base_payload + f'where parent_game = null; search "{query}"; limit {limit}; offset {offset};'

    def payload_for_id(self, game_id: int) -> str:
        return self.base_payload + f"where id = {game_id};"

    def build_url(self, base: str, uri: str, query_params: dict) -> str:
        query_string = urlencode({**query_params})
        if query_string:
            return f"{base}{uri}?{query_string}"
        else:
            return f"{base}{uri}"

    def refresh_access_token(self) -> str:
        auth_url = self.build_url(
            self.auth_url,
            "",
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
        )
        before = time.time()
        with httpx.Client() as client:
            response = client.post(auth_url)
            response.raise_for_status()
            auth = response.json()
            auth["expires_at"] = before + auth["expires_in"]
            self.auth = auth
            return auth

    def auth_valid(self) -> bool:
        return self.auth is not None and time.time() < self.auth["expires_at"]

    def auth_token(self) -> str:
        if not self.auth_valid():
            self.auth = self.refresh_access_token()
        return self.auth["access_token"]

    async def games_count(self) -> int:
        url = self.build_url(self.base_url, "/games/count", {})
        headers = {
            "Client-ID": self.client_id,
            "Accept": self.accept,
            "Authorization": f"Bearer {self.auth_token()}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["count"]

    async def game_search(self, query: str, offset: int = 0, limit: int = 20) -> BaseIGDBSearchResults:
        url = self.build_url(self.base_url, "/games", {})
        headers = {
            "Client-ID": self.client_id,
            "Accept": self.accept,
            "Authorization": f"Bearer {self.auth_token()}",
        }
        payload = self.payload_for_search(query, limit, offset)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=payload)
            data = response.json()
        games = [BaseIGDBGame.model_validate(game) for game in data]
        games = sorted(games, key=cmp_to_key(partial(compare, query)))
        return BaseIGDBSearchResults(limit=limit, offset=offset, results=games)

    def game_by_id(self, game_id: int) -> BaseIGDBGame | None:
        url = self.build_url(self.base_url, "/games", {})
        headers = {
            "Client-ID": self.client_id,
            "Accept": self.accept,
            "Authorization": f"Bearer {self.auth_token()}",
        }
        payload = self.payload_for_id(game_id)
        with httpx.Client() as client:
            response = client.post(url, headers=headers, data=payload)
            data = response.json()
        if len(data) == 0:
            return None
        else:
            return BaseIGDBGame.model_validate(data[0])


async def search_igdb_game(name: str):
    IGDB_CLIENT_ID = config.IGDB_CLIENT_ID
    IGDB_CLIENT_SECRET = config.IGDB_CLIENT_SECRET
    igdb = IGDBClient(IGDB_CLIENT_ID, IGDB_CLIENT_SECRET)
    paginated = await igdb.game_search(name)
    return paginated.results


def get_igdb_game_by_id(game_id: int) -> BaseIGDBGame | None:
    IGDB_CLIENT_ID = config.IGDB_CLIENT_ID
    IGDB_CLIENT_SECRET = config.IGDB_CLIENT_SECRET
    igdb = IGDBClient(IGDB_CLIENT_ID, IGDB_CLIENT_SECRET)
    return igdb.game_by_id(game_id)


if __name__ == "__main__":
    asyncio.run(search_igdb_game("Tomb raider"))
    # print(get_igdb_game_by_id(10734))
