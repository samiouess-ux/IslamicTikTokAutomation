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
    """Keep ordinary parts within the normal cap; isolate a longer whole ayah if allowed."""
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
    parts: list[list[T]] = []
    current: list[T] = []
    current_duration = 0.0
    for item, number in zip(ayahs, numbers):
        duration = float(durations_seconds[number])
        if duration <= 0:
            raise ValueError(f"Invalid processed duration for ayah {number}.")
        if maximum_seconds is not None and duration > maximum_seconds:
            if exceptional_single_ayah_seconds is None or duration > exceptional_single_ayah_seconds:
                break
            if current:
                parts.append(current)
                current = []
                current_duration = 0.0
            # Exceptional long ayahs are always their own part.
            parts.append([item])
            continue
        if maximum_seconds is not None and current and current_duration + duration > maximum_seconds:
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
