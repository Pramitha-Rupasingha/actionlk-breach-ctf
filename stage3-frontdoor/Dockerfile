FROM php:8.2-apache

# mariadb-server co-located in the container (per report: "not a separately
# networked service" — only Apache's port 80 is ever published to players).
RUN apt-get update && apt-get install -y --no-install-recommends \
        mariadb-server \
        default-mysql-client \
    && docker-php-ext-install mysqli \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /var/www/html/
COPY init.sql /docker-entrypoint-initdb.d/init.sql
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown -R www-data:www-data /var/www/html

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
