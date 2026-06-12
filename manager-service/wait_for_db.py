#!/usr/bin/env python3
"""
Wait for PostgreSQL to be ready before running migrations.
Retries database connection with exponential backoff.
"""
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db(max_retries=30, initial_delay=1):
    """Wait for database to be ready."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)

    # Parse database URL
    parsed = urlparse(database_url)

    db_config = {
        'dbname': parsed.path[1:],  # Remove leading /
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 5432,
    }

    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempting database connection ({attempt}/{max_retries})...")
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("✓ Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            if attempt == max_retries:
                print(f"ERROR: Could not connect after {max_retries} attempts", file=sys.stderr)
                print(f"Last error: {e}", file=sys.stderr)
                sys.exit(1)
            print(f"  Database not ready: {e}")
            print(f"  Waiting {delay}s before retry...")
            time.sleep(delay)
            delay = min(delay * 1.5, 10)  # Exponential backoff, max 10s

if __name__ == '__main__':
    wait_for_db()
