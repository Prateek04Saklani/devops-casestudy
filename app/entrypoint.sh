#!/bin/sh
set -e
mkdir -p /shared/static
cp -r /app/static/. /shared/static/
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --worker-tmp-dir /tmp app:app