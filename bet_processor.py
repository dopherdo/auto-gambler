#!/usr/bin/env python3
"""
Bet Processor - Handles processing scraped PrizePicks links and placing bets
"""

import json
import os
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from prizepicks_automation import PrizePicksAutomation

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class BetProcessor:
    def __init__(self, headless=False, auto_place_bets=None):
        self.headless = headless
        self.auto_place_bets = auto_place_bets if auto_place_bets is not None else config.AUTO_PLACE_BETS
        self.automation = None
        self.processed_links = set()
        self.successful_bets = []
        self.failed_bets = []
        
    def initialize_automation(self):
        """Initialize the PrizePicks automation."""
        try:
            self.automation = PrizePicksAutomation(headless=self.headless)
            self.automation.setup_driver()
            
            # Try to load cookies first
            if not self.automation.load_cookies():
                logger.info("No saved cookies found, attempting login...")
                if not self.automation.login():
                    logger.error("Failed to login to PrizePicks")
                    return False
            
            logger.info("PrizePicks automation initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing automation: {e}")
            return False
    
    def load_scraped_links(self, filepath: str) -> List[Dict]:
        """Load scraped links from a JSON file."""
        try:
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract links from the data structure
            links = []
            if isinstance(data, list):
                # If it's a list of messages, extract links from each message
                for message in data:
                    content = message.get('content', '')
                    for pattern in [
                        r'https?://prizepicks\.com/[^\s]+',
                        r'https?://.*prizepicks.*[^\s]+',
                        r'https?://prizepicks\.onelink\.me/[^\s]+'
                    ]:
                        import re
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            links.append({
                                'link': match,
                                'message_id': message.get('id'),
                                'author': message.get('author'),
                                'timestamp': message.get('timestamp')
                            })
            else:
                # If it's already a list of links
                links = data
            
            logger.info(f"Loaded {len(links)} links from {filepath}")
            return links
            
        except Exception as e:
            logger.error(f"Error loading scraped links: {e}")
            return []
    
    def filter_new_links(self, links: List[Dict]) -> List[Dict]:
        """Filter out links that have already been processed."""
        new_links = []
        for link_data in links:
            link = link_data['link']
            if link not in self.processed_links:
                new_links.append(link_data)
                self.processed_links.add(link)
        
        logger.info(f"Found {len(new_links)} new links out of {len(links)} total")
        return new_links
    
    def validate_link(self, link: str) -> bool:
        """Validate that a link is a proper PrizePicks link."""
        import re
        patterns = [
            r'https?://prizepicks\.com/[^\s]+',
            r'https?://.*prizepicks.*[^\s]+',
            r'https?://prizepicks\.onelink\.me/[^\s]+'
        ]
        
        for pattern in patterns:
            if re.match(pattern, link, re.IGNORECASE):
                return True
        
        return False
    
    def place_bet(self, link_data: Dict, unit_size: int = None) -> Dict:
        """Place a bet from a link."""
        if unit_size is None:
            unit_size = config.DEFAULT_UNIT_SIZE
        
        link = link_data['link']
        result = {
            'link': link,
            'message_id': link_data.get('message_id'),
            'author': link_data.get('author'),
            'timestamp': link_data.get('timestamp'),
            'unit_size': unit_size,
            'success': False,
            'error': None,
            'placed_at': datetime.now().isoformat()
        }
        
        try:
            logger.info(f"Attempting to place bet for link: {link}")
            
            if not self.automation:
                result['error'] = "Automation not initialized"
                return result
            
            # Place the bet
            success = self.automation.place_bet_from_link(link, unit_size)
            
            if success:
                result['success'] = True
                self.successful_bets.append(result)
                logger.info(f"Successfully placed bet for link: {link}")
            else:
                result['error'] = "Bet placement failed"
                self.failed_bets.append(result)
                logger.error(f"Failed to place bet for link: {link}")
            
        except Exception as e:
            result['error'] = str(e)
            self.failed_bets.append(result)
            logger.error(f"Error placing bet for link {link}: {e}")
        
        return result
    
    def process_links(self, links: List[Dict], unit_size: int = None) -> Dict:
        """Process a list of links and place bets."""
        results = {
            'total_links': len(links),
            'successful_bets': 0,
            'failed_bets': 0,
            'results': []
        }
        
        if not self.auto_place_bets:
            logger.info("Auto-place bets is disabled. Links will be validated only.")
            for link_data in links:
                link = link_data['link']
                if self.validate_link(link):
                    results['successful_bets'] += 1
                    logger.info(f"Valid link found: {link}")
                else:
                    results['failed_bets'] += 1
                    logger.warning(f"Invalid link: {link}")
            return results
        
        if not self.automation:
            logger.error("Automation not initialized. Cannot place bets.")
            return results
        
        for i, link_data in enumerate(links, 1):
            logger.info(f"Processing link {i}/{len(links)}: {link_data['link']}")
            
            result = self.place_bet(link_data, unit_size)
            results['results'].append(result)
            
            if result['success']:
                results['successful_bets'] += 1
            else:
                results['failed_bets'] += 1
            
            # Add delay between bets to avoid rate limiting
            if i < len(links):
                time.sleep(2)
        
        return results
    
    def save_results(self, results: Dict, filename: str = None):
        """Save processing results to a JSON file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bet_results_{timestamp}.json"
            
            # Create results directory if it doesn't exist
            results_dir = os.path.join(os.path.dirname(__file__), "results")
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return None
    
    def get_summary(self) -> Dict:
        """Get a summary of all processed bets."""
        return {
            'total_processed': len(self.processed_links),
            'successful_bets': len(self.successful_bets),
            'failed_bets': len(self.failed_bets),
            'success_rate': len(self.successful_bets) / len(self.processed_links) if self.processed_links else 0
        }
    
    def close(self):
        """Clean up resources."""
        if self.automation:
            self.automation.close()

def process_scraped_file(filepath: str, headless: bool = True, auto_place: bool = None, unit_size: int = None):
    """Process a scraped file and place bets."""
    processor = BetProcessor(headless=headless, auto_place_bets=auto_place)
    
    try:
        # Initialize automation
        if not processor.initialize_automation():
            logger.error("Failed to initialize automation")
            return
        
        # Load and process links
        links = processor.load_scraped_links(filepath)
        if not links:
            logger.warning("No links found in file")
            return
        
        # Filter new links
        new_links = processor.filter_new_links(links)
        if not new_links:
            logger.info("No new links to process")
            return
        
        # Process the links
        results = processor.process_links(new_links, unit_size)
        
        # Save results
        processor.save_results(results)
        
        # Print summary
        summary = processor.get_summary()
        logger.info(f"Processing complete: {summary}")
        
    finally:
        processor.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process scraped PrizePicks links and place bets")
    parser.add_argument('file', help='Path to scraped links JSON file')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--auto-place', action='store_true', help='Automatically place bets')
    parser.add_argument('--unit-size', type=int, help='Unit size for bets')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    
    args = parser.parse_args()
    
    headless = args.headless and not args.no_headless
    auto_place = args.auto_place if args.auto_place is not None else config.AUTO_PLACE_BETS
    
    process_scraped_file(args.file, headless=headless, auto_place=auto_place, unit_size=args.unit_size) 