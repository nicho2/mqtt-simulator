# MQTT Simulator

Ce projet fournit une application FastAPI simulant des capteurs MQTT et expose des métriques pour Prometheus.
Un `docker-compose.yml` permet également de lancer Prometheus et Grafana.

## Première installation

Clonez le dépôt puis exécutez le script de bootstrap pour créer l'environnement virtuel et installer les dépendances:

```bash
git clone <repo>
cd mqtt-simulator
./bootstrap.sh
source .venv/bin/activate
```

## Lancer l'application sans Docker

```bash
uvicorn app.main:app --reload
```

L'API est alors disponible sur <http://localhost:8000>.

## Installation manuelle

Si vous préférez ne pas utiliser `bootstrap.sh`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Installation avec Docker

```bash
docker compose up --build
```

- API: <http://localhost:8000>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000>

Arrêtez les services avec `docker compose down`.

## Utilisation

- Lancer la suite de tests:

```bash
python -m pytest -v
```

- Documentation interactive: `http://localhost:8000/docs`
- Métriques Prometheus: `http://localhost:8000/metrics`

## Développement frontend (optionnel)

### Install dependencies

```bash
# Create a Vue 3 project with Vite
npm create vite@latest my-app -- --template vue
cd my-app
npm install

# Add Vuetify and other plugins
npm install vuetify@^3 vue-router@4 pinia vue-i18n@9
# Vuetify plugin + Sass for preprocessing
npm install -D vite-plugin-vuetify sass
```

The Vuetify plugin will automatically import component styles when `autoImport` is enabled in `vite.config.ts`.
