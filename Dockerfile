# Analysis environment. Mount the repo so data/ and reports/ stay on the host:
#   docker build -t switchback . && docker run --rm -v "$PWD":/app switchback python scripts/run_m1.py
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app/src MPLBACKEND=Agg
