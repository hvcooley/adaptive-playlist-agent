import argparse
import json
import os
from datetime import datetime, timezone

from constants.llm_settings import ANTHROPIC_MODEL, PROMPT_VERSION
from evaluator import aggregate, score
from llm_client import generate_artists

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_EVAL_QUERIES_PATH = os.path.join(_MODULE_DIR, "eval_queries.json")
_RESULTS_LOG_PATH = os.path.join(_MODULE_DIR, "results_log.jsonl")


def _load_eval_queries() -> list[dict]:
    with open(_EVAL_QUERIES_PATH) as f:
        return json.load(f)


def _log_result(record: dict) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": ANTHROPIC_MODEL,
        "prompt_version": PROMPT_VERSION,
        **record,
    }
    with open(_RESULTS_LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


def run_eval_set() -> None:
    """Runs every query in eval_queries.json, scores it against its gold
    artist list, and logs both per-query and aggregate metrics."""
    eval_queries = _load_eval_queries()
    per_query_scores = []

    for entry in eval_queries:
        predicted = generate_artists(entry["query"])
        result = score(predicted, entry["expected_artists"])
        per_query_scores.append(result)

        print(f"[{entry['id']}] {entry['query']}")
        print(f"  predicted: {predicted}")
        print(f"  precision={result['precision']} recall={result['recall']} f1={result['f1']}")
        print(f"  missed: {result['missed']}")
        print()

        _log_result(
            {
                "mode": "eval",
                "query_id": entry["id"],
                "query": entry["query"],
                "predicted": predicted,
                "expected": entry["expected_artists"],
                **result,
            }
        )

    agg = aggregate(per_query_scores)
    print("=== aggregate across eval set ===")
    print(f"precision={agg['precision']} recall={agg['recall']} f1={agg['f1']}")

    _log_result({"mode": "eval_aggregate", **agg, "num_queries": len(eval_queries)})


def run_interactive() -> None:
    """Free-form query, unscored — there's no gold answer for arbitrary
    input, so this is for exploration only, not evaluation."""
    query = input("Describe the playlist you want: ").strip()
    predicted = generate_artists(query)

    print("\nRecommended artists (unscored — no gold answer for free-form input):")
    for artist in predicted:
        print(f"  - {artist}")

    _log_result({"mode": "interactive", "query": query, "predicted": predicted})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baseline LLM playlist generation + retrieval-style evaluation."
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Run the full labeled eval_queries.json set and score against gold artists.",
    )
    args = parser.parse_args()

    if args.eval:
        run_eval_set()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
