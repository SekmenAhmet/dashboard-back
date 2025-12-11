"""
Module de récupération des données.
Gère le téléchargement et la mise en cache des données du dataset.
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path


class DataRetriever:
    """Gestionnaire de récupération et mise en cache des données."""

    def __init__(self, raw_data_dir: str = "../data/raw", cache_duration_hours: int = 24):
        """
        Initialise le récupérateur de données.

        Args:
            raw_data_dir: Répertoire de stockage des données brutes
            cache_duration_hours: Durée de validité du cache en heures
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def _is_cache_valid(self, file_path: Path) -> bool:
        """
        Vérifie si le cache est encore valide.

        Args:
            file_path: Chemin du fichier à vérifier

        Returns:
            True si le cache est valide, False sinon
        """
        if not file_path.exists():
            return False

        file_modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        return datetime.now() - file_modified_time < self.cache_duration

    def get_data(self, source_path: str, force_refresh: bool = False) -> str:
        """
        Récupère les données depuis la source et les met en cache.

        Args:
            source_path: Chemin de la source de données
            force_refresh: Force le rafraîchissement même si le cache est valide

        Returns:
            Chemin du fichier de données dans le cache
        """
        filename = Path(source_path).name
        cached_file = self.raw_data_dir / filename

        # Vérifier si le cache est valide
        if not force_refresh and self._is_cache_valid(cached_file):
            print(f"✓ Utilisation du cache: {cached_file}")
            return str(cached_file)

        # Copier les données vers le cache
        print(f"→ Récupération des données depuis: {source_path}")

        if os.path.exists(source_path):
            shutil.copy2(source_path, cached_file)
            print(f"✓ Données sauvegardées dans: {cached_file}")
        else:
            raise FileNotFoundError(f"Source de données introuvable: {source_path}")

        return str(cached_file)

    def clear_cache(self) -> None:
        """Supprime tous les fichiers du cache."""
        for file in self.raw_data_dir.glob("*"):
            if file.is_file():
                file.unlink()
                print(f"✓ Cache supprimé: {file}")


def main():
    """Point d'entrée principal pour la récupération des données."""
    # Configuration
    data_source = os.path.join(os.path.dirname(__file__), "..", "data", "city_lifestyle_dataset.csv")

    # Initialiser le récupérateur
    retriever = DataRetriever(
        raw_data_dir=os.path.join(os.path.dirname(__file__), "..", "data", "raw"),
        cache_duration_hours=24
    )

    # Récupérer les données
    try:
        cached_path = retriever.get_data(data_source)
        print(f"\n✓ Données disponibles: {cached_path}")
    except Exception as e:
        print(f"✗ Erreur lors de la récupération: {e}")
        raise


if __name__ == "__main__":
    main()
