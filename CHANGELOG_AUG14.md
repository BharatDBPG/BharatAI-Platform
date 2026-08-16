# BharatAI Platform — Changes & Fixes (August 14, 2026)

## Summary
Full day of bug fixes, deployments, and platform stabilisation. Production is now on **v1.4.3** (stable). **v1.4.4** is built and pushed, pending deploy after demo (after 11 AM).

---

## Bugs Fixed

### 1. Normal Login — 500 Internal Server Error
- **Cause:** `BHARATAI_COOKIE_DOMAIN` had a hardcoded default of `.bharatai.gov.in` in `env.py`. The Vaarta cookie-setting block ran on every login and threw an unhandled exception.
- **Fix:** Removed all Vaarta/bharatai_token cookie code from 4 files:
  - `backend/open_webui/env.py`
  - `backend/open_webui/routers/auths.py`
  - `backend/open_webui/utils/auth.py`
  - `backend/open_webui/utils/oauth.py`

### 2. Parichay Users Getting "Account Activation Pending"
- **Cause:** DB config has `DEFAULT_USER_ROLE=pending` which overrides the env var. `get_user_role()` was returning `pending` for new OAuth users.
- **Fix:** In `oauth.py`, after `get_user_role()`, if result is `pending` → force to `user`. Applied for both new and existing Parichay users. Existing admins unaffected (their role is `admin`, not `pending`).

### 3. CAPTCHA `.decode()` Error — Normal Login 500
- **Cause:** Redis client returning `str` instead of `bytes` for the CAPTCHA value. Calling `.decode()` on a `str` raises `AttributeError`.
- **Fix:** `auths.py` line 158 — `stored_str = stored if isinstance(stored, str) else stored.decode()`

### 4. "Invalid Token" After Normal Login — No Models, No Chats
- **Cause:** Concurrent session control code sets `revoked_at = int(time.time())` at login. New token's `iat` is the same timestamp. Check `iat <= revoked_at` → True → immediately revoked the brand-new token.
- **Fix:** `auth.py` — changed `<=` to `<`. Old tokens (iat < revoked_at) still revoked. New token (iat == revoked_at) stays valid.

### 5. Functions/Pipes Not Working (ASR, TTS, MT, OCR etc.)
- **Cause:** `ENABLE_RISK_TOOL_EXEC=False` in deployment — blocking all pipe/function execution.
- **Fix:** Added `ENABLE_RISK_TOOL_EXEC=true` env var to deployment. All functions now visible and executable.

---

## Features Removed

### Vaarta Meeting Notes Button (Sidebar)
- Removed from `src/lib/components/layout/Sidebar.svelte` — both collapsed and expanded sidebar views.
- Removed `VAARTA_URL` constant and related comment from `src/routes/auth/+page.svelte`.
- **Reason:** Vaarta team wants full OIDC integration (separate from OpenWebUI). Recommendation: both platforms integrate independently with Parichay as the common IDP.

---

## Improvements Added

### OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true
- **Why:** If an existing user (normal login) logs in via Parichay with the same email, they get merged into the same account — all chats and history preserved. Without this, a second duplicate account would be created.
- **Applied:** As env var in deployment.

---

## Pending — Deploy After Demo (After 11 AM)

### v1.4.4 — Parichay Back Button Fix
- **Issue:** Clicking back on the Parichay staging login page stays on staging server instead of returning to bharatai.gov.in.
- **Fix:** Changed `window.location.href` to `window.location.replace()` in `src/routes/auth/+page.svelte` line 950. This replaces the history entry instead of adding one — back button goes to previous page correctly.
- **Image:** `akashbhujbal5101/bharatai-platform:v1.4.4`
- **Digest:** `sha256:ea5f92f8b2c041d5b9f37f61e0200aaaa4796313b906625ef1a7997e5dd46ac6`
- **Deploy command:**
```bash
kubectl --context chncdacapp01-customer@chncdacapp01 -n kp-meity set image deployment/open-webui-v2 open-webui=akashbhujbal5101/bharatai-platform:v1.4.4
```

---

## Current Production State (as of Aug 14 EOD)

| Item | Status |
|------|--------|
| Image | v1.4.3 |
| Normal login | Working ✅ |
| Parichay login (staging) | Working ✅ |
| Functions (ASR/TTS/MT/OCR) | Working ✅ |
| Vaarta button | Removed ✅ |
| Account merge (same email) | Enabled ✅ |
| Back button fix | v1.4.4 pending deploy |

## Environment Variables Added to Deployment (Aug 14)

| Variable | Value | Purpose |
|----------|-------|---------|
| `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` | `true` | Merge existing accounts on Parichay login |
| `ENABLE_RISK_TOOL_EXEC` | `true` | Enable pipe/filter function execution |

---

## Full Deployment Env Vars (Current State)

