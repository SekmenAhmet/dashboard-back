"""
Module de traitement et analyse des données City Lifestyle.
Fournit des fonctionnalités d'analyse statistique et de visualisation.
"""
import hashlib
from typing import Any

import pandas as pd


class CityLifestyleDataProcessor:
    """Processeur de données pour l'analyse du style de vie urbain."""

    def __init__(self, csv_path: str) -> None:
        """
        Initialise le processeur avec les données du CSV.

        Args:
            csv_path: Chemin du fichier CSV contenant les données
        """
        self.df = pd.read_csv(csv_path)
        self._preprocess_data()

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

    def _ensure_geolocation(self) -> None:
        """Ajoute lat/lon synthétiques si le dataset n'en dispose pas."""
        if "latitude" not in self.df.columns or "longitude" not in self.df.columns:
            coords = self.df.apply(
                lambda row: self._deterministic_point(f"{row['city_name']}-{row['country']}", row["country"]),
                axis=1,
                result_type="expand",
            )
            coords.columns = ["latitude", "longitude"]
            self.df[["latitude", "longitude"]] = coords

    def _preprocess_data(self) -> None:
        """Nettoie et prepare les donnees."""
        self._ensure_geolocation()
        numeric_cols = [
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
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

    def get_overview_stats(self) -> dict[str, Any]:
        """
        Calcule les statistiques générales du dataset.

        Returns:
            Dictionnaire contenant les statistiques globales
        """
        return {
            "total_cities": len(self.df),
            "countries": list(self.df["country"].unique()),
            "avg_population_density": float(self.df["population_density"].mean()),
            "avg_income": float(self.df["avg_income"].mean()),
            "avg_happiness": float(self.df["happiness_score"].mean()),
            "income_range": {
                "min": float(self.df["avg_income"].min()),
                "max": float(self.df["avg_income"].max())
            },
            "happiness_range": {
                "min": float(self.df["happiness_score"].min()),
                "max": float(self.df["happiness_score"].max())
            },
            "avg_air_quality": float(self.df["air_quality_index"].mean()),
            "avg_internet_penetration": float(self.df["internet_penetration"].mean())
        }

    def get_cities_by_country(self) -> dict[str, list]:
        """
        Calcule la répartition des villes par pays.

        Returns:
            Dictionnaire avec les statistiques par pays
        """
        country_stats = self.df.groupby("country").agg({
            "city_name": "count",
            "population_density": "mean",
            "avg_income": "mean",
            "happiness_score": "mean"
        }).reset_index()
        country_stats.columns = ["country", "city_count", "avg_population_density", "avg_income", "avg_happiness"]

        return {
            "countries": country_stats["country"].tolist(),
            "city_count": country_stats["city_count"].tolist(),
            "avg_population_density": country_stats["avg_population_density"].tolist(),
            "avg_income": country_stats["avg_income"].tolist(),
            "avg_happiness": country_stats["avg_happiness"].tolist()
        }

    def get_top_cities(self, metric: str = "happiness_score", top_n: int = 10) -> dict[str, list]:
        """
        Récupère les N meilleures villes selon une métrique.

        Args:
            metric: Métrique à utiliser pour le classement
            top_n: Nombre de villes à retourner

        Returns:
            Dictionnaire avec les données des meilleures villes
        """
        columns = ["city_name", "country", metric, "avg_income", "happiness_score"]
        columns = list(dict.fromkeys(columns))

        if metric == "air_quality_index":
            top_cities = self.df.nsmallest(top_n, metric)[columns].copy()
        else:
            top_cities = self.df.nlargest(top_n, metric)[columns].copy()
        metric_values = top_cities[metric].to_numpy().ravel().tolist()

        return {
            "cities": top_cities["city_name"].tolist(),
            "countries": top_cities["country"].tolist(),
            "metric_values": metric_values,
            "avg_income": top_cities["avg_income"].tolist(),
            "happiness_score": top_cities["happiness_score"].tolist(),
        }

    def get_income_analysis(self) -> dict[str, Any]:
        """
        Analyse détaillée des revenus par pays.

        Returns:
            Dictionnaire avec les statistiques de revenus
        """
        income_by_country = self.df.groupby("country")["avg_income"].agg([
            "mean", "median", "std", "min", "max"
        ]).reset_index()

        return {
            "by_country": {
                "countries": income_by_country["country"].tolist(),
                "mean": income_by_country["mean"].tolist(),
                "median": income_by_country["median"].tolist(),
                "std": income_by_country["std"].tolist(),
                "min": income_by_country["min"].tolist(),
                "max": income_by_country["max"].tolist()
            }
        }

    def get_geographic_data(self) -> dict[str, list]:
        """
        Récupère les données géographiques pour visualisation sur carte.

        Returns:
            Dictionnaire avec les données géographiques des villes
        """
        geo_data = self.df[
            [
                "city_name",
                "country",
                "population_density",
                "avg_income",
                "internet_penetration",
                "avg_rent",
                "happiness_score",
                "air_quality_index",
                "public_transport_score",
                "green_space_ratio",
                "latitude",
                "longitude",
            ]
        ].copy()

        return {
            "cities": geo_data["city_name"].tolist(),
            "countries": geo_data["country"].tolist(),
            "population_density": geo_data["population_density"].tolist(),
            "avg_income": geo_data["avg_income"].tolist(),
            "internet_penetration": geo_data["internet_penetration"].tolist(),
            "avg_rent": geo_data["avg_rent"].tolist(),
            "happiness_score": geo_data["happiness_score"].tolist(),
            "air_quality_index": geo_data["air_quality_index"].tolist(),
            "public_transport_score": geo_data["public_transport_score"].tolist(),
            "green_space_ratio": geo_data["green_space_ratio"].tolist(),
            "latitude": geo_data["latitude"].tolist(),
            "longitude": geo_data["longitude"].tolist(),
        }

    def get_correlations(self) -> dict[str, Any]:
        """
        Calcule les corrélations entre variables numériques.

        Returns:
            Dictionnaire avec la matrice de corrélation
        """
        numeric_cols = ["population_density", "avg_income", "internet_penetration", "avg_rent",
                       "air_quality_index", "public_transport_score", "happiness_score", "green_space_ratio"]
        corr_matrix = self.df[numeric_cols].corr()

        return {
            "columns": numeric_cols,
            "correlation_matrix": corr_matrix.values.tolist()
        }

    def get_quality_of_life_analysis(self) -> dict[str, dict]:
        """
        Analyse les facteurs de qualité de vie.

        Returns:
            Dictionnaire avec les statistiques de qualité de vie
        """
        return {
            "air_quality_distribution": self.df["air_quality_index"].describe().to_dict(),
            "transport_quality": self.df["public_transport_score"].describe().to_dict(),
            "green_spaces": self.df["green_space_ratio"].describe().to_dict(),
            "internet_access": self.df["internet_penetration"].describe().to_dict()
        }

    def get_happiness_analysis(self) -> dict[str, Any]:
        """
        Analyse le bonheur par pays et facteurs.

        Returns:
            Dictionnaire avec les statistiques de bonheur
        """
        happiness_by_country = self.df.groupby("country").agg({
            "happiness_score": ["mean", "min", "max", "std"],
            "city_name": "count"
        }).reset_index()
        happiness_by_country.columns = ["country", "avg_happiness", "min_happiness", "max_happiness", "std_happiness", "city_count"]

        return {
            "by_country": {
                "countries": happiness_by_country["country"].tolist(),
                "avg_happiness": happiness_by_country["avg_happiness"].tolist(),
                "min_happiness": happiness_by_country["min_happiness"].tolist(),
                "max_happiness": happiness_by_country["max_happiness"].tolist(),
                "std_happiness": happiness_by_country["std_happiness"].tolist(),
                "city_count": happiness_by_country["city_count"].tolist()
            }
        }

    def get_city_comparison(self, cities: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Compare plusieurs villes sur différents indicateurs.

        Args:
            cities: Liste des noms de villes à comparer (None pour top 10)

        Returns:
            Liste de dictionnaires avec les données de comparaison
        """
        if cities is None:
            cities = self.df["city_name"].head(10).tolist()

        comparison_data = []
        for city in cities:
            city_data = self.df[self.df["city_name"] == city]
            if len(city_data) > 0:
                city_row = city_data.iloc[0]
                comparison_data.append({
                    "city_name": city,
                    "country": city_row["country"],
                    "population_density": float(city_row["population_density"]),
                    "avg_income": float(city_row["avg_income"]),
                    "internet_penetration": float(city_row["internet_penetration"]),
                    "avg_rent": float(city_row["avg_rent"]),
                    "air_quality_index": float(city_row["air_quality_index"]),
                    "public_transport_score": float(city_row["public_transport_score"]),
                    "happiness_score": float(city_row["happiness_score"]),
                    "green_space_ratio": float(city_row["green_space_ratio"])
                })

        return comparison_data

    def get_advanced_insights(self) -> dict[str, Any]:
        """
        Génère des insights avancés et corrélations.

        Returns:
            Dictionnaire avec les insights calculés
        """
        insights = {
            "happiness_income_correlation": float(self.df["happiness_score"].corr(self.df["avg_income"])),
            "happiness_air_quality_correlation": float(self.df["happiness_score"].corr(self.df["air_quality_index"])),
            "happiness_green_space_correlation": float(self.df["happiness_score"].corr(self.df["green_space_ratio"])),
            "happiest_country": self.df.groupby("country")["happiness_score"].mean().idxmax(),
            "highest_income_country": self.df.groupby("country")["avg_income"].mean().idxmax(),
            "best_transport_country": self.df.groupby("country")["public_transport_score"].mean().idxmax(),
            "greenest_country": self.df.groupby("country")["green_space_ratio"].mean().idxmax(),
            "most_connected_country": self.df.groupby("country")["internet_penetration"].mean().idxmax()
        }

        return insights

    def get_filters_options(self) -> dict[str, list[str]]:
        """
        Retourne toutes les options disponibles pour les filtres.

        Returns:
            Dictionnaire avec les options de filtrage
        """
        return {
            "countries": sorted(self.df["country"].unique().tolist()),
            "cities": sorted(self.df["city_name"].unique().tolist())
        }

    def apply_filters(self, filters: dict[str, Any]) -> pd.DataFrame:
        """
        Applique des filtres au dataframe.

        Args:
            filters: Dictionnaire de filtres à appliquer

        Returns:
            DataFrame original avant filtrage
        """
        filtered_df = self.df.copy()

        if "country" in filters and filters["country"]:
            filtered_df = filtered_df[filtered_df["country"].isin(filters["country"])]

        if "city" in filters and filters["city"]:
            filtered_df = filtered_df[filtered_df["city_name"].isin(filters["city"])]

        if "min_happiness" in filters and filters["min_happiness"]:
            filtered_df = filtered_df[filtered_df["happiness_score"] >= filters["min_happiness"]]

        if "max_happiness" in filters and filters["max_happiness"]:
            filtered_df = filtered_df[filtered_df["happiness_score"] <= filters["max_happiness"]]

        if "min_income" in filters and filters["min_income"]:
            filtered_df = filtered_df[filtered_df["avg_income"] >= filters["min_income"]]

        if "max_income" in filters and filters["max_income"]:
            filtered_df = filtered_df[filtered_df["avg_income"] <= filters["max_income"]]

        original_df = self.df
        self.df = filtered_df
        return original_df

    def restore_dataframe(self, original_df: pd.DataFrame) -> None:
        """
        Restaure le dataframe original.

        Args:
            original_df: DataFrame à restaurer
        """
        self.df = original_df