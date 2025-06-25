import discord
import re
import logging
import asyncio
from discord.ext import commands
import config
from prizepicks_automation import PrizePicksAutomation

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class PrizePicksBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(command_prefix='!', intents=intents)
        self.automation = None
        
    async def setup_hook(self):
        """Set up bot when it starts."""
        logger.info("Setting up PrizePicks bot...")
        
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
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
            
        # Only process messages from the target channel
        if str(message.channel.id) != config.DISCORD_CHANNEL_ID:
            return
            
        # Check if message contains a PrizePicks link
        prizepicks_links = self.extract_prizepicks_links(message.content)
        
        if prizepicks_links:
            logger.info(f"Found PrizePicks links in message: {prizepicks_links}")
            
            # Process each link
            for link in prizepicks_links:
                await self.process_prizepicks_link(link, message)
        
        # Process commands
        await self.process_commands(message)
    
    def extract_prizepicks_links(self, content):
        """Extract PrizePicks links from message content."""
        # Pattern to match PrizePicks URLs
        patterns = [
            r'https?://app\.prizepicks\.com/[^\s]+',
            r'https?://prizepicks\.com/[^\s]+',
            r'https?://.*prizepicks.*[^\s]+'
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            links.extend(matches)
        
        return list(set(links))  # Remove duplicates
    
    async def process_prizepicks_link(self, link, message):
        """Process a PrizePicks link by triggering automation."""
        try:
            logger.info(f"Processing PrizePicks link: {link}")
            
            # Send confirmation message
            await message.channel.send(f"🎯 Processing PrizePicks link: {link}")
            
            # Run automation in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, self.run_automation, link)
            
            if success:
                await message.channel.send("✅ Slip submitted successfully!")
            else:
                await message.channel.send("❌ Failed to submit slip. Check logs for details.")
                
        except Exception as e:
            logger.error(f"Error processing PrizePicks link: {e}")
            await message.channel.send(f"❌ Error processing link: {str(e)}")
    
    def run_automation(self, link):
        """Run the PrizePicks automation for a given link."""
        try:
            # Initialize automation
            self.automation = PrizePicksAutomation(headless=False)  # Set to True for production
            self.automation.setup_driver()
            
            # Try to load cookies first
            cookies_loaded = self.automation.load_cookies()
            
            # Login if cookies didn't work
            if not cookies_loaded:
                if not self.automation.login():
                    logger.error("Failed to login to PrizePicks")
                    return False
            
            # Navigate to the link
            if not self.automation.navigate_to_link(link):
                logger.error("Failed to navigate to PrizePicks link")
                return False
            
            # Submit the slip
            success = self.automation.submit_slip()
            
            return success
            
        except Exception as e:
            logger.error(f"Error in automation: {e}")
            return False
        finally:
            # Clean up
            if self.automation:
                self.automation.close()
    
    @commands.command(name='test')
    async def test_command(self, ctx):
        """Test command to verify bot is working."""
        await ctx.send("🤖 PrizePicks bot is running!")
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Check bot status."""
        await ctx.send(f"✅ Bot is online and monitoring channel <#{config.DISCORD_CHANNEL_ID}>")
    
    @commands.command(name='manual')
    async def manual_submit(self, ctx, link: str):
        """Manually submit a PrizePicks link."""
        if not link.startswith('http'):
            await ctx.send("❌ Please provide a valid URL")
            return
            
        await ctx.send(f"🔄 Manually processing link: {link}")
        await self.process_prizepicks_link(link, ctx)

def run_bot():
    """Run the Discord bot."""
    if not config.DISCORD_TOKEN:
        logger.error("Discord token not found in environment variables")
        return
    
    bot = PrizePicksBot()
    
    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    run_bot() 