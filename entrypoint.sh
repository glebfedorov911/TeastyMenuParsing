#!/bin/sh
set -e

echo "Waiting connect to database"

until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME"; do
  echo "Waiting access"
  sleep 5
done

echo "Database is available"

echo "Start app"
exec uvicorn src.main:app --host 0.0.0.0 --port 8012 --reload