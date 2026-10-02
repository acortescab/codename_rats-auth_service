# Code Review

- **Branch:** `feature/code-review` (at `develop` @ `4d2ae40`)
- **Date:** 2026-10-02
- **Scope:** `feature/code-review` has no diff against `develop`, so this reviews the current application code: `app/` (routes, services, repositories, models, config), `Dockerfile`, `docker-compose-prod.yml`, `scripts/deploy.sh`, `scripts/rollback.sh` and `.github/workflows/ci_tests.yml`.
- **Not covered:** the test suite and Alembic migrations were not reviewed. Nothing was executed; all findings come from reading the code.

## Summary

| # | Severity | Finding |
|---|----------|---------|
| 1 | High | Plaintext passwords are printed to stdout on registration |
| 2 | High | Refresh tokens are accepted as access tokens |
| 3 | High | Expired or malformed JWTs cause a 500 instead of a 401 |
| 4 | Medium | `/login` rate limit is never applied (decorator order) |
| 5 | Medium | Passwords over 72 bytes can crash bcrypt (500) |
| 6 | Medium | Rollback script does not roll back the image; it can also wipe recent data |
| 7 | Medium | Deploy has no health check or automatic rollback (smoke-tests/rollback jobs commented out) |
| 8 | Medium | Guest login is a bearer credential: `device_id` alone yields tokens |
| 9 | Medium | Refresh-token rotation is not atomic |
| 10 | Low | `.dockerignore` does not exclude `.env` or `secrets/` |
| 11 | Low | Tokens are written to logs; logger name is a string literal |
| 12 | Low | Login leaks account existence through timing |
| 13 | Low | Smaller issues (dead/buggy code, config, conventions) |

---

## High

### 1. Plaintext passwords are printed to stdout
`app/services/player_service.py:40`

```python
print(f"password is {password}")
```

`register_user` prints the user's raw password. Logging goes to stdout and is collected by Docker, so every registration leaves a plaintext password in the container logs (and in any log aggregator behind it).

**Fix:** delete the line. Check existing logs for exposure and consider the affected passwords compromised.

### 2. Refresh tokens are accepted as access tokens
`app/services/auth_service.py:58`, `:122`, `:146`; `app/services/token_service.py:24`, `:74`

`get_player_by_token` only checks that the JWT signature is valid and that `sub` maps to a player. Access and refresh tokens are signed with the same key and have no `type`/`typ` claim, so:

- A 7-day refresh token works on `/me` and `/link-account`, which are meant to take a 30-minute access token. This defeats the short access-token lifetime.
- Refresh tokens are revoked server-side, but `/me` and `/link-account` never check the database. A "revoked" (logged-out) refresh token still authenticates on these endpoints until its `exp`.
- Access tokens carry no `jti`, so they can never be revoked. `/logout` documents "requires refresh token", but nothing enforces that. Passing an access token returns 401 "Invalid token" from the missing `jti`, which is confusing.

**Fix:** add a `type` claim (`access` / `refresh`) and check it in each consumer. For `/me`, `/link-account` and the like, require `type == "access"`. For `/refresh-token` and `/logout`, require `type == "refresh"`. Also check `iss`/`aud`, and add `jti` to access tokens if revocation is needed.

### 3. Expired or malformed JWTs produce a 500
`app/services/token_service.py:102-106`

`decode_token` calls `jwt.decode` directly. PyJWT raises `ExpiredSignatureError` / `InvalidTokenError` (and `DecodeError`) on bad input, but all callers do `if not payload: raise InvalidToken(...)` and the routes catch only `InvalidToken`. The `if not payload` branches are therefore dead code for these cases.

Result: any expired, tampered or garbage token sent to `/me`, `/logout`, `/refresh-token` or `/link-account` returns **500 Internal Server Error** rather than 401. Expiry is the normal case, so clients will hit this regularly after 30 minutes.

**Fix:** catch `jwt.PyJWTError` in `decode_token` and raise `InvalidToken`. Also pass `options={"require": ["exp", "iat", "sub"]}`.

---

## Medium

### 4. `/login` rate limit is never applied
`app/api/v0/routes/auth.py:81-83`

```python
@limiter.limit("20/minute")
@router.post("/login", response_model=LoginResponse)
def login(...)
```

Decorators apply bottom-up. `@router.post` registers the undecorated function first, and the limiter wraps a function that is no longer the registered route. The limit has no effect. `/guest-login` has the correct order (`@router.post` on top). `/register`, `/refresh-token` and `/link-account` have no limit at all.

**Fix:** put `@router.post` above `@limiter.limit`. Add limits to `/register`, `/refresh-token` and `/link-account`, with a stricter limit on `/login` (20/min per IP is generous for credential stuffing). Also, behind the ALB/proxy `get_remote_address` will see the proxy IP. Use trusted `X-Forwarded-For` handling (e.g. uvicorn `--proxy-headers` with `--forwarded-allow-ips`), or all clients share one bucket.

