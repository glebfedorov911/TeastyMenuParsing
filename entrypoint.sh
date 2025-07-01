#!/bin/sh
set -e

echo "Start app"

exec uvicorn src.main:app --host 0.0.0.0 --port 8012 --reload
