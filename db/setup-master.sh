#!/bin/bash
echo "host replication all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"
echo "host all all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"

set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $PG_REP_USER REPLICATION LOGIN CONNECTION LIMIT 100 ENCRYPTED PASSWORD '$PG_REP_PASSWORD';
    CREATE TABLE mail (id SERIAL PRIMARY KEY, email VARCHAR(50));
    CREATE TABLE phone (id SERIAL PRIMARY KEY, phone_number VARCHAR(20));

EOSQL

cat >> ${PGDATA}/postgresql.conf <<EOF
log_destination = 'csvlog'
logging_collector = on
log_replication_commands = on
wal_level = hot_standby
archive_mode = on
archive_command = 'cd .'
max_wal_senders = 8
wal_keep_segments = 8
hot_standby = on
log_directory = '/var/log/postgresql/'
log_filename = 'db.log'
EOF