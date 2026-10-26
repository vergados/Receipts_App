#!/usr/bin/env bash
# Real-browser click test. Needs the backend (port 8000, on a COPY of receipts.db)
# and the frontend (npm run dev, port 3000) running; see frontend/e2e/click-test.mjs.
set -euo pipefail
cd "$(dirname "$0")/../frontend"
npm run test:click
