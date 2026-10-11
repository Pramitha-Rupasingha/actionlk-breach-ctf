#!/usr/bin/env bash
# Resets both live challenge stages to their initial state by recreating the
# containers from their images (docker compose restart keeps container data).
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up -d --force-recreate --no-deps stage3-frontdoor stage5-behindthedoor
docker compose ps stage3-frontdoor stage5-behindthedoor



