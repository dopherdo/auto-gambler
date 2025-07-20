# Auto-Gambler Setup Guide 🛠️

This guide will walk you through setting up the auto-gambler bot step by step.

## ⚠️ Important Warnings

- **Use Alt Account Only**: Never use your main Discord account
- **Violates Discord ToS**: This is a self-bot, which breaks Discord's terms
- **Educational Purposes**: Use responsibly and at your own risk
- **Legal Compliance**: Ensure you follow all applicable gambling laws

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] Python 3.8+ installed
- [ ] Chrome browser (version 138+)
- [ ] Discord alt account (not your main account)
- [ ] PrizePicks account (already logged in)
- [ ] Access to target Discord server

## 🚀 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd auto-gambler

# Install required packages
pip install -r requirements.txt
```

### Step 2: Get Discord Token

1. **Create Alt Account**: Create a new Discord account (never use your main)
2. **Enable Developer Mode**:
   - Open Discord
   - Go to User Settings → Advanced
   - Enable "Developer Mode"
3. **Get Token**:
   - Press F12 to open Developer Tools
   - Go to Network tab
   - Send a message in any channel
   - Look for requests to Discord API
   - Find the "authorization" header value (this is your token)

### Step 3: Configure Environment

Create a `.env` file in the project directory:

```bash
# Create .env file
echo "TOKEN=your_discord_alt_token_here" > .env
```

Replace `your_discord_alt_token_here` with your actual Discord token.

### Step 4: Configure Discord Settings

Edit `rules.py` with your Discord server information:

```python
# Get these IDs by right-clicking and "Copy ID" (Developer Mode must be enabled)

# Channel ID to monitor
ACCEPTABLE_CHANNELS = [YOUR_CHANNEL_ID]

# Server/Guild ID to monitor  
ACCEPTABLE_GUILDS = [YOUR_GUILD_ID]

# Role mention required in messages (optional)
ACCEPTABLE_ROLES = ["@&YOUR_ROLE_ID"]
```

#### How to Get IDs:

1. **Channel ID**: Right-click the channel → "Copy ID"
2. **Guild ID**: Right-click the server name → "Copy ID"
3. **Role ID**: Right-click the role → "Copy ID"

### Step 5: Configure Chrome Version

Check your Chrome version and update `runbot.py` if needed:

```python
# In runbot.py, line ~25
driver = uc.Chrome(version_main=YOUR_CHROME_VERSION)
```

To find your Chrome version:
1. Open Chrome
2. Go to `chrome://version/`
3. Note the version number (e.g., 138.0.7204.158 → use 138)

### Step 6: Test the Setup

Run a quick test to ensure everything is working:

```bash
python runbot.py
```

You should see:
```
🚀 Starting Auto-Gambler Bot...
⚠️ Remember: Use alt account only - violates Discord ToS
Logged in as YourAltAccount#1234
```

## 🎯 Configuration Options

### Discord Validation Rules

In `rules.py`, you can customize:

- **Multiple Channels**: Add more channel IDs to `ACCEPTABLE_CHANNELS`
- **Multiple Servers**: Add more guild IDs to `ACCEPTABLE_GUILDS`
- **Role Requirements**: Add role mentions to `ACCEPTABLE_ROLES`

### Browser Automation Settings

In `runbot.py`, you can adjust:

- **Delay Timing**: Modify `human_delay()` function
- **Button Selectors**: Add new selectors to `place_button_selectors`
- **Success Indicators**: Add new success patterns to `success_selectors`

## 🔧 Troubleshooting

### Common Issues

#### 1. "TOKEN not found" Error
```bash
# Ensure .env file exists and contains:
TOKEN=your_actual_token_here
```

#### 2. Chrome Version Mismatch
```bash
# Update Chrome or change version in runbot.py
driver = uc.Chrome(version_main=YOUR_VERSION)
```

#### 3. "Not valid guild and channel" Error
- Check that channel and guild IDs are correct
- Ensure the bot account has access to the server/channel
- Verify Developer Mode is enabled when copying IDs

#### 4. "Could not find place entry button" Error
- PrizePicks may have updated their website
- Check console output for selector attempts
- Update selectors in `place_prizepick_slip()` function

#### 5. Discord Login Issues
- Ensure you're using an alt account token
- Check if the account is not locked or suspended
- Verify the token is valid and not expired

### Debug Mode

Add debug prints to see what's happening:

```python
# In runbot.py, add these lines for debugging
print(f"Current URL: {driver.current_url}")
print(f"Page title: {driver.title}")
print(f"Message content: {message.content}")
```

## 🚨 Security Best Practices

### Account Safety
- ✅ Use dedicated alt account only
- ✅ Never share your token
- ✅ Keep token secure and private
- ✅ Don't use on public networks
- ❌ Never use main Discord account

### Operational Safety
- ✅ Test with small amounts first
- ✅ Monitor the bot while running
- ✅ Keep browser visible during testing
- ✅ Set up proper error handling
- ❌ Don't run unattended initially

## 📝 Testing Checklist

Before running in production:

- [ ] Bot connects to Discord successfully
- [ ] Bot responds to messages in target channel
- [ ] PrizePicks links are detected correctly
- [ ] Browser automation works (test with small amounts)
- [ ] Success/failure reactions are added to messages
- [ ] Error handling works properly

## 🎯 Running the Bot

### Development Mode (Visible Browser)
```bash
python runbot.py
```

### Production Mode (Headless)
For production, you may want to modify the Chrome driver to run headless:

```python
# In runbot.py, modify the driver initialization
driver = uc.Chrome(version_main=138, headless=True)
```

## 📊 Monitoring

Monitor the bot's activity:

1. **Console Output**: Watch for processing messages
2. **Discord Reactions**: Check for 🌭, ✅, ❌ reactions
3. **Browser Activity**: Monitor Chrome for automation
4. **Error Logs**: Watch for any error messages

## 🔄 Maintenance

### Regular Tasks
- Update Chrome version if needed
- Check for PrizePicks website changes
- Monitor Discord account status
- Review and update selectors if needed

### Updates
- Keep dependencies updated: `pip install -r requirements.txt --upgrade`
- Monitor for Discord API changes
- Check for Selenium/Chrome driver updates

---

**Remember: Use responsibly and at your own risk! 🎲** 