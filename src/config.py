from pathlib import Path

# Configuration en dur pour simplifier le déploiement
BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_RAW_CSV = BASE_DIR / "data" / "city_lifestyle_dataset.csv"
DEFAULT_CLEANED_CSV = BASE_DIR / "data" / "cleaned" / "city_lifestyle_cleaned.csv"
DEFAULT_RAW_CACHE_DIR = BASE_DIR / "data" / "raw"

# Configuration serveur
server = {
    "PORT": 5000,
}

# Chemin du CSV source
csv_path = str(DEFAULT_RAW_CSV)