| Variable | Value |
|----------|-------|
| `BHARATAI_COOKIE_DOMAIN` | `.bharatai.gov.in` *(legacy, unused in v1.4.3+)* |
| `BHARATAI_COOKIE_NAME` | `bharatai_token` *(legacy, unused in v1.4.3+)* |
| `CORS_ALLOW_ORIGIN` | `https://bharatai.gov.in;https://vaarta.bharatai.gov.in` |
| `DATABASE_POOL_MAX_OVERFLOW` | `20` |
| `DATABASE_POOL_RECYCLE` | `3600` |
| `DATABASE_POOL_SIZE` | `60` |
| `DATABASE_POOL_TIMEOUT` | `30` |
| `DATABASE_USER_ACTIVE_STATUS_UPDATE_INTERVAL` | `300` |
| `DEFAULT_USER_ROLE` | `user` |
| `ENABLE_COMPRESSION_MIDDLEWARE` | `false` |
| `ENABLE_DB_MIGRATIONS` | `false` |
| `ENABLE_FORWARD_USER_INFO_HEADERS` | `True` |
| `ENABLE_OAUTH_SIGNUP` | `True` |
| `ENABLE_ORJSON` | `True` |
| `ENABLE_RAG_HYBRID_SEARCH` | `True` |
| `ENABLE_RISK_TOOL_EXEC` | `true` |
| `ENABLE_SIGNUP` | `False` |
| `ENABLE_WEBSOCKET_SUPPORT` | `true` |
| `HF_HUB_DISABLE_XET` | `1` |
| `MAX_UPLOAD_SIZE` | `260` |
| `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` | `true` |
| `OPENAI_API_BASE_URL` | `http://litellm-replica.kp-meity.svc.cluster.local:4000/v1` |
| `OPENAI_API_KEY` | `sk-litellm-master-key` |
| `PARICHAY_API_URL` | `https://parichay.staging.nic.in` *(switch to prod after go-live)* |
| `PARICHAY_CLIENT_ID` | `BharatAIPlatformds35gfDoh76PgycA` |
| `PARICHAY_CLIENT_SECRET` | `9N40MDWplIDeNj0Nahj3cdZtGP1VMTDn` *(staging — update for prod)* |
| `PARICHAY_REDIRECT_URI` | `https://bharatai.gov.in/oauth/parichay/callback` |
| `PDF_EXTRACT_IMAGES` | `False` |
| `QDRANT_URI` | `http://qdrant.kp-meity.svc.cluster.local:6333` |
| `RAG_CHUNK_OVERLAP` | `100` |
| `RAG_CHUNK_SIZE` | `3000` |
| `RAG_CONCURRENT_TASKS` | `8` |
| `RAG_EMBEDDING_BATCH_SIZE` | `256` |
| `RAG_EMBEDDING_ENGINE` | `openai` |
| `RAG_EMBEDDING_MODEL` | `bge-m3` |
| `RAG_OPENAI_API_BASE_URL` | `http://bge-m3-embedding.kp-meity.svc.cluster.local:8000/v1` |
| `RAG_RERANKING_MODEL` | `BAAI/bge-reranker-v2-m3` |
| `REDIS_URL` | `redis://redis.kp-meity.svc.cluster.local:6379/0` |
| `S3_BUCKET_NAME` | `user-uploads` |
| `S3_ENDPOINT_URL` | `http://10.185.27.73:9000` |
| `SENTENCE_TRANSFORMERS_HOME` | `/app/backend/data/cache/embedding` |
| `STORAGE_LOCAL_CACHE` | `false` |
| `STORAGE_PROVIDER` | `s3` |
| `THREAD_POOL_SIZE` | `2000` |
| `VECTOR_DB` | `qdrant` |
| `WEBSOCKET_MANAGER` | `redis` |
| `WEBUI_AUTH` | `True` |
| `WEBUI_NAME` | `India AI LLM` |

> **Note for prod Parichay switch:** Update `PARICHAY_API_URL` → prod URL and `PARICHAY_CLIENT_SECRET` → `DeNj0Nahj3cdZtGP19N40MDWplIVMTDn`

---

## Known Issue — Browser Cache After Deployment

**Symptom:** Some users see old UI (CAPTCHA not loading, old JS) after a new deployment. Other users on fresh browsers are unaffected.

**Cause:** Browsers aggressively cache JS bundles. Users who visited bharatai.gov.in before the deployment have the old bundle cached.

**Immediate workaround:** Hard refresh — `Ctrl + Shift + R` on bharatai.gov.in. Do this on Sir's browser before any demo.

**Permanent fix (pending):** Set proper `Cache-Control` headers at the Nginx/Ingress level so browsers always fetch fresh JS on new deployments. Requires Nginx/Ingress config change — to be done after demo in a maintenance window.

