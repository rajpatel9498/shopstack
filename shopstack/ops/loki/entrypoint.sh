#!/bin/sh

# Create necessary directories
mkdir -p /tmp/loki/boltdb-shipper-active
mkdir -p /tmp/loki/boltdb-shipper-cache
mkdir -p /tmp/loki/chunks
mkdir -p /tmp/loki/compactor

# Set permissions
chmod -R 777 /tmp/loki

# Start Loki
exec /usr/bin/loki -config.file=/etc/loki/local-config.yaml
