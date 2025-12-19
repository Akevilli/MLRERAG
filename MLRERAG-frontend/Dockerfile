FROM python:3.13.9-trixie AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


FROM python:3.13.9-slim-trixie AS final

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.enableCORS", "false"]