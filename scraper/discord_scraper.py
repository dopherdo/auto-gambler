#!/usr/bin/env python3
"""
Discord Scraper - Scrapes messages from Discord channels
Based on https://github.com/dfrnoch/discord-scraper.git
"""

import discord
import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from discord.ext import commands
import sys
import os
import time
import requests
from dotenv import load_dotenv
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

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

class DiscordScraper(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        self.scraped_messages = []
        
    async def setup_hook(self):
        """Set up bot when it starts."""
        logger.info("Setting up Discord scraper...")
        
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Check if we're in the target server
        target_guild = self.get_guild(int(config.DISCORD_SERVER_ID))
        if target_guild:
            logger.info(f"Connected to target server: {target_guild.name}")
        else:
            logger.warning(f"Not connected to target server (ID: {config.DISCORD_SERVER_ID})")
    
    async def scrape_channel(self, channel_id, limit=100):
        """Scrape messages from a specific channel."""
        try:
            channel = self.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return []
            
            logger.info(f"Scraping messages from #{channel.name}")
            
            messages = []
            async for message in channel.history(limit=limit):
                message_data = {
                    'id': str(message.id),
                    'author': message.author.display_name,
                    'author_id': str(message.author.id),
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                    'attachments': [att.url for att in message.attachments],
                    'embeds': [embed.to_dict() for embed in message.embeds],
                    'reactions': [{'emoji': str(reaction.emoji), 'count': reaction.count} for reaction in message.reactions]
                }
                messages.append(message_data)
            
            logger.info(f"Scraped {len(messages)} messages from #{channel.name}")
            return messages
            
        except Exception as e:
            logger.error(f"Error scraping channel {channel_id}: {e}")
            return []
    
    def save_messages(self, messages, filename=None):
        """Save scraped messages to a JSON file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scraped_messages_{timestamp}.json"
            
            # Create scraped directory if it doesn't exist
            scraped_dir = os.path.join(os.path.dirname(__file__), "..", "scraped")
            if not os.path.exists(scraped_dir):
                os.makedirs(scraped_dir)
            
            filepath = os.path.join(scraped_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(messages)} messages to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving messages: {e}")
            return None
    
    def extract_prizepicks_links(self, messages):
        """Extract PrizePicks links from scraped messages."""
        links = []
        for msg in messages:
            content = msg.get('content', '')
            for pattern in LINK_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    links.append({
                        'link': match,
                        'message_id': msg['id'],
                        'author': msg['author'],
                        'timestamp': msg['timestamp']
                    })
        
        return links
    
    @commands.command(name='scrape')
    async def scrape_command(self, ctx, limit: int = 100):
        """Scrape messages from the current channel."""
        try:
            await ctx.send(f"🔍 Scraping {limit} messages from #{ctx.channel.name}...")
            
            messages = await self.scrape_channel(ctx.channel.id, limit)
            
            if messages:
                filename = f"{ctx.channel.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = self.save_messages(messages, filename)
                
                if filepath:
                    await ctx.send(f"✅ Scraped {len(messages)} messages! Saved to: `{filepath}`")
                    
                    # Extract PrizePicks links
                    prizepicks_links = self.extract_prizepicks_links(messages)
                    if prizepicks_links:
                        await ctx.send(f"🎯 Found {len(prizepicks_links)} PrizePicks links!")
                        for link_data in prizepicks_links[:5]:  # Show first 5
                            await ctx.send(f"  • {link_data['link']} (by {link_data['author']})")
                        if len(prizepicks_links) > 5:
                            await ctx.send(f"  ... and {len(prizepicks_links) - 5} more")
                else:
                    await ctx.send("❌ Failed to save messages")
            else:
                await ctx.send("❌ No messages found or error occurred")
                
        except Exception as e:
            logger.error(f"Error in scrape command: {e}")
            await ctx.send(f"❌ Error: {str(e)}")
    
    @commands.command(name='scrape_target')
    async def scrape_target_command(self, ctx, limit: int = 100):
        """Scrape messages from the configured target channel."""
        try:
            if str(ctx.channel.id) != config.DISCORD_CHANNEL_ID:
                await ctx.send("❌ This command can only be used in the target channel")
                return
            
            await ctx.send(f"🎯 Scraping {limit} messages from target channel...")
            
            messages = await self.scrape_channel(config.DISCORD_CHANNEL_ID, limit)
            
            if messages:
                filename = f"target_channel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = self.save_messages(messages, filename)
                
                if filepath:
                    await ctx.send(f"✅ Scraped {len(messages)} messages from target channel! Saved to: `{filepath}`")
                    
                    # Extract PrizePicks links
                    prizepicks_links = self.extract_prizepicks_links(messages)
                    if prizepicks_links:
                        await ctx.send(f"🎯 Found {len(prizepicks_links)} PrizePicks links in target channel!")
                        for link_data in prizepicks_links:
                            await ctx.send(f"  • {link_data['link']} (by {link_data['author']} at {link_data['timestamp']})")
                else:
                    await ctx.send("❌ Failed to save messages")
            else:
                await ctx.send("❌ No messages found or error occurred")
                
        except Exception as e:
            logger.error(f"Error in scrape_target command: {e}")
            await ctx.send(f"❌ Error: {str(e)}")
    
    @commands.command(name='links')
    async def links_command(self, ctx, limit: int = 100):
        """Extract and display PrizePicks links from recent messages."""
        try:
            await ctx.send(f"🔍 Searching for PrizePicks links in last {limit} messages...")
            
            messages = await self.scrape_channel(ctx.channel.id, limit)
            
            if messages:
                prizepicks_links = self.extract_prizepicks_links(messages)
                
                if prizepicks_links:
                    await ctx.send(f"🎯 Found {len(prizepicks_links)} PrizePicks links:")
                    
                    for i, link_data in enumerate(prizepicks_links, 1):
                        timestamp = datetime.fromisoformat(link_data['timestamp']).strftime("%Y-%m-%d %H:%M")
                        await ctx.send(f"{i}. {link_data['link']}\n   By: {link_data['author']} | {timestamp}")
                else:
                    await ctx.send("❌ No PrizePicks links found in recent messages")
            else:
                await ctx.send("❌ No messages found or error occurred")
                
        except Exception as e:
            logger.error(f"Error in links command: {e}")
            await ctx.send(f"❌ Error: {str(e)}")
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Check scraper status and configuration."""
        target_guild = self.get_guild(int(config.DISCORD_SERVER_ID))
        target_channel = self.get_channel(int(config.DISCORD_CHANNEL_ID))
        
        status_msg = f"🤖 **Discord Scraper Status**\n"
        status_msg += f"• Connected to {len(self.guilds)} guilds\n"
        status_msg += f"• Target Server: {target_guild.name if target_guild else 'Not found'}\n"
        status_msg += f"• Target Channel: #{target_channel.name if target_channel else 'Not found'}\n"
        status_msg += f"• Current Channel: #{ctx.channel.name}\n"
        
        await ctx.send(status_msg)

    async def scheduled_scrape_loop(self, channel_id, start_time_str):
        """
        Start scraping at a specific time each day, run for 10 minutes,
        scrape every 3 seconds, deduplicate links.
        """
        # Parse start_time_str (e.g., '08:00' or '14:00')
        now = datetime.now()
        start_time = datetime.strptime(start_time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if now > start_time:
            # If the time has already passed today, schedule for tomorrow
            start_time += timedelta(days=1)
        wait_seconds = (start_time - now).total_seconds()
        logger.info(f"Waiting until {start_time.strftime('%Y-%m-%d %H:%M:%S')} to start scheduled scraping...")
        await asyncio.sleep(wait_seconds)

        logger.info("Starting scheduled scraping loop!")
        used_links = set()
        end_time = datetime.now() + timedelta(minutes=10)
        channel = self.get_channel(int(channel_id))
        if not channel:
            logger.error(f"Channel {channel_id} not found")
            return
        while datetime.now() < end_time:
            messages = await self.scrape_channel(channel_id, limit=2)
            links = self.extract_prizepicks_links(messages)
            new_links = []
            for link_data in links:
                link = link_data['link']
                if link not in used_links:
                    used_links.add(link)
                    new_links.append(link_data)
            if new_links:
                logger.info(f"New unique links found: {[l['link'] for l in new_links]}")
                # Optionally, save or process new_links here
            await asyncio.sleep(3)
        logger.info("Scheduled scraping loop finished.")

    async def run_scraper_now_loop(self, channel_id):
        """
        Immediately start scraping for 10 minutes, every 3 seconds, deduplicating links.
        """
        logger.info("Starting immediate scraping loop!")
        used_links = set()
        end_time = datetime.now() + timedelta(minutes=10)
        channel = self.get_channel(int(channel_id))
        if not channel:
            logger.error(f"Channel {channel_id} not found")
            return
        while datetime.now() < end_time:
            messages = await self.scrape_channel(channel_id, limit=2)
            links = self.extract_prizepicks_links(messages)
            new_links = []
            for link_data in links:
                link = link_data['link']
                if link not in used_links:
                    used_links.add(link)
                    new_links.append(link_data)
            if new_links:
                logger.info(f"New unique links found: {[l['link'] for l in new_links]}")
                # Optionally, save or process new_links here
            await asyncio.sleep(3)
        logger.info("Immediate scraping loop finished.")

def run_scraper():
    """Run the Discord scraper."""
    if not config.DISCORD_TOKEN:
        logger.error("Discord token not found in environment variables")
        return
    
    scraper = DiscordScraper()
    
    try:
        scraper.run(config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error running scraper: {e}")

def run_scheduled_scraper():
    """Run the Discord scraper in scheduled mode (CLI entry point)."""
    import argparse
    parser = argparse.ArgumentParser(description="Run scheduled Discord scraping.")
    parser.add_argument('--channel', type=str, default=None, help='Channel ID to scrape (default: config.DISCORD_CHANNEL_ID)')
    parser.add_argument('--start', type=str, required=True, help='Start time in HH:MM (24h) format')
    args = parser.parse_args()

    channel_id = args.channel or config.DISCORD_CHANNEL_ID
    start_time_str = args.start

    scraper = DiscordScraper()
    async def runner():
        await scraper.start(config.DISCORD_TOKEN, reconnect=True)
        await scraper.wait_until_ready()
        await scraper.scheduled_scrape_loop(channel_id, start_time_str)
        await scraper.close()
    asyncio.run(runner())

def run_scraper_now():
    """Run the Discord scraper in immediate mode (CLI entry point)."""
    import argparse
    parser = argparse.ArgumentParser(description="Run immediate Discord scraping.")
    parser.add_argument('--channel', type=str, default=None, help='Channel ID to scrape (default: config.DISCORD_CHANNEL_ID)')
    args = parser.parse_args()

    channel_id = args.channel or config.DISCORD_CHANNEL_ID

    scraper = DiscordScraper()
    async def runner():
        await scraper.start(config.DISCORD_TOKEN, reconnect=True)
        await scraper.wait_until_ready()
        await scraper.run_scraper_now_loop(channel_id)
        await scraper.close()
    asyncio.run(runner())

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'scheduled':
        sys.argv.pop(1)  # Remove 'scheduled' so argparse doesn't get confused
        run_scheduled_scraper()
    elif len(sys.argv) > 1 and sys.argv[1] == 'now':
        sys.argv.pop(1)  # Remove 'now'
        run_scraper_now()
    else:
        run_scraper()
