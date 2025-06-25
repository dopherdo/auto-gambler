#!/usr/bin/env python3
"""
Manual testing script for PrizePicks automation.
Use this to test each component step by step before running the full automation.
"""

import sys
import time
import logging
from prizepicks_automation import PrizePicksAutomation
import config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_login():
    """Test PrizePicks login functionality."""
    print("\n=== Testing Login ===")
    
    automation = PrizePicksAutomation(headless=False)
    try:
        automation.setup_driver()
        
        # Test login
        success = automation.login()
        if success:
            print("✅ Login successful!")
            return automation
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return None

def test_navigation(automation, test_link):
    """Test navigation to a PrizePicks link."""
    print(f"\n=== Testing Navigation to: {test_link} ===")
    
    try:
        success = automation.navigate_to_link(test_link)
        if success:
            print("✅ Navigation successful!")
            return True
        else:
            print("❌ Navigation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during navigation test: {e}")
        return False

def test_slip_submission(automation):
    """Test slip submission functionality."""
    print("\n=== Testing Slip Submission ===")
    
    try:
        success = automation.submit_slip()
        if success:
            print("✅ Slip submission successful!")
            return True
        else:
            print("❌ Slip submission failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during submission test: {e}")
        return False

def test_full_workflow(test_link):
    """Test the complete workflow from login to submission."""
    print(f"\n=== Testing Full Workflow ===")
    
    automation = None
    try:
        # Step 1: Login
        automation = test_login()
        if not automation:
            return False
        
        # Step 2: Navigate to link
        if not test_navigation(automation, test_link):
            return False
        
        # Step 3: Submit slip
        if not test_slip_submission(automation):
            return False
        
        print("✅ Full workflow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during full workflow test: {e}")
        return False
    finally:
        if automation:
            automation.close()

def interactive_test():
    """Interactive testing mode."""
    print("🤖 PrizePicks Automation Manual Testing")
    print("=" * 50)
    
    while True:
        print("\nChoose a test option:")
        print("1. Test login only")
        print("2. Test navigation (requires login)")
        print("3. Test slip submission (requires navigation)")
        print("4. Test full workflow")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            automation = test_login()
            if automation:
                automation.close()
                
        elif choice == "2":
            test_link = input("Enter PrizePicks link to test: ").strip()
            if test_link:
                automation = test_login()
                if automation:
                    test_navigation(automation, test_link)
                    automation.close()
                    
        elif choice == "3":
            test_link = input("Enter PrizePicks link to test: ").strip()
            if test_link:
                automation = test_login()
                if automation:
                    if test_navigation(automation, test_link):
                        test_slip_submission(automation)
                    automation.close()
                    
        elif choice == "4":
            test_link = input("Enter PrizePicks link to test: ").strip()
            if test_link:
                test_full_workflow(test_link)
                
        elif choice == "5":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == "login":
            automation = test_login()
            if automation:
                automation.close()
        elif sys.argv[1] == "workflow" and len(sys.argv) > 2:
            test_full_workflow(sys.argv[2])
        else:
            print("Usage:")
            print("  python manual_test.py login")
            print("  python manual_test.py workflow <prizepicks_link>")
            print("  python manual_test.py (for interactive mode)")
    else:
        # Interactive mode
        interactive_test()

if __name__ == "__main__":
    main() 