import json
import tempfile
import unittest
from pathlib import Path

from src.validate_questions import (
    DEFAULT_QUESTION_FILE,
    EXPECTED_STAGE_COUNTS,
    EXPECTED_TOTAL,
    parse_args,
    validate_question_bank,
)


class ValidateQuestionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dirs: list[tempfile.TemporaryDirectory] = []

    def tearDown(self) -> None:
        for directory in self.temp_dirs:
            directory.cleanup()

    def test_valid_question_bank(self) -> None:
        errors = validate_question_bank(self.write_bank(valid_bank()))

        self.assertEqual(errors, [])

    def test_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text("[", encoding="utf-8")

            errors = validate_question_bank(path)

        self.assertTrue(errors)

    def test_duplicate_ids(self) -> None:
        questions = valid_bank()
        questions[1]["id"] = questions[0]["id"]

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("duplicate id" in error for error in errors))

    def test_missing_required_field(self) -> None:
        questions = valid_bank()
        del questions[0]["topic"]

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("missing required field" in error for error in errors))

    def test_invalid_question_type(self) -> None:
        questions = valid_bank()
        questions[0]["type"] = "essay"

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("invalid question type" in error for error in errors))

    def test_multiple_choice_without_options(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "multiple_choice")
        del question["options"]

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("need options" in error for error in errors))

    def test_multiple_choice_correct_answer_must_match_option(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "multiple_choice")
        question["correct_answer"] = "Missing option"

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("must match one option" in error for error in errors))

    def test_true_false_correct_answer_must_be_boolean(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "true_false")
        question["correct_answer"] = "true"

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("must be a boolean" in error for error in errors))

    def test_fill_blank_without_correct_answer(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "fill_blank")
        del question["correct_answer"]

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("fill_blank questions need correct_answer" in error for error in errors))

    def test_predict_output_without_correct_answer(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "predict_output")
        del question["correct_answer"]

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("predict_output questions need correct_answer" in error for error in errors))

    def test_short_answer_without_oral_model_answer(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "short_answer")
        del question["oral_model_answer"]

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("need oral_model_answer" in error for error in errors))

    def test_oral_explanation_without_grading_checklist(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "oral_explanation")
        del question["grading_checklist"]

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("need grading_checklist" in error for error in errors))

    def test_grading_checklist_must_be_non_empty_list_of_strings(self) -> None:
        questions = valid_bank()
        question = first_question_of_type(questions, "short_answer")
        question["grading_checklist"] = []

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("non-empty list of strings" in error for error in errors))

    def test_invalid_stage(self) -> None:
        questions = valid_bank()
        questions[0]["stage"] = "unknown_stage"

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("invalid stage" in error for error in errors))

    def test_invalid_difficulty(self) -> None:
        questions = valid_bank()
        questions[0]["difficulty"] = 11

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("difficulty must be" in error for error in errors))

    def test_stage_count_must_match_expected_count(self) -> None:
        questions = valid_bank()
        questions.pop()

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any("must contain exactly" in error for error in errors))

    def test_total_count_must_be_expected_total(self) -> None:
        questions = valid_bank()
        questions.append(valid_question("extra_q", "lesson_1_python_basics", "multiple_choice"))

        errors = validate_question_bank(self.write_bank(questions))

        self.assertTrue(any(str(EXPECTED_TOTAL) in error for error in errors))

    def test_default_question_file_argument(self) -> None:
        args = parse_args([])

        self.assertEqual(args.questions, DEFAULT_QUESTION_FILE)

    def test_custom_question_file_argument(self) -> None:
        args = parse_args(["data/real_questions.json"])

        self.assertEqual(args.questions, Path("data/real_questions.json"))

    def write_bank(self, questions: list[dict[str, object]]) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.temp_dirs.append(directory)
        path = Path(directory.name) / "questions.json"
        path.write_text(json.dumps(questions), encoding="utf-8")
        return path


def valid_bank() -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    type_cycle = [
        "multiple_choice",
        "true_false",
        "fill_blank",
        "predict_output",
        "short_answer",
        "oral_explanation",
    ]

    for stage, count in EXPECTED_STAGE_COUNTS.items():
        for index in range(count):
            question_type = type_cycle[index % len(type_cycle)]
            question_id = f"{stage}_{index + 1:03d}"
            questions.append(valid_question(question_id, stage, question_type))

    return questions


def valid_question(
    question_id: str,
    stage: str,
    question_type: str,
) -> dict[str, object]:
    question: dict[str, object] = {
        "id": question_id,
        "stage": stage,
        "lesson": "Cours",
        "topic": "topic",
        "difficulty": 2,
        "type": question_type,
        "prompt": "Question ?",
        "explanation": "Explication.",
    }

    if question_type == "multiple_choice":
        question["options"] = ["A", "B"]
        question["correct_answer"] = "A"
    elif question_type == "true_false":
        question["correct_answer"] = True
    elif question_type in {"fill_blank", "predict_output"}:
        question["correct_answer"] = "A"
    elif question_type in {"short_answer", "oral_explanation"}:
        question["oral_model_answer"] = "Réponse modèle."
        question["grading_checklist"] = ["Point attendu"]

    return question


def first_question_of_type(
    questions: list[dict[str, object]],
    question_type: str,
) -> dict[str, object]:
    for question in questions:
        if question["type"] == question_type:
            return question
    raise AssertionError(f"No question of type {question_type}")


if __name__ == "__main__":
    unittest.main()
