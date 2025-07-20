#!/usr/bin/env python3
"""
Test Automation - Comprehensive testing for the auto-gambler system
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
import argparse

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from prizepicks_automation import PrizePicksAutomation
from bet_processor import BetProcessor

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class AutomationTester:
    def __init__(self, headless=False):
        self.headless = headless
        self.automation = None
        self.bet_processor = None
        self.test_results = {}
        
    def test_prizepicks_automation(self):
        """Test the PrizePicks automation component."""
        logger.info("🧪 Testing PrizePicks Automation...")
        
        try:
            # Test 1: Initialize automation
            logger.info("  Testing automation initialization...")
            self.automation = PrizePicksAutomation(headless=self.headless)
            self.automation.setup_driver()
            self.test_results['automation_init'] = True
            logger.info("  ✅ Automation initialized successfully")
            
            # Test 2: Login functionality
            logger.info("  Testing login functionality...")
            login_success = self.automation.login()
            self.test_results['login'] = login_success
            if login_success:
                logger.info("  ✅ Login successful")
            else:
                logger.warning("  ⚠️ Login failed - check credentials")
            
            # Test 3: Check if logged in
            logger.info("  Testing login status check...")
            is_logged_in = self.automation.is_logged_in()
            self.test_results['login_status'] = is_logged_in
            if is_logged_in:
                logger.info("  ✅ Login status verified")
            else:
                logger.warning("  ⚠️ Not logged in")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Automation test failed: {e}")
            self.test_results['automation_init'] = False
            return False
    
    def test_link_validation(self, test_links):
        """Test link validation functionality."""
        logger.info("🧪 Testing Link Validation...")
        
        try:
            from bet_processor import BetProcessor
            processor = BetProcessor()
            
            for i, link in enumerate(test_links, 1):
                logger.info(f"  Testing link {i}: {link}")
                is_valid = processor.validate_link(link)
                self.test_results[f'link_validation_{i}'] = is_valid
                
                if is_valid:
                    logger.info(f"  ✅ Link {i} is valid")
                else:
                    logger.warning(f"  ⚠️ Link {i} is invalid")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Link validation test failed: {e}")
            return False
    
    def test_bet_processor(self):
        """Test the bet processor component."""
        logger.info("🧪 Testing Bet Processor...")
        
        try:
            # Test 1: Initialize bet processor
            logger.info("  Testing bet processor initialization...")
            self.bet_processor = BetProcessor(headless=self.headless, auto_place_bets=False)
            init_success = self.bet_processor.initialize_automation()
            self.test_results['bet_processor_init'] = init_success
            
            if init_success:
                logger.info("  ✅ Bet processor initialized successfully")
            else:
                logger.warning("  ⚠️ Bet processor initialization failed")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Bet processor test failed: {e}")
            self.test_results['bet_processor_init'] = False
            return False
    
    def test_sample_link_processing(self, test_link):
        """Test processing a sample link (without placing bet)."""
        logger.info("🧪 Testing Sample Link Processing...")
        
        if not self.automation:
            logger.error("  ❌ Automation not initialized")
            return False
        
        try:
            logger.info(f"  Testing navigation to: {test_link}")
            
            # Test navigation
            nav_success = self.automation.navigate_to_link(test_link)
            self.test_results['link_navigation'] = nav_success
            
            if nav_success:
                logger.info("  ✅ Link navigation successful")
                
                # Test slip verification
                slip_verified = self.automation.verify_slip_details()
                self.test_results['slip_verification'] = slip_verified
                
                if slip_verified:
                    logger.info("  ✅ Slip details verified")
                else:
                    logger.warning("  ⚠️ Slip verification failed")
                
                # Test unit size setting (without submitting)
                unit_success = self.automation.set_unit_size(config.DEFAULT_UNIT_SIZE)
                self.test_results['unit_size_setting'] = unit_success
                
                if unit_success:
                    logger.info(f"  ✅ Unit size set to {config.DEFAULT_UNIT_SIZE}")
                else:
                    logger.warning("  ⚠️ Unit size setting failed")
                
            else:
                logger.warning("  ⚠️ Link navigation failed")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Sample link processing test failed: {e}")
            return False
    
    def test_configuration(self):
        """Test configuration settings."""
        logger.info("🧪 Testing Configuration...")
        
        try:
            # Test required environment variables
            required_vars = [
                'DISCORD_TOKEN',
                'DISCORD_SERVER_ID', 
                'DISCORD_CHANNEL_ID',
                'PRIZEPICKS_EMAIL',
                'PRIZEPICKS_PASSWORD'
            ]
            
            missing_vars = []
            for var in required_vars:
                value = getattr(config, var, None)
                if not value:
                    missing_vars.append(var)
                else:
                    self.test_results[f'config_{var}'] = True
            
            if missing_vars:
                logger.warning(f"  ⚠️ Missing configuration variables: {missing_vars}")
                for var in missing_vars:
                    self.test_results[f'config_{var}'] = False
            else:
                logger.info("  ✅ All required configuration variables present")
            
            # Test automation settings
            self.test_results['config_auto_place'] = config.AUTO_PLACE_BETS
            self.test_results['config_unit_size'] = config.DEFAULT_UNIT_SIZE
            
            logger.info(f"  ✅ Auto-place bets: {config.AUTO_PLACE_BETS}")
            logger.info(f"  ✅ Default unit size: {config.DEFAULT_UNIT_SIZE}")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Configuration test failed: {e}")
            return False
    
    def run_comprehensive_test(self, test_link=None):
        """Run all tests in sequence."""
        logger.info("🚀 Starting Comprehensive Automation Test Suite")
        logger.info("=" * 60)
        
        # Test 1: Configuration
        self.test_configuration()
        
        # Test 2: Link validation
        test_links = [
            "https://prizepicks.com/some-valid-link",
            "https://app.prizepicks.com/another-link",
            "https://prizepicks.onelink.me/test-link",
            "https://invalid-site.com/not-prizepicks"
        ]
        self.test_link_validation(test_links)
        
        # Test 3: PrizePicks automation
        automation_success = self.test_prizepicks_automation()
        
        # Test 4: Bet processor
        self.test_bet_processor()
        
        # Test 5: Sample link processing (if automation worked and link provided)
        if automation_success and test_link:
            self.test_sample_link_processing(test_link)
        
        # Print summary
        self.print_test_summary()
        
        # Cleanup
        self.cleanup()
        
        return self.test_results
    
    def print_test_summary(self):
        """Print a summary of test results."""
        logger.info("=" * 60)
        logger.info("📊 Test Results Summary")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
        
        if failed_tests > 0:
            logger.warning("\n⚠️ Some tests failed. Please check the configuration and try again.")
        else:
            logger.info("\n🎉 All tests passed! The automation system is ready to use.")
    
    def cleanup(self):
        """Clean up resources."""
        if self.automation:
            self.automation.close()
        if self.bet_processor:
            self.bet_processor.close()

def create_test_environment():
    """Create a test environment with sample data."""
    logger.info("🔧 Creating Test Environment...")
    
    # Create test directories
    test_dirs = ['scraped', 'results', 'screenshots', 'logs']
    for dir_name in test_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logger.info(f"  Created directory: {dir_name}")
    
    # Create sample scraped data
    sample_data = [
        {
            'id': '123456789',
            'author': 'TestUser',
            'content': 'Check out this pick: https://prizepicks.com/sample-link-1',
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': '123456790',
            'author': 'AnotherUser',
            'content': 'Here\'s another one: https://app.prizepicks.com/sample-link-2',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    sample_file = 'scraped/sample_test_data.json'
    with open(sample_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    logger.info(f"  Created sample data: {sample_file}")
    return sample_file

def main():
    parser = argparse.ArgumentParser(description="Test the auto-gambler automation system")
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    parser.add_argument('--test-link', type=str, help='Test link to process (optional)')
    parser.add_argument('--create-env', action='store_true', help='Create test environment')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    
    args = parser.parse_args()
    
    headless = args.headless and not args.no_headless
    
    if args.create_env:
        create_test_environment()
        return
    
    # Run tests
    tester = AutomationTester(headless=headless)
    
    if args.quick:
        logger.info("🏃 Running Quick Tests...")
        tester.test_configuration()
        tester.test_link_validation(["https://prizepicks.com/test"])
    else:
        tester.run_comprehensive_test(args.test_link)

if __name__ == "__main__":
    main() 