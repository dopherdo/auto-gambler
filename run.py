#!/usr/bin/env python3
"""
Main launcher script for Auto Gambler.
Can run Discord bot, scraper, or manual testing based on command line arguments.
"""

import sys
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'DISCORD_TOKEN',
        'DISCORD_SERVER_ID', 
        'DISCORD_CHANNEL_ID',
        'PRIZEPICKS_EMAIL',
        'PRIZEPICKS_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set up your .env file using env_example.txt as a template.")
        return False
    
    return True

def check_scraper_environment():
    """Check if environment variables are set for scraper (only Discord needed)."""
    required_vars = [
        'DISCORD_TOKEN',
        'DISCORD_SERVER_ID', 
        'DISCORD_CHANNEL_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables for scraper:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set up your .env file using env_example.txt as a template.")
        return False
    
    return True

def main():
    """Main function."""
    print("🤖 Auto Gambler - PrizePicks Automation")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run.py bot          # Start Discord bot")
        print("  python run.py scraper      # Start Discord scraper")
        print("  python run.py test         # Start manual testing")
        print("  python run.py test-scraper # Test scraper functionality")
        print("  python run.py check        # Check environment setup")
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        print("🔍 Checking environment setup...")
        if check_environment():
            print("✅ Environment setup looks good!")
        else:
            print("❌ Environment setup incomplete.")
        return
    
    elif command == "bot":
        print("🤖 Starting Discord bot...")
        if not check_environment():
            return
        
        try:
            from discord_bot import run_bot
            run_bot()
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
    
    elif command == "scraper":
        print("🔍 Starting Discord scraper...")
        if not check_scraper_environment():
            return
        
        try:
            from scraper.discord_scraper import run_scraper
            run_scraper()
        except KeyboardInterrupt:
            print("\n🛑 Scraper stopped by user")
        except Exception as e:
            print(f"❌ Error starting scraper: {e}")
    
    elif command == "test":
        print("🧪 Starting manual testing...")
        if not check_environment():
            return
        
        try:
            from manual_test import main as test_main
            test_main()
        except KeyboardInterrupt:
            print("\n🛑 Testing stopped by user")
        except Exception as e:
            print(f"❌ Error during testing: {e}")
    
    elif command == "test-scraper":
        print("🧪 Testing scraper functionality...")
        if not check_scraper_environment():
            return
        
        try:
            from scraper.test_scraper import main as scraper_test_main
            scraper_test_main()
        except KeyboardInterrupt:
            print("\n🛑 Scraper testing stopped by user")
        except Exception as e:
            print(f"❌ Error during scraper testing: {e}")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: bot, scraper, test, test-scraper, check")

if __name__ == "__main__":
    main() 