#!/usr/bin/env python3
"""
Run Django migrations for all services on Railway PostgreSQL.
This script runs migrations directly from local machine.
"""

import os
import sys
import subprocess
from pathlib import Path

# Database configurations
SERVICES = [
    ('customer-service', 'customer_db'),
    ('product-service', 'product_db'),
    ('cart-service', 'cart_db'),
    ('staff-service', 'staff_db'),
    ('manager-service', 'manager_db'),
    ('catalog-service', 'catalog_db'),
    ('order-service', 'order_db'),
    ('ship-service', 'ship_db'),
    ('pay-service', 'pay_db'),
    ('comment-rate-service', 'comment_rate_db'),
    ('recommender-ai-service', 'recommender_db'),
    ('api-gateway', 'gateway_db'),
]

def run_migrations(service_dir, database_url):
    """Run Django migrations for a service"""
    print(f"\n{'='*60}")
    print(f"Migrating {service_dir}")
    print(f"{'='*60}")

    # manage.py is at: <service-dir>/<service_name>/manage.py
    service_name = service_dir.replace('-', '_')
    project_root = Path(__file__).parent.parent.resolve()
    manage_py = project_root / service_dir / service_name / 'manage.py'

    if not manage_py.exists():
        print(f"  ERROR: manage.py not found at {manage_py}")
        return False

    # Set environment variables
    env = os.environ.copy()
    env['DATABASE_URL'] = database_url
    env['DJANGO_SETTINGS_MODULE'] = f'{service_name}.settings'

    # Run migrations
    try:
        result = subprocess.run(
            [sys.executable, str(manage_py), 'migrate', '--noinput'],
            cwd=str(manage_py.parent),
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"  SUCCESS: Migrations completed")
            if result.stdout:
                # Print only important lines
                for line in result.stdout.split('\n'):
                    if 'Applying' in line or 'OK' in line:
                        print(f"    {line}")
            return True
        else:
            print(f"  ERROR: Migration failed")
            print(f"  {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ERROR: Migration timeout")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("ERROR: DATABASE_URL argument required")
        print("Usage: python run_migrations_railway.py <DATABASE_URL>")
        sys.exit(1)

    database_url = sys.argv[1]

    print("="*60)
    print("RUNNING RAILWAY MIGRATIONS")
    print("="*60)
    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    success_count = 0
    fail_count = 0

    for service_dir, db_name in SERVICES:
        # Build database URL for this service
        service_db_url = database_url.rsplit('/', 1)[0] + '/' + db_name

        if run_migrations(service_dir, service_db_url):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Success: {success_count}/{len(SERVICES)}")
    print(f"  Failed:  {fail_count}/{len(SERVICES)}")

    if fail_count > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
