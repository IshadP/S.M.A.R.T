# import logging
# import joblib
# import re
# import urllib.parse
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
# from telegram.error import TimedOut, NetworkError

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# # Telegram Bot Token
# TOKEN = "8179425287:AAH32pr8qcwJuctSXx5GmJdtmeuJ4Zz3ggU"

# # Load spam detection models
# try:
#     message_model = joblib.load("Spam_model.pkl")
#     message_vectorizer = joblib.load("spam_count_vectorizer.pkl")
    
#     # Load the malicious link detection model and its vectorizer
#     link_model = joblib.load("model.pkl")
#     # Assuming you have a vectorizer for the link model; if it's a different name, update it
#     link_vectorizer = joblib.load("tfidf_vectorizer.pkl")
    
#     logger.info("All detection models loaded successfully.")
# except Exception as e:
#     logger.error(f"Error loading detection models: {e}")
#     raise

# # Function to clean text (Consistent with training)
# def clean_text(text):
#     text = text.lower().strip()  # Convert to lowercase
#     text = re.sub(r"\W+", " ", text)  # Remove special characters
#     text = re.sub(r"\d+", "", text)  # Remove numbers
#     return text.strip()

# # Function to extract URLs from text
# def extract_urls(text):
#     # URL regex pattern - matches common URL formats
#     url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[\w=&%+\.-]*)?(?:#[\w-]*)?'
#     return re.findall(url_pattern, text)

# # Function to preprocess URL for the link model
# def preprocess_url(url):
#     # This function should preprocess the URL in the same way as during training
#     # Since your model expects 590,757 features, it's likely using a text vectorizer
    
#     # Basic URL preprocessing (modify this according to your training process)
#     # For example, you might want to extract and process various parts of the URL
#     parsed_url = urllib.parse.urlparse(url)
    
#     # Create a text representation of the URL features
#     url_text = f"{parsed_url.scheme} {parsed_url.netloc} {parsed_url.path} {parsed_url.params} {parsed_url.query} {parsed_url.fragment}"
#     return url_text

# # Function to check if a link is malicious
# def is_malicious_link(url):
#     try:
#         # Preprocess the URL
#         processed_url = preprocess_url(url)
        
#         # Transform using the link vectorizer
#         url_features = link_vectorizer.transform([processed_url])
        
#         # Predict using the malicious link model
#         prediction = link_model.predict(url_features)[0]
        
#         return bool(prediction)  # Return True if malicious, False otherwise
#     except Exception as e:
#         logger.error(f"Error checking malicious link: {e}")
#         return False  # Default to safe in case of errors

# # Function to analyze messages for both spam and malicious links
# async def analyze_message(update: Update, context: CallbackContext) -> None:
#     message_text = update.message.text
    
#     # First check for malicious links in the message
#     try:
#         urls = extract_urls(message_text)
#         if urls:
#             malicious_links = []
#             for url in urls:
#                 if is_malicious_link(url):
#                     malicious_links.append(url)
            
#             if malicious_links:
#                 warning_text = f"⚠️ MALICIOUS LINK DETECTED: Found {len(malicious_links)} dangerous link(s) in your message"
#                 await update.message.reply_text(warning_text, 
#                                               reply_to_message_id=update.message.message_id)
#                 # Log the detected malicious links
#                 logger.warning(f"Detected malicious links: {malicious_links}")
#     except Exception as e:
#         logger.error(f"Error in malicious link detection: {e}")
    
#     # Then check for spam content separately
#     try:
#         user_message = clean_text(message_text)
#         transformed_text = message_vectorizer.transform([user_message])
#         spam_prediction = message_model.predict(transformed_text)[0]
        
#         if spam_prediction != 1:
#             await update.message.reply_text("🚨 Message Appears to be Spam", 
#                                           reply_to_message_id=update.message.message_id)
#     except Exception as e:
#         logger.error(f"Error in spam detection: {e}")

# # Start Command
# async def start(update: Update, context: CallbackContext) -> None:
#     await update.message.reply_text("Hello! I check messages for both spam content and malicious links.")

# # Error Handler
# async def error_handler(update: Update, context: CallbackContext) -> None:
#     logger.error(f"Update {update} caused error: {context.error}")
#     if isinstance(context.error, (TimedOut, NetworkError)):
#         await update.message.reply_text("Sorry, I encountered a network issue. Please try again later.")
#     else:
#         await update.message.reply_text("An unexpected error occurred. Please try again.")

# # Main Function
# def main():
#     app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))
#     app.add_error_handler(error_handler)
#     logger.info("Bot is running for spam and malicious link detection...")
#     app.run_polling()

# if __name__ == "__main__":
#     main()

import logging
import joblib
import re
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import TimedOut, NetworkError
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = os.getenv("BOT_TOKEN")

# Load all detection models
try:
    # Spam detection models
    message_model = joblib.load("Spam_model.pkl")
    message_vectorizer = joblib.load("spam_count_vectorizer.pkl")
    
    # Malicious link detection models
    link_model = joblib.load("model.pkl")
    link_vectorizer = joblib.load("tfidf_vectorizer.pkl")
    
    # Fake news detection models
    nb_model = joblib.load("naive_bayes_model.pkl")
    nb_title_model = joblib.load("naive_bayes_title_model.pkl")
    nb_text_model = joblib.load("naive_bayes_text_model.pkl")
    
    tfidf_vectorizer = joblib.load("tfidf_vectorizer (2).pkl")
    tfidf_title_vectorizer = joblib.load("tfidf_vectorizer_title.pkl")
    tfidf_text_vectorizer = joblib.load("tfidf_vectorizer_text.pkl")
    
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
    parsed_url = urllib.parse.urlparse(url)
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

