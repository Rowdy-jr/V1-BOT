import os
import logging
import threading
import time
import requests
import json
from flask import Flask, request
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

# Flask app for Render Web Service
app = Flask(__name__)

# Get bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables!")
    exit(1)

# Initialize bot
bot = TeleBot(BOT_TOKEN)

print("SECRET INFO BOT - STARTING...")
print(f"Token loaded: {len(BOT_TOKEN)} characters")

@app.route('/')
def home():
    return "Secret Info Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'OK'

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
    """Ping the app every 5 minutes to prevent sleep on free server"""
    render_url = os.getenv('RENDER_URL', 'https://v1-bot-cd3b.onrender.com')
    
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
        
        # Wait 5 minutes before next ping
        time.sleep(300)

def save_users():
    """Save premium users to file"""
    data = {
        'premium_users': list(premium_users),
        'full_premium_users': list(full_premium_users)
    }
    with open('premium_users.json', 'w') as f:
        json.dump(data, f)

def load_users():
    """Load premium users from file"""
    try:
        with open('premium_users.json', 'r') as f:
            data = json.load(f)
            premium_users.update(data.get('premium_users', []))
            full_premium_users.update(data.get('full_premium_users', []))
    except FileNotFoundError:
        pass  # First time running

# Secret Info packages
SECRET_INFO = {
    'basic': {
        'price': 15,
        'name': 'Basic Secret Info',
        'features': [
            "Crypto earning methods (tested)",
            "Cheap electronics supplier contacts",
            "Universal search bot access",
            "News & content channels",
            "Basic security alerts"
        ],
        'warnings': [
            "This is information only - not financial advice",
            "You are 100% responsible for your decisions",
            "No refunds - all sales are final",
            "Verify sellers before any purchases"
        ]
    },
    'advanced': {
        'price': 25,
        'name': 'Advanced Secret Info',
        'features': [
            "Advanced crypto earning strategies",
            "Direct supplier contacts (electronics)",
            "Premium search bots + filters",
            "Exclusive bot collection",
            "Premium content channels",
            "Real-time security alerts",
            "Dark web monitoring info",
            "Priority support access",
            "Future updates included"
        ],
        'warnings': [
            "EXTREME RISK: Crypto may result in total loss",
            "Information only - not financial advice",
            "Dark web content for educational purposes",
            "18+ age verification required",
            "NO REFUNDS - all sales are final",
            "You bear full responsibility for all actions"
        ]
    }
}

# Terms & Conditions
TERMS_CONDITIONS = """
TERMS & CONDITIONS

1. AGE REQUIREMENT: You must be 18+ years old to purchase.

2. INFORMATION ONLY: All content provided is for informational purposes only, not advice.

3. NO GUARANTEES: There are no guarantees of any outcomes.

4. FULL RESPONSIBILITY: You are 100% responsible for your decisions and outcomes.

5. NO REFUNDS: All sales are final. No refunds for any reason.

6. LEGAL COMPLIANCE: You must comply with all local laws and regulations.

7. PROHIBITED USE: Illegal activities are strictly forbidden.

8. RISK ACKNOWLEDGMENT: You understand and accept all risks involved.

9. SERVICE TERMS: We reserve the right to modify services.

10. LIABILITY LIMITATION: We are not liable for any losses or damages.

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

# Load existing premium users
load_users()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start command"""
    user = message.from_user
    user_id = user.id
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        types.InlineKeyboardButton("Available Solutions", callback_data="solutions"),
        types.InlineKeyboardButton("Secret Info Packages", callback_data="packages"),
        types.InlineKeyboardButton("Terms & Conditions", callback_data="terms"),
        types.InlineKeyboardButton("Contact Admin", callback_data="contact_admin"),
        types.InlineKeyboardButton("My Access", callback_data="my_account")
    ]
    
    for button in buttons:
        markup.add(button)
    
    # Check user tier
    user_tier = "No Access"
    if user_id in full_premium_users:
        user_tier = "Advanced Secret Info"
    elif user_id in premium_users:
        user_tier = "Basic Secret Info"
    
    welcome_text = f"""
Welcome to Secret Info Bot, {user.first_name}!

Your Current Access: {user_tier}

This bot provides exclusive information packages.

Choose an option below to explore what's available.

All secret info requires accepting our terms.
    """
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    logger.info(f"User {user.first_name} (ID: {user_id}) started - Tier: {user_tier}")

