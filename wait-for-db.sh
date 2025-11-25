#!/bin/sh
# wait until Postgres is ready
while ! pg_isready -h db -U $POSTGRES_USER; do
  echo "Waiting for Postgres..."
  sleep 2
done