#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "Starting VAST Services Python Backend..."

docker compose up --build
