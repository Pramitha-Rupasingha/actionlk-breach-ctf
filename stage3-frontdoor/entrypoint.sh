#!/bin/bash
set -e

DATADIR="/var/lib/mysql"

if [ ! -d "$DATADIR/mysql" ]; then
    echo "[entrypoint] Initialising MariaDB data directory..."
    mariadb-install-db --user=mysql --datadir="$DATADIR" >/dev/null
fi

echo "[entrypoint] Starting MariaDB..."
service mariadb start

echo "[entrypoint] Waiting for MariaDB to accept connections..."
until mysqladmin ping --silent 2>/dev/null; do
    sleep 1
done

echo "[entrypoint] Ensuring database + app user exist..."
mysql -u root <<-EOSQL
CREATE DATABASE IF NOT EXISTS actionlk_portal;
CREATE USER IF NOT EXISTS 'portal_app'@'localhost' IDENTIFIED BY '${DB_APP_PASSWORD}';
GRANT ALL PRIVILEGES ON actionlk_portal.* TO 'portal_app'@'localhost';
CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY '${DB_ADMIN_PASSWORD}';
FLUSH PRIVILEGES;
EOSQL

if ! mysql -u root actionlk_portal -e "SELECT 1 FROM users LIMIT 1;" >/dev/null 2>&1; then
    echo "[entrypoint] Loading schema + seed data..."
    mysql -u root actionlk_portal < /docker-entrypoint-initdb.d/init.sql
fi

echo "[entrypoint] Starting Apache in the foreground..."
exec apache2-foreground
