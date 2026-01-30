# City Lifestyle Dashboard - Backend API

Backend REST API pour le dashboard d'analyse du style de vie urbain. Fournit des endpoints pour analyser les données de qualité de vie dans différentes villes à travers le monde.

## Table des matières

- [User Guide](#user-guide)
- [Data](#data)
- [Dev Guide](#dev-guide)
- [Rapport d'analyse](#rapport-danalyse)
- [Copyright](#copyright)

---

## User Guide

### Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. Clonez le repository :
```bash
git clone <repository-url>
cd dashboard-back
```

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

### Utilisation

#### 1. Lancement de l'API (pipeline auto)

```bash
python src/main.py
```

L'API sera accessible sur `http://localhost:5000`

Pendant le démarrage, le backend :
- récupère le CSV depuis `data/city_lifestyle_dataset.csv` vers `data/raw/` avec cache 24h,
- nettoie les données vers `data/cleaned/city_lifestyle_cleaned.csv` (doublons, valeurs manquantes, bornage, géolocalisation synthétique),
- charge le CSV nettoyé dans l'API.

#### 2. Récupération des données (optionnel)

```bash
python src/get_data.py
```

Ce script force la mise en cache de la source (copie locale ou téléchargement HTTP) dans `data/raw/`.

#### 3. Nettoyage des données (optionnel)

```bash
python src/clean_data.py
```

Ce script lit `data/city_lifestyle_dataset.csv` ou votre source, puis écrit le fichier nettoyé dans `data/cleaned/`.

#### 4. Utilisation avec Docker

```bash
# Build l'image
docker build -t city-lifestyle-api .

# Run le conteneur
docker run -p 5000:5000 city-lifestyle-api
```

### Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Informations sur l'API |
| `/api/overview` | GET | Statistiques générales |
| `/api/cities/by-country` | GET | Répartition des villes par pays |
| `/api/cities/top/<metric>` | GET | Top N villes selon une métrique |
| `/api/income/analysis` | GET | Analyse détaillée des revenus |
| `/api/geographic` | GET | Données géographiques pour cartes |
| `/api/correlations` | GET | Corrélations entre variables |
| `/api/quality-of-life` | GET | Analyse qualité de vie |
| `/api/happiness/analysis` | GET | Analyse du bonheur par pays |
| `/api/city/comparison` | POST | Comparaison entre villes |
| `/api/insights` | GET | Insights avancés |
| `/api/filters` | GET | Options de filtrage disponibles |

#### Exemples de requêtes

```bash
# Obtenir les statistiques générales
curl http://localhost:5000/api/overview

# Top 10 villes les plus heureuses
curl http://localhost:5000/api/cities/top/happiness_score?top_n=10

# Comparer des villes spécifiques
curl -X POST http://localhost:5000/api/city/comparison \
  -H "Content-Type: application/json" \
  -d '{"cities": ["Old Vista", "Beachport", "Falls"]}'
```

---

## Data

### Source des données

- **Dataset** : City Lifestyle Dataset (synthétique, inclus dans le repo)
- **Fichier** : `data/city_lifestyle_dataset.csv`
- **Format** : CSV (Comma Separated Values)
- **Taille** : 300 lignes (299 villes + 1 en-tête)
- **Régions couvertes** : Europe, Asie, Afrique, Amérique du Nord, Amérique du Sud, Océanie
- **Accès public & reproductible** : fichier versionné dans `data/`; possibilité de remplacer par une URL publique via `CSV_PATH`

### Description du dataset

Le dataset contient des informations sur la qualité de vie dans différentes villes (continents multiples). Il permet d'analyser les facteurs qui influencent le bonheur et le bien-être des habitants.
Note : dans le dataset fourni, la colonne `country` contient des continents/régions (ex. Europe, Asia), pas des pays au sens strict.

### Structure des données

| Colonne | Type | Description | Unité/Plage |
|---------|------|-------------|-------------|
| `city_name` | String | Nom de la ville | - |
| `country` | String | Région/continent | 6 régions |
| `population_density` | Float | Densité de population | Habitants/km² (0-100000) |
| `avg_income` | Float | Revenu moyen | €/mois (0-10000) |
| `internet_penetration` | Float | Taux de pénétration internet | % (0-100) |
| `avg_rent` | Float | Loyer moyen | €/mois (0-50000) |
| `air_quality_index` | Float | Indice de qualité de l'air | AQI (0-500) |
| `public_transport_score` | Float | Score des transports publics | Score (0-100) |
| `happiness_score` | Float | Indice de bonheur | Score (0-10) |
| `green_space_ratio` | Float | Ratio d'espaces verts | % (0-100) |
| `latitude` | Float | Latitude (synthétique si absente) | -55 à 70 |
| `longitude` | Float | Longitude (synthétique si absente) | -130 à 150 |

### Statistiques descriptives

- Observations : 300 lignes (299 villes)
- Variables numériques : 11 métriques continues
- Variable catégorielle : `country` (continent)

**Caractéristiques (ordre de grandeur)** :
- Densité de population moyenne : ~3 000 hab/km²
- Revenu moyen : ~3 500 €/mois (unité interne du dataset)
- Bonheur moyen : ~7.8/10
- Pénétration internet : ~80%

### Notes sur la qualité des données

Le pipeline de nettoyage ([clean_data.py](src/clean_data.py)) effectue les opérations suivantes :
- Suppression des doublons (basé sur `city_name` + `country`)
- Remplacement des valeurs manquantes (médiane pour numériques, "Unknown" pour texte)
- Validation et normalisation des plages de valeurs
- Conversion des types de données
- Ajout de coordonnées `latitude`/`longitude` synthétiques si absentes (pour garantir la cartographie)

### Note sur la géolocalisation

Le CSV source n’inclut pas de coordonnées réelles. Des coordonnées synthétiques déterministes sont générées lors du nettoyage pour permettre l’affichage carte. Pour des positions réelles, remplacez le CSV par un fichier géocodé ou renseignez `CSV_PATH` vers une source publique contenant lat/lon.

### Accès et reproductibilité

- **Accès** : Le fichier CSV est inclus dans le repository (`data/city_lifestyle_dataset.csv`)
- **Format public** : CSV standard, lisible par tous les outils d'analyse
- **Reproductibilité** : Pipeline automatisé avec `get_data.py` et `clean_data.py`

---

## Dev Guide

### Architecture du projet

```
dashboard-back/
├── data/                          # Données du projet
│   ├── raw/                      # Données brutes (cache)
│   ├── cleaned/                  # Données nettoyées
│   └── city_lifestyle_dataset.csv # Dataset source
├── src/                          # Code source
│   ├── main.py                  # Point d'entrée API Flask
│   ├── config.py                # Configuration
│   ├── get_data.py              # Récupération et cache
│   ├── clean_data.py            # Nettoyage des données
│   └── data_processor.py        # Traitement et analyse
├── .ruff.toml                   # Configuration du linter
├── requirements.txt             # Dépendances Python
├── Dockerfile                   # Configuration Docker
└── README.md                    # Documentation
```

### Modules principaux

#### 1. [main.py](src/main.py) - API Flask
- Définit tous les endpoints REST
- Gère le CORS pour les requêtes cross-origin
- Gère les erreurs avec try/catch
- Utilise `CityLifestyleDataProcessor` pour les données

#### 2. [get_data.py](src/get_data.py) - Récupération des données
- Classe `DataRetriever` pour la gestion du cache
- Système de cache avec durée configurable (24h par défaut)
- Méthode `get_data()` avec option `force_refresh`
- Méthode `clear_cache()` pour nettoyer le cache

#### 3. [clean_data.py](src/clean_data.py) - Nettoyage
- Classe `DataCleaner` pour le pipeline de nettoyage
- Suppression des doublons
- Gestion des valeurs manquantes
- Validation des plages numériques
- Génération de rapport de nettoyage

#### 4. [data_processor.py](src/data_processor.py) - Analyse
- Classe `CityLifestyleDataProcessor` pour toutes les analyses
- Méthodes pour statistiques, corrélations, insights
- Filtrage et comparaison de villes
- Prétraitement automatique des données

#### 5. [config.py](src/config.py) - Configuration
- Chargement des variables d'environnement
- Configuration du serveur Flask
- Gestion des chemins (compatibilité locale/Docker)

### Qualité du code

**Standards appliqués** :
- ✅ Docstrings sur toutes les fonctions et classes (format Google)
- ✅ Type hints systématiques (`dict[str, Any]`, `list[str]`, etc.)
- ✅ Code organisé en classes avec séparation des responsabilités
- ✅ Gestion des erreurs avec try/except
- ✅ Nommage explicite et cohérent

**Linting et formatage** :
- Outil : **Ruff** (linter + formatter ultra-rapide)
- Configuration : [.ruff.toml](.ruff.toml)
- Règles activées : pycodestyle, pyflakes, isort, pep8-naming, flake8-bugbear, etc.

```bash
# Vérifier le code
ruff check src/

# Corriger automatiquement
ruff check --fix src/

# Formater le code
ruff format src/
```

### Développement

#### Ajouter un nouvel endpoint

1. Ouvrez [src/main.py](src/main.py)
2. Ajoutez une nouvelle fonction avec le décorateur `@app.route`
3. Utilisez `processor` pour accéder aux données
4. Retournez `jsonify(data)` avec gestion d'erreur

Exemple :
```python
@app.route("/api/mon-endpoint", methods=["GET"])
def mon_endpoint() -> Response:
    """Description de l'endpoint"""
    try:
        data = processor.ma_nouvelle_methode()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

#### Ajouter une nouvelle analyse

1. Ouvrez [src/data_processor.py](src/data_processor.py)
2. Ajoutez une méthode à la classe `CityLifestyleDataProcessor`
3. Utilisez `self.df` (pandas DataFrame) pour analyser les données
4. Retournez un dictionnaire JSON-sérialisable

#### Tests

Pour tester l'API manuellement :
1. Importez la collection Postman : `Dashboard_API.postman_collection.json`
2. Ou utilisez curl/httpie pour les requêtes

#### Configuration

Le backend est configuré pour fonctionner directement sans configuration supplémentaire :
- **Port** : 5000 (par défaut)
- **CSV source** : `data/city_lifestyle_dataset.csv`

### Dépendances

Voir [requirements.txt](requirements.txt) pour la liste complète.

Principales dépendances :
- **Flask** (3.0.0) : Framework web
- **Flask-CORS** (4.0.0) : Gestion CORS
- **pandas** (2.1.4) : Manipulation de données
- **numpy** (1.26.2) : Calculs numériques
- **plotly** (5.18.0) : Visualisations (si besoin)
- **scipy** (1.11.4) : Statistiques avancées
- **requests** (2.31.0) : Requêtes HTTP
- **ruff** (0.1.8) : Linting et formatage

### Workflow de développement

1. Créer une branche feature
2. Faire vos modifications
3. Lancer ruff : `ruff check --fix src/`
4. Tester l'API localement
5. Committer et push
6. Créer une Pull Request

---

## Rapport d'analyse

### Objectif du projet

Analyser les facteurs qui influencent la qualité de vie et le bonheur dans des villes à travers plusieurs continents, en étudiant les corrélations entre différentes métriques urbaines.

### Métriques analysées

Le dashboard analyse 9 variables principales :
1. **Densité de population** - Impact de l'urbanisation
2. **Revenu moyen** - Pouvoir d'achat des habitants
3. **Pénétration internet** - Connectivité numérique
4. **Loyer moyen** - Coût de la vie
5. **Qualité de l'air** - Santé environnementale
6. **Transports publics** - Mobilité urbaine
7. **Indice de bonheur** - Variable cible principale
8. **Espaces verts** - Qualité de vie environnementale

### Questions de recherche

1. **Quels facteurs influencent le plus le bonheur ?**
   - Corrélation bonheur ↔ revenu
   - Corrélation bonheur ↔ qualité de l'air
   - Corrélation bonheur ↔ espaces verts

2. **Existe-t-il des différences régionales ?**
   - Comparaison des moyennes par région/continent
   - Identification des régions les plus performantes

3. **Quelles villes offrent la meilleure qualité de vie ?**
   - Top 10 villes par métrique
   - Profils de villes "idéales"

### Insights principaux

L'API fournit plusieurs endpoints d'analyse :

- **`/api/correlations`** : Matrice de corrélation entre toutes les variables
- **`/api/insights`** : Insights automatiques (région la plus heureuse, meilleurs transports, etc.)
- **`/api/happiness/analysis`** : Analyse détaillée du bonheur par région

### Méthodologie

1. **Collecte** : Dataset de 299 villes réparties sur 6 continents (Europe, Asie, Afrique, Amériques, Océanie)
2. **Nettoyage** : Pipeline automatisé (doublons, valeurs manquantes, outliers)
3. **Analyse** : Statistiques descriptives, corrélations, comparaisons
4. **API** : Exposition des données via endpoints REST pour visualisation

### Histogramme (Variable non catégorielle)

Variables disponibles pour histogrammes :
- `avg_income` : Distribution des revenus moyens
- `happiness_score` : Distribution des indices de bonheur
- `air_quality_index` : Distribution de la qualité de l'air
- `population_density` : Distribution de la densité de population

Exemple d'utilisation :
```python
import pandas as pd
import plotly.express as px

df = pd.read_csv("data/city_lifestyle_dataset.csv")
fig = px.histogram(df, x="avg_income", nbins=30,
                   title="Distribution des revenus moyens")
```

### Carte géolocalisée

Les coordonnées lat/lon synthétiques sont générées automatiquement par `clean_data.py` avec des bounding boxes par continent (Europe, Asie, Amériques, Afrique, Océanie) afin de limiter les points dans les océans. Pour des positions réelles, fournissez un CSV géocodé ou renseignez `CSV_PATH` vers une source publique incluant `latitude` et `longitude`.

### Limites et améliorations futures

**Limites actuelles** :
- Coordonnées GPS synthétiques (non réelles) pour la cartographie
- Dataset synthétique (non basé sur des données réelles)
- Pas de données temporelles (évolution dans le temps)
- Distribution inégale entre continents (Europe: 60 villes, Asie: 80, Afrique: 35, etc.)

**Améliorations possibles** :
- Intégrer des données réelles avec coordonnées GPS précises
- Ajouter des séries temporelles pour suivre l'évolution
- Ajouter plus de métriques (éducation, santé, sécurité, crime)
- Modèles prédictifs du bonheur
- Équilibrer la répartition géographique des villes

---

## Copyright

### Licence

Ce projet est développé dans un cadre éducatif à l'ESIEE Paris.

**Année académique** : 2024-2025
**Cours** : Dashboard interactif et visualisation de données

### Auteurs

Projet réalisé par l'équipe de développement du City Lifestyle Dashboard.

### Technologies utilisées

- **Backend** : Python 3.11, Flask
- **Analyse de données** : pandas, numpy, scipy
- **Visualisation** : plotly
- **Linting** : Ruff
- **Containerisation** : Docker

### Ressources externes

- [Flask Documentation](https://flask.palletsprojects.com/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

### Crédits

Dataset synthétique créé pour des fins pédagogiques.

### Mentions légales

Ce projet est destiné à un usage éducatif uniquement. Toute utilisation commerciale nécessite l'autorisation des auteurs.

---

**Version** : 1.0.0
**Dernière mise à jour** : Décembre 2024
**Contact** : Voir le fichier CONTRIBUTORS ou les commits Git
