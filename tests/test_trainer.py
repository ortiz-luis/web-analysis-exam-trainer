import unittest
from pathlib import Path

from src.trainer import QUESTION_FILE, parse_args


class TrainerArgumentTests(unittest.TestCase):
    def test_default_question_file(self) -> None:
        args = parse_args([])

        self.assertEqual(args.questions, QUESTION_FILE)

    def test_custom_question_file(self) -> None:
        args = parse_args(["--questions", "data/real_questions.json"])

        self.assertEqual(args.questions, Path("data/real_questions.json"))


if __name__ == "__main__":
    unittest.main()
