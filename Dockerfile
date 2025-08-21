FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY lemnisiana ./lemnisiana
COPY configs ./configs
ENV LEM_CONFIG=/app/configs/default.yaml
EXPOSE 8000
CMD ["uvicorn", "lemnisiana.orchestrator.app:app", "--host", "0.0.0.0", "--port", "8000"]