### 5. Long passwords can crash bcrypt
`app/schemas/auth.py:46-49`, `app/core/security.py:21`

`RegisterRequest.password` allows up to 128 **characters**, but bcrypt only handles 72 **bytes**. Recent `bcrypt` releases (4.1+/5.x) raise `ValueError` for longer input, which becomes a 500. Multi-byte characters hit the limit sooner than 72 characters.

**Fix:** enforce the limit in bytes in the validator (`len(v.encode()) <= 72`), or pre-hash with SHA-256 before bcrypt. Also validate `name` (length) and `device_id` (length, non-empty); both are currently unconstrained strings.

### 6. Rollback script does not roll back the image, and may wipe data
`scripts/rollback.sh:8-16`, `scripts/deploy.sh:19`

- `rollback.sh` prefers `.previous-image-tag`, but nothing ever writes that file. `deploy.sh` just overwrites `.current-image-tag` with `$IMAGE_TAG`. The fallback is therefore the *current* (bad) tag, and "rollback" redeploys the image that just failed.
- If `.last-backup-file` exists, the script drops and recreates the production database and restores the pre-deploy dump. Everything written since that backup (registrations, guest accounts, refresh-token rotations, revocations) is lost. This happens even when the failed deploy made no schema change. There is no confirmation and no separation between "roll back the image" and "restore the data".
- In `deploy.sh` the backup is taken with `2>/dev/null` and failure is silently ignored, so a stale `.last-backup-file` from an earlier deploy can be restored later. The backup step also only runs on the 2nd+ deploy (`.current-image-tag` must exist), and backups are never pruned.
- Both scripts download `docker-compose-prod.yml` from the `main` branch on GitHub at deploy time. That may not match the image tag being deployed or rolled back to, and any change on `main` is executed on the host.
- There is no `set -u`/`pipefail`; `$IMAGE_TAG`, `$DB_USER` etc. can silently be empty.

**Fix:** in `deploy.sh`, copy the old tag to `.previous-image-tag` before writing the new one, and write the new tag only after a successful health check. Make DB restore an explicit opt-in (e.g. a flag), because restoring on every rollback discards data. Remove the stderr suppression, delete `.last-backup-file` if the dump fails, and ship the compose file with the release instead of fetching it from `main`.

### 7. Deploy has no health check or automatic rollback
`.github/workflows/ci_tests.yml` (~line 133; commit `fa29241`)

