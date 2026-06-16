"""Minimal terminal quiz trainer."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Any

from src.progress import (
    Progress,
    get_pending_stage_questions,
    get_stage_questions,
)
from src.question_loader import load_questions


QUESTION_FILE = Path("data/questions_sample.json")
AUTOMATIC_TYPES = {"multiple_choice", "true_false", "fill_blank", "predict_output"}


def main() -> None:
    args = parse_args()
    questions = load_questions(args.questions)
    progress = Progress()

    print("Web Analysis Exam Trainer")
    print("Press Ctrl+C to exit.\n")

    try:
        run_training_loop(questions, progress)
    except KeyboardInterrupt:
        print("\nProgress saved. See you next round.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the terminal quiz trainer.")
    parser.add_argument(
        "--questions",
        type=Path,
        default=QUESTION_FILE,
        help="Path to the question bank JSON file.",
    )
    return parser.parse_args(argv)


def run_training_loop(questions: list[dict[str, Any]], progress: Progress) -> None:
    while True:
        current_stage = progress.current_unlocked_stage(questions)
        if current_stage is None:
            print("Congratulations! All available stages are complete.")
            return

        ask_current_stage(questions, progress, current_stage)


def ask_current_stage(
    questions: list[dict[str, Any]],
    progress: Progress,
    stage: str,
) -> None:
    queue = deque(get_pending_stage_questions(questions, progress, stage))
    repeated_wrong_ids: set[str] = set()
    stage_questions = get_stage_questions(questions, stage)
    total_in_stage = len(stage_questions)

    while queue and not progress.is_stage_complete(questions, stage):
        question = queue.popleft()
        correct_in_stage = progress.count_correct_in_stage(questions, stage)
        question_number = stage_questions.index(question) + 1

        is_correct = ask_question(
            question,
            stage=stage,
            question_number=question_number,
            correct_in_stage=correct_in_stage,
            total_in_stage=total_in_stage,
        )

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


def ask_question(
    question: dict[str, Any],
    stage: str,
    question_number: int,
    correct_in_stage: int,
    total_in_stage: int,
) -> bool:
    print_question(question, stage, question_number, correct_in_stage, total_in_stage)

    question_type = question["type"]
    if question_type == "oral_explanation":
        return ask_oral_question(question)

    if question_type in AUTOMATIC_TYPES:
        answer = input("Your answer: ").strip()
        return normalize_answer(answer) == normalize_answer(question["correct_answer"])

    raise ValueError(f"Unsupported question type: {question_type}")


def print_question(
    question: dict[str, Any],
    stage: str,
    question_number: int,
    correct_in_stage: int,
    total_in_stage: int,
) -> None:
    print(f"Stage: {stage}")
    print(
        f"Question {question_number}/{total_in_stage} "
        f"- Correct in stage: {correct_in_stage}/{total_in_stage}"
    )
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
