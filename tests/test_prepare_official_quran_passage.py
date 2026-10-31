import unittest

from prepare_official_quran_passage import choose_contiguous_passage


class PassagePackingTests(unittest.TestCase):
    def test_selects_consecutive_verses_until_target(self):
        self.assertEqual(
            choose_contiguous_passage({1: 18.0, 2: 20.0, 3: 19.0, 4: 15.0}, 1),
            [1, 2, 3, 4],
        )

    def test_stops_before_exceeding_hard_limit(self):
        self.assertEqual(
            choose_contiguous_passage({1: 30.0, 2: 30.0, 3: 10.0}, 1),
            [1, 2],
        )

    def test_single_ayah_over_limit_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "alone exceeds"):
            choose_contiguous_passage({7: 66.0}, 7)

    def test_does_not_skip_missing_ayah(self):
        self.assertEqual(
            choose_contiguous_passage({1: 25.0, 3: 25.0}, 1),
            [1],
        )

    def test_missing_start_fails(self):
        with self.assertRaisesRegex(ValueError, "Missing duration"):
            choose_contiguous_passage({2: 10.0}, 1)

    def test_rejects_non_positive_duration(self):
        with self.assertRaisesRegex(ValueError, "Invalid duration"):
            choose_contiguous_passage({1: 0.0}, 1)


if __name__ == "__main__":
    unittest.main()
