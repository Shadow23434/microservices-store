#!/bin/bash
# docker/postgres/init-multiple-db.sh
# Tự động tạo các database được liệt kê trong POSTGRES_MULTIPLE_DATABASES

set -e

function create_database() {
    local database=$1
    echo "  Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        db_trimmed=$(echo "$db" | xargs)  # trim whitespace
        create_database "$db_trimmed"
    done
    echo "Multiple databases created."
fi