"""Streamlit interface for the Web Analysis Exam Trainer."""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.progress import Progress, STAGE_ORDER, get_pending_stage_questions, get_stage_questions
from src.question_loader import load_questions
from src.trainer import AUTOMATIC_TYPES, OPEN_ANSWER_TYPES, check_answer, format_correct_answer


QUESTION_FILE = Path("data/questions_course.json")
PROGRESS_FILE = Path("streamlit_progress.json")
GUIDED_MODE = "Parcours guidé"
STAGE_MODE = "Pratique par étape"
RANDOM_MODE = "Série aléatoire"
MOCK_MODE = "Examen blanc"
MODES = [GUIDED_MODE, STAGE_MODE, RANDOM_MODE, MOCK_MODE]
MOCK_STAGES = [f"exam_mock_{index:02d}" for index in range(1, 11)]


def main() -> None:
    st.set_page_config(page_title="Web Analysis Exam Trainer")
    st.title("Web Analysis Exam Trainer")

    questions = load_questions(QUESTION_FILE)
    progress = Progress(PROGRESS_FILE)
    questions_by_id = {question["id"]: question for question in questions}

    controls = render_sidebar(questions, progress)
    if controls["reset_progress"]:
        reset_progress()

    context = build_context(questions, progress, controls)
    st.caption(context["label"])

    if controls["restart_session"] or should_start_session(context["key"]):
        start_session(context)

    if controls["new_random_series"] and controls["mode"] == RANDOM_MODE:
        start_session(context)

    render_session_summary_button()

    if st.session_state.get("session_finished"):
        render_session_grade()
        return

    queue = st.session_state.get("question_queue", [])
    if not queue:
        render_empty_session(context)
        return

    question = questions_by_id[queue[0]]
    render_header(question, context)
    render_question(question)
    render_answer_controls(question, progress, context)


def render_sidebar(questions: list[dict[str, Any]], progress: Progress) -> dict[str, Any]:
    st.sidebar.title("Mode de pratique")
    mode = st.sidebar.radio("Choisir un mode", MODES)

    available_stages = [stage for stage in STAGE_ORDER if get_stage_questions(questions, stage)]
    selected_stage = st.sidebar.selectbox("Étape", available_stages)
    random_count = st.sidebar.selectbox("Nombre de questions", [5, 10, 20], index=1)
    selected_mock = st.sidebar.selectbox("Examen blanc", MOCK_STAGES)

    new_random_series = st.sidebar.button("Nouvelle série aléatoire")
    restart_session = st.sidebar.button("Démarrer / redémarrer la session")
    reset_progress_button = st.sidebar.button("Reset progress")

    st.sidebar.divider()
    current_stage = progress.current_unlocked_stage(questions)
    st.sidebar.write(f"Stage guidé actuel : {current_stage or 'terminé'}")

    return {
        "mode": mode,
        "selected_stage": selected_stage,
        "random_count": int(random_count),
        "selected_mock": selected_mock,
        "new_random_series": new_random_series,
        "restart_session": restart_session,
        "reset_progress": reset_progress_button,
    }


def reset_progress() -> None:
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
    st.session_state.clear()
    st.rerun()


