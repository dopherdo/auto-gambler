"""
User Interface Utilities for Auto-Gambler Bot

This module provides pretty printing and formatting utilities for:
- Discord message display with colors
- Message history visualization
- Debug output formatting

Uses termcolor for colored console output to improve readability.
"""

import discord
from termcolor import colored


def pp_message(message: discord.Message):
    """
    Pretty print a Discord message with colored formatting.
    
    Displays message information in a readable format with:
    - Timestamp in yellow
    - Author name in cyan
    - Message content in green
    - Attachments in magenta
    - Embeds in blue
    
    Args:
        message (discord.Message): Discord message object to display
    """
    # Convert timestamp to local timezone for display
    localized_time = message.created_at.astimezone()

    # Format author name with discriminator
    author = colored(f"{message.author.name}#{message.author.discriminator}", "cyan")
    
    # Format timestamp
    timestamp = colored(localized_time.strftime("%Y-%m-%d %H:%M:%S"), "yellow")
    
    # Format message content
    content = colored(message.content, "green")

    # Print main message information
    print(f"[{timestamp}] {author}:\n{content}\n")

    # Display attachments if present
    if message.attachments:
        for attachment in message.attachments:
            print(colored(f"Attachment: {attachment.url}", "magenta"))

    # Display embeds if present
    if message.embeds:
        for embed in message.embeds:
            # Show embed title or "No Title" if missing
            title = embed.title if embed.title else 'No Title'
            print(colored(f"Embed: {title}", "blue"))
            
            # Show embed description if present
            if embed.description:
                print(colored(f"Description: {embed.description}", "white"))


async def pp_history(channel: discord.TextChannel, limit: int = 10):
    """
    Pretty print message history from a Discord channel.
    
    Retrieves and displays recent messages from a channel with
    colored formatting for easy reading and debugging.
    
    Args:
        channel (discord.TextChannel): Discord channel to fetch history from
        limit (int): Number of messages to retrieve (default: 10)
    """
    # Iterate through channel history
    async for message in channel.history(limit=limit):
        if message is not None:
            pp_message(message)
