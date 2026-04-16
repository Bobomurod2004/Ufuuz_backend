#!/bin/sh
set -e

APP_USER="${APP_USER:-app}"
APP_GROUP="${APP_GROUP:-app}"

run_manage_command() {
    if [ "$(id -u)" = "0" ]; then
        gosu "${APP_USER}:${APP_GROUP}" python manage.py "$@"
    else
        python manage.py "$@"
    fi
}

if [ "$(id -u)" = "0" ]; then
    mkdir -p /app/media /app/staticfiles /data
    chown -R "${APP_USER}:${APP_GROUP}" /app/media /app/staticfiles /data
fi

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    run_manage_command migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
    run_manage_command collectstatic --noinput
fi

if [ "$(id -u)" = "0" ]; then
    exec gosu "${APP_USER}:${APP_GROUP}" "$@"
fi

exec "$@"
