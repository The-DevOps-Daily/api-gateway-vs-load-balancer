#!/usr/bin/env bash
# Certificates, .env, the pinned load generator, and the backend image.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p certs tools
if [ ! -f certs/server.key ]; then
  openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 30 \
    -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" \
    -keyout certs/server.key -out certs/server.crt 2>/dev/null
  cat certs/server.crt certs/server.key > certs/server.pem
  chmod 644 certs/*
fi

if [ ! -f .env ]; then
  cp .env.example .env
  sed -i "s/^TYK_GW_SECRET=.*/TYK_GW_SECRET=$(openssl rand -hex 16)/" .env
fi

VEGETA=12.13.0
if [ ! -x tools/vegeta ]; then
  url="https://github.com/tsenart/vegeta/releases/download/v${VEGETA}"
  tarball="vegeta_${VEGETA}_linux_amd64.tar.gz"
  curl -fsSL -o "tools/$tarball" "$url/$tarball"
  curl -fsSL -o tools/checksums.txt "$url/vegeta_${VEGETA}_checksums.txt"
  (cd tools && grep " $tarball\$" checksums.txt | sha256sum -c -)
  tar -xzf "tools/$tarball" -C tools vegeta
fi
tools/vegeta -version | head -1

docker compose build backend
