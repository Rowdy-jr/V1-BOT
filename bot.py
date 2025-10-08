import os
import logging
import threading
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

# ð¯ ADDED: Flask app for Render Web Service port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "ð¤ Telegram Bot is running!"

def run_flask():
    """Run Flask app on port 8080 for Render"""
    app.run(host='0.0.0.0', port=8080)

def start_flask_server():
    """Start Flask in a separate thread"""
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("â Flask server started on port 8080")

print("ð PREMIUM TELEGRAM BOT - STARTING...")

# Get bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("â BOT_TOKEN not found in environment variables!")
    exit(1)

print(f"â Token loaded: {len(BOT_TOKEN)} characters")

# Initialize bot
bot = TeleBot(BOT_TOKEN)

# Premium content data - 2 TIERS ONLY
PREMIUM_CONTENT = {
    'premium': {
        'price': 15,
        'features': [
            "ð° Crypto Earning Tutorial (Tested Methods)",
            "ð Cheap Electronics Channels (Laptops/Mobiles)",
            "ð Universal Search Bot (Movies/Apps/Content)",
            "ð¤ Bot Discovery Bot", 
            "ð° News & 18+ Content Channels",
            "ð¡ï¸ Basic Cyber Security Alerts"
        ],
        'warnings': [
            "â ï¸ CRYPTO INVESTMENTS CAN LEAD TO COMPLETE FINANCIAL LOSS",
            "â ï¸ ONLY INVEST MONEY YOU CAN AFFORD TO LOSE",
            "â ï¸ VERIFY SELLERS BEFORE BUYING ELECTRONICS",
            "â ï¸ YOU ARE 100% RESPONSIBLE FOR YOUR FINANCIAL DECISIONS"
        ]
    },
    'full_premium': {
        'price': 25,
        'features': [
            "ð° ADVANCED Crypto Earning Strategies",
            "ð Electronics Supplier DIRECT Contacts", 
            "ð Premium Search Bot + Exclusive Filters",
            "ð¤ Exclusive Bot Collection + Custom Bots",
            "ð° Premium Content + 18+ Channels Access",
            "ð¡ï¸ REAL-TIME Cyber Threat Alerts",
            "ð Dark Web Security Monitoring",
            "â¡ Priority Customer Support",
            "ð Lifetime Future Updates",
            "ð¯ Custom Request Priority"
        ],
        'warnings': [
            "ð¨ EXTREME RISK: Crypto trading may result in TOTAL CAPITAL LOSS",
            "ð¨ DARK WEB CONTENT FOR EDUCATIONAL/SECURITY PURPOSES ONLY",
            "ð¨ ILLEGAL ACTIVITIES ARE STRICTLY PROHIBITED",
            "ð¨ 18+ AGE VERIFICATION REQUIRED",
            "ð¨ NO REFUNDS - ALL SALES ARE FINAL",
            "ð¨ YOU BEAR FULL RESPONSIBILITY FOR ALL ACTIONS"
        ]
    }
}

# Terms & Conditions
TERMS_CONDITIONS = """
ð TERMS & CONDITIONS

1. AGE REQUIREMENT: You must be 18+ years old to purchase.

2. NO FINANCIAL ADVICE: All crypto/content provided is for informational purposes only, not financial advice.

3. NO GUARANTEES: There are no guarantees of profits. Past performance â  future results.

4. FULL RESPONSIBILITY: You are 100% responsible for your investment decisions and outcomes.

5. NO REFUNDS: All sales are final. No refunds for any reason.

6. LEGAL COMPLIANCE: You must comply with all local laws and regulations.

7. PROHIBITED USE: Illegal activities, scams, or fraudulent use is strictly forbidden.

8. RISK ACKNOWLEDGMENT: You understand and accept all risks involved.

9. SERVICE TERMS: We reserve the right to modify or discontinue services.

10. LIABILITY LIMITATION: We are not liable for any financial losses, damages, or legal issues.

By purchasing, you automatically agree to all these terms.
"""

