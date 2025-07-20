import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_SERVER_ID = os.getenv('DISCORD_SERVER_ID')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# PrizePicks Configuration
PRIZEPICKS_URL = "https://app.prizepicks.com"
PRIZEPICKS_LOGIN_URL = "https://app.prizepicks.com/login"
PRIZEPICKS_EMAIL = os.getenv('PRIZEPICKS_EMAIL')
PRIZEPICKS_PASSWORD = os.getenv('PRIZEPICKS_PASSWORD')

# Bet Placement Configuration
DEFAULT_UNIT_SIZE = int(os.getenv('DEFAULT_UNIT_SIZE', '1'))
MAX_UNIT_SIZE = int(os.getenv('MAX_UNIT_SIZE', '10'))
AUTO_PLACE_BETS = os.getenv('AUTO_PLACE_BETS', 'false').lower() == 'true'

# Automation Settings
SUBMISSION_DELAY = 1  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds
ELEMENT_WAIT_TIMEOUT = 10  # seconds

# Scheduling
MORNING_TIME = "08:00"  # 8am PST
AFTERNOON_TIME = "14:00"  # 2pm PST
TIMEZONE = "US/Pacific"

# Verification Settings
SCREENSHOT_ON_SUBMISSION = True
LOG_LEVEL = "INFO"

# File Paths
SCREENSHOTS_DIR = "screenshots"
LOGS_DIR = "logs"
COOKIES_FILE = "prizepicks_cookies.pkl" 