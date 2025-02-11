FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get install && apt-get install -y \
    libx11-6 \ 
    libxext-dev \
    libxrender-dev \
    libxinerama-dev \
    libxi-dev \
    libxrandr-dev \
    libxcursor-dev \
    libxtst-dev \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

CMD ["python", "main.py"]