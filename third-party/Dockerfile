FROM pgvector/pgvector:0.8.1-pg18-trixie

COPY pg_hba.conf /etc/postgresql/pg_hba.conf
COPY 01_roles_script.sql /docker-entrypoint-initdb.d/
COPY 02_schema_script.sql /docker-entrypoint-initdb.d/
