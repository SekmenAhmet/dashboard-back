"""
API Flask pour le dashboard City Lifestyle.
Fournit des endpoints REST pour l'analyse des données urbaines.
"""
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from config import csv_path, server
from data_processor import CityLifestyleDataProcessor

app = Flask(__name__)
CORS(app)

# Initialiser le processeur de donnees
processor = CityLifestyleDataProcessor(csv_path)


@app.route("/")
def hello() -> Response:
    """Endpoint racine avec informations sur l'API."""
    return jsonify({
        "message": "City Lifestyle Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "overview": "/api/overview",
            "cities_by_country": "/api/cities/by-country",
            "top_cities": "/api/cities/top/<metric>",
            "income_analysis": "/api/income/analysis",
            "geographic": "/api/geographic",
            "correlations": "/api/correlations",
            "quality_of_life": "/api/quality-of-life",
            "happiness_analysis": "/api/happiness/analysis",
            "city_comparison": "/api/city/comparison",
            "insights": "/api/insights",
            "filters": "/api/filters"
        }
    })


@app.route("/api/overview", methods=["GET"])
def get_overview() -> Response:
    """Statistiques generales du dashboard"""
    try:
        stats = processor.get_overview_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cities/by-country", methods=["GET"])
def get_cities_by_country() -> Response:
    """Repartition des villes par pays"""
    try:
        data = processor.get_cities_by_country()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cities/top/<metric>", methods=["GET"])
def get_top_cities(metric: str) -> Response:
    """Top N villes selon une métrique"""
    try:
        valid_metrics = ["happiness_score", "avg_income", "internet_penetration",
                        "public_transport_score", "green_space_ratio", "air_quality_index"]
        if metric not in valid_metrics:
            return jsonify({"error": f"Invalid metric. Valid options: {valid_metrics}"}), 400

        top_n = int(request.args.get("top_n", 10))
        data = processor.get_top_cities(metric, top_n)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/income/analysis", methods=["GET"])
def get_income_analysis() -> Response:
    """Analyse detaillee des revenus"""
    try:
        data = processor.get_income_analysis()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/geographic", methods=["GET"])
def get_geographic() -> Response:
    """Donnees geographiques pour les cartes"""
    try:
        data = processor.get_geographic_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/correlations", methods=["GET"])
def get_correlations() -> Response:
    """Correlations entre variables numeriques"""
    try:
        data = processor.get_correlations()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/quality-of-life", methods=["GET"])
def get_quality_of_life() -> Response:
    """Analyse des facteurs de qualité de vie"""
    try:
        data = processor.get_quality_of_life_analysis()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/happiness/analysis", methods=["GET"])
def get_happiness_analysis() -> Response:
    """Analyse du bonheur par pays et facteurs"""
    try:
        data = processor.get_happiness_analysis()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/city/comparison", methods=["POST"])
def get_city_comparison() -> Response:
    """Comparaison entre villes"""
    try:
        cities = request.json.get("cities", None) if request.json else None
        data = processor.get_city_comparison(cities)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/insights", methods=["GET"])
def get_insights() -> Response:
    """Insights avances et statistiques"""
    try:
        data = processor.get_advanced_insights()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/filters", methods=["GET"])
def get_filters() -> Response:
    """Options disponibles pour les filtres"""
    try:
        data = processor.get_filters_options()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=int(server["PORT"]), host="0.0.0.0", debug=True)
