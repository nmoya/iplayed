# iplayed

Python project managed by uv.

## Additional dependencies

Pyxelate is a submodule dependency, so after cloning the project you should run:

```
git submodule update --init --recursive
```

The dependencies of the submodule are already covered by uv package.lock

# Example .env file

```
IGDB_CLIENT_ID=
IGDB_CLIENT_SECRET=
SSG_DIRECTORY=./iplayed_ssg
SSG_CONTENT_DIRECTORY=./iplayed_ssg/content/games
SSG_PIXELATED_COVERS_DIRECTORY=./iplayed_ssg/static/covers
```