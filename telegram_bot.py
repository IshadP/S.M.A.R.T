import logging
import joblib
import re
import urllib.parse
from telegram import Update
from telegram import ChatMember, ChatMemberAdministrator, ChatMemberOwner
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import TimedOut, NetworkError
import os
from dotenv import load_dotenv

load_dotenv()

bot_active = True
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

feature_states = {}
message_model = None
message_vectorizer = None
link_model = None
link_vectorizer = None
nb_model = None
nb_title_model = None
nb_text_model = None
tfidf_vectorizer = None
tfidf_title_vectorizer = None
tfidf_text_vectorizer = None

def load_models():
    """Load all detection models."""
    global message_model, message_vectorizer, link_model, link_vectorizer
    global nb_model, nb_title_model, nb_text_model
    global tfidf_vectorizer, tfidf_title_vectorizer, tfidf_text_vectorizer
    
    try:
        message_model = joblib.load("og_spam_model.pkl")
        message_vectorizer = joblib.load("og_spam_count_vectorizer.pkl")
        link_model = joblib.load("model.pkl")
        link_vectorizer = joblib.load("tfidf_vectorizer.pkl")
        nb_model = joblib.load("naive_bayes_model.pkl")
        nb_title_model = joblib.load("naive_bayes_title_model.pkl")
        nb_text_model = joblib.load("naive_bayes_text_model.pkl")
        tfidf_vectorizer = joblib.load("tfidf_vectorizer (2).pkl")
        tfidf_title_vectorizer = joblib.load("tfidf_vectorizer_title.pkl")
        tfidf_text_vectorizer = joblib.load("tfidf_vectorizer_text.pkl")
        logger.info("All detection models loaded successfully.")
        return True
    except Exception as e:
        logger.error(f"Error loading detection models: {e}")
        return False

def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r"\W+", " ", text)
    text = re.sub(r"\d+", "", text)
    return text.strip()