# Function to detect fake news
def detect_fake_news(title="", content=""):
    try:
        results = []
        
        # If we have both title and content
        if title and content:
            # Process with combined model
            combined_text = f"{title} {content}"
            combined_features = tfidf_vectorizer.transform([combined_text])
            combined_prediction = nb_model.predict(combined_features)[0]
            combined_prob = nb_model.predict_proba(combined_features)[0]
            fake_prob = combined_prob[1] if combined_prediction == 1 else combined_prob[0]
            results.append(("Combined analysis", combined_prediction, fake_prob))
        
        # If we have a title
        if title:
            # Process with title model
            title_features = tfidf_title_vectorizer.transform([title])
            title_prediction = nb_title_model.predict(title_features)[0]
            title_prob = nb_title_model.predict_proba(title_features)[0]
            fake_prob_title = title_prob[1] if title_prediction == 1 else title_prob[0]
            results.append(("Title analysis", title_prediction, fake_prob_title))
        
        # If we have content
        if content:
            # Process with content model
            content_features = tfidf_text_vectorizer.transform([content])
            content_prediction = nb_text_model.predict(content_features)[0]
            content_prob = nb_text_model.predict_proba(content_features)[0]
            fake_prob_content = content_prob[1] if content_prediction == 1 else content_prob[0]
            results.append(("Content analysis", content_prediction, fake_prob_content))
        
        return results
    except Exception as e:
        logger.error(f"Error detecting fake news: {e}")
        return []

# Extract title and content from a message
def extract_news_components(text):
    # Simple approach: first line could be title, rest is content
    lines = text.strip().split('\n')
    
    if len(lines) > 1:
        title = lines[0]
        content = '\n'.join(lines[1:])
    else:
        title = ""
        content = text
    
    return title, content

# Function to analyze messages for spam, malicious links, and fake news
async def analyze_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    
    # Check for malicious links
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
                logger.warning(f"Detected malicious links: {malicious_links}")
    except Exception as e:
        logger.error(f"Error in malicious link detection: {e}")
    
    # Check for spam content
    try:
        user_message = clean_text(message_text)
        transformed_text = message_vectorizer.transform([user_message])
        spam_prediction = message_model.predict(transformed_text)[0]
        
        if spam_prediction != 1:
            await update.message.reply_text("🚨 Message Appears to be Spam", 
                                          reply_to_message_id=update.message.message_id)
    except Exception as e:
        logger.error(f"Error in spam detection: {e}")
    
    # Check for fake news
    try:
        # Extract potential title and content
        title, content = extract_news_components(message_text)
        
        # Only proceed if we have enough text to analyze
        if len(message_text) > 50:  # Arbitrary threshold for meaningful analysis
            fake_news_results = detect_fake_news(title, content)
            
            if fake_news_results:
                # Check if any model classified this as fake news
                is_fake = any(result[1] == 1 for result in fake_news_results)
                
                if is_fake:
                    # Prepare detailed results
                    details = []
                    for analysis_type, prediction, probability in fake_news_results:
                        status = "FAKE" if prediction == 1 else "REAL"
                        confidence = probability * 100
                        details.append(f"{analysis_type}: {status} (Confidence: {confidence:.1f}%)")
                    
                    result_text = "🔍 POTENTIAL FAKE NEWS DETECTED:\n" + "\n".join(details)
                    
                    await update.message.reply_text(result_text, 
                                                  reply_to_message_id=update.message.message_id)
    except Exception as e:
        logger.error(f"Error in fake news detection: {e}")

# Command to explicitly analyze a specific news article
async def analyze_news(update: Update, context: CallbackContext) -> None:
    # Get text from command arguments or from replied message
    if context.args:
        news_text = ' '.join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        news_text = update.message.reply_to_message.text
    else:
        await update.message.reply_text("Please provide news text after the /checknews command or reply to a message")
        return
    
    title, content = extract_news_components(news_text)
    
    fake_news_results = detect_fake_news(title, content)
    
    if fake_news_results:
        # Prepare detailed results
        details = []
        for analysis_type, prediction, probability in fake_news_results:
            status = "FAKE" if prediction == 1 else "REAL"
            confidence = probability * 100
            details.append(f"{analysis_type}: {status} (Confidence: {confidence:.1f}%)")
        
        result_text = "🔍 News Analysis Results:\n" + "\n".join(details)
    else:
        result_text = "Unable to analyze the provided news text"
    
    await update.message.reply_text(result_text)

# Start Command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Hello! I am a security bot that can detect:\n"
        "1. Spam content in messages\n"
        "2. Malicious links in messages\n"
        "3. Fake news content\n\n"
        "Just send me a message to analyze it automatically, or use /checknews to specifically analyze for fake news."
    )

# Help Command
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Here's how to use this bot:\n\n"
        "• Send any message to check for spam, malicious links, and potentially fake news\n"
        "• Use /checknews followed by text to specifically analyze news content\n"
        "• You can also reply to a message with /checknews to analyze that message\n"
        "• For best fake news detection, format your text with a title on the first line\n"
        "  and the content on subsequent lines"
    )

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
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("checknews", analyze_news))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))
    
    app.add_error_handler(error_handler)
    
    logger.info("Bot is running with spam, malicious link, and fake news detection...")
    app.run_polling()

if __name__ == "__main__":
    main()