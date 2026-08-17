#!/bin/sh
set -e

echo "window.__API_BASE__ = \"${API_BASE}\";" > /usr/share/nginx/html/env-config.js

exec "$@"
