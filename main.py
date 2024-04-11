import telebot
from telebot import types
import subprocess
import os


TOKEN = ''
bot = telebot.TeleBot(TOKEN)


def generate_images(user_info):
    full_path = f'../../Images/{user_info["id"]}'  # insert your path
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    prompt = f'This book title is {user_info["title"]} .\n' \
             f'This book Genres is {user_info["genres"].lower()} .\n' \
             f'{user_info["annotation"].lower()}'

    command = [
        "python",
        "main.py",
        "--cfg",
        "cfg/eval_books.yml",
        "--gpu",
        "1",
        "--input_text",
        prompt,
        "--output_dir",
        full_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        itembtn = types.KeyboardButton('Create book cover')
        markup.add(itembtn)
        bot.send_message(user_info["id"], f"Book cover generated successfully!", reply_markup=markup)
        with open(full_path + '/0_s_0_g2.png', 'rb') as photo:
            bot.send_photo(user_info["id"], photo)
    else:
        error = result.stderr.decode("utf-8")
        print("Ошибка выполнения команды: {error}")
        bot.send_message(user_info["id"], f"Ooops... something went wrong: {error}")


@bot.message_handler(func=lambda message: message.text == 'Create book cover')
def start_message(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Send a message with book title', reply_markup=markup)
    user_info = {'id': message.chat.id}
    bot.register_next_step_handler(message, get_title, user_info)


def get_title(message, user_info):
    user_info['title'] = message.text
    bot.send_message(message.chat.id, 'Send a message with genres separated with commas\n'
                                      'Example:  '
                                      'mystery, fantasy, thriller')
    bot.register_next_step_handler(message, get_genres, user_info)


def get_genres(message, user_info):
    user_info['genres'] = message.text
    bot.send_message(message.chat.id, 'Send a message with annotation')
    bot.register_next_step_handler(message, get_annotation, user_info)


def get_annotation(message, user_info):
    user_info['annotation'] = message.text
    bot.send_message(message.chat.id, 'We are starting generation... The process may take a long time!')
    generate_images(user_info)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    itembtn = types.KeyboardButton('Create book cover')
    markup.add(itembtn)
    bot.send_message(message.chat.id, "Hello!\n "
                                      "This bot is made for book covers creations\n"
                                      "Press the button to start generation", reply_markup=markup)


bot.polling()
