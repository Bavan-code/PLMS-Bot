FROM library/python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
        --no-install-recommends \
        build-essential \
        python3-dev \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:5000", "--master", "-p", "2", "-w", "main:app"]
USER nobody