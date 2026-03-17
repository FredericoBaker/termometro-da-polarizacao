FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY libs/termopol_db /libs/termopol_db
RUN pip install --no-cache-dir -e /libs/termopol_db

COPY services/api/requirements.txt /app/services/api/requirements.txt
RUN pip install --no-cache-dir -r /app/services/api/requirements.txt

COPY services/api/src /app/services/api/src

ENV PYTHONPATH="/app/services/api/src:/libs/termopol_db/src"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
