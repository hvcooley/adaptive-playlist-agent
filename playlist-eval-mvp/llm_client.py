import os
import sys

import anthropic
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants.llm_settings import (
    ANTHROPIC_MODEL,
    LLM_MAX_TOKENS,
    UNIQUE_ARTISTS_FOR_PLAYLIST
)

_PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

_PLAYLIST_TOOL = {
    "name": "return_playlist",
    "description": "Return a playlist of artist recommendations for the user's query.",
    "input_schema": {
        "type": "object",
        "properties": {
            "artists": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Artist names recommended for the playlist, most relevant first.",
            }
        },
        "required": ["artists"],
    },
}


def _client() -> anthropic.Anthropic:
    load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def generate_artists(query: str, playlist_size: int = UNIQUE_ARTISTS_FOR_PLAYLIST) -> list[str]:
    """Asks the LLM for artists matching the query.

    No retrieval involved — this is the model's raw knowledge, used as the
    baseline that a future RAG pipeline should be able to beat. Song-level
    selection is a separate step, built once this artist-level result is
    evaluated and trusted.
    """
    response = _client().messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        tools=[_PLAYLIST_TOOL],
        tool_choice={"type": "tool", "name": "return_playlist"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"Recommend {playlist_size} artists for a playlist matching "
                    f"this description: {query!r}"
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "return_playlist":
            return list(block.input.get("artists", []))

    raise RuntimeError("LLM response did not include a return_playlist tool call")
