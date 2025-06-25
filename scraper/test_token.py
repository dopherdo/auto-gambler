import asyncio
import json
import os
import sys
from datetime import datetime
import discord

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

class TestClient(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (ID: {self.user.id})")
        await self.close()

intents = discord.Intents.default()
client = TestClient(intents=intents)

try:
    client.run(config.DISCORD_TOKEN)
except Exception as e:
    print(f"❌ Login failed: {e}")