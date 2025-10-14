# iplayed

Terminal UI (Textual) to manage game completions, sync IGDB data, and generate content for the static site in `iplayed_ssg`.

## Prerequisites

- Python 3.13+
- Git
- IGDB API credentials (Twitch Developer Console)
- A terminal that supports Textual (Windows Terminal, iTerm2, most modern terminals)

## Clone and initialize submodules

Pyxelate is included as a git submodule. After cloning, initialize submodules:

```
git clone https://github.com/<your-username>/iplayed.git
cd iplayed
git submodule update --init --recursive
```

## Setup environment variables

Create a `.env` file in the project root (loaded automatically by `python-dotenv`):

```
IGDB_CLIENT_ID=
IGDB_CLIENT_SECRET=
SSG_DIRECTORY=./iplayed_ssg
SSG_CONTENT_DIRECTORY=./iplayed_ssg/content/games
SSG_PIXELATED_COVERS_DIRECTORY=./iplayed_ssg/static/covers
```

Notes:
- `SSG_DIRECTORY` should point to the root of the companion static site repo in this project (`./iplayed_ssg`).
- Ensure the `SSG_CONTENT_DIRECTORY` exists. For first run: `mkdir -p iplayed_ssg/content/games`.
- Ensure the pixelated covers directory exists: `mkdir -p iplayed_ssg/static/covers`.

## Install dependencies (using uv)

This project is managed with [uv](https://docs.astral.sh/uv/). If you have uv installed:

```
uv sync
```

This creates a virtual environment (if not present) and installs dependencies from `pyproject.toml` and `uv.lock`.

### Alternative: using Python venv + pip

If you prefer not to use uv:

```
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

# Install dependencies directly from pyproject
pip install -U pip
pip install -r <(uv export --format requirements)  # if uv is available for export
# or install packages individually if you don't have uv:
pip install dotenv howlongtobeatpy httpx humanize matplotlib numba pydantic requests rich scikit-image scikit-learn textual toolz tqdm
```

## Run the app

From the project root:

```
# With uv
uv run python iplayed_cli/app.py

# Or with plain Python (after activating your venv)
python iplayed_cli/app.py
```

The app starts in a Textual TUI with a main menu:
- 1: Manage Completions
- 2: Review configuration (read-only summary of your .env)
- 3: Content management (generate markdown, pixelated images, refresh IGDB data)

## Tips

- IGDB rate limits can slow down refresh operations; the UI progress will update as work proceeds.
- Generated markdown is written to `SSG_CONTENT_DIRECTORY`; pixelated covers go to `SSG_PIXELATED_COVERS_DIRECTORY`; a copy of `completions.json` is written to `SSG_DIRECTORY/static/completions.json`.