The `smoke-tests` and `rollback` jobs are commented out, so `deploy` is the last job. A bad image goes live with nothing to detect or revert it (and see #6 for why `rollback.sh` would not revert it anyway). The `api` service in `docker-compose-prod.yml` also has no `healthcheck`.

**Fix:** restore the jobs once #6 is fixed. At minimum, add a post-deploy `curl --fail /v0/health` step and a compose healthcheck for `api`.

### 8. `device_id` is effectively a password for guest accounts
`app/api/v0/routes/auth.py:31`, `app/services/player_service.py:17`

`/guest-login` returns a fresh access+refresh token pair to anyone who submits a known `device_id`. There is no secret, no proof of possession, and no check on the format. If a device ID is guessable or leaks (logs, analytics, shared devices), the account can be taken over, and guest accounts can be linked to an email via `/link-account`. Each call also issues a new refresh token family without revoking previous ones.

**Fix:** have the server generate the device identifier (random, high-entropy) and return it once, or require a device secret/attestation. At minimum validate `device_id` as a UUID/min length and rate-limit it (already done for this endpoint).

### 9. Refresh-token rotation is not atomic
`app/services/token_service.py:52-72`

The flow is read token → check `revoked` → create new token (commit) → revoke old token (commit), as separate commits and without a row lock. Two concurrent requests with the same refresh token can both pass the `revoked` check and both receive new valid tokens. That breaks reuse detection (the family is never invalidated) and leaves two live descendants. Also, `revoke_by_jti`'s return value is ignored. It is the atomic compare-and-set that should gate token issuance.

**Fix:** revoke first with the conditional `UPDATE ... WHERE revoked = false` and only issue new tokens when it returns 1 row; otherwise treat as reuse and revoke the family. Do both in one transaction. Reads in this flow also use the *reader* session (`read_db`), so replica lag could cause the check to see stale data. Use the writer for token validation.

---

## Low

### 10. `.dockerignore` does not exclude `.env` or `secrets/`
`.dockerignore:9-10`, `Dockerfile:26`

`.dockerignore` lists `.env/` (a directory) and `.env.*`, but not a plain `.env` file or `secrets/`. `COPY . .` in a local build bakes both `.env` and the dev `secrets/private_key.pem` into the image layers. They are git-ignored, so CI builds from a clean checkout are not affected, but local builds pushed to ECR would be. Add `.env`, `secrets/`, `.git/` and `tests/` to `.dockerignore`. Related: the image runs as root; add a non-root `USER`. `gcc` is installed in the final image only to build wheels; a multi-stage build (or dropping it if wheels suffice) would shrink the image.

### 11. Tokens are logged, and loggers are mis-named
`app/services/auth_service.py:78`, `:153`, `:159`, `:167`; all modules using `logging.getLogger("__name__")`

- Full JWTs are written to the logs on decode failures (`f"... for token: {token}"`). A still-valid token in a log is a credential. Do not log tokens; log `jti`/`sub` or a short prefix at most. The raw `payload` is also logged at `:84`.
- `logging.getLogger("__name__")` passes the literal string `"__name__"`, so every module logs under the same logger name. It should be `logging.getLogger(__name__)`.
- `app/main.py` uses `print()` for lifecycle messages instead of `logging`.

### 12. Login timing leaks whether an email exists
`app/services/auth_service.py:93-101`

When the email is unknown, `login` returns immediately; when it exists, a bcrypt comparison (~100 ms) runs first. Response time reveals registered emails. (Registration also returns 409 "Email is already in use", which allows enumeration directly; that is a common product tradeoff but worth a conscious decision.) **Fix:** run a dummy `verify_password` against a fixed hash when the user is not found.

### 13. Smaller issues

- **Dead/buggy query:** `RefreshTokenRepository.get_by_player_id` (`app/repositories/refresh_token_repository.py:45-47`) filters on `player_id == player_id` (a Python comparison of the argument with itself → always `True`), not `RefreshToken.player_id == player_id`. It returns an arbitrary token. It appears unused; fix or remove it.
- **Type hints are wrong:** `player_id: int` in `TokenService`/repo, but IDs are UUIDs. `family_id: str = None` should be `str | None`.
- **`last_login` update can crash:** `PlayerRepository.update_last_login` dereferences `player` without a `None` check.
- **Naive datetimes:** `RefreshToken.expires_at/created_at` and `Player.created_at/last_login` use `DateTime` (no timezone) but are populated with timezone-aware `datetime.now(timezone.utc)`. A `fix_timezone` migration exists; confirm the models match it (`DateTime(timezone=True)`).
- **`link_account` is not atomic:** it updates the player and then revokes tokens in separate commits, and the "duplicate email" check is check-then-act; the unique constraint on `email` is the real guard but an `IntegrityError` there becomes a 500 (same for `register_user`). Catch `IntegrityError` and map to 409. `link_account` also revokes *all* tokens, including the one the client just used, and returns no new tokens, so the client has to log in again.
- **`/logout` has no `response_model` and returns `None`** (200 with `null`); consider 204. `/logout` revokes a single token but `/login` revokes **all** of a player's tokens, so logging in on one device logs out every other device. Confirm that is intended.
- **Unused/odd imports:** `app/api/v0/routes/auth.py` imports `PlayerService` and `TokenService` from `app.services.auth_service` (re-exports) instead of their own modules; `LoginRequest`/`PlayerServiceDep`/`get_player_service` are partly unused. `JWTAlgorithm` in `app/core/security.py` lists HS* algorithms while the app uses RS256 and never references the enum. `PlayerAccountType`'s docstring says "Encryptation algorithm" (copy/paste).
- **Config:** `Settings.load_secret_key` reads `secrets/private_key.pem` in dev, which crashes with `FileNotFoundError` at import/settings time if the file is missing, before the friendly validation in `lifespan` can run. `jwks` hard-codes `kid: "default"`, which blocks key rotation (the committed `.well-known/jwks.json` file looks like a stale copy of what the endpoint already serves; make sure they cannot diverge). Both `public_key_pem` and `jwks` re-parse the PEM on every call; `decode_token` therefore parses the private key on every request. Cache the public key.
- **Token lifetimes** (30 min / 7 days) are hard-coded in `TokenService`; move them to `Settings`.
- **Startup validation** uses `os.getenv` for the DB URLs while the rest of the config goes through `Settings`; `sys.exit(1)` inside a lifespan handler is abrupt (raise instead).
- **Style:** the codebase mixes CRLF/LF line endings and has trailing whitespace. A `.gitattributes`/formatter (ruff/black) in CI would keep diffs clean.

---

## What looks good

- Passwords are hashed with bcrypt and a per-password salt; password strength rules exist.
- Refresh tokens are stored hashed (SHA-256), with `jti` and a `family_id`, and reuse of a rotated token revokes the whole family. The design is sound; #9 is about making it race-free.
- RS256 with a public JWKS endpoint lets other services verify tokens without the private key.
- `decode_token` pins `algorithms=[...]`, which avoids algorithm-confusion attacks.
- Reader/writer DB split and dependency-injected services/repositories keep the layers easy to test.
- The prod compose file does not publish the Postgres port.

## Suggested order of work

1. Remove the password `print` (#1) and fix JWT error handling (#3). Both are one-to-few-line changes.
2. Add a token `type` claim and enforce it (#2).
3. Fix decorator order and add rate limits (#4), plus password byte-length validation (#5).
4. Fix the deploy/rollback scripts (#6), then restore the CI smoke-test and rollback jobs (#7).
5. Make refresh rotation atomic (#9), then work through the Low items.
