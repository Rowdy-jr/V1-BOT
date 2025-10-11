import os
import logging
import threading
import requests
import time
from flask import Flask
from telebot import TeleBot, types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app for Render Web Service port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is running!"

def run_flask():
    """Run Flask app on port 8080 for Render"""
    app.run(host='0.0.0.0', port=8080)

def start_flask_server():
    """Start Flask in a separate thread"""
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("Flask server started on port 8080")

def keep_alive_ping():
    """Ping the app every 10 minutes to prevent sleep on free server"""
    # Get your Render URL - replace with your actual URL
    render_url = os.getenv('RENDER_URL', 'https://v1-bot-cd3b.onrender.com')
    
    print(f"Starting keep-alive ping to: {render_url}")
    
    while True:
        try:
            response = requests.get(render_url, timeout=10)
            if response.status_code == 200:
                print(f"Keep-alive ping successful: {response.status_code}")
            else:
                print(f"Keep-alive ping warning: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Keep-alive ping failed: {e}")
        except Exception as e:
            print(f"Keep-alive ping error: {e}")
        
        # Wait 10 minutes before next ping
        time.sleep(300)

print("PREMIUM TELEGRAM BOT - STARTING...")

# Get bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables!")
    exit(1)

print(f"Token loaded: {len(BOT_TOKEN)} characters")

# Initialize bot
bot = TeleBot(BOT_TOKEN)

# Premium content data - 2 TIERS ONLY
PREMIUM_CONTENT = {
    'premium': {
        'price': 15,
        'features': [
            "Crypto Earning Tutorial (Tested Methods)",
            "Cheap Electronics Channels (Laptops/Mobiles)",
            "Universal Search Bot (Movies/Apps/Content)",
            "Bot Discovery Bot", 
            "News & 18+ Content Channels",
            "Basic Cyber Security Alerts"
        ],
        'warnings': [
            "CRYPTO INVESTMENTS CAN LEAD TO COMPLETE FINANCIAL LOSS",
            "ONLY INVEST MONEY YOU CAN AFFORD TO LOSE",
            "VERIFY SELLERS BEFORE BUYING ELECTRONICS",
            "YOU ARE 100% RESPONSIBLE FOR YOUR FINANCIAL DECISIONS"
        ]
    },
    'full_premium': {
        'price': 25,
        'features': [
            "ADVANCED Crypto Earning Strategies",
            "Electronics Supplier DIRECT Contacts", 
            "Premium Search Bot + Exclusive Filters",
            "Exclusive Bot Collection + Custom Bots",
            "Premium Content + 18+ Channels Access",
            "REAL-TIME Cyber Threat Alerts",
            "Dark Web Security Monitoring",
            "Priority Customer Support",
            "Lifetime Future Updates",
            "Custom Request Priority"
        ],
        'warnings': [
            "EXTREME RISK: Crypto trading may result in TOTAL CAPITAL LOSS",
            "DARK WEB CONTENT FOR EDUCATIONAL/SECURITY PURPOSES ONLY",
            "ILLEGAL ACTIVITIES ARE STRICTLY PROHIBITED",
            "18+ AGE VERIFICATION REQUIRED",
            "NO REFUNDS - ALL SALES ARE FINAL",
            "YOU BEAR FULL RESPONSIBILITY FOR ALL ACTIONS"
        ]
    }
}

# Terms & Conditions
TERMS_CONDITIONS = """
TERMS & CONDITIONS

1. AGE REQUIREMENT: You must be 18+ years old to purchase.

2. NO FINANCIAL ADVICE: All crypto/content provided is for informational purposes only, not financial advice.

3. NO GUARANTEES: There are no guarantees of profits. Past performance does not equal future results.

4. FULL RESPONSIBILITY: You are 100% responsible for your investment decisions and outcomes.

5. NO REFUNDS: All sales are final. No refunds for any reason.

6. LEGAL COMPLIANCE: You must comply with all local laws and regulations.

7. PROHIBITED USE: Illegal activities, scams, or fraudulent use is strictly forbidden.

8. RISK ACKNOWLEDGMENT: You understand and accept all risks involved.

9. SERVICE TERMS: We reserve the right to modify or discontinue services.

10. LIABILITY LIMITATION: We are not liable for any financial losses, damages, or legal issues.

By purchasing, you automatically agree to all these terms.
"""

