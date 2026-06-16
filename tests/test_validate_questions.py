import json
import tempfile
import unittest
from pathlib import Path

from src.validate_questions import validate_question_bank


class ValidateQuestionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dirs: list[tempfile.TemporaryDirectory] = []

    def tearDown(self) -> None:
        for directory in self.temp_dirs:
            directory.cleanup()

    def test_valid_question_bank(self) -> None:
        errors = validate_question_bank(self.write_bank([valid_question()]))

        self.assertEqual(errors, [])

    def test_duplicate_ids(self) -> None:
        errors = validate_question_bank(
            self.write_bank([valid_question("q1"), valid_question("q1")])
        )

        self.assertTrue(any("duplicate id" in error for error in errors))

    def test_missing_required_field(self) -> None:
        question = valid_question()
        del question["topic"]

        errors = validate_question_bank(self.write_bank([question]))

        self.assertTrue(any("missing required field" in error for error in errors))

    def test_invalid_question_type(self) -> None:
        question = valid_question()
        question["type"] = "essay"

        errors = validate_question_bank(self.write_bank([question]))

        self.assertTrue(any("invalid question type" in error for error in errors))

    def test_multiple_choice_without_options(self) -> None:
        question = valid_question()
        del question["options"]

        errors = validate_question_bank(self.write_bank([question]))

        self.assertTrue(any("need options" in error for error in errors))

    def test_oral_explanation_without_oral_model_answer(self) -> None:
        question = valid_question()
        question["type"] = "oral_explanation"
        del question["options"]
        del question["correct_answer"]

        errors = validate_question_bank(self.write_bank([question]))

        self.assertTrue(any("need oral_model_answer" in error for error in errors))

    def test_invalid_stage(self) -> None:
        question = valid_question()
        question["stage"] = "unknown_stage"

        errors = validate_question_bank(self.write_bank([question]))

        self.assertTrue(any("invalid stage" in error for error in errors))

    def test_invalid_difficulty(self) -> None:
        question = valid_question()
        question["difficulty"] = 11

        errors = validate_question_bank(self.write_bank([question]))

        self.assertTrue(any("difficulty must be" in error for error in errors))

    def write_bank(self, questions: list[dict[str, object]]) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.temp_dirs.append(directory)
        path = Path(directory.name) / "questions.json"
        path.write_text(json.dumps(questions), encoding="utf-8")
        return path


def valid_question(question_id: str = "q1") -> dict[str, object]:
    return {
        "id": question_id,
        "stage": "lesson_1_python_basics",
        "lesson": "Intro",
        "topic": "HTTP",
        "difficulty": 2,
        "type": "multiple_choice",
        "prompt": "Which method retrieves a page?",
        "options": ["GET", "POST"],
        "correct_answer": "GET",
        "explanation": "GET retrieves resources.",
    }


if __name__ == "__main__":
    unittest.main()
