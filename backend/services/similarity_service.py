from __future__ import annotations

import hashlib


def find_similar_seasons(features: dict) -> dict:
    """Return deterministic demo neighbors until a vector store is configured.

    Future feature vectors:
    crop, county, month, rainfall, temperature, drought severity, yield,
    soil type, and growing degree days.

    TODO(pgvector): persist normalized feature vectors and query with cosine
    distance using pgvector's <=> operator.
    TODO(ChromaDB): add an adapter implementing the same response contract.
    """
    seed = int(hashlib.sha256(repr(sorted(features.items())).encode()).hexdigest()[:8], 16)
    years = [2012 + ((seed + offset * 7) % 13) for offset in range(3)]
    scores = [91 - seed % 4, 86 - seed % 3, 80 - seed % 5]
    outcomes = [
        "Near-average yield; water demand increased late in the season.",
        "Yield held steady despite a short period of heat stress.",
        "Below-average rainfall increased sensitivity to irrigation timing.",
    ]
    return {
        "matches": [
            {"year": year, "similarity_percent": score, "outcome": outcome}
            for year, score, outcome in zip(years, scores, outcomes)
        ],
        "source": "Demo similarity model",
        "is_placeholder": True,
    }
