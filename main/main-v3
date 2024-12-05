import requests
import telebot
import logging
import threading
import time
from datetime import datetime
from functools import lru_cache
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import telegram.ext.filters as filters
from bs4 import BeautifulSoup
from config import TOKEN, CHANNEL_ID, MEDIUM_URL
import queue

bot=telebot.TeleBot(TOKEN)
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "سلام خوش اومدی")


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

        logger.info(f"Successfully fetched {len(posts)} posts from Medium.")
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
        try:
            context.bot.send_message(chat_id=CHANNEL_ID, text=f"{title}{link}")
            logger.info(f"Successfully sent post: {title}")
        except Exception as e:
            logger.error(f"Error sending post: {title} - {e}")

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
        logger.info(f"User {user_id} subscribed to the channel.")
    else:
        context.bot.send_message(chat_id=user_id, text="You are already subscribed to the channel.")
        logger.info(f"User {user_id} is already subscribed to the channel.")

def unsubscribe(update, context):
    user_id = update.effective_chat.id
    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        context.bot.send_message(chat_id=user_id, text="You have been unsubscribed from the channel.")
        logger.info(f"User {user_id} unsubscribed from the channel.")
    else:
        context.bot.send_message(chat_id=user_id, text="You are not subscribed to the channel.")
        logger.info(f"User {user_id} is not subscribed to the channel.")

# Command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the Medium post channel bot!")
    logger.info(f"User {update.effective_chat.id} started the bot.")

def help(update, context):
    help_message = """ Available commands:
                        /start - Start the bot
                        /subscribe - Subscribe to the Medium post channel
                        /unsubscribe - Unsubscribe from the Medium post channel    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)

def test_message(update, context):
    # Test message content
    message_text = "This is a test message from the bot."

    # Send the test message to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)

    # Log the test message
    logger.info(f"Sent test message to user {update.effective_chat.id}: {message_text}")

def main():
    q = queue.Queue()

# Add items to the queue
    q.put(1)
    q.put(2)
    q.put(3)

# Get items from the queue
    print(q.get())  # Output: 1
    print(q.get())  # Output: 2
    print(q.get())  # Output: 3
    updater = Updater(TOKEN)
    
    update_queue = queue.Queue()

    # Create the updater with the update queue
    updater = Updater(TOKEN, update_queue=update_queue)

    # Get the dispatcher from the updater
    dispatcher = updater.dispatcher

    # Add the test message command handler
    test_message_handler = CommandHandler('test', test_message)
    dispatcher.add_handler(test_message_handler)

    # Add other command handlers and start the bot
    # ...

    updater.start_polling()
    updater.idle()
bot.polling()    
