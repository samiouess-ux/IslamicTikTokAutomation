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
    """Pack complete contiguous ayahs toward the normal cap, with one extension up to the hard cap.

    A part may exceed maximum_seconds only when adding the next complete ayah
    keeps the total within exceptional_single_ayah_seconds. That extension
    closes the part immediately; no further ayah is added to it. An ayah that
    individually exceeds the normal cap may still be emitted alone when it
    fits the exceptional ceiling.
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

        if duration > maximum_seconds:
            if hard_cap is None or duration > hard_cap:
                break
            if current:
                parts.append(current)
                current = []
                current_duration = 0.0
            # An individually long ayah is always its own complete part.
            parts.append([item])
            continue

        if current and current_duration + duration > maximum_seconds:
            if hard_cap is not None and current_duration + duration <= hard_cap:
                # One complete ayah may extend this part beyond the target.
                current.append(item)
                parts.append(current)
                current = []
                current_duration = 0.0
                continue
            parts.append(current)
            current = []
            current_duration = 0.0

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
