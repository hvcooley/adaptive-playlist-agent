ANTHROPIC_MODEL = "claude-sonnet-5"

# `temperature` is deprecated/rejected for this model, so sampling isn't
# configurable here — reproducibility across eval runs isn't guaranteed.
LLM_MAX_TOKENS = 1024

PLAYLIST_SIZE = 10

UNIQUE_ARTISTS_FOR_PLAYLIST = 10

PROMPT_VERSION = "v1"
