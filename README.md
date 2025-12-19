# tfidf-recs – Movie Recommendations

Content‑based movie recommender built on TF‑IDF features and cosine similarity, with a small orchestration layer for versioned artifacts and a separate CLI REPL for trying recommendations.

This repo is designed as a playground project: the data pipeline, feature generation, model artifacts, and user‑facing CLI are all separated into clear layers.

## Table of Contents

- [Project Overview](#project-overview)
- [Environment & Setup](#environment--setup)
- [Dataset (MovieLens) – Not Tracked in Git](#dataset-movielens--not-tracked-in-git)
    - [Where to put the data](#where-to-put-the-data)
    - [How the data layer transforms the dataset](#how-the-data-layer-transforms-the-dataset)
- [Running the Pipelines](#running-the-pipelines)
    - [1. Generate processed data](#1-generate-processed-data)
    - [2. Train / update the recommendation artifacts](#2-train--update-the-recommendation-artifacts)
    - [3. Rerun / update a specific version (in-place)](#3-rerun--update-a-specific-version-in-place)
    - [4. Inspect existing versions](#4-inspect-existing-versions)
- [Running the Recommendation REPL](#running-the-recommendation-repl)
- [Development Notes](#development-notes)
- [Ethics & Licensing Notes](#ethics--licensing-notes)

---

## Project Overview

- **Data layer** (`src/data`)
	- Loads the MovieLens movies data (see “Dataset” below).
	- Applies text preprocessing (year extraction, genre expansion, text normalization) and writes a processed parquet file.
- **Orchestration layer** (`src/orchestration`)
	- Runs the end‑to‑end pipeline: load processed data → fit TF‑IDF vectorizer → build feature matrix → build similarity matrix.
	- Uses an **artifact registry** ([src/utils/artifacts_registry.py](src/utils/artifacts_registry.py)) to store versioned artifacts under `data/artifacts/`.
- **Engine layer** (`src/engine`)
	- `ContentBasedRecommender` wraps the feature & similarity matrices to expose a clean `recommend(movie_id, k=…)` API.
- **App layer** (`src/app/recommend_cli.py`)
	- A Click‑based interactive REPL for exploring the catalogue and receiving recommendations.

Directory snapshot (simplified):

```text
configs/
	data_config.yaml           # Data loading & transforms
	orchestration_config.yaml  # Pipeline steps & parameters
	registry_config.yaml       # Artifact storage layout
data/
	raw/                       # Place MovieLens CSV here (not tracked)
	processed/                 # Derived parquet from data pipeline
	artifacts/                 # Versioned model artifacts (npz, joblib, json)
src/
	data/                      # Data pipeline & transforms
	engine/                    # Recommender engine & similarity strategies
	orchestration/             # CLI + orchestrator + steps
	app/                       # User‑facing REPL
	utils/                     # Config loader, artifact registry, IO helpers
```

---

## Environment & Setup

This project uses a Conda environment described in [environment.yaml](environment.yaml).

```bash
conda env create -f environment.yaml
conda activate recsys
```

Install NLTK data used by the text preprocessing (the first run of the data pipeline may already do this):

```python
python -m nltk.downloader wordnet punkt stopwords
```

---

## Dataset (MovieLens) – Not Tracked in Git

This project uses the **MovieLens** dataset from GroupLens (e.g. MovieLens 20M / latest small release) for educational purposes. 

To respect the MovieLens license and good open‑source hygiene:

- **Raw data files are not committed to this repository.**
- You should download MovieLens yourself from the official source: https://grouplens.org/datasets/movielens/
- Follow the license terms published by GroupLens.

### Where to put the data

This code expects the `movies.csv` file to exist at:

```text
data/raw/movies.csv
```

For the standard MovieLens `movies.csv`, that means:

- Create the `data/raw/` directory if it doesn’t exist.
- Copy or symlink `movies.csv` from the MovieLens download into `data/raw/movies.csv`.

### How the data layer transforms the dataset

The raw MovieLens `movies.csv` is quite minimal: it contains `movieId`, `title`, and `genres`. The data pipeline in [src/data/pipeline.py](src/data/pipeline.py) and [configs/data_config.yaml](configs/data_config.yaml) transforms this into a richer, model‑ready table:

- Extracts the **release year** from the title (e.g. `"Toy Story (1995)" → year 1995`).
- Expands and cleans **genres** into a more usable form.
- Builds a **`combined_text`** field that concatenates title, year, and genres into a single text field suitable for TF‑IDF.
- Writes the processed dataframe to:

```text
data/processed/movies_processed.parquet
```

This derived file *is* safe to regenerate from raw data and therefore is also not tracked in git by default – you can recreate it any time by re‑running the data pipeline.

---

## Running the Pipelines

All orchestration commands assume you are in the repository root and the `recsys` Conda environment is active.

### 1. Generate processed data

Read `configs/data_config.yaml` and run the data pipeline:

```bash
python -m src.data.pipeline
```

This will read `data/raw/movies.csv`, apply the configured transformers, and write:

- `data/processed/movies_processed.parquet`

### 2. Train / update the recommendation artifacts

The orchestration CLI is in [src/orchestration/cli.py](src/orchestration/cli.py).

Run a full pipeline (create a new version):

```bash
python -m src.orchestration.cli run --data-config
```

This will:

1. Load the processed parquet file (`load_data` step).
2. Fit a TF‑IDF vectorizer (`vectorizer` step).
3. Build a sparse feature matrix (`features` step).
4. Compute a cosine similarity matrix (`similarity` step).

Artifacts are written under `data/artifacts/<version_id>/`, where `<version_id>` is something like `v1.20251219_152320`. The structure typically includes:

- `feature_matrix/features.npz`
- `similarity_matrix/similarity.npz`
- `vectorizer/vectorizer.joblib`
- `metadata/metadata.json`

### 3. Rerun / update a specific version (in-place)

If you've changed the feature logic but want to **reuse the same version ID**, you can rerun a specific version by calling `run` with `--version`:

```bash
python -m src.orchestration.cli run --version <version_id> --data-config
```

This loads the existing version, re-executes the configured pipeline steps, and overwrites that version's artifacts in-place.

### 4. Inspect existing versions

List versions:

```bash
python -m src.orchestration.cli list-versions
```

Inspect a version’s artifacts and metadata:

```bash
python -m src.orchestration.cli load --version <version_id>
```

If `--version` is omitted, `load` uses the latest version.

---

## Running the Recommendation REPL

The user‑facing CLI REPL lives in [src/app/recommend_cli.py](src/app/recommend_cli.py).

Start the REPL (using the latest model version):

```bash
python -m src.app.recommend_cli
```

Or pin a specific version when launching:

```bash
python -m src.app.recommend_cli --version <version_id>
```

Inside the REPL:

- Type **any text** → searches movie titles containing that text.
- Type a **movie ID** (e.g. `1`) → prints that movie and its top‑K similar movies.
- Type **`help`** → shows REPL help.
- Type **`quit` / `exit` / `q`** or press **Ctrl+C** → exit.

There is also a small helper command to inspect the active model version without entering the REPL:

```bash
python -m src.app.recommend_cli version
python -m src.app.recommend_cli --version <version_id> version
```

---

## Development Notes

- **Python version**: defined in [environment.yaml](environment.yaml) (currently Python 3.13).
- **Configs**: live in `configs/` and are loaded via [src/utils/config_loader.py](src/utils/config_loader.py).
- **Artifact registry**: behavior and layout controlled by `configs/registry_config.yaml` and implemented in [src/utils/artifacts_registry.py](src/utils/artifacts_registry.py).
- **Adding new steps**: extend [src/orchestration/steps.py](src/orchestration/steps.py) and wire them into [src/orchestration/orchestrator.py](src/orchestration/orchestrator.py) and `configs/orchestration_config.yaml`.

When contributing or extending this project:

- Do **not** commit any raw MovieLens data files (e.g. `movies.csv`, ratings files, full dumps).
- Prefer small, composable steps in the orchestration layer and keep the app/UI layer thin, delegating all logic to the engine and artifacts.

---

## Ethics & Licensing Notes

- This project is for **educational and experimental** purposes.
- The MovieLens dataset is owned and licensed by **GroupLens**. Always refer to their license before using the data in production or redistributing it.
- Avoid committing user or third‑party data to public repositories unless you have explicit permission and a clear policy for handling it.