#!/usr/bin/env bash
set -euo pipefail
cd /root
rm -rf CDML-X
git clone https://github.com/hemanthbreaker3-hash/CDML-X
cd CDML-X
# Copy .env.example to .env and fill required credentials before running.
if [[ ! -f .env ]]; then cp .env.example .env; fi
set -a
source .env
set +a
chmod +x deploy.vps start.sh
./deploy.vps
