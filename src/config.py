import os

from dotenv import load_dotenv

# Charger le .env depuis le dossier parent
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

server = {
    "PORT": os.getenv("PORT", 5000),
}

# Gerer le chemin du CSV de maniere flexible (local et Docker)
csv_path = os.getenv("CSV_PATH")
if csv_path and not os.path.isabs(csv_path):
    # Si le chemin est relatif, le resoudre depuis le dossier src
    csv_path = os.path.join(os.path.dirname(__file__), "..", csv_path)
    csv_path = os.path.normpath(csv_path)
