from discord import TextChannel
from dataclasses import dataclass

# Edit with channel/guild IDs that you want to monitor
ACCEPTABLE_CHANNELS = [1387259344508293180]
ACCEPTABLE_GUILDS = [1387259315236372611]
ACCEPTABLE_ROLES = ["@&1341949739259658242"]


@dataclass
class ProSlip:
    confidence: float | None
    link: str | None
    author: str | None


def valid_prizepick(string):
    return any((
        *[tag in string for tag in ACCEPTABLE_ROLES],
        "https://prizepicks.onelink.me/gCQS/shareEntry?entryId=" in string,
    ))


def valid_channel_and_guild(message):
    return all((
        message.channel.id in ACCEPTABLE_CHANNELS,
        message.guild.id in ACCEPTABLE_GUILDS))
