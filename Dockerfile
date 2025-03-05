# Используем базовый образ Ubuntu
FROM ubuntu:20.04

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y \
    build-essential \
    ngspice \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочий каталог
WORKDIR /app

# Скачиваем и распаковываем openvaf
RUN wget -O openvaf.tar.gz https://openva.fra1.cdn.digitaloceanspaces.com/openvaf_23_5_0_linux_amd64.tar.gz && \
    tar -xzf openvaf.tar.gz && \
    rm openvaf.tar.gz && \
    chmod +x openvaf

CMD ["./openvaf"]
