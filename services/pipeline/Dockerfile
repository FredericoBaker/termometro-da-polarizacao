FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY libs /app/libs
COPY services/pipeline /app/services/pipeline

RUN cd /app/services/pipeline && pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="/app/services/pipeline/src:/app/libs/termopol_db/src"

CMD ["python", "services/pipeline/run.py"]
