How to use package management in the data ingestion pipeline:


# Dev / local setup — editable install, picks up pyproject.toml
pip install -e ".[dev]"

# CI / production — deterministic, exact versions every time
pip install -r requirements.txt

# Regenerate the lockfile after bumping pyproject.toml
pip install -e . && pip freeze > requirements.txt