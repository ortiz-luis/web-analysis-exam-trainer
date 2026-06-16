import json
import tempfile
import unittest
from pathlib import Path

from src.progress import Progress


class ProgressTests(unittest.TestCase):
    def test_progress_file_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            progress_file = Path(directory) / "progress.json"

            Progress(progress_file)

            self.assertTrue(progress_file.exists())
            self.assertEqual(
                json.loads(progress_file.read_text(encoding="utf-8")),
                {"answers": {}},
            )

    def test_marking_correct(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")

            progress.record_correct("q1")

        self.assertEqual(progress.data["answers"]["q1"]["correct_count"], 1)
        self.assertEqual(progress.data["answers"]["q1"]["wrong_count"], 0)
        self.assertIs(progress.data["answers"]["q1"]["last_answer_correct"], True)

    def test_marking_wrong(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")

            progress.record_wrong("q1")

        self.assertEqual(progress.data["answers"]["q1"]["correct_count"], 0)
        self.assertEqual(progress.data["answers"]["q1"]["wrong_count"], 1)
        self.assertIs(progress.data["answers"]["q1"]["last_answer_correct"], False)

    def test_detecting_if_question_was_answered_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")

            self.assertFalse(progress.was_answered_correctly("q1"))

            progress.record_wrong("q1")
            self.assertFalse(progress.was_answered_correctly("q1"))

            progress.record_correct("q1")
            self.assertTrue(progress.was_answered_correctly("q1"))


if __name__ == "__main__":
    unittest.main()
