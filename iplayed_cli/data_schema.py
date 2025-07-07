from datetime import datetime
from enum import Enum
from typing import List

import humanize
import pydantic
from pydantic import BaseModel, Field, field_serializer


class BaseIGDBAssetSize(Enum):
    cover_small = "cover_small"  # 90 x 128 	Fit
    screenshot_med = "screenshot_med"  # 569 x 320 	Lfill, Center gravity
    cover_big = "cover_big"  # 264 x 374 	Fit
    logo_med = "logo_med"  # 284 x 160 	Fit
    screenshot_big = "screenshot_big"  # 889 x 500 	Lfill, Center gravity
    screenshot_huge = "screenshot_huge"  # 1280 x 720 	Lfill, Center gravity
    thumb = "thumb"  # 90 x 90 	Thumb, Center gravity
    micro = "micro"  # 35 x 35 	Thumb, Center gravity
    p720 = "720p"  # 1280 x 720 	Fit, Center gravity
    p1080 = "1080p"  # 1920 x 1080 	Fit, Center gravity


class BaseIGDBAsset(BaseModel):
    id: int
    alpha_channel: bool | None = None
    animated: bool | None = None
    height: int | None = None
    image_id: str
    url: str
    width: int | None = None

    def sized_url(self, size: str = "t_cover_big") -> str:
        return f"https://images.igdb.com/igdb/image/upload/{size}/{self.image_id}.jpg"

    @field_serializer("url")
    def serialize_url(self, value: str, _info) -> str:
        return f"https://images.igdb.com/igdb/image/upload/t_cover_big/{self.image_id}.jpg"


class BaseIGDBPlatform(BaseModel):
    id: int = Field(alias="_id")
    abbreviation: str | None = None
    name: str
    logo: BaseIGDBAsset | None = Field(alias="platform_logo", default=None)

    class Config:
        populate_by_name = True


class BaseIGDBReleaseData(BaseModel):
    id: int = Field(alias="_id")
    platform_id: int = Field(alias="platform")
    date: int
    human: str

    class Config:
        populate_by_name = True


class BaseIGDBNamedEntity(BaseModel):
    id: int = Field(alias="_id")
    name: str
    slug: str
    url: str
    updated_at: int
    created_at: int

    class Config:
        populate_by_name = True


class BaseIGDBReference(BaseModel):
    id: int = Field(alias="_id")
    name: str

    class Config:
        populate_by_name = True


class BaseIGDBGameCategory(Enum):
    main_game = BaseIGDBReference(_id=0, name="Main game")
    dlc_addon = BaseIGDBReference(_id=1, name="DLC / add-on")
    expansion = BaseIGDBReference(_id=2, name="Expansion")
    bundle = BaseIGDBReference(_id=3, name="Bundle")
    standalone_expansion = BaseIGDBReference(_id=4, name="Standalone expansion")
    mod = BaseIGDBReference(_id=5, name="Mod")
    episode = BaseIGDBReference(_id=6, name="Episode")
    season = BaseIGDBReference(_id=7, name="Season")
    remake = BaseIGDBReference(_id=8, name="Remake")
    remaster = BaseIGDBReference(_id=9, name="Remaster")
    expanded_game = BaseIGDBReference(_id=10, name="Expanded game")
    port = BaseIGDBReference(_id=11, name="Port")
    fork = BaseIGDBReference(_id=12, name="Fork")
    pack = BaseIGDBReference(_id=13, name="Pack")
    update = BaseIGDBReference(_id=14, name="Update")


class BaseIGDBGameStatus(Enum):
    released = BaseIGDBReference(_id=0, name="Released")
    alpha = BaseIGDBReference(_id=2, name="Alpha")
    beta = BaseIGDBReference(_id=3, name="Beta")
    early_access = BaseIGDBReference(_id=4, name="Early access")
    offline = BaseIGDBReference(_id=5, name="Offline")
    cancelled = BaseIGDBReference(_id=6, name="Cancelled")
    rumored = BaseIGDBReference(_id=7, name="Rumored")
    delisted = BaseIGDBReference(_id=8, name="Delisted")


class BaseIGDBGame(BaseModel):
    id: int = Field(alias="_id")
    slug: str
    name: str
    game_type: int
    game_status: int | None = None
    cover: BaseIGDBAsset | None = None
    artworks: List[BaseIGDBAsset] = Field(default_factory=list)
    platforms: List[BaseIGDBPlatform] = Field(default_factory=list)
    releases: List[BaseIGDBReleaseData] = Field(default_factory=list)
    genres: List[BaseIGDBNamedEntity] = Field(default_factory=list)
    game_modes: List[BaseIGDBNamedEntity] = Field(default_factory=list)
    alternative_names: List[BaseIGDBReference] = Field(default_factory=list)
    parent_game: BaseIGDBReference | None = None
    version_parent: BaseIGDBReference | None = None
    rating: float | None = None
    rating_count: int | None = None
    summary: str | None = None
    dlcs: List[BaseIGDBReference] = Field(default_factory=list)
    keywords: List[BaseIGDBReference] = Field(default_factory=list)
    created_at: int | None = None
    updated_at: int | None = None
    url: str
    total_rating: float | None = None
    total_rating_count: int | None = None
    first_release_date: int | None = None

    class Config:
        populate_by_name = True


