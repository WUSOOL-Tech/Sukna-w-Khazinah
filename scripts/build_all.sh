#!/usr/bin/env bash
# Regenerate every brand deliverable from the approved logo source and tokens.json.
set -euo pipefail
cd "$(dirname "$0")/.."
export NODE_PATH="${NODE_PATH:-$(npm root -g)}"
python3 scripts/build_logo.py
python3 scripts/build_cobrand.py
python3 scripts/build_tokens.py
node scripts/render_motion.cjs
node scripts/build_guidelines.cjs
