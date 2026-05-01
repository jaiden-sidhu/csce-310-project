"""
Utility script to hash passwords for testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.auth import hash_password

if __name__ == "__main__":
    password = input("Enter password to hash: ")
    hashed = hash_password(password)
    print(f"Hashed password: {hashed}")
    print("\nCopy this hash into the database for testing")
