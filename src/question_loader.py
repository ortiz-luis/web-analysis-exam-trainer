"""Question loading utilities for the terminal quiz trainer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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

AUTOMATIC_TYPES = {"multiple_choice", "true_false", "fill_blank", "predict_output"}
OPEN_ANSWER_TYPES = {"short_answer", "oral_explanation"}


def load_questions(path: str | Path) -> list[dict[str, Any]]:
    """Load questions from a JSON file."""
    question_path = Path(path)
    with question_path.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list):
        raise ValueError("Question file must contain a list of questions.")

    for question in questions:
        _validate_question(question)

    return questions


def _validate_question(question: Any) -> None:
    if not isinstance(question, dict):
        raise ValueError("Each question must be a JSON object.")

    missing_fields = REQUIRED_FIELDS - question.keys()
    if missing_fields:
        fields = ", ".join(sorted(missing_fields))
        raise ValueError(f"Question is missing required fields: {fields}")

    question_type = question["type"]

    if question_type in AUTOMATIC_TYPES and "correct_answer" not in question:
        raise ValueError("Automatically checkable questions need correct_answer.")

    if question_type in OPEN_ANSWER_TYPES:
        if "oral_model_answer" not in question:
            raise ValueError("Open-answer questions need oral_model_answer.")
        if "grading_checklist" not in question:
            raise ValueError("Open-answer questions need grading_checklist.")

    if question_type == "multiple_choice" and "options" not in question:
        raise ValueError("Multiple-choice questions need options.")
