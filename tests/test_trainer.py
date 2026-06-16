import unittest
from pathlib import Path

from src.trainer import QUESTION_FILE, check_answer, parse_args


class TrainerArgumentTests(unittest.TestCase):
    def test_default_question_file(self) -> None:
        args = parse_args([])

        self.assertEqual(args.questions, QUESTION_FILE)

    def test_custom_question_file(self) -> None:
        args = parse_args(["--questions", "data/real_questions.json"])

        self.assertEqual(args.questions, Path("data/real_questions.json"))


class TrainerAnswerCheckingTests(unittest.TestCase):
    def test_multiple_choice_accepts_correct_option_number(self) -> None:
        question = multiple_choice_question()

        self.assertTrue(check_answer(question, "2"))

    def test_multiple_choice_accepts_exact_correct_answer_text(self) -> None:
        question = multiple_choice_question()

        self.assertTrue(check_answer(question, "moyenne = total / 3"))

    def test_multiple_choice_rejects_wrong_option_number(self) -> None:
        question = multiple_choice_question()

        self.assertFalse(check_answer(question, "1"))

    def test_true_false_accepts_vrai_for_true(self) -> None:
        question = {"type": "true_false", "correct_answer": True}

        self.assertTrue(check_answer(question, "vrai"))

    def test_true_false_accepts_faux_for_false(self) -> None:
        question = {"type": "true_false", "correct_answer": False}

        self.assertTrue(check_answer(question, "faux"))

    def test_fill_blank_ignores_surrounding_spaces(self) -> None:
        question = {"type": "fill_blank", "correct_answer": "zip"}

        self.assertTrue(check_answer(question, "  zip  "))


def multiple_choice_question() -> dict[str, object]:
    return {
        "type": "multiple_choice",
        "options": [
            "moyenne = total * 3",
            "moyenne = total / 3",
            "moyenne = total + 3",
        ],
        "correct_answer": "moyenne = total / 3",
    }


if __name__ == "__main__":
    unittest.main()
