def _normalize(name: str) -> str:
    return name.strip().lower()


def score(predicted: list[str], expected: list[str]) -> dict:
    """Set-based precision/recall/F1 between predicted and expected artists.

    Order-agnostic on purpose: at this stage we're scoring whether the right
    artists showed up at all, not whether they're ranked well.
    """
    predicted_set = {_normalize(a) for a in predicted}
    expected_set = {_normalize(a) for a in expected}

    hits = predicted_set & expected_set

    precision = len(hits) / len(predicted_set) if predicted_set else 0.0 #matches divided by total size of our llm generated results
    recall = len(hits) / len(expected_set) if expected_set else 0.0 #matches divided by total size of the pre decided answers 
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "hits": sorted(hits),
        "missed": sorted(expected_set - predicted_set),
    }


def aggregate(scores: list[dict]) -> dict:
    if not scores:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    n = len(scores)
    return {
        "precision": round(sum(s["precision"] for s in scores) / n, 3),
        "recall": round(sum(s["recall"] for s in scores) / n, 3),
        "f1": round(sum(s["f1"] for s in scores) / n, 3),
    }
