"""
Quick verification script to check all modules load correctly
Run this BEFORE detect_hygiene.py to ensure setup is correct
"""

import sys
from pathlib import Path

print("🔍 Verifying PHASE 1 Setup...")
print("=" * 70)

# Check Python version
print(f"✓ Python Version: {sys.version.split()[0]}")

# Check required packages
packages = {
    'cv2': 'OpenCV',
    'mediapipe': 'MediaPipe',
    'numpy': 'NumPy'
}

all_ok = True
for package, name in packages.items():
    try:
        __import__(package)
        print(f"✓ {name} installed")
    except ImportError:
        print(f"✗ {name} NOT installed")
        all_ok = False

print("=" * 70)

if all_ok:
    print("✅ All dependencies installed successfully!")
    print("\nYou can now run:")
    print("   python backend\\detect_hygiene.py")
else:
    print("❌ Missing dependencies. Install with:")
    print("   pip install -r requirements_phase1.txt")

print("=" * 70)
