import json
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

    def test_short_answer_without_correct_answer_is_valid(self) -> None:
        question = base_question()
        question.update(
            {
                "type": "short_answer",
                "oral_model_answer": "Une reponse modele.",
                "grading_checklist": ["Point attendu"],
            }
        )

        questions = self.load_temp_questions([question])

        self.assertEqual(questions[0]["type"], "short_answer")
        self.assertNotIn("correct_answer", questions[0])

    def test_oral_explanation_without_correct_answer_is_valid(self) -> None:
        question = base_question()
        question.update(
            {
                "type": "oral_explanation",
                "oral_model_answer": "Une reponse orale modele.",
                "grading_checklist": ["Point attendu"],
            }
        )

        questions = self.load_temp_questions([question])

        self.assertEqual(questions[0]["type"], "oral_explanation")
        self.assertNotIn("correct_answer", questions[0])

    def test_automatically_checkable_question_without_correct_answer_is_invalid(self) -> None:
        question = base_question()
        question["type"] = "fill_blank"

        with tempfile.TemporaryDirectory() as directory:
            question_file = Path(directory) / "questions.json"
            question_file.write_text(json.dumps([question]), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "correct_answer"):
                load_questions(question_file)

    def load_temp_questions(self, questions: list[dict[str, object]]) -> list[dict]:
        with tempfile.TemporaryDirectory() as directory:
            question_file = Path(directory) / "questions.json"
            question_file.write_text(
                json.dumps(questions),
                encoding="utf-8",
            )
            return load_questions(question_file)


def base_question() -> dict[str, object]:
    return {
        "id": "q1",
        "stage": "lesson_1_python_basics",
        "lesson": "Cours 1",
        "topic": "functions",
        "difficulty": 3,
        "prompt": "Explique ce code.",
        "explanation": "Explication courte.",
    }


if __name__ == "__main__":
    unittest.main()
