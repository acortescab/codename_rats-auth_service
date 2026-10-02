#!/bin/bash
# Read-only smoke test against a deployed instance: ./scripts/smoke_test.sh <base-url>
# Never writes data and never touches the database, so it is safe to run against production.
set -euo pipefail

BASE_URL="${1:?usage: smoke_test.sh <base-url>}"
BASE_URL="${BASE_URL%/}"

check() {
  local name="$1" url="$2" expected="$3" body_match="${4:-}"
  local status body

  for attempt in 1 2 3 4 5 6; do
    body="$(mktemp)"
    status="$(curl -s -o "$body" -w '%{http_code}' --max-time 10 "$url" || true)"
    if [[ "$status" =~ ^($expected)$ ]] && { [ -z "$body_match" ] || grep -q "$body_match" "$body"; }; then
      echo "PASS: $name ($url -> $status)"
      rm -f "$body"
      return 0
    fi
    rm -f "$body"
    echo "Retry $attempt: $name returned $status, expected $expected"
    sleep 5
  done

  echo "FAIL: $name ($url)"
  return 1
}

check "health"            "$BASE_URL/v0/health/"          200 '"status":"ok"'
check "jwks is published" "$BASE_URL/.well-known/jwks.json" 200 '"kty":"RSA"'
# Without a token the protected endpoint must answer 401/403, proving the app and auth wiring are up.
check "auth is enforced"  "$BASE_URL/v0/auth/me"          "401|403"

echo "Smoke tests passed"
