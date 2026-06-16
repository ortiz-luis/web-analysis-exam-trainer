"""Minimal terminal quiz trainer."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from src.progress import Progress
from src.question_loader import load_questions


QUESTION_FILE = Path("data/questions_sample.json")
AUTOMATIC_TYPES = {"multiple_choice", "true_false", "fill_blank", "predict_output"}


def main() -> None:
    questions = load_questions(QUESTION_FILE)
    progress = Progress()
    queue = deque(questions)
    repeated_wrong_ids: set[str] = set()

    print("Web Analysis Exam Trainer")
    print("Press Ctrl+C to exit.\n")

    try:
        while queue:
            question = queue.popleft()
            is_correct = ask_question(question)

            if is_correct:
                progress.record_correct(question["id"])
                print("Correct.\n")
            else:
                progress.record_wrong(question["id"])
                print("Wrong.\n")

                if question["id"] not in repeated_wrong_ids:
                    repeated_wrong_ids.add(question["id"])
                    queue.append(question)

            print(question["explanation"])
            print()
    except KeyboardInterrupt:
        print("\nProgress saved. See you next round.")


def ask_question(question: dict[str, Any]) -> bool:
    print_question(question)

    question_type = question["type"]
    if question_type == "oral_explanation":
        return ask_oral_question(question)

    if question_type in AUTOMATIC_TYPES:
        answer = input("Your answer: ").strip()
        return normalize_answer(answer) == normalize_answer(question["correct_answer"])

    raise ValueError(f"Unsupported question type: {question_type}")


def print_question(question: dict[str, Any]) -> None:
    print(f"[{question['type']}] {question['prompt']}")

    if question.get("code"):
        print()
        print(question["code"])
        print()

    if question.get("options"):
        for index, option in enumerate(question["options"], start=1):
            print(f"{index}. {option}")


def ask_oral_question(question: dict[str, Any]) -> bool:
    input("Press Enter when you have answered aloud.")
    print("\nModel answer:")
    print(question["oral_model_answer"])

    while True:
        grade = input("Self-grade as correct or wrong [c/w]: ").strip().lower()
        if grade in {"c", "correct"}:
            return True
        if grade in {"w", "wrong"}:
            return False
        print("Please enter c or w.")


def normalize_answer(answer: Any) -> str:
    if isinstance(answer, bool):
        return "true" if answer else "false"
    return str(answer).strip().lower()


if __name__ == "__main__":
    main()