# Payment details
PAYMENT_INFO = {
    'payment_methods': [
        "USDT (TRC20): TFqaxyAJpr8AC2cbrJqiLte3egme53YH8A",
        "Contact for other payment options"
    ],
    'contact_admin': "@flexxerone"
}

# Store users and their tiers
premium_users = set()
full_premium_users = set()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start command"""
    user = message.from_user
    user_id = user.id
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        types.InlineKeyboardButton("Free Solutions", callback_data="free_solutions"),
        types.InlineKeyboardButton("Premium Tiers", callback_data="pricing_tiers"),
        types.InlineKeyboardButton("Terms & Conditions", callback_data="terms"),
        types.InlineKeyboardButton("Contact Admin", callback_data="contact_admin"),
        types.InlineKeyboardButton("My Account", callback_data="my_account")
    ]
    
    for button in buttons:
        markup.add(button)
    
    # Check user tier
    user_tier = "Free"
    if user_id in full_premium_users:
        user_tier = "Full Premium"
    elif user_id in premium_users:
        user_tier = "Premium"
    
    welcome_text = f"""
Welcome to Exclusive Helper Bot, {user.first_name}!

Your Current Tier: {user_tier}

Choose an option below:

- Free Telegram solutions
- Premium access tiers  
- Read terms & conditions
- Contact support
- Account information

All premium content requires accepting our terms.
    """
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    logger.info(f"User {user.first_name} (ID: {user_id}) started - Tier: {user_tier}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle inline button clicks"""
    try:
        user_id = call.from_user.id
        
        if call.data == "free_solutions":
            show_free_solutions(call)
        elif call.data == "pricing_tiers":
            show_pricing_tiers(call)
        elif call.data == "terms":
            show_terms(call)
        elif call.data == "contact_admin":
            contact_admin(call)
        elif call.data == "my_account":
            show_my_account(call)
        elif call.data == "premium_info":
            show_tier_info(call, 'premium')
        elif call.data == "full_premium_info":
            show_tier_info(call, 'full_premium')
        elif call.data == "back_main":
            back_to_main(call)
        elif call.data == "unblock_help":
            show_unblock_help(call)
        elif call.data == "sensitive_help":
            show_sensitive_help(call)
        elif call.data == "find_help":
            show_find_help(call)
        elif call.data == "security_help":
            show_security_help(call)
            
    except Exception as e:
        logger.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "Error occurred, please try again.")

def show_free_solutions(call):
    """Show actual free solutions that provide real value"""
    response = """
FREE TELEGRAM SOLUTIONS

Here are actual solutions to common Telegram problems:

UNBLOCK CHANNELS:
- Use Telegram Web: web.telegram.org
- Try Telegram X app from your app store
- Use a free VPN (Windscribe, ProtonVPN)
- Ask admin for invite link

SENSITIVE CONTENT ERROR:
1. Go to Settings > Privacy & Security
2. Find 'Sensitive Content' 
3. Disable the filter
*Note: Not available in all regions

FIND CHANNELS & BOTS:
- Search: "site:t.me keyword" on Google
- Use @BotFather to create your own bots
- Check Telegram directories like:
  * tgdrivel.com
  * telegramchannels.me

SECURITY TIPS:
- Enable 2FA in Settings
- Use usernames instead of phone numbers
- Be careful with third-party apps
- Regularly check active sessions

BASIC TROUBLESHOOTING:
- Clear cache in Settings
- Update Telegram to latest version
- Restart the app
- Check internet connection

FREE BOTS TO TRY:
- @BotFather - Create your own bots
- @Like - Get channel analytics
- @GroupHelpBot - Manage groups
- @StickerDownloadBot - Download stickers

These free solutions should help with most common issues! If you need advanced tools and exclusive content, consider upgrading to premium.
"""
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("Unblock Channels", callback_data="unblock_help"),
        types.InlineKeyboardButton("Fix Sensitive Content", callback_data="sensitive_help"),
        types.InlineKeyboardButton("Find Content", callback_data="find_help"),
        types.InlineKeyboardButton("Security Tips", callback_data="security_help"),
        types.InlineKeyboardButton("Premium Features", callback_data="pricing_tiers"),
        types.InlineKeyboardButton("Main Menu", callback_data="back_main")
    ]
    
    # Add buttons in rows
    markup.add(buttons[0], buttons[1])  # Row 1
    markup.add(buttons[2], buttons[3])  # Row 2
    markup.add(buttons[4])              # Row 3
    markup.add(buttons[5])              # Row 4
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_unblock_help(call):
    """Detailed help for unblocking channels"""
    response = """
COMPLETE GUIDE TO UNBLOCK TELEGRAM CHANNELS

Method 1: Use Telegram Web
- Visit: web.telegram.org
- Works even when app is blocked
- No installation needed

Method 2: Telegram X App
- Download from official app store
- Different infrastructure
- Often bypasses blocks

Method 3: Free VPN Services
- Windscribe (10GB free monthly)
- ProtonVPN (unlimited free)
- TurboVPN (mobile app)
- Setup guides available online

Method 4: Proxy Servers
1. Go to Settings > Data & Storage > Proxy
2. Add proxy manually or find public ones
3. Test connection

Method 5: Ask for Invite
- Contact channel admin directly
- Request private invite link
- Join through group discussions

Tip: VPNs are most reliable for consistent access.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back to Free Solutions", callback_data="free_solutions"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_sensitive_help(call):
    """Detailed help for sensitive content"""
    response = """
