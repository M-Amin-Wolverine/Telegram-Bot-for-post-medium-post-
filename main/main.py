import requests
import logging
import threading
import time
from datetime import datetime
from functools import lru_cache
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import telegram.ext.filters as filters
from bs4 import BeautifulSoup
from config import TOKEN, CHANNEL_ID, MEDIUM_URL

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Caching function
@lru_cache(maxsize=1000)
def get_medium_posts():
    try:
        response = requests.get(MEDIUM_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        posts = []
        for article in soup.find_all('article'):
            title = article.find('h2').text.strip()
            link = 'https://medium.com' + article.find('a')['href']
            posts.append((title, link))

        return posts
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Medium posts: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing Medium posts: {e}")
        return []

# Threaded message sending function
def send_posts(update, context):
    posts = get_medium_posts()
    for title, link in posts:
        context.bot.send_message(chat_id=CHANNEL_ID, text=f"{title}{link}")

# Scheduled post sending function
def scheduled_post_sending():
    while True:
        logger.info("Fetching and sending new Medium posts...")
        send_posts(None, None)
        logger.info("Posts sent. Sleeping for 1 hour.")
        time.sleep(3600)  # Sleep for 1 hour

# User subscription management
subscribed_users = set()

def subscribe(update, context):
    user_id = update.effective_chat.id
    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        context.bot.send_message(chat_id=user_id, text="You have been subscribed to the channel.")
    else:
        context.bot.send_message(chat_id=user_id, text="You are already subscribed to the channel.")

def unsubscribe(update, context):
    user_id = update.effective_chat.id
    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        context.bot.send_message(chat_id=user_id, text="You have been unsubscribed from the channel.")
    else:
        context.bot.send_message(chat_id=user_id, text="You are not subscribed to the channel.")

# Command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the Medium post channel bot!")

def help(update, context):
    help_text = (
        "Available commands:"  
        
        # Added 
        "/subscribe - Subscribe to the channel"
        "/unsubscribe - Unsubscribe from the channel" 
        # Removed extra "
        "/sendposts - Manually send the latest Medium posts"
        "/feedback - Send feedback or report issues"
    )

    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

def feedback(update, context):
    context.bot.send_message(chat_id=CHANNEL_ID, text=f"Feedback from {update.effective_chat.username}:\n{update.message.text}")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for your feedback!")

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.ad
