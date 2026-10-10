# iplayed

Terminal UI for recording game completions, fetching game data from IGDB, and publishing the data through the Zola static site in `iplayed_ssg`.

## Requirements

- Nix with `nix-shell`, or Python 3.14, [uv](https://docs.astral.sh/uv/), Zola 0.20.0, and Git installed manually
- IGDB API credentials from the Twitch Developer Console to use the CLI
- A modern terminal that supports [Textual](https://textual.textualize.io/)

The repository includes `shell.nix` for the required system tools: Python, uv, Zola 0.20.0, and Git. Python dependencies are installed from the committed `uv.lock` file.

## First-time setup

```sh
git clone --recurse-submodules https://github.com/<your-username>/iplayed.git
cd iplayed
```

If you cloned without `--recurse-submodules`, initialize the Zola theme and the other tracked submodules:

```sh
git submodule update --init --recursive
```

Enter the Nix development shell, if using Nix:

```sh
nix-shell
```

Install the locked Python dependencies:

```sh
uv sync
```

Create `.env` in the repository root. It is loaded automatically by `python-dotenv` and must not be committed:

```dotenv
IGDB_CLIENT_ID=
IGDB_CLIENT_SECRET=
SSG_DIRECTORY=./iplayed_ssg
SSG_CONTENT_DIRECTORY=./iplayed_ssg/content/games
```

`SSG_CONTENT_DIRECTORY` already exists in this checkout. Set the variables to absolute paths instead if the site is stored elsewhere.

## Run the CLI

From the repository root:

```sh
uv run python iplayed_cli/app.py
```

The CLI requires all four `.env` variables, even for screens that do not make an IGDB request. IGDB operations require network access and are subject to API rate limits. Its deploy action also requires Git authentication for the `origin` remote and pushes to `main`.

## Build the site

Generate Markdown from the completion data and copy the data used by the site's dashboard:

```sh
uv run python iplayed_cli/completions_to_markdown.py \
  --completions ./iplayed_cli/data/completions.json \
  --target-dir ./iplayed_ssg/content/games
cp ./iplayed_cli/data/completions.json ./iplayed_ssg/static/completions.json
```

Serve the site locally:

```sh
zola --root iplayed_ssg serve
```

Create a production build in `iplayed_ssg/public`:

```sh
zola --root iplayed_ssg build
```

The generated game Markdown, copied completion data, and Zola output are ignored by Git. The GitHub Actions workflow runs the same generation and build steps on pushes to `main`.
