import os
from pathlib import Path

from dotenv import load_dotenv

# Charger le .env depuis le dossier parent
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_RAW_CSV = BASE_DIR / "data" / "city_lifestyle_dataset.csv"
DEFAULT_CLEANED_CSV = BASE_DIR / "data" / "cleaned" / "city_lifestyle_cleaned.csv"
DEFAULT_RAW_CACHE_DIR = BASE_DIR / "data" / "raw"

server = {
    "PORT": int(os.getenv("PORT", 5000)),
}

# Gerer le chemin du CSV de maniere flexible (local et Docker)
csv_path_env = os.getenv("CSV_PATH")
if csv_path_env:
    resolved_csv_path = Path(csv_path_env)
    if not resolved_csv_path.is_absolute():
        resolved_csv_path = (BASE_DIR / csv_path_env).resolve()
else:
    # Par défaut on privilégie le fichier nettoyé s'il existe
    resolved_csv_path = DEFAULT_CLEANED_CSV if DEFAULT_CLEANED_CSV.exists() else DEFAULT_RAW_CSV

csv_path = str(resolved_csv_path)
