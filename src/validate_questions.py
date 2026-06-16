"""Validate quiz question banks."""

from __future__ import annotations

import json
import sys
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

AUTO_CHECKED_TYPES = {"true_false", "fill_blank", "predict_output"}


def validate_question_bank(path: str | Path = DEFAULT_QUESTION_FILE) -> list[str]:
    question_path = Path(path)
    try:
        questions = _read_questions(question_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return [f"{question_path}: {error}"]

    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, question in enumerate(questions, start=1):
        label = _question_label(question, index)
        errors.extend(_validate_required_fields(question, label))

        question_id = question.get("id")
        if question_id in seen_ids:
            errors.append(f"{label}: duplicate id {question_id!r}.")
        elif isinstance(question_id, str):
            seen_ids.add(question_id)

        errors.extend(_validate_type_rules(question, label))
        errors.extend(_validate_stage(question, label))
        errors.extend(_validate_difficulty(question, label))

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
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_QUESTION_FILE
    errors = validate_question_bank(path)
    print_validation_result(errors, path)
    return 1 if errors else 0


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
        if "correct_answer" not in question:
            errors.append(f"{label}: multiple_choice questions need correct_answer.")

    if question_type in AUTO_CHECKED_TYPES and "correct_answer" not in question:
        errors.append(f"{label}: {question_type} questions need correct_answer.")

    if question_type == "oral_explanation" and "oral_model_answer" not in question:
        errors.append(f"{label}: oral_explanation questions need oral_model_answer.")

    return errors


def _validate_stage(question: Any, label: str) -> list[str]:
    if not isinstance(question, dict):
        return []

    stage = question.get("stage")
    if stage in STAGE_ORDER:
        return []

    return [f"{label}: invalid stage {stage!r}."]


def _validate_difficulty(question: Any, label: str) -> list[str]:
    if not isinstance(question, dict):
        return []

    difficulty = question.get("difficulty")
    if isinstance(difficulty, int) and 1 <= difficulty <= 10:
        return []

    return [f"{label}: difficulty must be an integer from 1 to 10."]


if __name__ == "__main__":
    raise SystemExit(main())
