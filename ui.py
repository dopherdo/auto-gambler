import discord
from termcolor import colored


def pp_message(message: discord.Message):
    """Pretty prints a discord.py Message object with colors."""
    localized_time = message.created_at.astimezone()

    author = colored(f"{message.author.name}#{message.author.discriminator}", "cyan")
    timestamp = colored(localized_time.strftime("%Y-%m-%d %H:%M:%S"), "yellow")
    content = colored(message.content, "green")

    print(f"[{timestamp}] {author}:\n{content}\n")

    if message.attachments:
        for attachment in message.attachments:
            print(colored(f"Attachment: {attachment.url}", "magenta"))

    if message.embeds:
        for embed in message.embeds:
            print(colored(f"Embed: {embed.title if embed.title else 'No Title'}", "blue"))
            if embed.description:
                print(colored(f"Description: {embed.description}", "white"))

async def pp_history(channel: discord.TextChannel, limit: int = 10):
    """Pretty prints message history from a discord.py TextChannel object."""
    async for message in channel.history(limit=limit):
        if message is not None:
            pp_message(message)
