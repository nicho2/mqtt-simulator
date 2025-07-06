#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="certs"
CLIENTS=0

for arg in "$@"; do
    case "$arg" in
        --clients=*)
            CLIENTS="${arg#*=}"
            ;;
        *)
            echo "Usage: $0 [--clients=N]" >&2
            exit 1
            ;;
    esac
done

mkdir -p "$CERT_DIR"

generate_ca() {
    openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
        -subj "/CN=localhost" \
        -keyout "$CERT_DIR/ca.key" -out "$CERT_DIR/ca.pem"
}

generate_server() {
    openssl req -newkey rsa:4096 -nodes -subj "/CN=localhost" \
        -keyout "$CERT_DIR/server.key" -out "$CERT_DIR/server.csr"
    openssl x509 -req -sha256 -days 365 -in "$CERT_DIR/server.csr" \
        -CA "$CERT_DIR/ca.pem" -CAkey "$CERT_DIR/ca.key" \
        -CAcreateserial -CAserial "$CERT_DIR/ca.srl" \
        -out "$CERT_DIR/server.pem"
    rm "$CERT_DIR/server.csr"
}

generate_clients() {
    i=1
    while [ "$i" -le "$CLIENTS" ]; do
        openssl req -newkey rsa:4096 -nodes -subj "/CN=localhost" \
            -keyout "$CERT_DIR/client${i}.key" -out "$CERT_DIR/client${i}.csr"
        openssl x509 -req -sha256 -days 365 -in "$CERT_DIR/client${i}.csr" \
            -CA "$CERT_DIR/ca.pem" -CAkey "$CERT_DIR/ca.key" \
            -CAcreateserial -CAserial "$CERT_DIR/ca.srl" \
            -out "$CERT_DIR/client${i}.pem"
        rm "$CERT_DIR/client${i}.csr"
        i=$((i + 1))
    done
}

main() {
    generate_ca
    generate_server
    if [ "$CLIENTS" -gt 0 ]; then
        generate_clients
    fi
}

main
