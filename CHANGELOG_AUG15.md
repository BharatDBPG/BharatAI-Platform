# BharatAI Platform — Changes & Fixes (August 15, 2026)

## Docker Image
**`akashbhujbal5101/bharatai-platform:v1.4.5`**

---

## Bug Fixed — CERT-In Finding #1 (High Severity)

### Insufficient Session Invalidation on Password Change

**CERT-In Finding:** When a user resets or changes their password, the server updates
credentials in the database but fails to revoke active session tokens on other devices.

**Root Cause:** The `revoked_at` Redis key was only set on new login (concurrent session
control), not on password change. So an attacker with an active session remained logged
in even after the victim changed their password.

**Fix:** In `backend/open_webui/routers/auths.py` — `update_password` endpoint now sets
`revoked_at` in Redis immediately after a successful password update.

```
POST /api/v1/auths/update/password
→ password updated in DB
→ revoked_at = now() written to Redis for that user
→ all existing tokens (iat < revoked_at) immediately invalid
→ user must log in again on all devices
```

**File changed:** `backend/open_webui/routers/auths.py`

---

## CERT-In Audit Status (as of Aug 15)

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 1 | High | Insufficient Session Invalidation (password change) | Fixed in v1.4.5 ✅ |
| 2 | High | CAPTCHA Bypass (client-side only) | Fixed in v1.4.2 ✅ |
| 3 | High | Concurrent user login | Fixed in v1.4.2 ✅ |
| 4 | Medium | HSTS not enabled | Fixed in code (SecurityHeadersMiddleware) ✅ |
| 5 | Medium | Misconfigured CORS | Fixed via CORS_ALLOW_ORIGIN env var ✅ |
| 6 | Low | Missing custom error page | Pending ❌ |
| 7 | Low | CSP not implemented | Fixed in code (SecurityHeadersMiddleware) ✅ |
| 8 | Low | X-Content-Type-Options missing | Fixed in code (SecurityHeadersMiddleware) ✅ |
| 9 | Low | DOMPurify XSS CVE-2026-66010 | Fixed — upgraded to v3.4.13 ✅ |

**All High and Medium findings resolved. Only 1 Low finding pending (custom error page).**

---

## Deployment Plan

1. Deploy `v1.4.5` to **CERT-In reference/test environment** for validation
2. After CERT-In confirms — deploy to **production** (H100 cluster, kp-meity namespace)

### Deploy Command (Reference Env)
> Update image name as per reference env setup.

### Deploy Command (Production — H100)
```bash
kubectl --context chncdacapp01-customer@chncdacapp01 -n kp-meity \
  set image deployment/open-webui-v2 \
  open-webui=akashbhujbal5101/bharatai-platform:v1.4.5
```
