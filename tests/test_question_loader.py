import tempfile
import unittest
from pathlib import Path

from src.question_loader import load_questions


class QuestionLoaderTests(unittest.TestCase):
    def test_load_questions_from_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            question_file = Path(directory) / "questions.json"
            question_file.write_text(
                """
                [
                  {
                    "id": "q1",
                    "stage": "sample",
                    "lesson": "Intro",
                    "topic": "HTTP",
                    "difficulty": "easy",
                    "type": "true_false",
                    "prompt": "GET retrieves resources.",
                    "correct_answer": true,
                    "explanation": "GET is used for retrieval."
                  }
                ]
                """,
                encoding="utf-8",
            )

            questions = load_questions(question_file)

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["id"], "q1")
        self.assertIs(questions[0]["correct_answer"], True)

    def test_load_questions_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            question_file = Path(directory) / "questions.json"
            question_file.write_text('[{"id": "q1"}]', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing required fields"):
                load_questions(question_file)


if __name__ == "__main__":
    unittest.main()
