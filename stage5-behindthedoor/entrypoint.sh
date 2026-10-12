#!/bin/bash
set -e

FTP_USER="${FTP_USER:-filesvc}"
FTP_PASSWORD="${FTP_PASSWORD:-changeme}"
PASV_ADDRESS="${PASV_ADDRESS:-127.0.0.1}"

if ! id "$FTP_USER" >/dev/null 2>&1; then
    echo "[entrypoint] Creating FTP user '$FTP_USER'..."
    useradd -m -d "/home/$FTP_USER" -s /usr/sbin/nologin "$FTP_USER"
fi
echo "${FTP_USER}:${FTP_PASSWORD}" | chpasswd

mkdir -p "/home/$FTP_USER"
cp /app/ftp_hint.txt "/home/$FTP_USER/hint.txt"
chown root:root "/home/$FTP_USER" "/home/$FTP_USER/hint.txt"
chmod 755 "/home/$FTP_USER"
chmod 644 "/home/$FTP_USER/hint.txt"

mkdir -p /var/run/vsftpd/empty
PASV_ADDRESS="$PASV_ADDRESS" envsubst '${PASV_ADDRESS}' \
    < /etc/vsftpd.conf.template > /etc/vsftpd.conf

echo "[entrypoint] Starting vsftpd..."
vsftpd /etc/vsftpd.conf &

echo "[entrypoint] Starting Flask file portal on :80..."
exec python3 app.py