FIX SENSITIVE CONTENT FILTER

Step-by-Step Solution:

1. Open Telegram Settings
2. Tap 'Privacy and Security'
3. Scroll to find 'Sensitive Content'
4. Disable the filter

If option is missing:
- Your country/region may restrict this
- Try using a VPN first
- Some iOS restrictions apply

VPN Method:
1. Install free VPN (Windscribe/ProtonVPN)
2. Connect to different country
3. Restart Telegram
4. Check if option appears

Alternative Solutions:
- Use Telegram Web version
- Try different Telegram client
- Ask sender to use different media format

Safety Note: This filter exists to protect users. Disable responsibly.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back to Free Solutions", callback_data="free_solutions"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_find_help(call):
    """Detailed help for finding content"""
    response = """
FIND TELEGRAM CHANNELS & BOTS

Search Methods:

Google Search Tricks:
- "site:t.me keyword"
- "telegram channel keyword"
- "t.me/group keyword"

Telegram Directories:
- tgdrivel.com
- telegramchannels.me
- tgram.io
- telegram-group.com

Bot Discovery:
- @BotFather - Official bot list
- @StoreBot - Bot store
- Search within Telegram: "@botname"

Social Media:
- Reddit: r/TelegramChannels
- Twitter: Search "telegram channel"
- Facebook groups

Networking:
- Ask in related groups
- Check bio/links of influencers
- Join discussion groups

Advanced Tips:
- Use specific keywords
- Check channel engagement
- Verify channel authenticity
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back to Free Solutions", callback_data="free_solutions"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_security_help(call):
    """Detailed security tips"""
    response = """
TELEGRAM SECURITY GUIDE

Essential Security Settings:

Two-Factor Authentication:
1. Settings > Privacy & Security > 2FA
2. Set strong password
3. Save recovery email

Privacy Settings:
- Phone number: Nobody
- Last seen: My Contacts  
- Profile photo: My Contacts
- Groups: My Contacts

Session Management:
- Regularly check Active Sessions
- Terminate unfamiliar sessions
- Use passcode lock

Safety Practices:
- Don't click suspicious links
- Verify sender identity
- Be careful with files
- Use official apps only

Channel Safety:
- Check member count & activity
- Read channel description
- Verify admin credibility
- Avoid too-good-to-be-true offers

Quick Security Check:
- 2FA enabled
- Privacy settings configured  
- Active sessions reviewed
- Official app used
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back to Free Solutions", callback_data="free_solutions"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_terms(call):
    """Show terms and conditions"""
    response = f"""
TERMS & CONDITIONS - MUST READ

{TERMS_CONDITIONS}

BY MAKING ANY PURCHASE, YOU AUTOMATICALLY AGREE TO ALL THESE TERMS.

Continue only if you fully understand and accept these conditions.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Continue to Pricing", callback_data="pricing_tiers"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_pricing_tiers(call):
    """Show both premium tiers"""
    response = f"""
PREMIUM ACCESS TIERS

Choose your level:

PREMIUM TIER - ${PREMIUM_CONTENT['premium']['price']}
- Crypto earning methods
- Electronics deals
- Search bots & content
- Basic security alerts

FULL PREMIUM - ${PREMIUM_CONTENT['full_premium']['price']}
- Advanced crypto strategies  
- Supplier direct contacts
- Real-time monitoring
- Priority support + Updates

