FROM python:3.13.9-trixie

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["fastapi", "run", "main.py"]