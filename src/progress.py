"""Persistent progress tracking for quiz answers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_PROGRESS = {"answers": {}}


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
