from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_RAW_CSV = BASE_DIR / "data" / "city_lifestyle_dataset.csv"
DEFAULT_CLEANED_CSV = BASE_DIR / "data" / "cleaned" / "city_lifestyle_cleaned.csv"
DEFAULT_RAW_CACHE_DIR = BASE_DIR / "data" / "raw"

server = {
    "PORT": 5000,
}

csv_path = str(DEFAULT_RAW_CSV)