#!/usr/bin/env bash
# Usage: lighthouse_run.sh <url> <out-dir>   Runs Lighthouse (mobile + desktop) and saves JSON summaries.
set -uo pipefail
URL="$1"; OUT="${2:-qa-output}"; mkdir -p "$OUT"
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME_PATH:-$(ls /opt/pw-browsers/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1)}"
[ -z "$CHROME" ] && CHROME="$(command -v google-chrome || command -v chromium || true)"
export CHROME_PATH="$CHROME"
for preset in mobile desktop; do
  FLAGS=(--quiet --output=json --output-path="$OUT/lighthouse-$preset.json" --chrome-flags="--headless=new --no-sandbox")
  [ "$preset" = desktop ] && FLAGS+=(--preset=desktop)
  node "$HERE/node_modules/lighthouse/cli/index.js" "$URL" "${FLAGS[@]}" >/dev/null 2>"$OUT/lighthouse-$preset.err" \
    && echo "lighthouse $preset ok" || echo "lighthouse $preset FAILED (see $OUT/lighthouse-$preset.err)"
done
