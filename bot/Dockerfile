FROM python:3.10-slim
WORKDIR /code

RUN apt update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install  -r requirements.txt
COPY . .

CMD ["python", "main.py"]