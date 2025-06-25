#!/usr/bin/env python3
"""
Standalone Discord Scraper Test
Tests the scraper functionality with your configured Discord server and channel.
"""

import os
import requests
from dotenv import load_dotenv
import re

load_dotenv()
USER_TOKEN = os.getenv("DISCORD_USER_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

HEADERS = {
    "Authorization": USER_TOKEN,
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

LINK_PATTERNS = [
    r'https?://app\.prizepicks\.com/[^\s]+',
    r'https?://prizepicks\.com/[^\s]+',
    r'https?://.*prizepicks.*[^\s]+',
    r'https?://prizepicks\.onelink\.me/[^\s]+'
]

def fetch_recent_messages(channel_id, limit=2):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"[ERROR] Failed to fetch messages: {resp.status_code} {resp.text}")
        return []

def extract_prizepicks_links(messages):
    links = []
    for msg in messages:
        content = msg.get('content', '')
        for pattern in LINK_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                links.append({
                    'link': match,
                    'message_id': msg['id'],
                    'author': msg['author']['username'],
                    'timestamp': msg['timestamp']
                })
    return links

def test_api_connectivity():
    print("\n[TEST] Discord API connectivity...")
    messages = fetch_recent_messages(CHANNEL_ID, limit=1)
    if messages:
        print(f"[PASS] Successfully fetched messages from channel {CHANNEL_ID}.")
        return True
    else:
        print(f"[FAIL] Could not fetch messages from channel {CHANNEL_ID}.")
        return False

def test_scrape_channel():
    print("\n[TEST] Scrape channel for recent messages...")
    messages = fetch_recent_messages(CHANNEL_ID, limit=5)
    if messages:
        print(f"[PASS] scrape_channel returned {len(messages)} messages.")
        for msg in messages:
            print(f"- [{msg['timestamp']}] {msg['author']['username']}: {msg['content']}")
        return True
    else:
        print("[FAIL] scrape_channel did not return messages as expected.")
        return False

def test_link_extraction():
    print("\n[TEST] PrizePicks link extraction...")
    messages = fetch_recent_messages(CHANNEL_ID, limit=10)
    links = extract_prizepicks_links(messages)
    if links:
        print(f"[PASS] Found {len(links)} PrizePicks links:")
        for link in links:
            print(f"  • {link['link']} (by {link['author']})")
        return True
    else:
        print("[FAIL] No PrizePicks links found in recent messages.")
        return False

def main():
    print("🧪 Running Discord Scraper Raw Requests Tests")
    print("=" * 50)
    
    api_ok = test_api_connectivity()
    scrape_ok = test_scrape_channel()
    link_ok = test_link_extraction()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"• Discord API Connectivity: {'✅' if api_ok else '❌'}")
    print(f"• scrape_channel: {'✅' if scrape_ok else '❌'}")
    print(f"• Link Extraction: {'✅' if link_ok else '❌'}")
    
    if api_ok and scrape_ok and link_ok:
        print("\n🎉 All tests passed! Your scraper is ready to use.")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main() 