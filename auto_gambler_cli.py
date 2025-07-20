#!/usr/bin/env python3
"""
Auto Gambler CLI - Command line interface for the auto-gambler system
"""

import argparse
import sys
import os
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from scraper.discord_scraper import DiscordScraper
from bet_processor import BetProcessor
from test_automation import AutomationTester

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

def run_discord_scraper():
    """Run the Discord scraper bot."""
    logger.info("🤖 Starting Discord Scraper...")
    
    if not config.DISCORD_TOKEN:
        logger.error("Discord token not found. Please set DISCORD_TOKEN in your environment.")
        return False
    
    try:
        scraper = DiscordScraper()
        scraper.run(config.DISCORD_TOKEN)
        return True
    except Exception as e:
        logger.error(f"Error running Discord scraper: {e}")
        return False

def run_scheduled_scraping():
    """Run scheduled scraping."""
    import asyncio
    
    parser = argparse.ArgumentParser(description="Run scheduled Discord scraping")
    parser.add_argument('--channel', type=str, default=None, help='Channel ID to scrape')
    parser.add_argument('--start', type=str, required=True, help='Start time in HH:MM format')
    args = parser.parse_args()
    
    channel_id = args.channel or config.DISCORD_CHANNEL_ID
    start_time = args.start
    
    logger.info(f"⏰ Starting scheduled scraping at {start_time} for channel {channel_id}")
    
    try:
        scraper = DiscordScraper()
        async def runner():
            await scraper.start(config.DISCORD_TOKEN, reconnect=True)
            await scraper.wait_until_ready()
            await scraper.scheduled_scrape_loop(channel_id, start_time)
            await scraper.close()
        
        asyncio.run(runner())
        return True
    except Exception as e:
        logger.error(f"Error in scheduled scraping: {e}")
        return False

def run_immediate_scraping():
    """Run immediate scraping."""
    import asyncio
    
    parser = argparse.ArgumentParser(description="Run immediate Discord scraping")
    parser.add_argument('--channel', type=str, default=None, help='Channel ID to scrape')
    args = parser.parse_args()
    
    channel_id = args.channel or config.DISCORD_CHANNEL_ID
    
    logger.info(f"🚀 Starting immediate scraping for channel {channel_id}")
    
    try:
        scraper = DiscordScraper()
        async def runner():
            await scraper.start(config.DISCORD_TOKEN, reconnect=True)
            await scraper.wait_until_ready()
            await scraper.run_scraper_now_loop(channel_id)
            await scraper.close()
        
        asyncio.run(runner())
        return True
    except Exception as e:
        logger.error(f"Error in immediate scraping: {e}")
        return False

def process_scraped_file():
    """Process a scraped file and place bets."""
    parser = argparse.ArgumentParser(description="Process scraped PrizePicks links")
    parser.add_argument('file', help='Path to scraped links JSON file')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--auto-place', action='store_true', help='Automatically place bets')
    parser.add_argument('--unit-size', type=int, help='Unit size for bets')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    args = parser.parse_args()
    
    headless = args.headless and not args.no_headless
    auto_place = args.auto_place if args.auto_place is not None else config.AUTO_PLACE_BETS
    unit_size = args.unit_size if args.unit_size is not None else config.DEFAULT_UNIT_SIZE
    
    logger.info(f"📁 Processing file: {args.file}")
    logger.info(f"🤖 Auto-place: {auto_place}")
    logger.info(f"💰 Unit size: {unit_size}")
    
    try:
        from bet_processor import process_scraped_file as process_file
        process_file(args.file, headless=headless, auto_place=auto_place, unit_size=unit_size)
        return True
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return False

def place_single_bet():
    """Place a single bet from a link."""
    parser = argparse.ArgumentParser(description="Place a single bet from a PrizePicks link")
    parser.add_argument('link', help='PrizePicks link to place bet from')
    parser.add_argument('--unit-size', type=int, default=config.DEFAULT_UNIT_SIZE, help='Unit size for bet')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    args = parser.parse_args()
    
    headless = args.headless and not args.no_headless
    
    logger.info(f"🎯 Placing bet for link: {args.link}")
    logger.info(f"💰 Unit size: {args.unit_size}")
    
    try:
        processor = BetProcessor(headless=headless, auto_place_bets=True)
        
        if not processor.initialize_automation():
            logger.error("Failed to initialize automation")
            return False
        
        link_data = {
            'link': args.link,
            'message_id': 'manual',
            'author': 'CLI',
            'timestamp': datetime.now().isoformat()
        }
        
        result = processor.place_bet(link_data, args.unit_size)
        
        if result['success']:
            logger.info("✅ Bet placed successfully!")
        else:
            logger.error(f"❌ Failed to place bet: {result.get('error', 'Unknown error')}")
        
        processor.close()
        return result['success']
        
    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        return False

