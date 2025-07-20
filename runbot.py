import discord
from discord.message import Message

from rules import valid_prizepick, valid_channel_and_guild
from ui import pp_message, pp_history

from enum import Enum
from dataclasses import dataclass
import os
import time
import random

import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

driver = uc.Chrome(version_main=138)

def human_delay():
    """Add random human-like delays"""
    time.sleep(random.uniform(1.5, 3.5))

def place_prizepick_slip(url):
    """Automatically place a PrizePick slip"""
    try:
        print(f"Opening PrizePick link: {url}")
        driver.get(url)
        
        # Wait for page to load
        human_delay()
        
        # Wait for the page to be fully loaded
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("Page loaded, looking for place entry button...")
        human_delay()
        
        # Try multiple possible selectors for the place entry button
        place_button_selectors = [
            "button[data-testid='place-entry-button']",
            "button:contains('Place Entry')",
            "button:contains('Place Bet')",
            "button:contains('Submit')",
            "[data-testid='submit-button']",
            "button[type='submit']",
            ".place-entry-btn",
            ".submit-btn",
            "button.btn-primary",
            "button.btn-success"
        ]
        
        place_button = None
        for selector in place_button_selectors:
            try:
                if "contains" in selector:
                    # Handle text-based selectors
                    text = selector.split("'")[1]
                    place_button = driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                else:
                    place_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                if place_button and place_button.is_displayed() and place_button.is_enabled():
                    print(f"Found place button with selector: {selector}")
                    break
            except NoSuchElementException:
                continue
        
        if place_button:
            print("Clicking place entry button...")
            human_delay()
            place_button.click()
            
            # Wait for confirmation or success
            human_delay()
            
            # Check for success message or confirmation
            success_selectors = [
                "div[data-testid='success-message']",
                ".success-message",
                ".confirmation-message",
                "div:contains('Entry placed')",
                "div:contains('Success')"
            ]
            
            for selector in success_selectors:
                try:
                    if "contains" in selector:
                        text = selector.split("'")[1]
                        success_element = driver.find_element(By.XPATH, f"//div[contains(text(), '{text}')]")
                    else:
                        success_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if success_element.is_displayed():
                        print("✅ Slip placed successfully!")
                        return True
                except NoSuchElementException:
                    continue
            
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
    confidence: float | None
    link: str | None
    author: str | None


pending_picks = dict()

client = discord.Client()

# ======= [ CLIENT ] =======


@client.event
async def on_ready():
    print("Logged in as", client.user)


@client.event
async def on_message(message: Message):
    if not isinstance(message.channel, discord.TextChannel):
        return

    if not valid_channel_and_guild(message):
        print("Not valid guild and channel:", message.channel.id)
        return

    if not valid_prizepick(message.content):
        print("Not valid prizepick:", message.content)
        return

    await message.add_reaction("🌭")
    
    # Extract the PrizePick URL from the message
    import re
    url_match = re.search(r'https://prizepicks\.onelink\.me/gCQS/shareEntry\?entryId=[^\s]+', message.content)
    if url_match:
        url = url_match.group(0)
        print(f"Processing PrizePick link: {url}")
        
        # Place the slip automatically
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
    import dotenv

    dotenv.load_dotenv()

    TOKEN = os.getenv("TOKEN")

    if TOKEN is not None:
        client.run(TOKEN)
