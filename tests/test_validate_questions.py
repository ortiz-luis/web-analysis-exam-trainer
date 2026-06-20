import json
import tempfile
import unittest
from pathlib import Path

from src.validate_questions import (
    DEFAULT_QUESTION_FILE,
    EXAM_V2_EXPECTED_TOTAL,
    EXAM_V2_STAGE_COUNTS,
    EXAM_V2_STAGE_ORDER,
    EXPECTED_STAGE_COUNTS,
    EXPECTED_TOTAL,
    STRESS_DIFFICULTY_GROUPS,
    STRESS_EXPECTED_TOTAL,
    STRESS_STAGE_COUNTS,
    STRESS_STAGE_ORDER,
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

    def test_exam_v2_argument(self) -> None:
        args = parse_args(["data/exam_mocks_v2.json", "--exam-v2"])

        self.assertTrue(args.exam_v2)

    def test_stress_argument(self) -> None:
        args = parse_args(["data/exam_mocks_stress.json", "--stress"])

        self.assertTrue(args.stress)

    def test_existing_course_bank_is_valid(self) -> None:
        errors = validate_question_bank(Path("data/questions_course.json"))

        self.assertEqual(errors, [])

    def test_exam_v2_bank_is_valid(self) -> None:
        errors = validate_question_bank(Path("data/exam_mocks_v2.json"), exam_v2=True)

        self.assertEqual(errors, [])

    def test_exam_v2_stage_counts(self) -> None:
        questions = read_json(Path("data/exam_mocks_v2.json"))

        self.assertEqual(len(questions), EXAM_V2_EXPECTED_TOTAL)
        for stage in EXAM_V2_STAGE_ORDER:
            count = sum(1 for question in questions if question["stage"] == stage)
            self.assertEqual(count, EXAM_V2_STAGE_COUNTS[stage])

    def test_exam_v2_schema(self) -> None:
        questions = read_json(Path("data/exam_mocks_v2.json"))

        for question in questions:
            with self.subTest(question_id=question["id"]):
                self.assertIn(question["stage"], EXAM_V2_STAGE_ORDER)
                if question["type"] == "multiple_choice":
                    self.assertIn(question["correct_answer"], question["options"])
                if question["type"] == "true_false":
                    self.assertIsInstance(question["correct_answer"], bool)
                if question["type"] in {"short_answer", "oral_explanation"}:
                    self.assertNotIn("correct_answer", question)
                    self.assertIsInstance(question["oral_model_answer"], str)
                    self.assertTrue(question["grading_checklist"])

    def test_stress_bank_is_valid(self) -> None:
        errors = validate_question_bank(Path("data/exam_mocks_stress.json"), stress=True)

        self.assertEqual(errors, [])

    def test_stress_stage_counts(self) -> None:
        questions = read_json(Path("data/exam_mocks_stress.json"))

        self.assertEqual(len(questions), STRESS_EXPECTED_TOTAL)
        self.assertEqual({question["stage"] for question in questions}, set(STRESS_STAGE_ORDER))
        for stage in STRESS_STAGE_ORDER:
            count = sum(1 for question in questions if question["stage"] == stage)
            self.assertEqual(count, STRESS_STAGE_COUNTS[stage])

    def test_stress_has_ten_mocks_per_difficulty(self) -> None:
        questions = read_json(Path("data/exam_mocks_stress.json"))
        stages = {question["stage"] for question in questions}

        for group in STRESS_DIFFICULTY_GROUPS:
            group_stages = [
                stage for stage in stages if stage.startswith(f"stress_{group}_")
            ]
            self.assertEqual(len(group_stages), 10)

    def test_stress_schema_by_type(self) -> None:
        questions = read_json(Path("data/exam_mocks_stress.json"))

        for question in questions:
            with self.subTest(question_id=question["id"]):
                self.assertIn(question["stage"], STRESS_STAGE_ORDER)
                self.assertTrue(str(question["prompt"]).strip())
                self.assertTrue(str(question["explanation"]).strip())
                if question["type"] == "multiple_choice":
                    self.assertIn(question["correct_answer"], question["options"])
                if question["type"] == "true_false":
                    self.assertIsInstance(question["correct_answer"], bool)
                if question["type"] in {"fill_blank", "predict_output"}:
                    self.assertIn("correct_answer", question)
                if question["type"] in {"short_answer", "oral_explanation"}:
                    self.assertNotIn("correct_answer", question)
                    self.assertTrue(str(question["oral_model_answer"]).strip())
                    self.assertTrue(question["grading_checklist"])

    def test_no_duplicate_ids_across_course_v2_and_stress_banks(self) -> None:
        questions = (
            read_json(Path("data/questions_course.json"))
            + read_json(Path("data/exam_mocks_v2.json"))
            + read_json(Path("data/exam_mocks_stress.json"))
        )
        ids = [question["id"] for question in questions]

        self.assertEqual(len(ids), len(set(ids)))

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


def read_json(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
