import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from quran_audio_parts import partition_contiguous_ayahs

class PartsTests(unittest.TestCase):
    def test_parts_cover_sequence(self):
        verses = [{'ayah': n} for n in range(1, 7)]
        parts, rest = partition_contiguous_ayahs(verses, {1: 20, 2: 22, 3: 25, 4: 30, 5: 31, 6: 4})
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1, 2], [3, 4], [5, 6]])
        self.assertEqual(rest, [])
    def test_long_verse_blocks_suffix(self):
        verses = [{'ayah': n} for n in range(1, 5)]
        parts, rest = partition_contiguous_ayahs(verses, {1: 30, 2: 66, 3: 10, 4: 10})
        self.assertEqual([[v['ayah'] for v in p] for p in parts], [[1]])
        self.assertEqual([v['ayah'] for v in rest], [2, 3, 4])
    def test_gap_rejected(self):
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            partition_contiguous_ayahs([{'ayah': 1}, {'ayah': 3}], {1: 10, 3: 10})

if __name__ == '__main__':
    unittest.main()