@bot.message_handler(commands=['addpremium'])
def add_premium_user(message):
    """Admin command to add users to premium"""
    if message.from_user.username != 'flexxerone':
        bot.reply_to(message, "Unauthorized access.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "Usage: /addpremium <user_id> <tier>\nTiers: basic, advanced")
            return
        
        user_id = int(parts[1])
        tier = parts[2].lower()
        
        if tier == 'basic':
            premium_users.add(user_id)
            save_users()
            bot.reply_to(message, f"User {user_id} added to Basic Secret Info.")
        elif tier == 'advanced':
            full_premium_users.add(user_id)
            save_users()
            bot.reply_to(message, f"User {user_id} added to Advanced Secret Info.")
        else:
            bot.reply_to(message, "Invalid tier. Use: basic, advanced")
            
    except ValueError:
        bot.reply_to(message, "Invalid user ID. Must be a number.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['removepremium'])
def remove_premium_user(message):
    """Admin command to remove users from premium"""
    if message.from_user.username != 'flexxerone':
        bot.reply_to(message, "Unauthorized access.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /removepremium <user_id>")
            return
        
        user_id = int(parts[1])
        
        premium_users.discard(user_id)
        full_premium_users.discard(user_id)
        save_users()
        
        bot.reply_to(message, f"User {user_id} removed from secret info access.")
        
    except ValueError:
        bot.reply_to(message, "Invalid user ID. Must be a number.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['listpremium'])
def list_premium_users(message):
    """Admin command to list premium users"""
    if message.from_user.username != 'flexxerone':
        bot.reply_to(message, "Unauthorized access.")
        return
    
    premium_list = "\n".join([str(uid) for uid in premium_users]) or "None"
    full_premium_list = "\n".join([str(uid) for uid in full_premium_users]) or "None"
    
    response = f"""
Basic Secret Info Users ({len(premium_users)}):
{premium_list}

Advanced Secret Info Users ({len(full_premium_users)}):
{full_premium_list}
"""
    bot.reply_to(message, response)

@bot.message_handler(commands=['verify'])
def verify_payment(message):
    """User sends this after making payment"""
    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.first_name
    
    response = f"""
Payment Verification

User: {user_name}
ID: {user_id}

Please contact @flexxerone with:
1. This user ID: {user_id}
2. Payment proof (screenshot)
3. Package purchased (Basic/Advanced)

We will activate your secret info access within 24 hours.
"""
    bot.reply_to(message, response)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle inline button clicks"""
    try:
        user_id = call.from_user.id
        
        if call.data == "solutions":
            show_solutions(call)
        elif call.data == "packages":
            show_packages(call)
        elif call.data == "terms":
            show_terms(call)
        elif call.data == "contact_admin":
            contact_admin(call)
        elif call.data == "my_account":
            show_my_account(call)
        elif call.data == "basic_info":
            show_package_info(call, 'basic')
        elif call.data == "advanced_info":
            show_package_info(call, 'advanced')
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

def show_solutions(call):
    """Show available solutions"""
    response = """
AVAILABLE SOLUTIONS

Here are solutions to common Telegram issues:

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
- Check Telegram directories

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

For exclusive information and advanced methods, check our secret info packages.
"""
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("Unblock Channels", callback_data="unblock_help"),
        types.InlineKeyboardButton("Fix Sensitive Content", callback_data="sensitive_help"),
        types.InlineKeyboardButton("Find Content", callback_data="find_help"),
        types.InlineKeyboardButton("Security Tips", callback_data="security_help"),
        types.InlineKeyboardButton("Secret Info Packages", callback_data="packages"),
        types.InlineKeyboardButton("Main Menu", callback_data="back_main")
    ]
    
    markup.add(buttons[0], buttons[1])
    markup.add(buttons[2], buttons[3])
    markup.add(buttons[4])
    markup.add(buttons[5])
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_packages(call):
    """Show secret info packages"""
    response = f"""
SECRET INFO PACKAGES

Exclusive information packages available:

BASIC SECRET INFO - ${SECRET_INFO['basic']['price']}
- Crypto earning methods
- Electronics supplier contacts
- Search bot access
- Content channels
- Security alerts

ADVANCED SECRET INFO - ${SECRET_INFO['advanced']['price']}
- Advanced crypto strategies  
- Direct supplier contacts
- Premium bots + filters
- Real-time monitoring
- Priority support + Updates

Both packages require accepting our Terms & Conditions.
"""
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("Basic Secret Info - $15", callback_data="basic_info"),
        types.InlineKeyboardButton("Advanced Secret Info - $25", callback_data="advanced_info"),
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

def show_package_info(call, package):
    """Show detailed information for a specific package"""
    package_data = SECRET_INFO[package]
    
    response = f"""
{package_data['name']} - ${package_data['price']}

IMPORTANT NOTES:
"""
    
    for warning in package_data['warnings']:
        response += f"- {warning}\n"
    
    response += f"\nINFORMATION INCLUDED:\n"
    for feature in package_data['features']:
        response += f"- {feature}\n"
    
    payment_methods = "\n".join(PAYMENT_INFO['payment_methods'])
    response += f"""

PAYMENT METHODS:
{payment_methods}

AFTER PAYMENT:
Contact: {PAYMENT_INFO['contact_admin']}
Include: Your Telegram ID + Payment Proof

Send EXACT amount: ${package_data['price']} USDT

By purchasing, you confirm:
- You are 18+ years old
- You read and accept ALL Terms & Conditions  
- You understand this is information only
- You take FULL responsibility for your actions
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Review Terms Again", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("Back to Packages", callback_data="packages"))
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
    
    if user_id in full_premium_users:
        tier = "Advanced Secret Info"
        features = SECRET_INFO['advanced']['features']
    elif user_id in premium_users:
        tier = "Basic Secret Info"
        features = SECRET_INFO['basic']['features']
    else:
        tier = "No Access"
        features = ["Available solutions only"]
    
    response = f"""
ACCOUNT INFORMATION

User: {user.first_name}
ID: {user_id}
Access: {tier}

Your Information Access:
"""
    
    for feature in features[:6]:
        response += f"- {feature}\n"
    
    if len(features) > 6:
        response += f"- ... and {len(features)-6} more\n"
    
    if tier == "No Access":
        response += "\nPurchase a secret info package to unlock exclusive information!"
    
    markup = types.InlineKeyboardMarkup()
    if tier == "No Access":
        markup.add(types.InlineKeyboardButton("View Packages", callback_data="packages"))
        markup.add(types.InlineKeyboardButton("Read Terms First", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# [Keep all the helper functions: show_unblock_help, show_sensitive_help, show_find_help, show_security_help, show_terms, contact_admin, back_to_main]
# These remain the same as before...

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

Method 4: Proxy Servers
1. Go to Settings > Data & Storage > Proxy
2. Add proxy manually
3. Test connection

Method 5: Ask for Invite
- Contact channel admin directly
- Request private invite link

Tip: VPNs are most reliable for consistent access.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back to Solutions", callback_data="solutions"))
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

Safety Note: This filter exists to protect users. Disable responsibly.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back to Solutions", callback_data="solutions"))
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

Bot Discovery:
- @BotFather - Official bot list
- @StoreBot - Bot store
- Search within Telegram: "@botname"

Social Media:
- Reddit: r/TelegramChannels
- Twitter: Search "telegram channel"

Networking:
- Ask in related groups
- Check bio/links of influencers

Advanced Tips:
- Use specific keywords
- Check channel engagement
- Verify channel authenticity
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back to Solutions", callback_data="solutions"))
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
    markup.add(types.InlineKeyboardButton("Back to Solutions", callback_data="solutions"))
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
    markup.add(types.InlineKeyboardButton("Continue to Packages", callback_data="packages"))
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
    markup.add(types.InlineKeyboardButton("Secret Info Packages", callback_data="packages"))
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
        send_welcome(call.message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all other messages"""
    send_welcome(message)

def main():
    """Start the bot using webhooks"""
    print("=" * 60)
    print("SECRET INFO BOT - READY!")
    print("=" * 60)
    print(f"Basic Secret Info: ${SECRET_INFO['basic']['price']}")
    print(f"Advanced Secret Info: ${SECRET_INFO['advanced']['price']}")
    print("Accepting: USDT (TRC20)")
    print("Admin: @flexxerone")
    print("Information Packages Only")
    print("=" * 60)
    
    # Start Flask server
    start_flask_server()
    
    # Start keep-alive ping
    keep_alive_thread = threading.Thread(target=keep_alive_ping)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    print("Keep-alive ping started (every 5 minutes)")
    
    # Set up webhook
    render_url = os.getenv('RENDER_URL', 'https://v1-bot-cd3b.onrender.com')
    webhook_url = f"{render_url}/webhook"
    
    try:
        # Remove any existing webhook first
        bot.remove_webhook()
        time.sleep(1)
        
        # Set new webhook
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
        print("Bot is ready! Telegram will send updates to the webhook.")
        print("Flask server running on port 8080")
        print("=" * 60)
        
        # Keep the main thread alive
        while True:
            time.sleep(3600)  # Sleep for 1 hour
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
