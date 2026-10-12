#!/usr/bin/env bash
# Applies the ActionLK terminal theme to a RUNNING CTFd through its REST API:
#   - Theme Header  <- branding/theme-header.html
#   - Logo          <- branding/actionlk-logo.svg
#   - Small icon    <- branding/actionlk-favicon.svg
#
# Usage (run from the project root, on the Ubuntu VM):
#   CTFD_TOKEN=ctfd_xxxxxxxx bash scripts/apply_theme.sh [ctfd-url]
#
# Get the token once: log in to CTFd as admin -> Settings -> Access Tokens -> Generate.
# Do NOT commit the token anywhere. Re-running is safe (it re-uploads the logo/icon
# as new files, which is harmless).
set -euo pipefail

CTFD_URL="${1:-${CTFD_URL:-http://localhost:8000}}"
: "${CTFD_TOKEN:?Set CTFD_TOKEN first (CTFd -> Settings -> Access Tokens -> Generate)}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../branding" && pwd)"
for f in theme-header.html actionlk-logo.svg actionlk-favicon.svg; do
  [ -f "$DIR/$f" ] || { echo "Missing $DIR/$f" >&2; exit 1; }
done

api() {  # api METHOD /path [extra curl args...]
  local method="$1" path="$2"; shift 2
  curl -sS --fail-with-body -X "$method" "$CTFD_URL/api/v1$path" \
       -H "Authorization: Token $CTFD_TOKEN" "$@"
}

set_config() {  # set_config KEY VALUE
  python3 -c 'import json,sys; print(json.dumps({sys.argv[1]: sys.argv[2]}))' "$1" "$2" \
    | api PATCH /configs -H "Content-Type: application/json" --data @- >/dev/null
}

upload() {  # upload FILE  -> prints the stored file location
  api POST /files -F "file=@$1" -F "type=standard" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"][0]["location"])'
}

echo "[1/3] Theme header"
set_config theme_header "$(cat "$DIR/theme-header.html")"

echo "[2/3] Logo"
set_config ctf_logo "$(upload "$DIR/actionlk-logo.svg")"

echo "[3/3] Small icon (favicon)"
set_config ctf_small_icon "$(upload "$DIR/actionlk-favicon.svg")"

echo "Done. Hard-refresh the browser (Ctrl+Shift+R) on $CTFD_URL"
