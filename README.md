# Auto Gambler - PrizePicks Automation

An automated system that monitors a Discord server for PrizePicks links and automatically submits gambling slips with verification.

## Features

- 🤖 **Discord Bot Integration** - Monitors specified Discord channel for PrizePicks links
- 🌐 **Web Automation** - Handles PrizePicks website login and navigation
- ⚡ **Automatic Submission** - Submits slips with configurable delays
- ✅ **Verification System** - Screenshots and success indicators for verification
- 🍪 **Session Management** - Saves cookies to avoid repeated logins
- 📅 **Scheduling Ready** - Designed for 8am/2pm PST automation

## Prerequisites

- Python 3.8+
- Chrome browser installed
- Discord bot token
- PrizePicks account credentials

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd auto-gambler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` with your credentials:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   DISCORD_SERVER_ID=your_discord_server_id_here
   DISCORD_CHANNEL_ID=your_discord_channel_id_here
   PRIZEPICKS_EMAIL=your_prizepicks_email@example.com
   PRIZEPICKS_PASSWORD=your_prizepicks_password_here
   ```

## Setup Steps

### 1. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable "Message Content Intent" in bot settings
6. Generate invite link with permissions:
   - Read Messages/View Channels
   - Send Messages
   - Use Slash Commands

### 2. Manual Testing (Recommended First Step)

Before running the full automation, test each component:

```bash
# Interactive testing mode
python manual_test.py

# Or test specific components
python manual_test.py login
python manual_test.py workflow "https://app.prizepicks.com/your-link"
```

### 3. Configuration

Edit `config.py` to customize:
- Submission delays
- Timeouts
- Screenshot settings
- Scheduling times

## Usage

### Manual Testing

```bash
# Test login only
python manual_test.py login

# Test full workflow with a link
python manual_test.py workflow "https://app.prizepicks.com/your-link"

# Interactive testing
python manual_test.py
```

### Discord Bot

```bash
# Start the Discord bot
python discord_bot.py
```

The bot will:
- Monitor the specified Discord channel
- Automatically detect PrizePicks links
- Process and submit slips
- Provide status updates

### Bot Commands

- `!test` - Test if bot is running
- `!status` - Check bot status
- `!manual <link>` - Manually submit a PrizePicks link

## Step-by-Step Implementation Plan

### Phase 1: Foundation & Manual Testing ✅
1. ✅ Set up project structure with dependencies
2. ✅ Create basic web automation for PrizePicks
3. ✅ Build manual testing framework
4. 🔄 **Next: Test PrizePicks workflow manually**

### Phase 2: Core Automation
5. Test Discord bot with sample links
6. Refine web automation based on testing
7. Implement robust error handling
8. Add verification strategies

### Phase 3: Production & Deployment
9. Add scheduling system for 8am/2pm PST
10. Deploy to cloud/server
11. Add monitoring and logging

## Current Status

**Ready for Phase 1, Step 4**: Manual testing of PrizePicks workflow

### Next Steps:

1. **Set up your `.env` file** with Discord and PrizePicks credentials
2. **Run manual testing**:
   ```bash
   python manual_test.py
   ```
3. **Test login functionality** first
4. **Test with a real PrizePicks link** to understand the workflow
5. **Refine selectors** in `prizepicks_automation.py` based on actual website structure

## File Structure

```
auto-gambler/
├── config.py              # Configuration settings
├── prizepicks_automation.py  # Web automation logic
├── discord_bot.py         # Discord bot implementation
├── manual_test.py         # Manual testing framework
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
├── screenshots/           # Screenshots for verification
├── logs/                  # Application logs
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - The system uses `webdriver-manager` to auto-download ChromeDriver
   - Ensure Chrome browser is installed

2. **Login Problems**
   - Check PrizePicks credentials in `.env`
   - Try manual login first to verify account status

3. **Discord Bot Not Responding**
   - Verify bot token and permissions
   - Check server and channel IDs

4. **Element Not Found Errors**
   - PrizePicks may have updated their website
   - Update selectors in `prizepicks_automation.py`

### Debug Mode

Enable detailed logging by setting in `config.py`:
```python
LOG_LEVEL = "DEBUG"
```

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for sensitive data
- Consider using a dedicated Discord bot account
- Be aware of PrizePicks terms of service regarding automation

## Legal Disclaimer

This tool is for educational purposes. Users are responsible for complying with:
- PrizePicks terms of service
- Local gambling laws and regulations
- Discord terms of service

Use at your own risk and discretion.

## Contributing

1. Test thoroughly before making changes
2. Update documentation for any new features
3. Follow the existing code style
4. Add appropriate error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.