Both tiers require accepting our Terms & Conditions.
"""
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("Premium - $15", callback_data="premium_info"),
        types.InlineKeyboardButton("Full Premium - $25", callback_data="full_premium_info"),
        types.InlineKeyboardButton("Read Terms First", callback_data="terms"),
        types.InlineKeyboardButton("Main Menu", callback_data="back_main")
    ]
    
    for button in buttons:
        markup.add(button)
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_tier_info(call, tier):
    """Show detailed information for a specific tier"""
    tier_data = PREMIUM_CONTENT[tier]
    
    if tier == 'premium':
        response = f"""
PREMIUM TIER - ${tier_data['price']}

CRITICAL WARNINGS:
"""
    else:  # full_premium
        response = f"""
FULL PREMIUM - ${tier_data['price']}

EXTREME RISK WARNINGS:
"""
    
    # Add warnings
    for warning in tier_data['warnings']:
        response += f"- {warning}\n"
    
    # Add features
    response += f"\nINCLUDED FEATURES:\n"
    for feature in tier_data['features']:
        response += f"- {feature}\n"
    
    # Add payment info
    payment_methods = "\n".join(PAYMENT_INFO['payment_methods'])
    response += f"""

PAYMENT METHODS:
{payment_methods}

AFTER PAYMENT:
Contact: {PAYMENT_INFO['contact_admin']}
Include: Your Telegram ID + Payment Proof

Send EXACT amount: ${tier_data['price']} USDT

By purchasing, you confirm:
- You are 18+ years old
- You read and accept ALL Terms & Conditions  
- You understand ALL risks involved
- You take FULL responsibility for your actions
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Review Terms Again", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("Back to Pricing", callback_data="pricing_tiers"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_my_account(call):
    """Show user account information"""
    user_id = call.from_user.id
    user = call.from_user
    
    # Determine user tier
    if user_id in full_premium_users:
        tier = "Full Premium"
        features = PREMIUM_CONTENT['full_premium']['features']
    elif user_id in premium_users:
        tier = "Premium"
        features = PREMIUM_CONTENT['premium']['features']
    else:
        tier = "Free"
        features = ["Free solutions only"]
    
    response = f"""
ACCOUNT INFORMATION

User: {user.first_name}
ID: {user_id}
Tier: {tier}

Your Access:
"""
    
    for feature in features[:6]:
        response += f"- {feature}\n"
    
    if len(features) > 6:
        response += f"- ... and {len(features)-6} more\n"
    
    if tier == "Free":
        response += "\nUpgrade to unlock premium features!"
    
    markup = types.InlineKeyboardMarkup()
    if tier == "Free":
        markup.add(types.InlineKeyboardButton("Upgrade Now", callback_data="pricing_tiers"))
        markup.add(types.InlineKeyboardButton("Read Terms First", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def contact_admin(call):
    """Show admin contact information"""
    response = f"""
CONTACT ADMIN

For payments, support, or questions:

Admin: {PAYMENT_INFO['contact_admin']}

Required Information:
- Your Telegram ID
- Payment method & proof  
- Specific issue/question

Response Time: Within 24 hours

Payment Address:
USDT (TRC20): TFqaxyAJpr8AC2cbrJqiLte3egme53YH8A

Please read Terms & Conditions before contacting about payments.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Pricing Tiers", callback_data="pricing_tiers"))
    markup.add(types.InlineKeyboardButton("Terms & Conditions", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def back_to_main(call):
    """Return to main menu"""
    try:
        send_welcome(call.message)
    except:
        # If editing fails, send new message
        send_welcome(call.message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all other messages"""
    send_welcome(message)

def main():
    """Start the bot"""
    print("=" * 60)
    print("PREMIUM TELEGRAM BOT - READY TO EARN!")
    print("=" * 60)
    print(f"Premium Tier: ${PREMIUM_CONTENT['premium']['price']}")
    print(f"Full Premium: ${PREMIUM_CONTENT['full_premium']['price']}")
    print("Accepting: USDT (TRC20)")
    print("Admin: @flexxerone")
    print("Clear Terms & Warnings Included")
    print("=" * 60)
    
    # Start Flask server for Render Web Service
    start_flask_server()
    
    # START KEEP-ALIVE PING
    keep_alive_thread = threading.Thread(target=keep_alive_ping)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    print("Keep-alive ping started (every 10 minutes)")
    
    try:
        print("Bot is running and polling for messages...")
        print("Test your bot by sending /start on Telegram")
        print("Flask server running on port 8080")
        print("=" * 60)
        
        # Start bot polling
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
