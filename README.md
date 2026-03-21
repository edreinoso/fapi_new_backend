# UEFA Fantasy Data Analysis

Jupyter notebook project for fetching and analyzing UEFA Champions League Fantasy player data.

## What it does

- Fetches player data from the UEFA Fantasy API
- Cleans and structures the data into a pandas DataFrame
- Explores player stats: total points, goals, assists, minutes played, and more
- Filters active players and groups stats by position and team
- Ranks top players per position

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```sh
# Install dependencies
uv sync

# Launch Jupyter (or use VS Code with the .venv kernel)
uv run jupyter lab
```

## Dependencies

- `requests` — HTTP client for API calls
- `pandas` — DataFrames and data analysis
- `boto3` — AWS SDK
- `ipykernel` — Jupyter kernel support