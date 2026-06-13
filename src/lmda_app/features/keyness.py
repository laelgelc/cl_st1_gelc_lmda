from __future__ import annotations

import math
from enum import StrEnum


class KeywordStatus(StrEnum):
    """Keyword status labels."""

    POSITIVE = "POSKW"
    NEGATIVE = "NEGKW"
    NOT_KEYWORD = "NOTKW"


def log_likelihood(
        target_count: int,
        comparison_count: int,
        target_size: int,
        comparison_size: int,
) -> float:
    """Calculate log-likelihood for target/comparison presence counts.

    The v1 implementation preserves the reference workflow behaviour:
    if either observed count is zero, return 0.0.
    """
    if target_count == 0 or comparison_count == 0:
        return 0.0

    total_size = target_size + comparison_size
    total_count = target_count + comparison_count

    if total_size == 0 or total_count == 0:
        return 0.0

    expected_target = target_size * total_count / total_size
    expected_comparison = comparison_size * total_count / total_size

    if expected_target == 0 or expected_comparison == 0:
        return 0.0

    return 2 * (
            target_count * math.log(target_count / expected_target)
            + comparison_count * math.log(comparison_count / expected_comparison)
    )


def per_1k(count: int, size: int) -> float:
    """Calculate presence rate per 1,000 texts."""
    if size == 0:
        return 0.0

    return (count / size) * 1000


def expected_count(
        target_count: int,
        comparison_count: int,
        target_size: int,
        comparison_size: int,
) -> float:
    """Calculate expected target count."""
    total_size = target_size + comparison_size

    if total_size == 0:
        return 0.0

    return target_size * (target_count + comparison_count) / total_size


def percentage_difference(target_rate: float, comparison_rate: float) -> float:
    """Calculate percentage difference between target and comparison rates."""
    denominator = (target_rate + comparison_rate) / 2

    if denominator == 0:
        return 0.0

    return 100 * (target_rate - comparison_rate) / denominator


def classify_keyword_status(
        ll_value: float,
        percent_diff: float,
        threshold: float,
) -> KeywordStatus:
    """Classify a lemma as POSKW, NEGKW, or NOTKW."""
    if ll_value < threshold:
        return KeywordStatus.NOT_KEYWORD

    if percent_diff > 0:
        return KeywordStatus.POSITIVE

    return KeywordStatus.NEGATIVE