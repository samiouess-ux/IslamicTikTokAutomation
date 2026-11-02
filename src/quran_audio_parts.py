"""Safe partitioning of ordered Quran ayahs into review-video duration parts."""
from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def partition_contiguous_ayahs(
    ayahs: Sequence[T],
    durations_seconds: dict[int, float],
    maximum_seconds: float = 65.0,
) -> tuple[list[list[T]], list[T]]:
    """Return ordered whole-ayah parts and an unprocessed suffix.

    An ayah longer than the limit blocks itself and every later ayah. No ayah
    is split, skipped, reordered, or silently discarded.
    """
    if maximum_seconds <= 0:
        raise ValueError("maximum_seconds must be positive.")
    numbers = [int(item["ayah"]) for item in ayahs]  # type: ignore[index]
    if not numbers:
        return [], []
    if len(numbers) != len(set(numbers)):
        raise ValueError("Requested ayahs contain duplicates.")
    if any(right != left + 1 for left, right in zip(numbers, numbers[1:])):
        raise ValueError("Requested ayahs must be one contiguous ordered range.")

    parts: list[list[T]] = []
    current: list[T] = []
    current_duration = 0.0
    blocked_at: int | None = None
    for index, (item, number) in enumerate(zip(ayahs, numbers)):
        duration = float(durations_seconds[number])
        if duration <= 0:
            raise ValueError(f"Invalid processed duration for ayah {number}.")
        if duration > maximum_seconds:
            blocked_at = index
            break
        if current and current_duration + duration > maximum_seconds:
            parts.append(current)
            current = []
            current_duration = 0.0
        current.append(item)
        current_duration += duration
    if current:
        parts.append(current)

    consumed = sum(len(part) for part in parts)
    remaining = list(ayahs[consumed:])
    flattened = [int(item["ayah"]) for part in parts for item in part]
    if flattened != numbers[:consumed] or flattened + [int(x["ayah"]) for x in remaining] != numbers:
        raise AssertionError("Ayah partition did not preserve the exact requested sequence.")
    if blocked_at is not None and not remaining:
        raise AssertionError("Oversized ayah must remain unprocessed.")
    return parts, remaining