class BaseIGDBSearchResults(BaseModel):
    limit: int
    offset: int
    results: List[BaseIGDBGame] = Field(default_factory=list)


class PersonalCompletion(BaseModel):
    completed_at: datetime | None = None
    hours_played: float | None = None
    played_platforms: List[BaseIGDBReference] = Field(default_factory=list)
    played_dlcs: List[BaseIGDBReference] = Field(default_factory=list)
    is_favorite: bool = False
    rating: float | None = None

    @property
    def played_platforms_names(self) -> List[str]:
        return [platform.name for platform in self.played_platforms]


class DataEntry(pydantic.BaseModel):
    game: BaseIGDBGame
    completion: PersonalCompletion

    @staticmethod
    def from_base_igdb_game(game: BaseIGDBGame) -> "DataEntry":
        return DataEntry(
            game=game,
            completion=PersonalCompletion(
                completed_at=datetime.now(),
                hours_played=None,
                played_platforms=[],
                played_dlcs=[],
                is_favorite=False,
                rating=0,
            ),
        )

    def selection_refs(self, options, selections: List[str]) -> List[BaseIGDBReference]:
        return [BaseIGDBReference(_id=option.id, name=option.name) for option in options if option.name in selections]


# {
#     "game": {
#         "id": 10734,
#         "name": "Horizon Chase",
#         "slug": "horizon-chase",
#         "cover": {
#             "id": 96531,
#             "alpha_channel": false,
#             "animated": false,
#             "height": 540,
#             "image_id": "co22hf",
#             "url": "//images.igdb.com/igdb/image/upload/t_thumb/co22hf.jpg",
#             "width": 405,
#         },
#         "platforms": [
#             {
#                 "_id": 6,
#                 "abbreviation": "PC",
#                 "name": "PC (Microsoft Windows)",
#                 "logo": {
#                     "id": 670,
#                     "alpha_channel": false,
#                     "animated": false,
#                     "height": 69,
#                     "image_id": "plim",
#                     "url": "//images.igdb.com/igdb/image/upload/t_thumb/plim.jpg",
#                     "width": 375,
#                 },
#             },
#             {
#                 "_id": 34,
#                 "abbreviation": "Android",
#                 "name": "Android",
#                 "logo": {
#                     "id": 831,
#                     "alpha_channel": true,
#                     "animated": false,
#                     "height": 110,
#                     "image_id": "pln3",
#                     "url": "//images.igdb.com/igdb/image/upload/t_thumb/pln3.jpg",
#                     "width": 640,
#                 },
#             },
#             {
#                 "_id": 39,
#                 "abbreviation": "iOS",
#                 "name": "iOS",
#                 "logo": {
#                     "id": 248,
#                     "alpha_channel": true,
#                     "animated": false,
#                     "height": 1000,
#                     "image_id": "pl6w",
#                     "url": "//images.igdb.com/igdb/image/upload/t_thumb/pl6w.jpg",
#                     "width": 1000,
#                 },
#             },
#         ],
#         "genres": [
#             {
#                 "_id": 10,
#                 "name": "Racing",
#                 "slug": "racing",
#                 "url": "https://www.igdb.com/genres/racing",
#                 "updated_at": 1323289215,
#                 "created_at": 1297639288,
#             },
#             {
#                 "_id": 14,
#                 "name": "Sport",
#                 "slug": "sport",
#                 "url": "https://www.igdb.com/genres/sport",
#                 "updated_at": 1323289215,
#                 "created_at": 1297639288,
#             },
#             {
#                 "_id": 32,
#                 "name": "Indie",
#                 "slug": "indie",
#                 "url": "https://www.igdb.com/genres/indie",
#                 "updated_at": 1341431954,
#                 "created_at": 1341431954,
#             },
#         ],
#         "artworks": [],
#         "releases": [],
#         "game_modes": [
#             {
#                 "_id": 1,
#                 "name": "Single player",
#                 "slug": "single-player",
#                 "url": "https://www.igdb.com/game_modes/single-player",
#                 "updated_at": 1323289216,
#                 "created_at": 1298968834,
#             }
#         ],
#         "alternative_names": [],
#         "parent_game": null,
#         "rating": null,
#         "rating_count": null,
#         "summary": "A racing game for iOS and Android. Inspired by Outrun and Top Gear.",
#         "themes": [],
#         "dlcs": [],
#         "keywords": [{"_id": 4205, "name": "motorsports"}],
#         "created_at": null,
#         "updated_at": null,
#         "url": "https://www.igdb.com/games/horizon-chase",
#         "total_rating": 71.40076527448345,
#         "total_rating_count": 13,
#         "first_release_date": null,
#         "category": 0,
#         "status": null,
#         "version_parent": null,
#     },
#     "completion": {
#         "completed_at": "2023-03-18T20:17:17.463Z",
#         "hours_played": null,
#         "played_platforms": ["Android"],
#         "is_favorite": false,
#         "rating": null,
#     },
# }
