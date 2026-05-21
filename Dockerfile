FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e .

ENV KHUKRA_DATA_ROOT=/data
ENV KHUKRA_ENV=production
ENV KHUKRA_API_PORT=8000

EXPOSE 8000

VOLUME ["/data"]

CMD ["uvicorn", "khukra.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
