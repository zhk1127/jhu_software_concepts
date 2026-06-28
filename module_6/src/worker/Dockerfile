FROM python:3.12-slim

WORKDIR /app

COPY src/worker/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.worker.consumer"]
