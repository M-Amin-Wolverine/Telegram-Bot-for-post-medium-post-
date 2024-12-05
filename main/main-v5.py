import os
import telebot
import logging
import threading
import time
from datetime import datetime, timedelta
from functools import lru_cache
import requests
from bs4 import BeautifulSoup
from config import TOKEN, CHANNEL_ID, MEDIUM_URL, CHAT_ID
import redis
import xml.etree.ElementTree as ET
import aiohttp

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='log.txt',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Caching function
@lru_cache(maxsize=5000)
def find_posts(posts):
    for post in posts:
        title = post['title']
        link = post['link']
        logging.info(f"Found post: {title:<10} - {link}")

def get_medium_posts():
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)

        # Send GET request to Medium
        response = requests.get(MEDIUM_URL, headers=HEADERS)
        response.raise_for_status()

        # Parse the response content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = []

        # Extract post titles and links
        for article in soup.find_all('article'):
            title = article.find('h2').text.strip() if article.find('h2') else 'No Title'
            link = 'https://medium.com' + article.find('a')['href']
            posts.append((title, link))
            logger.info(f"Found post: {title:<10} - {link}")

        logger.info(f"Successfully fetched {len(posts)} posts from Medium.")

        # Save posts to Redis and a file
        with open('medium_posts2.txt', 'w', encoding='utf-8') as file:
            for i, post in enumerate(posts, 1):
                title, link = post
                r.set(f'post_{i}_title', title)
                r.set(f'post_{i}_link', link)
                file.write(f'{i}. {title:<15} {link}')

        return posts
    except requests.HTTPError as e:
        logger.error(f"Error fetching Medium posts: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing Medium posts: {e}")
        return []

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Authorization': '22f4e88de61639aeff19833c9ac7a71bde546b46fe7e89d273096d25efd3e38d3'
}

# Threaded message sending function
def send_posts(chat_id):
    posts = get_medium_posts()
    for title, link in posts:
        try:
            bot.send_message(chat_id=chat_id, text=f"{title:<10}{link}")
            logger.info(f"Successfully sent post: {title}")
        except Exception as e:
            logger.error(f"Error sending post: {title} - {e}")

# Scheduled post sending function
def scheduled_post_sending():
    while True:
        logger.info("Fetching and sending new Medium posts...")
        send_posts(CHANNEL_ID)
        logger.info("Posts sent. Sleeping for 1 hour.")
        time.sleep(3600)  # Sleep for 1 hour

# User subscription management
subscribed_users = set()

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Welcome! How can I help you today?")

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    user_id = message.chat.id
    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        bot.send_message(chat_id=user_id, text="عضویت شما موفقیت آمیز بود!")
        logger.info(f"User {user_id} subscribed to the channel.")
    else:
        bot.send_message(chat_id=user_id, text="You are already subscribed to the channel.")
        logger.info(f"User {user_id} is already subscribed to the channel.")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    user_id = message.chat.id
    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        bot.send_message(chat_id=user_id, text="ای بابا از پیشمون رفتی که !! عیبی نداره برمیگردی بابا")
        logger.info(f"User {user_id} unsubscribed from the channel.")
    else:
        bot.send_message(chat_id=user_id, text="اول برادریت رو نشون بده بعد ادعاارثت بشه !!")
        logger.info(f"User {user_id} is not subscribed to the channel.")

@bot.message_handler(commands=['help'])
def help(message):
    help_message = """Available commands:
                    /start - شروع
                    /subscribe - عضویت
                    /unsubscribe - خارج شدن از عضویت"""
    bot.send_message(chat_id=message.chat.id, text=help_message)
@bot.message_handler(commands=['new_post'])
def post_new(message):
    user_id = message.chat.id
    if user_id in subscribed_users:
        try:
            # Fetch the latest posts from Medium
            posts = get_medium_posts()
            x=0
            # Check if there are any new posts
            if posts:
                
                    title, link = posts[0]
                    bot.send_message(chat_id=CHAT_ID, text=f"{title}{link}")
                    logger.info(f"New post published: {title}")
                    bot.send_message(chat_id=user_id, text="New post published!")
                    
            else:
                bot.send_message(chat_id=user_id, text="No new posts found.")
        except Exception as e:
            logger.error(f"Error posting new post: {e}")
            bot.send_message(chat_id=user_id, text="An error occurred while posting the new post.")
    else:
        bot.send_message(chat_id=user_id, text="You are not subscribed to the channel.")

def send_scheduled_posts():
    # Here, you should add the logic to send the scheduled posts
    # This could involve checking a database or other data source
    # for scheduled posts, and then sending them using your bot
    print("Sending scheduled posts...")

# Replace with the chat ID of the channel you want to forward to
CHAT_ID2 = CHAT_ID

# Create a Telebot instance

# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(chat_id=CHAT_ID2, text="This is a test message from the bot.")

@bot.message_handler(content_types=['text'])
def send_testing_post(message):
     # Forward the message to the specified channel
     try:
         response_text = f"Thank you for your message! I have received it and will respond shortly."
         bot.send_message(chat_id=CHAT_ID2, text=response_text)
     except telebot.apihelper.ApiTelegramException as e:
         print(f"Error forwarding message: {e}")

# def main():
#     # Start the scheduled post sending in a separate thread
#     threading.Thread(target=send_scheduled_posts).start()

#     # Start the bot
#     bot.polling()

# if __name__ == '__main__':
#     main()
# @bot.message_handler(content_types=['text'])
# def respond_to_message(message):
#     # Craft a response to the message
#     try:


def main():
    # Start the scheduled post():
    # Start the scheduled post sending in a separate thread
    threading.Thread(target=send_scheduled_posts).start()
    while True:
        posts = get_medium_posts()
        if posts:
            for i in range(10):
                if i < len(posts):
                    title, link = posts[i]
                    send_posts(title, link)
                else:
                    break
                time.sleep(40)  # Wait 1 minute before sending the next 10 posts
                time.sleep(10)  # Wait 20 seconds for a rest period
        else:
            logger.info("No new posts found. Waiting 1 minute before checking again.")
            time.sleep(30) 
        bot.polling()

if __name__ == '__main__':
    main()
