#!/usr/bin/env python3
"""
Quick Start Script for PathoTracer v2
This script will set up everything and run the application
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("PathoTracer v2 - Quick Start")
    print("=" * 60)
    
    # Step 1: Run setup
    print("\n📦 Step 1: Setting up project structure...")
    if not run_command("python setup.py", "Project setup"):
        return False
    
    # Step 2: Install dependencies
    print("\n📋 Step 2: Installing dependencies...")
    if not run_command("pip install -r requirements.txt", "Dependencies installation"):
        print("⚠️  You may need to install dependencies manually:")
        print("   pip install -r requirements.txt")
    
    # Step 3: Create environment file
    print("\n🔧 Step 3: Creating environment configuration...")
    if Path('.env.template').exists() and not Path('.env').exists():
        try:
            import shutil
            shutil.copy('.env.template', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your database settings")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    
    # Step 4: Check if we can run the app
    print("\n🚀 Step 4: Checking if we can run the application...")
    
    try:
        import streamlit
        print("✅ Streamlit is available")
        
        # Check if main.py exists
        if Path('main.py').exists():
            print("✅ main.py found")
            
            # Ask user if they want to start the app
            print("\n" + "=" * 60)
            print("🎉 Setup completed successfully!")
            print("=" * 60)
            
            start_app = input("\n🚀 Do you want to start the application now? (y/n): ").lower().strip()
            
            if start_app in ['y', 'yes']:
                print("\n🚀 Starting PathoTracer v2...")
                print("📱 The app will open in your browser at http://localhost:8501")
                print("🛑 Press Ctrl+C to stop the application")
                print("-" * 60)
                
                try:
                    subprocess.run(["streamlit", "run", "main.py"], check=True)
                except KeyboardInterrupt:
                    print("\n\n🛑 Application stopped by user")
                except subprocess.CalledProcessError as e:
                    print(f"\n❌ Failed to start application: {e}")
                    print("\n🔧 To start manually, run:")
                    print("   streamlit run main.py")
            else:
                print("\n🔧 To start the application later, run:")
                print("   streamlit run main.py")
                
        else:
            print("❌ main.py not found")
            print("📝 Please make sure you have all the application files")
            
    except ImportError:
        print("❌ Streamlit not installed")
        print("🔧 Please install dependencies first:")
        print("   pip install -r requirements.txt")
    
    print("\n📖 For more information, see README.md")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Quick start interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Quick start failed: {e}")
        print("🔧 Try running setup manually:")
        print("   python setup.py")
        print("   pip install -r requirements.txt")
        print("   streamlit run main.py")
        sys.exit(1)