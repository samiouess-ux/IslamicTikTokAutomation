"""Keep Quran ayahs whole and in their exact contiguous order."""
from __future__ import annotations
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def partition_contiguous_ayahs(
    ayahs: Sequence[T],
    durations_seconds: dict[int, float],
    maximum_seconds: float | None = None,
    exceptional_single_ayah_seconds: float | None = None,
) -> tuple[list[list[T]], list[T]]:
    """Pack each contiguous part as far as possible without crossing its hard cap.

    maximum_seconds is the preferred 45-second target. When the next whole,
    contiguous ayah takes the part above that target, keep adding subsequent
    complete ayahs while the combined part remains at or below
    exceptional_single_ayah_seconds (the 60-second hard cap). The target is
    not a reason to stop early. No ayah is split, skipped, reordered, or sped up.
    An ayah longer than the hard cap blocks the sequence at that point.
    """
    if maximum_seconds is not None and maximum_seconds <= 0:
        raise ValueError("maximum_seconds must be positive.")
    if exceptional_single_ayah_seconds is not None:
        if maximum_seconds is None or exceptional_single_ayah_seconds < maximum_seconds:
            raise ValueError("exceptional_single_ayah_seconds must be at least the normal maximum.")
    numbers = [int(item["ayah"]) for item in ayahs]  # type: ignore[index]
    if not numbers:
        return [], []
    if len(numbers) != len(set(numbers)):
        raise ValueError("Requested ayahs contain duplicates.")
    if any(right != left + 1 for left, right in zip(numbers, numbers[1:])):
        raise ValueError("Requested ayahs must be one contiguous ordered range.")

    hard_cap = exceptional_single_ayah_seconds or maximum_seconds
    parts: list[list[T]] = []
    current: list[T] = []
    current_duration = 0.0
    for item, number in zip(ayahs, numbers):
        duration = float(durations_seconds[number])
        if duration <= 0:
            raise ValueError(f"Invalid processed duration for ayah {number}.")

        if maximum_seconds is None:
            current.append(item)
            continue

        if hard_cap is not None and duration > hard_cap:
            if current:
                parts.append(current)
                current = []
                current_duration = 0.0
            # This ayah cannot be included intact. Stop here; never skip it.
            break

        if current and hard_cap is not None and current_duration + duration > hard_cap:
            parts.append(current)
            current = [item]
            current_duration = duration
            continue

        current.append(item)
        current_duration += duration

    if current:
        parts.append(current)
    selected_count = sum(len(group) for group in parts)
    remaining = list(ayahs[selected_count:])
    flattened = [int(item["ayah"]) for group in parts for item in group]  # type: ignore[index]
    if flattened != numbers[:selected_count]:
        raise AssertionError("Ayah partition did not preserve the exact requested prefix.")
    return parts, remaining
