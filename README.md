# Web Analysis Exam Trainer

This project will become a terminal-based adaptive quiz trainer.
Its goal is to help students prepare for a 20-minute oral exam in "Outils d'analyse du Web".
The question bank will be built only from the official course notebooks.
The trainer will focus on repeated practice, recall, and oral-style explanations.
Questions answered incorrectly will be scheduled again later.
Progress is saved locally in progress.json.
Questions unlock stage by stage as each available stage is completed.

## Commands

- `python -m src.validate_questions data/questions_course.json`
- `python -m src.validate_questions data/exam_mocks_v2.json --exam-v2`
- `python -m src.validate_questions data/exam_mocks_stress.json --stress`
- `python -m unittest discover`
- `python -m src.trainer --questions data/questions_course.json`
- `streamlit run src/app_streamlit.py`

## Exam mock batteries

The main course bank in `data/questions_course.json` contains the guided practice
questions and the first 10 exam mocks. The second exam-only battery is stored in
`data/exam_mocks_v2.json` with 20 additional five-question mocks designed to
avoid memorized answers. In Streamlit, `Examen blanc` exposes both Batterie V1
and Batterie V2.

## Examen blanc stress

`data/exam_mocks_stress.json` contains 150 exclusive harder questions based only
on the official course notebooks. The Streamlit mode `Examen blanc stress`
offers three levels: Difficile, Très difficile, and Extra difficile. Each level
contains 10 timed five-question mocks, with timer choices of disabled, 30, 45,
or 60 seconds per question.

## Double-click launcher

- Double-click `launch_web_trainer.bat`
- The first launch may take longer because dependencies are installed.
- The app opens in the browser.
- Close the terminal window to stop the app.

## Installer sur un Mac

- Copy or unzip the project folder on the Mac.
- Double-click `launch_web_trainer_mac.command`.
- The first launch may take longer because dependencies are installed.
- If macOS says the file cannot be opened because it is not executable, run once: `chmod +x launch_web_trainer_mac.command`
- If Python is missing, the launcher will try Homebrew or open the Python download page.
- Progress is local to each computer.

## Déploiement Streamlit Community Cloud

- Push project to GitHub.
- App entry point: `streamlit_app.py`
- Set environment variable `WEB_TRAINER_PROGRESS_MODE=cloud`
- Deploy.
- Share the app URL.