# UPDATED WITH YOUR REAL PAYMENT DETAILS
PAYMENT_INFO = {
    'payment_methods': [
        "ð USDT (TRC20): TFqaxyAJpr8AC2cbrJqiLte3egme53YH8A",
        "ð± Contact for other payment options"
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
        types.InlineKeyboardButton("ð Free Solutions", callback_data="free_solutions"),
        types.InlineKeyboardButton("ð° Premium Tiers", callback_data="pricing_tiers"),
        types.InlineKeyboardButton("ð Terms & Conditions", callback_data="terms"),
        types.InlineKeyboardButton("ð Contact Admin", callback_data="contact_admin"),
        types.InlineKeyboardButton("ð My Account", callback_data="my_account")
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
ð¤ Welcome to Exclusive Helper Bot, {user.first_name}!

ð¯ Your Current Tier: {user_tier}

ð¡ Choose an option below:

â¢ ð Free Telegram solutions
â¢ ð° Premium access tiers  
â¢ ð Read terms & conditions
â¢ ð Contact support
â¢ ð Account information

ð All premium content requires accepting our terms.
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
            
    except Exception as e:
        logger.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "â Error occurred, please try again.")

def show_free_solutions(call):
    """Show free solutions menu"""
    response = """
ð FREE SOLUTIONS

Basic Telegram help:

â¢ Unblock restricted channels
â¢ Fix sensitive content errors  
â¢ Find public channels
â¢ Basic troubleshooting guides

ð Upgrade to premium for exclusive money-making content!
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ð° Premium Tiers", callback_data="pricing_tiers"))
    markup.add(types.InlineKeyboardButton("ð Read Terms First", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("ð Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_terms(call):
    """Show terms and conditions"""
    response = f"""
ð TERMS & CONDITIONS - MUST READ

{TERMS_CONDITIONS}

ð¨ BY MAKING ANY PURCHASE, YOU AUTOMATICALLY AGREE TO ALL THESE TERMS.

Continue only if you fully understand and accept these conditions.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ð° Continue to Pricing", callback_data="pricing_tiers"))
    markup.add(types.InlineKeyboardButton("ð Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_pricing_tiers(call):
    """Show both premium tiers"""
    response = f"""
ð° PREMIUM ACCESS TIERS

Choose your level:

ð PREMIUM TIER - ${PREMIUM_CONTENT['premium']['price']}
â¢ Crypto earning methods
â¢ Electronics deals
â¢ Search bots & content
â¢ Basic security alerts

â¡ FULL PREMIUM - ${PREMIUM_CONTENT['full_premium']['price']}
â¢ Advanced crypto strategies  
â¢ Supplier direct contacts
â¢ Real-time monitoring
â¢ Priority support + Updates

ð Both tiers require accepting our Terms & Conditions.
"""
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("ð Premium - $15", callback_data="premium_info"),
        types.InlineKeyboardButton("â¡ Full Premium - $25", callback_data="full_premium_info"),
        types.InlineKeyboardButton("ð Read Terms First", callback_data="terms"),
        types.InlineKeyboardButton("ð Main Menu", callback_data="back_main")
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
ð PREMIUM TIER - ${tier_data['price']}

ð´ **CRITICAL WARNINGS:**
"""
    else:  # full_premium
        response = f"""
â¡ FULL PREMIUM - ${tier_data['price']}

ð¨ **EXTREME RISK WARNINGS:**
"""
    
    # Add warnings
    for warning in tier_data['warnings']:
        response += f"â¢ {warning}\n"
    
    # Add features
    response += f"\nâ **INCLUDED FEATURES:**\n"
    for feature in tier_data['features']:
        response += f"â¢ {feature}\n"
    
    # Add payment info
    payment_methods = "\n".join(PAYMENT_INFO['payment_methods'])
    response += f"""
    
ð³ **PAYMENT METHODS:**
{payment_methods}

ð **AFTER PAYMENT:**
Contact: {PAYMENT_INFO['contact_admin']}
Include: Your Telegram ID + Payment Proof

ð° **Send EXACT amount: ${tier_data['price']} USDT**

â **By purchasing, you confirm:**
â¢ You are 18+ years old
â¢ You read and accept ALL Terms & Conditions  
â¢ You understand ALL risks involved
â¢ You take FULL responsibility for your actions
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ð Review Terms Again", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("ð° Back to Pricing", callback_data="pricing_tiers"))
    markup.add(types.InlineKeyboardButton("ð Main Menu", callback_data="back_main"))
    
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
ð ACCOUNT INFORMATION

ð¤ User: {user.first_name}
ð ID: {user_id}
ð¯ Tier: {tier}

ð Your Access:
"""
    
    for feature in features[:6]:
        response += f"â¢ {feature}\n"
    
    if len(features) > 6:
        response += f"â¢ ... and {len(features)-6} more\n"
    
    if tier == "Free":
        response += "\nð Upgrade to unlock premium features!"
    
    markup = types.InlineKeyboardMarkup()
    if tier == "Free":
        markup.add(types.InlineKeyboardButton("ð° Upgrade Now", callback_data="pricing_tiers"))
        markup.add(types.InlineKeyboardButton("ð Read Terms First", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("ð Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(
        response,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def contact_admin(call):
    """Show admin contact information"""
    response = f"""
ð CONTACT ADMIN

For payments, support, or questions:

ð¤ Admin: {PAYMENT_INFO['contact_admin']}

ð Required Information:
â¢ Your Telegram ID
â¢ Payment method & proof  
â¢ Specific issue/question

â° Response Time: Within 24 hours

ð Payment Address:
USDT (TRC20): TFqaxyAJpr8AC2cbrJqiLte3egme53YH8A

ð Please read Terms & Conditions before contacting about payments.
"""
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ð° Pricing Tiers", callback_data="pricing_tiers"))
    markup.add(types.InlineKeyboardButton("ð Terms & Conditions", callback_data="terms"))
    markup.add(types.InlineKeyboardButton("ð Main Menu", callback_data="back_main"))
    
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
    print("ð¤ 2-TIER PREMIUM BOT - READY TO EARN!")
    print("=" * 60)
    print(f"ð Premium Tier: ${PREMIUM_CONTENT['premium']['price']}")
    print(f"â¡ Full Premium: ${PREMIUM_CONTENT['full_premium']['price']}")
    print("ð³ Accepting: USDT (TRC20)")
    print("ð¤ Admin: @flexxerone")
    print("ð Clear Terms & Warnings Included")
    print("=" * 60)
    
    # ð¯ ADDED: Start Flask server for Render Web Service
    start_flask_server()
    
    try:
        print("â Bot is running and polling for messages...")
        print("ð± Test your bot by sending /start on Telegram")
        print("ð Flask server running on port 8080")
         print("=")
        
        # Start bot polling
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except Exception as e:
        logger.error(f"â Failed to start bot: {e}")
        print(f"â Error: {e}")

if __name__ == '__main__':
    main()