def build_context(
    questions: list[dict[str, Any]],
    progress: Progress,
    controls: dict[str, Any],
) -> dict[str, Any]:
    mode = controls["mode"]

    if mode == GUIDED_MODE:
        current_stage = progress.current_unlocked_stage(questions)
        if current_stage is None:
            return {
                "key": f"{GUIDED_MODE}:complete",
                "mode": mode,
                "label": "Mode actuel : Parcours guidé | Tous les stages sont terminés",
                "question_ids": [],
                "repeat_wrong": True,
                "auto_finish": False,
            }
        pending = get_pending_stage_questions(questions, progress, current_stage)
        return {
            "key": f"{GUIDED_MODE}:{current_stage}",
            "mode": mode,
            "label": f"Mode actuel : {mode} | Stage : {current_stage}",
            "question_ids": [question["id"] for question in pending],
            "repeat_wrong": True,
            "auto_finish": False,
        }

    if mode == STAGE_MODE:
        stage = controls["selected_stage"]
        stage_questions = get_stage_questions(questions, stage)
        pending = get_pending_stage_questions(questions, progress, stage)
        active_questions = pending or stage_questions
        return {
            "key": f"{STAGE_MODE}:{stage}",
            "mode": mode,
            "label": f"Mode actuel : {mode} | Étape : {stage}",
            "question_ids": [question["id"] for question in active_questions],
            "repeat_wrong": True,
            "auto_finish": False,
        }

    if mode == RANDOM_MODE:
        count = controls["random_count"]
        return {
            "key": f"{RANDOM_MODE}:{count}",
            "mode": mode,
            "label": f"Mode actuel : {mode} | Nombre : {count}",
            "question_ids": random_question_ids(questions, progress, count),
            "repeat_wrong": False,
            "auto_finish": True,
        }

    mock_stage = controls["selected_mock"]
    mock_questions = get_stage_questions(questions, mock_stage)
    return {
        "key": f"{MOCK_MODE}:{mock_stage}",
        "mode": mode,
        "label": f"Mode actuel : {mode} | Examen : {mock_stage}",
        "question_ids": [question["id"] for question in mock_questions],
        "repeat_wrong": False,
        "auto_finish": True,
    }


def random_question_ids(
    questions: list[dict[str, Any]],
    progress: Progress,
    count: int,
) -> list[str]:
    incomplete = [
        question
        for question in questions
        if not progress.was_answered_correctly(question["id"])
    ]
    pool = incomplete if len(incomplete) >= count else questions
    selected = random.sample(pool, min(count, len(pool)))
    return [question["id"] for question in selected]


def should_start_session(context_key: str) -> bool:
    return st.session_state.get("session_context") != context_key


def start_session(context: dict[str, Any]) -> None:
    st.session_state["session_context"] = context["key"]
    st.session_state["session_mode"] = context["mode"]
    st.session_state["session_label"] = context["label"]
    st.session_state["question_queue"] = list(context["question_ids"])
    st.session_state["repeat_wrong"] = context["repeat_wrong"]
    st.session_state["auto_finish"] = context["auto_finish"]
    st.session_state["attempted_questions"] = 0
    st.session_state["correct_answers"] = 0
    st.session_state["incorrect_answers"] = 0
    st.session_state["session_finished"] = False


def render_session_summary_button() -> None:
    if st.button("Terminer la session et voir la note"):
        st.session_state["session_finished"] = True
        st.rerun()


def render_empty_session(context: dict[str, Any]) -> None:
    if context["key"] == f"{GUIDED_MODE}:complete":
        st.success("Félicitations, tous les stages sont terminés.")
    elif st.session_state.get("auto_finish"):
        st.session_state["session_finished"] = True
        st.rerun()
    else:
        st.info("Aucune question disponible pour cette session.")
        render_session_grade()


def render_session_grade() -> None:
    attempted = st.session_state.get("attempted_questions", 0)
    correct = st.session_state.get("correct_answers", 0)
    incorrect = st.session_state.get("incorrect_answers", 0)

    if attempted == 0:
        st.info("Aucune question répondue dans cette session.")
        return

    score = round(20 * correct / attempted, 1)
    percentage = round(100 * correct / attempted, 1)
    st.subheader("Bilan de session")
    st.write(f"Nombre de questions répondues : {attempted}")
    st.write(f"Nombre de réponses correctes : {correct}")
    st.write(f"Nombre de réponses incorrectes : {incorrect}")
    st.write(f"Note finale sur 20 : {score}")
    st.write(f"Percentage score : {percentage}%")


def render_header(question: dict[str, Any], context: dict[str, Any]) -> None:
    queue = st.session_state.get("question_queue", [])
    total = len(queue) + st.session_state.get("attempted_questions", 0)
    current_index = st.session_state.get("attempted_questions", 0) + 1
    st.caption(
        f"{context['label']} | "
        f"Question : {current_index}/{total} | "
        f"Type : {question['type']} | "
        f"Difficulté : {question['difficulty']}"
    )
    st.divider()


