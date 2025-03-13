import logging
import joblib
import re
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import TimedOut, NetworkError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = "8179425287:AAH32pr8qcwJuctSXx5GmJdtmeuJ4Zz3ggU"

# Load spam detection models
try:
    message_model = joblib.load(".pkl")
    message_vectorizer = joblib.load("spam_count_vectorizer.pkl")
    
    # Load the malicious link detection model and its vectorizer
    link_model = joblib.load("model.pkl")
    # Assuming you have a vectorizer for the link model; if it's a different name, update it
    link_vectorizer = joblib.load("tfidf_vectorizer.pkl")
    
    logger.info("All detection models loaded successfully.")
except Exception as e:
    logger.error(f"Error loading detection models: {e}")
    raise

# Function to clean text (Consistent with training)
def clean_text(text):
    text = text.lower().strip()  # Convert to lowercase
    text = re.sub(r"\W+", " ", text)  # Remove special characters
    text = re.sub(r"\d+", "", text)  # Remove numbers
    return text.strip()

# Function to extract URLs from text
def extract_urls(text):
    # URL regex pattern - matches common URL formats
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[\w=&%+\.-]*)?(?:#[\w-]*)?'
    return re.findall(url_pattern, text)

# Function to preprocess URL for the link model
def preprocess_url(url):
    # This function should preprocess the URL in the same way as during training
    # Since your model expects 590,757 features, it's likely using a text vectorizer
    
    # Basic URL preprocessing (modify this according to your training process)
    # For example, you might want to extract and process various parts of the URL
    parsed_url = urllib.parse.urlparse(url)
    
    # Create a text representation of the URL features
    url_text = f"{parsed_url.scheme} {parsed_url.netloc} {parsed_url.path} {parsed_url.params} {parsed_url.query} {parsed_url.fragment}"
    return url_text

# Function to check if a link is malicious
def is_malicious_link(url):
    try:
        # Preprocess the URL
        processed_url = preprocess_url(url)
        
        # Transform using the link vectorizer
        url_features = link_vectorizer.transform([processed_url])
        
        # Predict using the malicious link model
        prediction = link_model.predict(url_features)[0]
        
        return bool(prediction)  # Return True if malicious, False otherwise
    except Exception as e:
        logger.error(f"Error checking malicious link: {e}")
        return False  # Default to safe in case of errors

# Function to analyze messages for both spam and malicious links
async def analyze_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    
    # First check for malicious links in the message
    try:
        urls = extract_urls(message_text)
        if urls:
            malicious_links = []
            for url in urls:
                if is_malicious_link(url):
                    malicious_links.append(url)
            
            if malicious_links:
                warning_text = f"⚠️ MALICIOUS LINK DETECTED: Found {len(malicious_links)} dangerous link(s) in your message"
                await update.message.reply_text(warning_text, 
                                              reply_to_message_id=update.message.message_id)
                # Log the detected malicious links
                logger.warning(f"Detected malicious links: {malicious_links}")
    except Exception as e:
        logger.error(f"Error in malicious link detection: {e}")
    
    # Then check for spam content separately
    try:
        user_message = clean_text(message_text)
        transformed_text = message_vectorizer.transform([user_message])
        spam_prediction = message_model.predict(transformed_text)[0]
        
        if spam_prediction != 1:
            await update.message.reply_text("🚨 Message Appears to be Spam", 
                                          reply_to_message_id=update.message.message_id)
    except Exception as e:
        logger.error(f"Error in spam detection: {e}")

# Start Command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I check messages for both spam content and malicious links.")

# Error Handler
async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f"Update {update} caused error: {context.error}")
    if isinstance(context.error, (TimedOut, NetworkError)):
        await update.message.reply_text("Sorry, I encountered a network issue. Please try again later.")
    else:
        await update.message.reply_text("An unexpected error occurred. Please try again.")

# Main Function
def main():
    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))
    app.add_error_handler(error_handler)
    logger.info("Bot is running for spam and malicious link detection...")
    app.run_polling()

if __name__ == "__main__":
    main()