def run_tests():
    """Run the test suite."""
    parser = argparse.ArgumentParser(description="Run automation tests")
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    parser.add_argument('--test-link', type=str, help='Test link to process')
    parser.add_argument('--create-env', action='store_true', help='Create test environment')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    args = parser.parse_args()
    
    headless = args.headless and not args.no_headless
    
    logger.info("🧪 Running automation tests...")
    
    try:
        tester = AutomationTester(headless=headless)
        
        if args.create_env:
            from test_automation import create_test_environment
            create_test_environment()
            return True
        
        if args.quick:
            tester.test_configuration()
            tester.test_link_validation(["https://prizepicks.com/test"])
        else:
            tester.run_comprehensive_test(args.test_link)
        
        return True
        
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False

def show_status():
    """Show system status and configuration."""
    logger.info("📊 Auto Gambler System Status")
    logger.info("=" * 50)
    
    # Configuration status
    logger.info("Configuration:")
    logger.info(f"  Discord Token: {'✅ Set' if config.DISCORD_TOKEN else '❌ Missing'}")
    logger.info(f"  Discord Server ID: {'✅ Set' if config.DISCORD_SERVER_ID else '❌ Missing'}")
    logger.info(f"  Discord Channel ID: {'✅ Set' if config.DISCORD_CHANNEL_ID else '❌ Missing'}")
    logger.info(f"  PrizePicks Email: {'✅ Set' if config.PRIZEPICKS_EMAIL else '❌ Missing'}")
    logger.info(f"  PrizePicks Password: {'✅ Set' if config.PRIZEPICKS_PASSWORD else '❌ Missing'}")
    
    logger.info("\nAutomation Settings:")
    logger.info(f"  Auto-place bets: {'✅ Enabled' if config.AUTO_PLACE_BETS else '❌ Disabled'}")
    logger.info(f"  Default unit size: {config.DEFAULT_UNIT_SIZE}")
    logger.info(f"  Max unit size: {config.MAX_UNIT_SIZE}")
    
    logger.info("\nTiming Settings:")
    logger.info(f"  Morning time: {config.MORNING_TIME}")
    logger.info(f"  Afternoon time: {config.AFTERNOON_TIME}")
    logger.info(f"  Timezone: {config.TIMEZONE}")
    
    # Check directories
    logger.info("\nDirectories:")
    dirs_to_check = ['scraped', 'results', 'screenshots', 'logs']
    for dir_name in dirs_to_check:
        exists = os.path.exists(dir_name)
        status = "✅ Exists" if exists else "❌ Missing"
        logger.info(f"  {dir_name}: {status}")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Auto Gambler - Automated PrizePicks betting from Discord links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Discord scraper bot
  python auto_gambler_cli.py scraper

  # Run scheduled scraping at 8 AM
  python auto_gambler_cli.py scheduled --start 08:00

  # Run immediate scraping for 10 minutes
  python auto_gambler_cli.py immediate

  # Process a scraped file
  python auto_gambler_cli.py process scraped/messages.json --auto-place

  # Place a single bet
  python auto_gambler_cli.py bet "https://prizepicks.com/link" --unit-size 2

  # Run tests
  python auto_gambler_cli.py test --no-headless

  # Show system status
  python auto_gambler_cli.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scraper command
    scraper_parser = subparsers.add_parser('scraper', help='Run Discord scraper bot')
    
    # Scheduled command
    scheduled_parser = subparsers.add_parser('scheduled', help='Run scheduled scraping')
    scheduled_parser.add_argument('--channel', type=str, help='Channel ID to scrape')
    scheduled_parser.add_argument('--start', type=str, required=True, help='Start time in HH:MM format')
    
    # Immediate command
    immediate_parser = subparsers.add_parser('immediate', help='Run immediate scraping')
    immediate_parser.add_argument('--channel', type=str, help='Channel ID to scrape')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process scraped file')
    process_parser.add_argument('file', help='Path to scraped links JSON file')
    process_parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    process_parser.add_argument('--auto-place', action='store_true', help='Automatically place bets')
    process_parser.add_argument('--unit-size', type=int, help='Unit size for bets')
    process_parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    
    # Bet command
    bet_parser = subparsers.add_parser('bet', help='Place a single bet')
    bet_parser.add_argument('link', help='PrizePicks link to place bet from')
    bet_parser.add_argument('--unit-size', type=int, help='Unit size for bet')
    bet_parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    bet_parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run automation tests')
    test_parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    test_parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    test_parser.add_argument('--test-link', type=str, help='Test link to process')
    test_parser.add_argument('--create-env', action='store_true', help='Create test environment')
    test_parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    success = False
    
    if args.command == 'scraper':
        success = run_discord_scraper()
    elif args.command == 'scheduled':
        success = run_scheduled_scraping()
    elif args.command == 'immediate':
        success = run_immediate_scraping()
    elif args.command == 'process':
        success = process_scraped_file()
    elif args.command == 'bet':
        success = place_single_bet()
    elif args.command == 'test':
        success = run_tests()
    elif args.command == 'status':
        success = show_status()
    
    if success:
        logger.info("✅ Command completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Command failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 