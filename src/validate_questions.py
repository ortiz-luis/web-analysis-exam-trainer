"""Validate quiz question banks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from src.progress import STAGE_ORDER


DEFAULT_QUESTION_FILE = Path("data/questions_sample.json")

REQUIRED_FIELDS = {
    "id",
    "stage",
    "lesson",
    "topic",
    "difficulty",
    "type",
    "prompt",
    "explanation",
}

ALLOWED_TYPES = {
    "multiple_choice",
    "true_false",
    "fill_blank",
    "predict_output",
    "short_answer",
    "oral_explanation",
}

AUTO_CHECKED_TYPES = {"multiple_choice", "true_false", "fill_blank", "predict_output"}
OPEN_ANSWER_TYPES = {"short_answer", "oral_explanation"}

EXPECTED_STAGE_COUNTS = {
    "lesson_1_python_basics": 35,
    "lesson_2_pandas_minimal": 35,
    "lesson_3_html_bs4_scraping": 35,
    "lesson_4_allocine_scraping": 35,
    "integrated_practice": 25,
    "exam_mock_01": 5,
    "exam_mock_02": 5,
    "exam_mock_03": 5,
    "exam_mock_04": 5,
    "exam_mock_05": 5,
    "exam_mock_06": 5,
    "exam_mock_07": 5,
    "exam_mock_08": 5,
    "exam_mock_09": 5,
    "exam_mock_10": 5,
}
EXPECTED_TOTAL = 215

EXAM_V2_STAGE_ORDER = [f"exam_v2_{index:02d}" for index in range(1, 21)]
EXAM_V2_STAGE_COUNTS = {stage: 5 for stage in EXAM_V2_STAGE_ORDER}
EXAM_V2_EXPECTED_TOTAL = 100

STRESS_DIFFICULTY_GROUPS = ("difficile", "tres_difficile", "extra_difficile")
STRESS_STAGE_ORDER = [
    f"stress_{group}_{index:02d}"
    for group in STRESS_DIFFICULTY_GROUPS
    for index in range(1, 11)
]
STRESS_STAGE_COUNTS = {stage: 5 for stage in STRESS_STAGE_ORDER}
STRESS_EXPECTED_TOTAL = 150
STRESS_STAGE_PATTERN = re.compile(
    r"^stress_(difficile|tres_difficile|extra_difficile)_(0[1-9]|10)$"
)


def validate_question_bank(
    path: str | Path = DEFAULT_QUESTION_FILE,
    *,
    exam_v2: bool = False,
    stress: bool = False,
) -> list[str]:
    question_path = Path(path)
    try:
        questions = _read_questions(question_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return [f"{question_path}: {error}"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    stage_order, expected_counts, expected_total = _validation_shape(exam_v2, stress)

    for index, question in enumerate(questions, start=1):
        label = _question_label(question, index)
        errors.extend(_validate_required_fields(question, label))
        errors.extend(_validate_non_empty_text(question, label))

        question_id = question.get("id")
        if question_id in seen_ids:
            errors.append(f"{label}: duplicate id {question_id!r}.")
        elif isinstance(question_id, str):
            seen_ids.add(question_id)

        errors.extend(_validate_type_rules(question, label))
        errors.extend(_validate_stage(question, label, stage_order))
        errors.extend(_validate_difficulty(question, label))

    errors.extend(_validate_stage_counts(questions, stage_order, expected_counts, expected_total))
    if stress:
        errors.extend(_validate_stress_structure(questions))

    return errors


def print_validation_result(
    errors: list[str],
    path: str | Path = DEFAULT_QUESTION_FILE,
) -> None:
    if not errors:
        print(f"Question bank is valid: {path}")
        return

    print(f"Question bank is invalid: {path}")
    for error in errors:
        print(f"- {error}")


def main() -> int:
    args = parse_args()
    errors = validate_question_bank(
        args.questions,
        exam_v2=args.exam_v2,
        stress=args.stress,
    )
    print_validation_result(errors, args.questions)
    return 1 if errors else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a quiz question bank.")
    parser.add_argument(
        "questions",
        nargs="?",
        type=Path,
        default=DEFAULT_QUESTION_FILE,
        help="Path to the question bank JSON file.",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--exam-v2",
        action="store_true",
        help="Validate the second exam-only mock question bank.",
    )
    mode_group.add_argument(
        "--stress",
        action="store_true",
        help="Validate the difficult timed mock exam question bank.",
    )
    return parser.parse_args(argv)


def _validation_shape(
    exam_v2: bool,
    stress: bool,
) -> tuple[list[str], dict[str, int], int]:
    if stress:
        return STRESS_STAGE_ORDER, STRESS_STAGE_COUNTS, STRESS_EXPECTED_TOTAL
    if exam_v2:
        return EXAM_V2_STAGE_ORDER, EXAM_V2_STAGE_COUNTS, EXAM_V2_EXPECTED_TOTAL
    return STAGE_ORDER, EXPECTED_STAGE_COUNTS, EXPECTED_TOTAL


def _read_questions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list):
        raise ValueError("question bank must be a list")

    return questions


def _question_label(question: Any, index: int) -> str:
    if isinstance(question, dict) and question.get("id"):
        return f"Question {question['id']!r}"
    return f"Question #{index}"


def _validate_required_fields(question: Any, label: str) -> list[str]:
    if not isinstance(question, dict):
        return [f"{label}: question must be an object."]

    missing = REQUIRED_FIELDS - question.keys()
    if not missing:
        return []

    fields = ", ".join(sorted(missing))
    return [f"{label}: missing required field(s): {fields}."]


def _validate_non_empty_text(question: Any, label: str) -> list[str]:
    if not isinstance(question, dict):
        return []

    errors: list[str] = []
    for field in ("prompt", "explanation"):
        value = question.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}: {field} must be a non-empty string.")
    return errors


def _validate_type_rules(question: Any, label: str) -> list[str]:
    if not isinstance(question, dict):
        return []

    errors: list[str] = []
    question_type = question.get("type")

    if question_type not in ALLOWED_TYPES:
        errors.append(f"{label}: invalid question type {question_type!r}.")
        return errors

    if question_type == "multiple_choice":
        if "options" not in question:
            errors.append(f"{label}: multiple_choice questions need options.")
        elif not isinstance(question["options"], list) or not question["options"]:
            errors.append(f"{label}: multiple_choice options must be a non-empty list.")

    if question_type in AUTO_CHECKED_TYPES and "correct_answer" not in question:
        errors.append(f"{label}: {question_type} questions need correct_answer.")

    if question_type == "multiple_choice" and "correct_answer" in question:
        options = question.get("options")
        if isinstance(options, list) and question["correct_answer"] not in options:
            errors.append(
                f"{label}: multiple_choice correct_answer must match one option."
            )

    if question_type == "true_false" and "correct_answer" in question:
        if not isinstance(question["correct_answer"], bool):
            errors.append(f"{label}: true_false correct_answer must be a boolean.")

    if question_type in OPEN_ANSWER_TYPES:
        if "oral_model_answer" not in question:
            errors.append(f"{label}: {question_type} questions need oral_model_answer.")
        if "grading_checklist" not in question:
            errors.append(f"{label}: {question_type} questions need grading_checklist.")
        else:
            errors.extend(_validate_grading_checklist(question, label))

    return errors


def _validate_grading_checklist(
    question: dict[str, Any],
    label: str,
) -> list[str]:
    grading_checklist = question["grading_checklist"]
    if not isinstance(grading_checklist, list) or not grading_checklist:
        return [f"{label}: grading_checklist must be a non-empty list of strings."]

    if not all(isinstance(item, str) and item for item in grading_checklist):
        return [f"{label}: grading_checklist must be a non-empty list of strings."]

    return []


def _validate_stage(question: Any, label: str, allowed_stages: list[str]) -> list[str]:
    if not isinstance(question, dict):
        return []

    stage = question.get("stage")
    if stage in allowed_stages:
        return []

    return [f"{label}: invalid stage {stage!r}."]


def _validate_difficulty(question: Any, label: str) -> list[str]:
    if not isinstance(question, dict):
        return []

    difficulty = question.get("difficulty")
    if isinstance(difficulty, int) and 1 <= difficulty <= 10:
        return []

    return [f"{label}: difficulty must be an integer from 1 to 10."]


def _validate_stage_counts(
    questions: list[dict[str, Any]],
    stage_order: list[str],
    expected_counts: dict[str, int],
    expected_total: int,
) -> list[str]:
    errors: list[str] = []

    if len(questions) != expected_total:
        errors.append(
            f"Question bank must contain exactly {expected_total} questions; "
            f"found {len(questions)}."
        )

    stage_counts = {
        stage: sum(
            1
            for question in questions
            if isinstance(question, dict) and question.get("stage") == stage
        )
        for stage in stage_order
    }

    for stage in stage_order:
        expected_count = expected_counts[stage]
        actual_count = stage_counts[stage]
        if actual_count != expected_count:
            errors.append(
                f"Stage {stage!r} must contain exactly {expected_count} questions; "
                f"found {actual_count}."
            )

    return errors


def _validate_stress_structure(questions: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    stages = [
        question.get("stage")
        for question in questions
        if isinstance(question, dict) and isinstance(question.get("stage"), str)
    ]
    unique_stages = set(stages)

    if len(unique_stages) != 30:
        errors.append(
            f"Stress bank must contain exactly 30 stages; found {len(unique_stages)}."
        )

    groups = {
        match.group(1)
        for stage in unique_stages
        if (match := STRESS_STAGE_PATTERN.match(stage))
    }
    if groups != set(STRESS_DIFFICULTY_GROUPS):
        found = ", ".join(sorted(groups)) or "none"
        errors.append(f"Stress bank must contain exactly 3 difficulty groups; found {found}.")

    for group in STRESS_DIFFICULTY_GROUPS:
        group_stages = [
            stage
            for stage in unique_stages
            if STRESS_STAGE_PATTERN.match(stage)
            and stage.startswith(f"stress_{group}_")
        ]
        if len(group_stages) != 10:
            errors.append(
                f"Stress difficulty group {group!r} must contain exactly 10 mocks; "
                f"found {len(group_stages)}."
            )

    for stage in unique_stages:
        if not STRESS_STAGE_PATTERN.match(stage):
            errors.append(f"Stress stage {stage!r} does not match the required pattern.")

    return errors


if __name__ == "__main__":
    raise SystemExit(main())
