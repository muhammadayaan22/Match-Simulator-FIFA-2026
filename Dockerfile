# FIFA 2026 AI ORACLE — Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System deps for xgboost / scientific stack
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Build the dataset, database, and trained models at image build time
RUN python data/generate_teams.py && \
    python data/generate_matches.py && \
    python database/build_db.py && \
    python models/train_models.py

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
