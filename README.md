# Auto-Gambler 🤖

An automated Discord bot that monitors specific channels for PrizePicks links and automatically places bets using undetected Chrome automation.

## ⚠️ Important Disclaimers

- **Educational purposes only** - Use responsibly and at your own risk
- **Terms of Service** - This violates Discord's ToS. Use an alt account only
- **Legal Compliance** - Ensure you comply with all applicable gambling laws
- **Account Security** - Never use your main Discord account

## 🚀 Features

- **Discord Monitoring**: Monitors specific channels for PrizePicks links
- **Automatic Bet Placement**: Uses undetected Chrome to place bets automatically
- **Human-like Behavior**: Random delays and natural interaction patterns
- **Smart Link Detection**: Validates PrizePicks URLs before processing
- **Reaction Feedback**: Provides visual feedback in Discord with emojis

## 📋 Prerequisites

- Python 3.8+
- Chrome browser (version 138+)
- Discord alt account token
- PrizePicks account (already logged in)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd auto-gambler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Create .env file
   echo "TOKEN=your_discord_alt_token_here" > .env
   ```

4. **Configure channels and guilds**
   Edit `rules.py` with your target Discord server and channel IDs:
   ```python
   ACCEPTABLE_CHANNELS = [YOUR_CHANNEL_ID]
   ACCEPTABLE_GUILDS = [YOUR_GUILD_ID]
   ACCEPTABLE_ROLES = ["@&YOUR_ROLE_ID"]
   ```

## 🎯 Usage

### Running the Bot
```bash
python runbot.py
```

### How It Works

1. **Discord Monitoring**: Bot connects to Discord and monitors specified channels
2. **Link Detection**: Scans messages for valid PrizePicks URLs
3. **Validation**: Checks for required role mentions and valid channels
4. **Automation**: Opens Chrome browser and navigates to PrizePicks link
5. **Bet Placement**: Automatically clicks the submit button
6. **Feedback**: Adds reactions to Discord messages (🌭, ✅, ❌)

### Message Processing Flow

```
Discord Message → Validation → URL Extraction → Browser Automation → Bet Placement → Feedback
```

## ⚙️ Configuration

### Discord Settings (`rules.py`)
- `ACCEPTABLE_CHANNELS`: List of channel IDs to monitor
- `ACCEPTABLE_GUILDS`: List of guild/server IDs to monitor  
- `ACCEPTABLE_ROLES`: List of role mentions required in messages

### Browser Settings (`runbot.py`)
- Chrome version: 138 (configured for undetected-chromedriver)
- Human-like delays: 1.5-3.5 seconds between actions
- Multiple button selectors for robustness

## 🔧 Technical Details

### Key Technologies
- **discord.py-self**: Discord bot library (self-bot, violates ToS)
- **undetected-chromedriver**: Anti-detection browser automation
- **Selenium**: Web automation framework
- **python-dotenv**: Environment variable management

### Anti-Detection Features
- Undetected Chrome driver
- Random human-like delays
- Multiple CSS selectors for button detection
- Natural interaction patterns

## 🚨 Security & Best Practices

### Account Safety
- ✅ Use dedicated alt account only
- ✅ Never use main Discord account
- ✅ Keep token secure and private
- ❌ Don't share your token
- ❌ Don't use on public networks

### Operational Safety
- ✅ Test with small amounts first
- ✅ Monitor the bot while running
- ✅ Keep browser visible during testing
- ✅ Set up proper error handling
- ❌ Don't run unattended initially

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Version Mismatch**
   ```bash
   # Update Chrome or adjust version in runbot.py
   driver = uc.Chrome(version_main=YOUR_CHROME_VERSION)
   ```

2. **Discord Token Issues**
   - Ensure token is valid and from alt account
   - Check if account has proper permissions

3. **PrizePicks Login Required**
   - Manually log into PrizePicks in Chrome first
   - Ensure account is not locked or suspended

4. **Button Not Found**
   - PrizePicks may have updated their website
   - Check console output for selector attempts
   - Update selectors in `place_prizepick_slip()` function

### Debug Mode
Add debug prints to see what's happening:
```python
print(f"Current URL: {driver.current_url}")
print(f"Page title: {driver.title}")
```

## 📁 Project Structure

```
auto-gambler/
├── runbot.py          # Main bot logic and automation
├── rules.py           # Discord validation rules
├── ui.py              # Pretty printing utilities
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (create this)
└── README.md         # This file
```

## 🔄 Development

### Adding New Features
1. **New Button Selectors**: Add to `place_button_selectors` list
2. **New Validation Rules**: Modify `rules.py` functions
3. **Enhanced Logging**: Use `ui.py` functions for pretty output

### Testing
```bash
# Test with a sample PrizePicks link
python -c "
from runbot import place_prizepick_slip
place_prizepick_slip('https://prizepicks.onelink.me/gCQS/shareEntry?entryId=test')
"
```

## 📝 Key Notes

1. **Undetected Chrome**: Essential for avoiding detection
2. **Alt Account**: Always use Discord alt account (violates ToS)
3. **Mobile Emulation**: Consider using BlueStacks for mobile environment
4. **Location Spoofing**: Use VPN or mobile emulator for location diversity
5. **Responsible Use**: Educational purposes only, use at your own risk

## ⚖️ Legal Disclaimer

This software is provided for educational purposes only. Users are responsible for:
- Complying with Discord's Terms of Service
- Following local gambling laws and regulations
- Understanding the risks of automated betting
- Using this software responsibly and ethically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Remember: Use responsibly and at your own risk! 🎲**
