#!/bin/bash

set -u

cd "$(dirname "$0")" || {
  echo "Impossible de trouver le dossier du projet."
  read -r -p "Appuyez sur Entrée pour fermer cette fenêtre..."
  exit 1
}

pause_on_error() {
  echo
  echo "Une erreur est survenue pendant le lancement du trainer."
  echo "Veuillez lire le message ci-dessus."
  read -r -p "Appuyez sur Entrée pour fermer cette fenêtre..."
  exit 1
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 est requis pour lancer Web Analysis Exam Trainer."
  echo
  if command -v brew >/dev/null 2>&1; then
    echo "Homebrew est disponible. Installation de Python avec Homebrew..."
    brew install python || pause_on_error
    echo
    echo "Python vient d'être installé. Fermez cette fenêtre puis relancez launch_web_trainer_mac.command."
  else
    echo "Homebrew n'est pas disponible."
    echo "Ouverture de la page officielle de téléchargement de Python pour macOS..."
    open "https://www.python.org/downloads/macos/"
    echo "Installez Python 3, puis relancez launch_web_trainer_mac.command."
  fi
  read -r -p "Appuyez sur Entrée pour fermer cette fenêtre..."
  exit 0
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Création de l'environnement virtuel local..."
  python3 -m venv .venv || pause_on_error
fi

echo "Mise à jour de pip..."
.venv/bin/python -m pip install --upgrade pip || pause_on_error

echo "Installation des dépendances..."
.venv/bin/python -m pip install -r requirements.txt || pause_on_error

echo "Lancement de Web Analysis Exam Trainer..."
.venv/bin/python -m streamlit run src/app_streamlit.py || pause_on_error