def extract_urls(text):
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[\w=&%+\.-]*)?(?:#[\w-]*)?'
    return re.findall(url_pattern, text)

def preprocess_url(url):
    parsed_url = urllib.parse.urlparse(url)
    url_text = f"{parsed_url.scheme} {parsed_url.netloc} {parsed_url.path} {parsed_url.params} {parsed_url.query} {parsed_url.fragment}"
    return url_text

def detect_spam(message_text):
    try:
        user_message = clean_text(message_text)
        transformed_text = message_vectorizer.transform([user_message])
        spam_prediction = message_model.predict(transformed_text)[0]
        return spam_prediction != 1  # Return True if spam is detected
    except Exception as e:
        logger.error(f"Error in spam detection: {e}")
        return False

def detect_malicious_links(message_text):
    try:
        urls = extract_urls(message_text)
        if not urls:
            return []
            
        malicious_links = []
        for url in urls:
            if is_malicious_link(url):
                malicious_links.append(url)
        return malicious_links
    except Exception as e:
        logger.error(f"Error in malicious link detection: {e}")
        return []

def is_malicious_link(url):
    try:
        processed_url = preprocess_url(url)
        url_features = link_vectorizer.transform([processed_url])
        prediction = link_model.predict(url_features)[0]
        return bool(prediction)
    except Exception as e:
        logger.error(f"Error checking malicious link: {e}")
        return False

def extract_news_components(text):
    lines = text.strip().split('\n')
    if len(lines) > 1:
        title = lines[0]
        content = '\n'.join(lines[1:])
    else:
        title = ""
        content = text
    return title, content

def detect_fake_news(title="", content=""):
    try:
        results = []
        if title and content:
            combined_text = f"{title} {content}"
            combined_features = tfidf_vectorizer.transform([combined_text])
            combined_prediction = nb_model.predict(combined_features)[0]
            combined_prob = nb_model.predict_proba(combined_features)[0]
            fake_prob = combined_prob[1] if combined_prediction == 1 else combined_prob[0]
            results.append(("Combined analysis", combined_prediction, fake_prob))
        if title:
            title_features = tfidf_title_vectorizer.transform([title])
            title_prediction = nb_title_model.predict(title_features)[0]
        return results
    except Exception as e:
        logger.error(f"Error detecting fake news: {e}")
        return []

async def is_admin(update: Update) -> bool:
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        member = await update.effective_chat.get_member(user_id)

        # Check if the user is an admin or the owner
        return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def stop(update: Update, context: CallbackContext) -> None:
    global bot_active
    bot_active = False 
    await update.message.reply_text("Bot has been stopped. Type /start to activate it again.")

async def toggle_feature(update: Update, context: CallbackContext) -> None:
    if not await is_admin(update):
        await update.message.reply_text("❌ You must be a group admin to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /toggle <feature> <on/off>\nAvailable features: spam, links, fake_news")
        return

    feature, state = context.args[0].lower(), context.args[1].lower()
    chat_id = update.effective_chat.id

    if feature not in ["spam", "links", "fake_news"]:
        await update.message.reply_text("Invalid feature. Available features: spam, links, fake_news")
        return

    if state not in ["on", "off"]:
        await update.message.reply_text("Invalid state. Use 'on' or 'off'.")
        return

    if chat_id not in feature_states:
        feature_states[chat_id] = {"spam": True, "links": True, "fake_news": True}

    feature_states[chat_id][feature] = (state == "on")
    await update.message.reply_text(f"Feature '{feature}' has been turned {'ON' if state == 'on' else 'OFF'}.")

async def analyze_message(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in feature_states:
        feature_states[chat_id] = {"spam": True, "links": True, "fake_news": True}

    message_text = update.message.text

    # Malicious link detection
    if feature_states[chat_id]["links"]:
        malicious_links = detect_malicious_links(message_text)
        if malicious_links:
            warning_text = f"⚠️ MALICIOUS LINK DETECTED: Found {len(malicious_links)} dangerous link(s) in your message"
            await update.message.reply_text(warning_text, reply_to_message_id=update.message.message_id)
            logger.warning(f"Detected malicious links: {malicious_links}")

    # Spam detection
    if feature_states[chat_id]["spam"]:
        if detect_spam(message_text):
            await update.message.reply_text("🚨 Message Appears to be Spam", reply_to_message_id=update.message.message_id)

    # Fake news detection
    if feature_states[chat_id]["fake_news"] and len(message_text) > 50:
        title, content = extract_news_components(message_text)
        fake_news_results = detect_fake_news(title, content)
        if fake_news_results:
            is_fake = any(result[1] == 1 for result in fake_news_results)
            if is_fake:
                details = []
                for analysis_type, prediction, probability in fake_news_results:
                    status = "FAKE" if prediction == 1 else "REAL"
                    confidence = probability * 100
                    details.append(f"{analysis_type}: {status} (Confidence: {confidence:.1f}%)")
                result_text = "🔍 POTENTIAL FAKE NEWS DETECTED:\n" + "\n".join(details)
                await update.message.reply_text(result_text, reply_to_message_id=update.message.message_id)

async def analyze_news(update: Update, context: CallbackContext) -> None:
    global bot_active
    if not bot_active:
        return
    if context.args:
        news_text = ' '.join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        news_text = update.message.reply_to_message.text
    else:
        await update.message.reply_text("Please provide news text after the /checkmessage command or reply to a message")
        return
        
    title, content = extract_news_components(news_text)
    fake_news_results = detect_fake_news(title, content)
    
    if fake_news_results:
        details = []
        for analysis_type, prediction, probability in fake_news_results:
            status = "FAKE" if prediction == 1 else "REAL"
            confidence = probability * 100
            details.append(f"{analysis_type}: {status} (Confidence: {confidence:.1f}%)")
        result_text = "🔍 News Analysis Results:\n" + "\n".join(details)
    else:
        result_text = "Unable to analyze the provided news text"
        
    await update.message.reply_text(result_text)

async def feature_status(update: Update, context: CallbackContext) -> None:
    """Display the current status of detection features."""
    chat_id = update.effective_chat.id
    if chat_id not in feature_states:
        feature_states[chat_id] = {"spam": True, "links": True, "fake_news": True}

    status = feature_states[chat_id]
    status_text = (
        f"Feature Status:\n"
        f"• Spam Detection: {'ON' if status['spam'] else 'OFF'}\n"
        f"• Malicious Link Detection: {'ON' if status['links'] else 'OFF'}\n"
        f"• Fake News Detection: {'ON' if status['fake_news'] else 'OFF'}"
    )
    await update.message.reply_text(status_text)

async def start(update: Update, context: CallbackContext) -> None:
    global bot_active
    bot_active = True
    await update.message.reply_text(
        "Hello! I am a security bot that can detect:\n"
        "1. Spam content in messages\n"
        "2. Malicious links in messages\n"
        "3. Fake news content\n\n"
        "Just send me a message to analyze it automatically, or use /checkmessage to specifically analyze for fake news."
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Here's how to use this bot:\n\n"
        "• Send any message to check for spam, malicious links, and potentially fake news.\n"
        "• Use /checkmessage followed by text to specifically analyze news content.\n"
        "• You can also reply to a message with /checkmessage to analyze that message.\n"
        "• Use /toggle <feature> <on/off> to enable or disable specific features:\n"
        "  - Available features: spam, links, fake_news.\n"
        "  - Example: /toggle spam off\n"
        "• Use /status to check the current status of all features.\n"
        "• For best fake news detection, format your text with a title on the first line\n"
        "  and the content on subsequent lines."
    )

async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f"Update {update} caused error: {context.error}")
    if isinstance(context.error, (TimedOut, NetworkError)):
        await update.message.reply_text("Sorry, I encountered a network issue. Please try again later.")
    else:
        await update.message.reply_text("An unexpected error occurred. Please try again.")

def main():
    # Load all models first
    if not load_models():
        logger.error("Failed to load models. Exiting...")
        return
        
    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("checkmessage", analyze_news))
    app.add_handler(CommandHandler("toggle", toggle_feature))
    app.add_handler(CommandHandler("status", feature_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))
    app.add_error_handler(error_handler)
    
    logger.info("Bot is running with spam, malicious link, and fake news detection...")
    app.run_polling()

if __name__ == "__main__":
    main()