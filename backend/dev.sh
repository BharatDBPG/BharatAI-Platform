# *.bharatai.gov.in entries let you test the domain-scoped `bharatai_token` cookie
# locally via an /etc/hosts alias; browsers discard it when served from `localhost`.
# Respects CORS_ALLOW_ORIGIN if already exported.
export CORS_ALLOW_ORIGIN="http://localhost:5173;http://localhost:8080;http://local.bharatai.gov.in:5173;http://local.bharatai.gov.in:8080"
PORT="${PORT:-8080}"
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-*}" --reload
