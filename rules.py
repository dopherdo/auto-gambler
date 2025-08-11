"""
Discord Validation Rules for Auto-Gambler Bot

This module contains validation functions and configuration for:
- Acceptable Discord channels and servers to monitor
- PrizePicks link validation

⚠️ IMPORTANT: Update these IDs with your specific Discord server information
"""

from discord import TextChannel
from dataclasses import dataclass

# ======= [ DISCORD CONFIGURATION ] =======

# List of Discord channel IDs to monitor for PrizePicks links
# Get channel ID by right-clicking channel and "Copy ID" (Developer Mode must be enabled)
ACCEPTABLE_CHANNELS = [1171620108301520956]

# List of Discord server IDs to monitor
# Get server ID by right-clicking server name and "Copy ID" (Developer Mode must be enabled)
ACCEPTABLE_SERVERS = [1171551737803440239]



@dataclass
class ProSlip:
    """
    Data class representing a professional slip/pick from Discord.
    
    Attributes:
        confidence (float | None): Confidence level of the pick (0.0-1.0)
        link (str | None): PrizePicks share link URL
        author (str | None): Discord username of the pick author
    """
    confidence: float | None
    link: str | None
    author: str | None


def valid_prizepick(string):
    """
    Validate if a message contains valid PrizePicks content.
    
    This function checks if the message contains valid PrizePicks share links.
    Supports both plain URLs and Markdown formatted links [text](URL).
    
    Args:
        string (str): Discord message content to validate
        
    Returns:
        bool: True if message contains valid PrizePicks content, False otherwise
    """
    # Check for valid PrizePicks share link pattern (supports Markdown and plain URLs)
    return "https://prizepicks.onelink.me/gCQS/shareEntry?entryId=" in string


def valid_channel_and_server(message):
    """
    Validate if a message is from an acceptable channel and server.
    
    This function ensures the bot only processes messages from:
    1. Configured Discord channels (ACCEPTABLE_CHANNELS)
    2. Configured Discord servers (ACCEPTABLE_SERVERS)
    
    Args:
        message: Discord message object to validate
        
    Returns:
        bool: True if message is from acceptable channel/server, False otherwise
    """
    return all((
        # Check if message channel is in acceptable channels list
        message.channel.id in ACCEPTABLE_CHANNELS,
        # Check if message servers is in acceptable servers list
        message.servers.id in ACCEPTABLE_SERVERS
    ))
