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
OPEN_ANSWER_TYPES = {"short_answer", "oral_explanation"}


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
            print("Wrong.")
            if question["type"] in AUTOMATIC_TYPES:
                print(f"Correct answer: {format_correct_answer(question)}")
            print()

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
    if question_type in OPEN_ANSWER_TYPES:
        return ask_oral_question(question)

    if question_type in AUTOMATIC_TYPES:
        prompt = (
            "Your answer (option number): "
            if question_type == "multiple_choice"
            else "Your answer: "
        )
        return check_answer(question, input(prompt))

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

    if question.get("grading_checklist"):
        print("\nGrading checklist:")
        for item in question["grading_checklist"]:
            print(f"- {item}")

    while True:
        grade = input("Self-grade as correct or wrong [c/w]: ").strip().lower()
        if grade in {"c", "correct"}:
            return True
        if grade in {"w", "wrong"}:
            return False
        print("Please enter c or w.")


def check_answer(question: dict[str, Any], raw_answer: str) -> bool:
    question_type = question["type"]

    if question_type == "multiple_choice":
        selected_answer = answer_to_option_text(question, raw_answer)
        return selected_answer == str(question["correct_answer"]).strip()

    if question_type == "true_false":
        user_answer = parse_bool_answer(raw_answer)
        correct_answer = bool(question["correct_answer"])
        return user_answer is not None and user_answer == correct_answer

    if question_type in {"fill_blank", "predict_output"}:
        return raw_answer.strip() == str(question["correct_answer"]).strip()

    raise ValueError(f"Unsupported automatically checked type: {question_type}")


def answer_to_option_text(question: dict[str, Any], raw_answer: str) -> str:
    answer = raw_answer.strip()
    if answer.isdigit():
        option_index = int(answer) - 1
        options = question.get("options", [])
        if 0 <= option_index < len(options):
            return str(options[option_index]).strip()
    return answer


def parse_bool_answer(raw_answer: str) -> bool | None:
    normalized = raw_answer.strip().lower()
    if normalized in {"true", "t", "vrai", "v", "yes", "y"}:
        return True
    if normalized in {"false", "f", "faux", "no", "n"}:
        return False
    return None


def format_correct_answer(question: dict[str, Any]) -> str:
    correct_answer = question["correct_answer"]
    if isinstance(correct_answer, bool):
        return "true" if correct_answer else "false"
    return str(correct_answer)


if __name__ == "__main__":
    main()
