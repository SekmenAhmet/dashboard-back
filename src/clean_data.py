"""
Module de nettoyage et préparation des données.
Traite les données brutes et génère des données nettoyées prêtes à l'analyse.
"""
import hashlib
from pathlib import Path

import pandas as pd


class DataCleaner:
    """Gestionnaire de nettoyage et validation des données."""

    def __init__(self) -> None:
        """Initialise le nettoyeur de données."""
        self.df: pd.DataFrame | None = None
        self.cleaning_report: dict = {}

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Charge les données depuis un fichier CSV.

        Args:
            file_path: Chemin du fichier CSV

        Returns:
            DataFrame pandas avec les données chargées
        """
        print(f"→ Chargement des données depuis: {file_path}")
        self.df = pd.read_csv(file_path)
        print(f"✓ {len(self.df)} lignes chargées")
        return self.df

    def remove_duplicates(self) -> int:
        """
        Supprime les doublons du dataset.

        Returns:
            Nombre de doublons supprimés
        """
        initial_count = len(self.df)
        self.df.drop_duplicates(subset=["city_name", "country"], keep="first", inplace=True)
        duplicates_removed = initial_count - len(self.df)

        if duplicates_removed > 0:
            print(f"✓ {duplicates_removed} doublons supprimés")
        else:
            print("✓ Aucun doublon trouvé")

        return duplicates_removed

    def handle_missing_values(self) -> dict:
        """
        Gère les valeurs manquantes dans le dataset.

        Returns:
            Dictionnaire avec les statistiques de valeurs manquantes
        """
        missing_stats = {}

        # Identifier les valeurs manquantes
        missing_counts = self.df.isnull().sum()
        columns_with_missing = missing_counts[missing_counts > 0]

        if len(columns_with_missing) == 0:
            print("✓ Aucune valeur manquante détectée")
            return missing_stats

        # Traiter chaque colonne avec des valeurs manquantes
        for col in columns_with_missing.index:
            missing_count = int(missing_counts[col])
            missing_stats[col] = missing_count

            # Pour les colonnes numériques, remplacer par la médiane
            if self.df[col].dtype in ["float64", "int64"]:
                median_value = self.df[col].median()
                self.df[col].fillna(median_value, inplace=True)
                print(f"✓ {missing_count} valeurs manquantes dans '{col}' remplacées par la médiane ({median_value:.2f})")

            # Pour les colonnes textuelles, remplacer par 'Unknown'
            else:
                self.df[col].fillna("Unknown", inplace=True)
                print(f"✓ {missing_count} valeurs manquantes dans '{col}' remplacées par 'Unknown'")

        return missing_stats

    def validate_numeric_ranges(self) -> dict:
        """
        Valide les plages de valeurs des colonnes numériques.

        Returns:
            Dictionnaire avec les valeurs aberrantes trouvées
        """
        outliers = {}

        # Définir les contraintes de validation
        validations = {
            "population_density": (0, 100000),
            "avg_income": (0, 200000),
            "internet_penetration": (0, 100),
            "avg_rent": (0, 50000),
            "air_quality_index": (0, 500),
            "public_transport_score": (0, 100),
            "happiness_score": (0, 10),
            "green_space_ratio": (0, 100),
        }

        for col, (min_val, max_val) in validations.items():
            if col in self.df.columns:
                # Identifier les valeurs hors limites
                out_of_range = self.df[(self.df[col] < min_val) | (self.df[col] > max_val)]

                if len(out_of_range) > 0:
                    outliers[col] = len(out_of_range)
                    print(f"⚠ {len(out_of_range)} valeurs hors limites dans '{col}' (attendu: {min_val}-{max_val})")

                    # Capper les valeurs aux limites
                    self.df[col] = self.df[col].clip(min_val, max_val)
                    print(f"✓ Valeurs normalisées dans la plage {min_val}-{max_val}")

        if not outliers:
            print("✓ Toutes les valeurs numériques sont dans les plages attendues")

        return outliers

    def convert_types(self) -> None:
        """Convertit les colonnes aux types appropriés."""
        numeric_columns = [
            "population_density",
            "avg_income",
            "internet_penetration",
            "avg_rent",
            "air_quality_index",
            "public_transport_score",
            "happiness_score",
            "green_space_ratio",
            "latitude",
            "longitude",
        ]

        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        print("✓ Types de données convertis")

    def _continent_box(self, continent: str) -> tuple[float, float, float, float]:
        """Retourne un bounding box réaliste (lat_min, lat_max, lon_min, lon_max) par continent."""
        boxes = {
            "Europe": (35.0, 70.0, -10.0, 40.0),
            "Asia": (5.0, 55.0, 60.0, 140.0),
            "North America": (25.0, 70.0, -130.0, -60.0),
            "South America": (-55.0, 15.0, -80.0, -35.0),
            "Africa": (-35.0, 35.0, -20.0, 50.0),
            "Oceania": (-50.0, 5.0, 110.0, 150.0),
        }
        return boxes.get(continent, (-55.0, 70.0, -130.0, 150.0))

    def _deterministic_point(self, seed: str, continent: str) -> tuple[float, float]:
        """Génère une paire lat/lon déterministe dans un bounding box de continent."""
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        frac_lat = int.from_bytes(digest[:8], "big") / float(1 << 64)
        frac_lon = int.from_bytes(digest[8:16], "big") / float(1 << 64)
        lat_min, lat_max, lon_min, lon_max = self._continent_box(continent)
        lat = lat_min + (lat_max - lat_min) * frac_lat
        lon = lon_min + (lon_max - lon_min) * frac_lon
        return lat, lon

    def ensure_geolocation(self) -> None:
        """Ajoute des coordonnées synthétiques si absentes pour permettre la cartographie."""
        if "latitude" not in self.df.columns or "longitude" not in self.df.columns:
            print("→ Ajout de coordonnées synthétiques (ancrées par continent)")
            coords = self.df.apply(
                lambda row: self._deterministic_point(f"{row['city_name']}-{row['country']}", row["country"]),
                axis=1,
                result_type="expand",
            )
            coords.columns = ["latitude", "longitude"]
            self.df[["latitude", "longitude"]] = coords
        else:
            print("✓ Coordonnées présentes dans le dataset")

    def generate_statistics(self) -> dict:
        """
        Génère des statistiques sur le dataset nettoyé.

        Returns:
            Dictionnaire avec les statistiques descriptives
        """
        stats = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "countries": len(self.df["country"].unique()),
            "cities": len(self.df["city_name"].unique()),
            "numeric_summary": self.df.describe().to_dict(),
        }

        return stats

    def save_cleaned_data(self, output_path: str) -> None:
        """
        Sauvegarde les données nettoyées.

        Args:
            output_path: Chemin du fichier de sortie
        """
        # Créer le répertoire si nécessaire
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Sauvegarder
        self.df.to_csv(output_path, index=False)
        print(f"✓ Données nettoyées sauvegardées dans: {output_path}")

    def clean(self, input_path: str, output_path: str) -> dict:
        """
        Exécute le pipeline complet de nettoyage.

        Args:
            input_path: Chemin du fichier source
            output_path: Chemin du fichier de sortie

        Returns:
            Rapport de nettoyage
        """
        print("\n" + "=" * 60)
        print("DÉBUT DU NETTOYAGE DES DONNÉES")
        print("=" * 60 + "\n")

        # Charger les données
        self.load_data(input_path)

        # Convertir les types
        self.convert_types()

        # Nettoyer
        duplicates = self.remove_duplicates()
        missing = self.handle_missing_values()
        outliers = self.validate_numeric_ranges()
        self.ensure_geolocation()

        # Générer les statistiques
        stats = self.generate_statistics()

        # Créer le rapport
        self.cleaning_report = {
            "duplicates_removed": duplicates,
            "missing_values": missing,
            "outliers_found": outliers,
            "final_statistics": stats,
        }

        # Sauvegarder
        self.save_cleaned_data(output_path)

        print("\n" + "=" * 60)
        print("NETTOYAGE TERMINÉ")
        print("=" * 60)
        print(f"✓ {stats['total_rows']} lignes | {stats['total_columns']} colonnes")
        print(f"✓ {stats['countries']} pays | {stats['cities']} villes\n")

        return self.cleaning_report


def main() -> None:
    """Point d'entrée principal pour le nettoyage des données."""
    # Configuration des chemins
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "data" / "city_lifestyle_dataset.csv"
    output_file = base_dir / "data" / "cleaned" / "city_lifestyle_cleaned.csv"

    # Créer et exécuter le nettoyeur
    cleaner = DataCleaner()

    try:
        report = cleaner.clean(str(input_file), str(output_file))
        print("\nRapport de nettoyage:")
        print(f"  - Doublons supprimés: {report['duplicates_removed']}")
        print(f"  - Valeurs manquantes traitées: {len(report['missing_values'])}")
        print(f"  - Colonnes avec valeurs aberrantes: {len(report['outliers_found'])}")

    except Exception as e:
        print(f"\n✗ Erreur lors du nettoyage: {e}")
        raise


if __name__ == "__main__":
    main()
