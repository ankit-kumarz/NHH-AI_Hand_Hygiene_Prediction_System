#!/bin/bash

# Hand Hygiene Compliance System - Database Initialization Script
# Creates SQLite database with all required tables

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "=========================================="
echo "Database Initialization"
echo "=========================================="
echo ""

# Check if Python exists
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "✗ Python is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Use python3 or python depending on what's available
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Initializing SQLite database..."
cd "$BACKEND_DIR"

# Create database by importing the module
$PYTHON_CMD << 'EOF'
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from database import db
    print("✓ Database initialized successfully")
    print(f"✓ Database file: {db.db_path}")
    
    # Print database info
    stats = db.get_overall_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total Employees: {stats.get('total_employees', 0)}")
    print(f"  Total Events: {stats.get('total_events', 0)}")
    
except Exception as e:
    print(f"✗ Error initializing database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Database initialization complete"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Populate with mock data:"
    echo "     python scripts/populate_mock_data.py"
    echo "  2. Start the system:"
    echo "     ./start.sh"
    echo ""
else
    echo ""
    echo "✗ Database initialization failed"
    exit 1
fi