def render_question(question: dict[str, Any]) -> None:
    st.subheader(question["prompt"])
    if question.get("code"):
        st.code(str(question["code"]), language="python")


def render_answer_controls(
    question: dict[str, Any],
    progress: Progress,
    context: dict[str, Any],
) -> None:
    if question["type"] in AUTOMATIC_TYPES:
        render_automatic_question(question, progress, context)
        return

    if question["type"] in OPEN_ANSWER_TYPES:
        render_open_question(question, progress, context)
        return

    st.error(f"Unsupported question type: {question['type']}")


def render_automatic_question(
    question: dict[str, Any],
    progress: Progress,
    context: dict[str, Any],
) -> None:
    with st.form(f"answer_{question['id']}"):
        answer = automatic_answer_input(question)
        submitted = st.form_submit_button("Valider")

    if not submitted:
        return

    is_correct = check_answer(question, answer)
    record_answer(question, progress, is_correct)
    render_answer_feedback("correct" if is_correct else "wrong", question)
    advance_queue(is_correct)
    finish_if_needed(context)
    wait_for_next_question()


def automatic_answer_input(question: dict[str, Any]) -> str:
    question_type = question["type"]
    if question_type == "multiple_choice":
        return st.radio(
            "Your answer (option number):",
            question["options"],
            key=f"input_{question['id']}_{st.session_state.get('session_context')}",
        )

    if question_type == "true_false":
        return st.radio(
            "Votre réponse :",
            ["vrai", "faux"],
            key=f"input_{question['id']}_{st.session_state.get('session_context')}",
        )

    return st.text_input(
        "Votre réponse :",
        key=f"input_{question['id']}_{st.session_state.get('session_context')}",
    )


def render_open_question(
    question: dict[str, Any],
    progress: Progress,
    context: dict[str, Any],
) -> None:
    st.text_area(
        "Votre réponse :",
        key=f"input_{question['id']}_{st.session_state.get('session_context')}",
        height=160,
    )
    st.markdown("### Réponse modèle")
    st.write(question["oral_model_answer"])
    st.markdown("### Checklist")
    for item in question["grading_checklist"]:
        st.write(f"- {item}")

    col_correct, col_wrong = st.columns(2)
    with col_correct:
        if st.button("Correct", key=f"correct_{question['id']}"):
            record_answer(question, progress, True)
            render_answer_feedback("correct", question)
            advance_queue(True)
            finish_if_needed(context)
            wait_for_next_question()

    with col_wrong:
        if st.button("Incorrect", key=f"wrong_{question['id']}"):
            record_answer(question, progress, False)
            render_answer_feedback("wrong", question)
            advance_queue(False)
            finish_if_needed(context)
            wait_for_next_question()


def record_answer(question: dict[str, Any], progress: Progress, is_correct: bool) -> None:
    if is_correct:
        progress.record_correct(question["id"])
        st.session_state["correct_answers"] += 1
    else:
        progress.record_wrong(question["id"])
        st.session_state["incorrect_answers"] += 1
    st.session_state["attempted_questions"] += 1


def advance_queue(is_correct: bool) -> None:
    if is_correct or not st.session_state.get("repeat_wrong"):
        remove_current_question_from_queue()
    else:
        rotate_current_question_to_end()


def finish_if_needed(context: dict[str, Any]) -> None:
    if context["auto_finish"] and not st.session_state.get("question_queue"):
        st.session_state["session_finished"] = True


def render_answer_feedback(result: str, question: dict[str, Any]) -> None:
    if result == "correct":
        st.success("✅ Correct.")
    else:
        st.error("❌ Wrong.")
        if question["type"] in AUTOMATIC_TYPES:
            st.write(f"Correct answer: {format_correct_answer(question)}")
    st.info(question["explanation"])


def wait_for_next_question() -> None:
    label = "Voir la note" if st.session_state.get("session_finished") else "Question suivante"
    if st.button(label):
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
