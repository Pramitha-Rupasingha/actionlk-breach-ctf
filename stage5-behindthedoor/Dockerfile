FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        vsftpd \
        gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY files/ /app/files/
COPY ftp_hint.txt /app/ftp_hint.txt
COPY vsftpd.conf.template /etc/vsftpd.conf.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# FTP control + passive data port range (must match docker-compose.yml)
EXPOSE 80 21 21100-21110

ENTRYPOINT ["/entrypoint.sh"]
