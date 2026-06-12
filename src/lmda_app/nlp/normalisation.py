from __future__ import annotations


def normalise_lemma(lemma: str) -> str:
    """Normalise a lemma for v1 processing."""
    return lemma.strip().lower()


def is_usable_lemma(lemma: str) -> bool:
    """Return whether a normalised lemma should be retained."""
    return bool(lemma)