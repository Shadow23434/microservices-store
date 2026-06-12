#!/usr/bin/env python3
"""
Wrapper script to run seed_all_services.py with Railway environment variables.
Parses DATABASE_URL and sets up the environment for the seed script.
"""

import os
import sys
from urllib.parse import urlparse

# Railway environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
API_URL = os.environ.get('API_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Usage: $env:DATABASE_URL='postgresql://...' python seed_railway_wrapper.py")
    sys.exit(1)

if not API_URL:
    print("ERROR: API_URL environment variable not set")
    print("Usage: $env:API_URL='https://your-app.up.railway.app' python seed_railway_wrapper.py")
    sys.exit(1)

# Parse DATABASE_URL
parsed = urlparse(DATABASE_URL)

# Set environment variables expected by seed_all_services.py
os.environ['POSTGRES_USER'] = parsed.username or 'postgres'
os.environ['POSTGRES_PASSWORD'] = parsed.password or ''
os.environ['POSTGRES_HOST'] = parsed.hostname
os.environ['POSTGRES_PORT'] = str(parsed.port or 5432)

# Override the PRODUCT_SERVICE_URL in seed_all_services.py
import seed_all_services

# Monkey patch the URL
seed_all_services.PRODUCT_SERVICE_URL = f"{API_URL}/api/products/"

print("=" * 60)
print("RAILWAY SEED WRAPPER")
print("=" * 60)
print(f"Database Host: {parsed.hostname}:{parsed.port}")
print(f"API URL: {API_URL}")
print(f"Product API: {seed_all_services.PRODUCT_SERVICE_URL}")
print("=" * 60)

# Run the seed function
try:
    seed_all_services.seed_all()
except KeyboardInterrupt:
    print("\n[WARNING] Seed interrupted by user.")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
