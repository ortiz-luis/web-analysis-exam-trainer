# Web Analysis Exam Trainer

This project will become a terminal-based adaptive quiz trainer.
Its goal is to help students prepare for a 20-minute oral exam in "Outils d'analyse du Web".
The question bank will be built only from the official course notebooks.
The trainer will focus on repeated practice, recall, and oral-style explanations.
Questions answered incorrectly will be scheduled again later.
Progress is saved locally in progress.json.
Questions unlock stage by stage as each available stage is completed.

## Commands

- `python -m src.trainer`
- `python -m src.trainer --questions data/questions_sample.json`
- `python -m src.validate_questions`
- `python -m src.validate_questions data/questions_sample.json`
- `python -m unittest discover`
