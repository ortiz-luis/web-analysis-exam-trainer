import json
import tempfile
import unittest
from pathlib import Path

from src.progress import Progress, get_pending_stage_questions


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

    def test_detecting_current_unlocked_stage(self) -> None:
        questions = sample_questions()

        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")

            self.assertEqual(
                progress.current_unlocked_stage(questions),
                "lesson_1_python_basics",
            )

    def test_completing_a_stage(self) -> None:
        questions = sample_questions()

        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")
            progress.record_correct("q1")
            progress.record_correct("q2")

            self.assertTrue(
                progress.is_stage_complete(questions, "lesson_1_python_basics")
            )

    def test_unlocking_the_next_stage(self) -> None:
        questions = sample_questions()

        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")
            progress.record_correct("q1")
            progress.record_correct("q2")

            self.assertEqual(
                progress.current_unlocked_stage(questions),
                "lesson_3_html_bs4_scraping",
            )

    def test_not_asking_questions_from_locked_stages(self) -> None:
        questions = sample_questions()

        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")
            current_stage = progress.current_unlocked_stage(questions)
            pending_questions = get_pending_stage_questions(
                questions,
                progress,
                current_stage,
            )

            self.assertEqual({question["id"] for question in pending_questions}, {"q1", "q2"})

    def test_detecting_all_stages_complete(self) -> None:
        questions = sample_questions()

        with tempfile.TemporaryDirectory() as directory:
            progress = Progress(Path(directory) / "progress.json")
            for question in questions:
                progress.record_correct(question["id"])

            self.assertTrue(progress.all_stages_complete(questions))
            self.assertIsNone(progress.current_unlocked_stage(questions))


def sample_questions() -> list[dict[str, str]]:
    return [
        {
            "id": "q1",
            "stage": "lesson_1_python_basics",
        },
        {
            "id": "q2",
            "stage": "lesson_1_python_basics",
        },
        {
            "id": "q3",
            "stage": "lesson_3_html_bs4_scraping",
        },
        {
            "id": "q4",
            "stage": "integrated_practice",
        },
    ]


if __name__ == "__main__":
    unittest.main()
