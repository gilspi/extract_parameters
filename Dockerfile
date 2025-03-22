FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    build-essential \
    ngspice \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN wget -O openvaf.tar.gz https://openva.fra1.cdn.digitaloceanspaces.com/openvaf_23_5_0_linux_amd64.tar.gz && \
    tar -xzf openvaf.tar.gz && \
    rm openvaf.tar.gz && \
    chmod +x openvaf

CMD ["./openvaf"]
