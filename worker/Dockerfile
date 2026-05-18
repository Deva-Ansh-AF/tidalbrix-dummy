FROM python:3.11-slim

LABEL description="TidalBrix dummy worker — prints mock processing steps and exits"

WORKDIR /app
COPY worker.py .

CMD ["python", "worker.py"]
