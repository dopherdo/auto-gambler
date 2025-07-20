"""
Discord Validation Rules for Auto-Gambler Bot

This module contains validation functions and configuration for:
- Acceptable Discord channels and guilds to monitor
- PrizePicks link validation
- Role-based access control

⚠️ IMPORTANT: Update these IDs with your specific Discord server information
"""

from discord import TextChannel
from dataclasses import dataclass

# ======= [ DISCORD CONFIGURATION ] =======

# List of Discord channel IDs to monitor for PrizePicks links
# Get channel ID by right-clicking channel and "Copy ID" (Developer Mode must be enabled)
ACCEPTABLE_CHANNELS = [1387259344508293180]

# List of Discord guild/server IDs to monitor
# Get guild ID by right-clicking server name and "Copy ID" (Developer Mode must be enabled)
ACCEPTABLE_GUILDS = [1387259315236372611]

# List of role mentions required in messages for validation
# Format: "@&ROLE_ID" - Get role ID by right-clicking role and "Copy ID"
ACCEPTABLE_ROLES = ["@&1341949739259658242"]


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
    
    This function checks if the message contains:
    1. Required role mentions (for access control)
    2. Valid PrizePicks share links
    
    Args:
        string (str): Discord message content to validate
        
    Returns:
        bool: True if message contains valid PrizePicks content, False otherwise
    """
    return any((
        # Check for required role mentions (access control)
        *[tag in string for tag in ACCEPTABLE_ROLES],
        # Check for valid PrizePicks share link pattern
        "https://prizepicks.onelink.me/gCQS/shareEntry?entryId=" in string,
    ))


def valid_channel_and_guild(message):
    """
    Validate if a message is from an acceptable channel and guild.
    
    This function ensures the bot only processes messages from:
    1. Configured Discord channels (ACCEPTABLE_CHANNELS)
    2. Configured Discord guilds/servers (ACCEPTABLE_GUILDS)
    
    Args:
        message: Discord message object to validate
        
    Returns:
        bool: True if message is from acceptable channel/guild, False otherwise
    """
    return all((
        # Check if message channel is in acceptable channels list
        message.channel.id in ACCEPTABLE_CHANNELS,
        # Check if message guild is in acceptable guilds list
        message.guild.id in ACCEPTABLE_GUILDS
    ))
