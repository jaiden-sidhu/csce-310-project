"""
Setup and Run Guide for Online Bookstore Application

This script helps with setting up and running the application.
"""

import sys
import os
import subprocess
import platform

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_mysql():
    """Check if MySQL is installed and accessible"""
    print_header("Checking MySQL Connection")
    try:
        import mysql.connector
        print("✓ mysql-connector-python is installed")
        return True
    except ImportError:
        print("✗ mysql-connector-python not found")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("\n✗ Failed to install dependencies")
        return False

def start_backend():
    """Start Flask backend server"""
    print_header("Starting Backend Server")
    print("Starting Flask server on http://localhost:5000...")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.call([sys.executable, "-m", "backend.app"])
    except KeyboardInterrupt:
        print("\n\nBackend server stopped")

def start_frontend():
    """Start Tkinter frontend"""
    print_header("Starting Frontend Application")
    print("Launching GUI application...\n")
    
    try:
        subprocess.call([sys.executable, "frontend/gui.py"])
    except Exception as e:
        print(f"Error starting frontend: {e}")

def print_setup_instructions():
    """Print setup instructions"""
    print_header("SETUP INSTRUCTIONS")
    
    instructions = """
1. DATABASE SETUP:
   - Open MySQL Command Line or MySQL Workbench
   - Run: CREATE DATABASE Project;
   - Copy and paste all commands from 'schema.sql' file
   - This will create tables and sample data

2. CONFIGURATION:
   - Edit 'config.py' if using different MySQL credentials
   - Default: user='root', password='lpsfrisco'

3. DEPENDENCIES:
   - Run: python setup_and_run.py
   - Select option 1 to install dependencies

4. RUNNING THE APPLICATION:
   - In Terminal 1: Start backend server (option 2)
   - In Terminal 2: Start frontend (option 3)

5. LOGIN AND TEST:
   - Use registration to create new account (recommended)
   - Or use sample credentials from README.md
   - Test customer and manager features

6. GENERATING TEST PASSWORDS:
   - Run: python hash_password.py
   - Use for updating test accounts in database
"""
    print(instructions)

def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("  Online Bookstore - Setup and Run Guide")
        print("="*60)
        print("\nSelect an option:")
        print("  1. Install Dependencies")
        print("  2. Start Backend Server")
        print("  3. Start Frontend Application")
        print("  4. Setup Instructions")
        print("  5. Generate Password Hash (for testing)")
        print("  6. Exit")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            install_dependencies()
        elif choice == "2":
            start_backend()
        elif choice == "3":
            start_frontend()
        elif choice == "4":
            print_setup_instructions()
        elif choice == "5":
            subprocess.call([sys.executable, "hash_password.py"])
        elif choice == "6":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    print_header("Welcome to Online Bookstore Setup")
    print("""
This script will help you:
- Install required Python packages
- Start the backend Flask server
- Launch the frontend Tkinter GUI
- Get setup instructions

Choose an option from the menu below.
    """)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted. Goodbye!")
        sys.exit(0)
