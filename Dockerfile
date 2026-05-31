FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

ENV BOT_MODE=webhook \
    DB_BACKEND=postgres \
    PORT=8080 \
    WEBHOOK_HOST=0.0.0.0 \
    WEBHOOK_PATH=/webhook

EXPOSE 8080

CMD ["python", "run.py"]