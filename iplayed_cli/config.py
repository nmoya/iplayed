import os

from dotenv import load_dotenv

load_dotenv()


IGDB_CLIENT_ID = os.environ["IGDB_CLIENT_ID"]
IGDB_CLIENT_SECRET = os.environ["IGDB_CLIENT_SECRET"]
SSG_DIRECTORY = os.environ["SSG_DIRECTORY"]
SSG_CONTENT_DIRECTORY = os.environ["SSG_CONTENT_DIRECTORY"]
SSG_PIXELATED_COVERS_DIRECTORY = os.environ["SSG_PIXELATED_COVERS_DIRECTORY"]
