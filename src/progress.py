"""Persistent progress tracking for quiz answers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_PROGRESS = {"answers": {}}

STAGE_ORDER = [
    "lesson_1_python_basics",
    "lesson_2_pandas_minimal",
    "lesson_3_html_bs4_scraping",
    "lesson_4_allocine_scraping",
    "integrated_practice",
    "exam_mock_01",
    "exam_mock_02",
    "exam_mock_03",
    "exam_mock_04",
    "exam_mock_05",
    "exam_mock_06",
    "exam_mock_07",
    "exam_mock_08",
    "exam_mock_09",
    "exam_mock_10",
]


class Progress:
    def __init__(self, path: str | Path = "progress.json") -> None:
        self.path = Path(path)
        self.data = self._load_or_create()

    def record_correct(self, question_id: str) -> None:
        self._record_answer(question_id, correct=True)

    def record_wrong(self, question_id: str) -> None:
        self._record_answer(question_id, correct=False)

    def was_answered_correctly(self, question_id: str) -> bool:
        answer = self.data["answers"].get(question_id)
        return bool(answer and answer.get("correct_count", 0) > 0)

    def count_correct_in_stage(self, questions: list[dict[str, Any]], stage: str) -> int:
        return sum(
            1
            for question in questions
            if question["stage"] == stage and self.was_answered_correctly(question["id"])
        )

    def is_stage_complete(self, questions: list[dict[str, Any]], stage: str) -> bool:
        stage_questions = get_stage_questions(questions, stage)
        return bool(stage_questions) and all(
            self.was_answered_correctly(question["id"]) for question in stage_questions
        )

    def current_unlocked_stage(self, questions: list[dict[str, Any]]) -> str | None:
        for stage in stages_with_questions(questions):
            if not self.is_stage_complete(questions, stage):
                return stage
        return None

    def all_stages_complete(self, questions: list[dict[str, Any]]) -> bool:
        return self.current_unlocked_stage(questions) is None

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2)
            file.write("\n")

    def _load_or_create(self) -> dict[str, Any]:
        if not self.path.exists():
            data = {"answers": {}}
            with self.path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
                file.write("\n")
            return data

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "answers" not in data or not isinstance(data["answers"], dict):
            raise ValueError("Progress file must contain an answers object.")

        return data

    def _record_answer(self, question_id: str, correct: bool) -> None:
        answer = self.data["answers"].setdefault(
            question_id,
            {
                "correct_count": 0,
                "wrong_count": 0,
                "last_answer_correct": None,
            },
        )

        if correct:
            answer["correct_count"] += 1
        else:
            answer["wrong_count"] += 1

        answer["last_answer_correct"] = correct
        self.save()


def stages_with_questions(questions: list[dict[str, Any]]) -> list[str]:
    stages_in_bank = {question["stage"] for question in questions}
    ordered_stages = [stage for stage in STAGE_ORDER if stage in stages_in_bank]
    unknown_stages = sorted(stages_in_bank - set(STAGE_ORDER))
    return ordered_stages + unknown_stages


def get_stage_questions(
    questions: list[dict[str, Any]],
    stage: str,
) -> list[dict[str, Any]]:
    return [question for question in questions if question["stage"] == stage]


def get_pending_stage_questions(
    questions: list[dict[str, Any]],
    progress: Progress,
    stage: str,
) -> list[dict[str, Any]]:
    return [
        question
        for question in get_stage_questions(questions, stage)
        if not progress.was_answered_correctly(question["id"])
    ]
