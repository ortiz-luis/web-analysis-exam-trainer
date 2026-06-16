"""Streamlit interface for the Web Analysis Exam Trainer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from src.progress import Progress, get_pending_stage_questions, get_stage_questions
from src.question_loader import load_questions
from src.trainer import AUTOMATIC_TYPES, OPEN_ANSWER_TYPES, check_answer, format_correct_answer


QUESTION_FILE = Path("data/questions_course.json")
PROGRESS_FILE = Path("streamlit_progress.json")


def main() -> None:
    st.set_page_config(page_title="Web Analysis Exam Trainer", page_icon="📚")
    st.title("Web Analysis Exam Trainer")

    questions = load_questions(QUESTION_FILE)
    progress = Progress(PROGRESS_FILE)

    if st.sidebar.button("Reset progress"):
        reset_progress()

    current_stage = progress.current_unlocked_stage(questions)
    if current_stage is None:
        st.success("Félicitations, tous les stages sont terminés.")
        return

    stage_questions = get_stage_questions(questions, current_stage)
    pending_questions = get_pending_stage_questions(questions, progress, current_stage)
    if not pending_questions:
        st.rerun()

    sync_question_queue(current_stage, pending_questions)
    question = next_question_from_queue(pending_questions)
    question_number = stage_questions.index(question) + 1
    correct_in_stage = progress.count_correct_in_stage(questions, current_stage)

    render_header(
        question,
        current_stage,
        question_number,
        correct_in_stage,
        len(stage_questions),
    )
    render_question(question)
    render_answer_controls(question, progress)


def reset_progress() -> None:
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
    st.session_state.clear()
    st.rerun()


def sync_question_queue(
    stage: str,
    pending_questions: list[dict[str, Any]],
) -> None:
    pending_ids = [question["id"] for question in pending_questions]
    if st.session_state.get("queue_stage") != stage:
        st.session_state["queue_stage"] = stage
        st.session_state["question_queue"] = pending_ids
        return

    current_queue = [
        question_id
        for question_id in st.session_state.get("question_queue", [])
        if question_id in pending_ids
    ]
    for question_id in pending_ids:
        if question_id not in current_queue:
            current_queue.append(question_id)
    st.session_state["question_queue"] = current_queue


def next_question_from_queue(
    pending_questions: list[dict[str, Any]],
) -> dict[str, Any]:
    queue = st.session_state["question_queue"]
    questions_by_id = {question["id"]: question for question in pending_questions}
    return questions_by_id[queue[0]]


def render_header(
    question: dict[str, Any],
    stage: str,
    question_number: int,
    correct_in_stage: int,
    total_in_stage: int,
) -> None:
    st.caption(
        f"Stage: {stage} | "
        f"Question: {question_number}/{total_in_stage} | "
        f"Correct: {correct_in_stage}/{total_in_stage} | "
        f"Type: {question['type']} | "
        f"Difficulty: {question['difficulty']}"
    )
    st.divider()


def render_question(question: dict[str, Any]) -> None:
    st.subheader(question["prompt"])
    if question.get("code"):
        st.code(str(question["code"]), language="python")


def render_answer_controls(question: dict[str, Any], progress: Progress) -> None:
    if question["type"] in AUTOMATIC_TYPES:
        render_automatic_question(question, progress)
        return

    if question["type"] in OPEN_ANSWER_TYPES:
        render_open_question(question, progress)
        return

    st.error(f"Unsupported question type: {question['type']}")


def render_automatic_question(question: dict[str, Any], progress: Progress) -> None:
    with st.form(f"answer_{question['id']}"):
        answer = automatic_answer_input(question)
        submitted = st.form_submit_button("Valider")

    if not submitted:
        return

    is_correct = check_answer(question, answer)
    if is_correct:
        progress.record_correct(question["id"])
        remove_current_question_from_queue()
        render_answer_feedback("correct", question)
    else:
        progress.record_wrong(question["id"])
        rotate_current_question_to_end()
        render_answer_feedback("wrong", question)

    wait_for_next_question()


def automatic_answer_input(question: dict[str, Any]) -> str:
    question_type = question["type"]
    if question_type == "multiple_choice":
        return st.radio(
            "Your answer (option number):",
            question["options"],
            key=f"input_{question['id']}",
        )

    if question_type == "true_false":
        return st.radio(
            "Votre réponse :",
            ["vrai", "faux"],
            key=f"input_{question['id']}",
        )

    return st.text_input("Votre réponse :", key=f"input_{question['id']}")


def render_open_question(question: dict[str, Any], progress: Progress) -> None:
    st.text_area("Votre réponse :", key=f"input_{question['id']}", height=160)
    st.markdown("### Réponse modèle")
    st.write(question["oral_model_answer"])
    st.markdown("### Checklist")
    for item in question["grading_checklist"]:
        st.write(f"- {item}")

    col_correct, col_wrong = st.columns(2)
    with col_correct:
        if st.button("Correct", key=f"correct_{question['id']}"):
            progress.record_correct(question["id"])
            remove_current_question_from_queue()
            render_answer_feedback("correct", question)
            wait_for_next_question()

    with col_wrong:
        if st.button("Incorrect", key=f"wrong_{question['id']}"):
            progress.record_wrong(question["id"])
            rotate_current_question_to_end()
            render_answer_feedback("wrong", question)
            wait_for_next_question()


def render_answer_feedback(result: str, question: dict[str, Any]) -> None:
    if result == "correct":
        st.success("✅ Correct.")
    else:
        st.error("❌ Wrong.")
        if question["type"] in AUTOMATIC_TYPES:
            st.write(f"Correct answer: {format_correct_answer(question)}")
    st.info(question["explanation"])


def wait_for_next_question() -> None:
    if st.button("Question suivante"):
        st.rerun()
    st.stop()


def remove_current_question_from_queue() -> None:
    queue = st.session_state.get("question_queue", [])
    if queue:
        st.session_state["question_queue"] = queue[1:]


def rotate_current_question_to_end() -> None:
    queue = st.session_state.get("question_queue", [])
    if queue:
        st.session_state["question_queue"] = queue[1:] + queue[:1]


if __name__ == "__main__":
    main()
