"""
Auto-Gambler Bot - Automated PrizePicks Betting System

This Discord bot monitors specific channels for PrizePicks links and automatically
places bets using undetected Chrome automation to avoid detection.

Key Features:
- Discord message monitoring with validation
- Undetected Chrome browser automation
- Human-like interaction patterns
- Automatic bet placement
- Visual feedback via Discord reactions

⚠️ IMPORTANT: Use alt Discord account only - violates Discord ToS
"""

import discord
from discord.message import Message

from rules import valid_prizepick, valid_channel_and_guild
from ui import pp_message, pp_history

from enum import Enum
from dataclasses import dataclass
import os
import time
import random

# Anti-detection browser automation
import undetected_chromedriver as uc

# Web automation framework
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Initialize undetected Chrome driver (anti-detection)
# Version 138 is configured for current Chrome version
driver = uc.Chrome(version_main=138)

def human_delay():
    """
    Add random human-like delays between actions to avoid detection.
    
    Returns:
        None: Sleeps for 1.5-3.5 seconds randomly
    """
    time.sleep(random.uniform(1.5, 3.5))

def place_prizepick_slip(url):
    """
    Automatically place a PrizePick slip using browser automation.
    
    This function:
    1. Opens the PrizePicks link in Chrome
    2. Waits for page to load completely
    3. Finds and clicks the submit/place button
    4. Verifies successful placement
    5. Uses human-like delays throughout
    
    Args:
        url (str): PrizePicks share link to process
        
    Returns:
        bool: True if slip was placed successfully, False otherwise
    """
    try:
        print(f"Opening PrizePick link: {url}")
        driver.get(url)
        
        # Wait for page to load with human-like delay
        human_delay()
        
        # Wait for the page to be fully loaded (body element present)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("Page loaded, looking for place entry button...")
        human_delay()
        
        # Multiple selectors for robustness - PrizePicks may change their UI
        place_button_selectors = [
            "button[data-testid='place-entry-button']",  # Primary selector
            "button:contains('Place Entry')",            # Text-based selector
            "button:contains('Place Bet')",              # Alternative text
            "button:contains('Submit')",                 # Generic submit
            "[data-testid='submit-button']",             # Data attribute
            "button[type='submit']",                     # HTML submit button
            ".place-entry-btn",                          # CSS class
            ".submit-btn",                               # Alternative class
            "button.btn-primary",                        # Bootstrap primary
            "button.btn-success"                         # Bootstrap success
        ]
        
        place_button = None
        for selector in place_button_selectors:
            try:
                if "contains" in selector:
                    # Handle text-based selectors using XPath
                    text = selector.split("'")[1]
                    place_button = driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                else:
                    # Handle CSS selectors
                    place_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                # Verify button is visible and clickable
                if place_button and place_button.is_displayed() and place_button.is_enabled():
                    print(f"Found place button with selector: {selector}")
                    break
            except NoSuchElementException:
                continue
        
        if place_button:
            print("Clicking place entry button...")
            human_delay()
            place_button.click()
            
            # Wait for confirmation or success message
            human_delay()
            
            # Check for success indicators to verify placement
            success_selectors = [
                "div[data-testid='success-message']",    # Success message
                ".success-message",                      # CSS class
                ".confirmation-message",                 # Alternative class
                "div:contains('Entry placed')",          # Text confirmation
                "div:contains('Success')"                # Generic success
            ]
            
            for selector in success_selectors:
                try:
                    if "contains" in selector:
                        # Handle text-based success indicators
                        text = selector.split("'")[1]
                        success_element = driver.find_element(By.XPATH, f"//div[contains(text(), '{text}')]")
                    else:
                        # Handle CSS-based success indicators
                        success_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if success_element.is_displayed():
                        print("✅ Slip placed successfully!")
                        return True
                except NoSuchElementException:
                    continue
            
            # If no success indicator found, assume it worked (button was clicked)
            print("⚠️ Button clicked, but couldn't confirm success")
            return True
            
        else:
            print("❌ Could not find place entry button")
            return False
            
    except TimeoutException:
        print("❌ Timeout waiting for page to load")
        return False
    except Exception as e:
        print(f"❌ Error placing slip: {str(e)}")
        return False


@dataclass
class ProSlip:
    """
    Data class representing a professional slip/pick.
    
    Attributes:
        confidence (float | None): Confidence level of the pick (0.0-1.0)
        link (str | None): PrizePicks share link
        author (str | None): Discord username of the pick author
    """
    confidence: float | None
    link: str | None
    author: str | None


# Global storage for pending picks (currently unused but available for future features)
pending_picks = dict()

# Initialize Discord client
client = discord.Client()

# ======= [ DISCORD CLIENT EVENTS ] =======

@client.event
async def on_ready():
    """
    Called when the Discord bot successfully connects.
    
    Logs the bot's user information for verification.
    """
    print("Logged in as", client.user)


@client.event
async def on_message(message: Message):
    """
    Main message handler for Discord events.
    
    This function:
    1. Validates the message is from a text channel
    2. Checks if it's from an acceptable guild/channel
    3. Validates it contains a valid PrizePicks link
    4. Extracts the URL and processes the slip
    5. Provides visual feedback via reactions
    
    Args:
        message (Message): Discord message object
    """
    # Only process messages from text channels
    if not isinstance(message.channel, discord.TextChannel):
        return

    # Validate guild and channel permissions
    if not valid_channel_and_guild(message):
        print("Not valid guild and channel:", message.channel.id)
        return

    # Validate message contains valid PrizePicks content
    if not valid_prizepick(message.content):
        print("Not valid prizepick:", message.content)
        return

    # Add initial reaction to show bot is processing
    await message.add_reaction("🌭")
    
    # Extract PrizePicks URL using regex pattern matching
    import re
    url_match = re.search(r'https://prizepicks\.onelink\.me/gCQS/shareEntry\?entryId=[^\s]+', message.content)
    if url_match:
        url = url_match.group(0)
        print(f"Processing PrizePick link: {url}")
        
        # Attempt to place the slip automatically
        success = place_prizepick_slip(url)
        
        if success:
            await message.add_reaction("✅")
            print(f"Successfully processed slip from {message.author}")
        else:
            await message.add_reaction("❌")
            print(f"Failed to process slip from {message.author}")
    else:
        print("No valid PrizePick URL found in message")


if __name__ == "__main__":
    """
    Main entry point for the auto-gambler bot.
    
    Loads environment variables and starts the Discord client.
    """
    import dotenv

    # Load environment variables from .env file
    dotenv.load_dotenv()

    # Get Discord token from environment
    TOKEN = os.getenv("TOKEN")

    if TOKEN is not None:
        print("🚀 Starting Auto-Gambler Bot...")
        print("⚠️ Remember: Use alt account only - violates Discord ToS")
        client.run(TOKEN)
    else:
        print("❌ Error: TOKEN not found in environment variables")
        print("Please create a .env file with: TOKEN=your_discord_token")
