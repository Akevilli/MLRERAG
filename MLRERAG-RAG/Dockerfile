FROM python:3.13.9-trixie AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --prefix=/install --no-cache-dir torch>=1.11.0 && \
    pip install --prefix=/install --no-cache-dir -U sentence-transformers && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


FROM python:3.13.9-slim-trixie AS final

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY --from=builder /install /usr/local

COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]