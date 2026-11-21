import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from quran_audio_parts import partition_contiguous_ayahs


class PartsTests(unittest.TestCase):
    def test_default_keeps_long_ayah_and_full_sequence_together(self):
        verses = [{'ayah': n} for n in range(1, 5)]
        parts, rest = partition_contiguous_ayahs(verses, {1: 30, 2: 66, 3: 10, 4: 10})
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1, 2, 3, 4]])
        self.assertEqual(rest, [])

    def test_explicit_normal_cap_defers_overflow_without_exception(self):
        verses = [{'ayah': n} for n in range(1, 5)]
        parts, rest = partition_contiguous_ayahs(verses, {1: 30, 2: 66, 3: 10, 4: 10}, 40)
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1]])
        self.assertEqual([v['ayah'] for v in rest], [2, 3, 4])

    def test_complete_next_ayah_can_extend_part_to_48_665_seconds(self):
        verses = [{'ayah': 1}, {'ayah': 2}, {'ayah': 3}]
        parts, rest = partition_contiguous_ayahs(
            verses, {1: 26.2, 2: 22.465, 3: 10}, 45, 60
        )
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1, 2]])
        self.assertEqual([v['ayah'] for v in rest], [3])

    def test_complete_next_ayah_can_extend_part_to_55_129_seconds(self):
        verses = [{'ayah': 1}, {'ayah': 2}, {'ayah': 3}]
        parts, rest = partition_contiguous_ayahs(
            verses, {1: 43.4, 2: 11.729, 3: 10}, 45, 60
        )
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1, 2]])
        self.assertEqual([v['ayah'] for v in rest], [3])

    def test_extension_is_not_allowed_above_60_seconds(self):
        verses = [{'ayah': 1}, {'ayah': 2}]
        parts, rest = partition_contiguous_ayahs(
            verses, {1: 43.4, 2: 16.7}, 45, 60
        )
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1]])
        self.assertEqual([v['ayah'] for v in rest], [2])

    def test_long_complete_ayah_between_45_and_60_stays_alone(self):
        verses = [{'ayah': 1}, {'ayah': 2}]
        parts, rest = partition_contiguous_ayahs(
            verses, {1: 46.733, 2: 10}, 45, 60
        )
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1], [2]])
        self.assertEqual(rest, [])

    def test_gap_rejected(self):
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            partition_contiguous_ayahs([{'ayah': 1}, {'ayah': 3}], {1: 10, 3: 10})


if __name__ == '__main__':
    unittest.main()
