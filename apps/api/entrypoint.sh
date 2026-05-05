#!/bin/sh
set -e

# Run migrations unless --no-migrate is passed
if [ "$1" != "--no-migrate" ]; then
    echo "Running database migrations..."
    uv run --no-sync alembic upgrade head
fi

# If first arg was --no-migrate, shift it off
if [ "$1" = "--no-migrate" ]; then
    shift
fi

exec "$@"
