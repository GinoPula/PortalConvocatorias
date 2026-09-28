#!/bin/sh
set -e

{
  echo "window.__API_BASE__ = \"${API_BASE}\";"
  echo "window.__RECAPTCHA_SITE_KEY__ = \"${RECAPTCHA_SITE_KEY}\";"
} > /usr/share/nginx/html/env-config.js

exec "$@"
