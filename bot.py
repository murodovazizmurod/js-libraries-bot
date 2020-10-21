import requests
import ast
import telebot
from telebot import types


polular = ["Vue", "Angular", "React", "Polymer", "Aurelia", "Backbone.js", "Mithril"]

def ret_welcome(name, total):
    return f"""👋🏻 **Здравствуйте, {str(name)[:30]}!**
Мы рады вас видеть в нашем телеграмм боте.
Здесь вы можете увидеть больше информации о любую библиотеку в JavaScript

Точнее:
    \t**Всего библиотек:** `{total}`

Популярные [👇](https://allit.uz/static/imgs/js.jpg)"""


def ret_home(total):
    return f"""У нас:
    \t**Всего библиотек:** `{total}`

Популярные 👇"""

def popular():
    markup = types.InlineKeyboardMarkup()
    for i in range(len(polular)):
        markup.add(types.InlineKeyboardButton(polular[i], callback_data="['get','"+polular[i]+"']"))
    markup.row(types.InlineKeyboardButton("🔍 Найти", callback_data="['find']"), types.InlineKeyboardButton("👨‍💻 Автор", callback_data="['author']"))
    return markup
    

def naz():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏘", callback_data="['home']"))
    return markup

bot = telebot.TeleBot("")

main = "https://api.cdnjs.com/libraries/"

query = "https://api.cdnjs.com/libraries?search="

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(chat_id=message.chat.id, text=ret_welcome(message.from_user.first_name, requests.get(main).json()["total"]), parse_mode="Markdown", reply_markup=popular())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data.startswith("['get'"):
            lib = str(ast.literal_eval(call.data)[1])
            detail = requests.get(main+str(lib).lower()).json()
            try:
                tags = ''
                for i in list(detail["keywords"]):
                    tags = tags + ' ' + i
                bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f'<b>Name:</b> {detail["name"].title()}\n<b>Description:</b> <code>{detail["description"]}</code> \nRepository: <a href=\"{detail["repository"]["url"]}\">{detail["repository"]["url"]}</a>\n<b>Home Page: </b> {detail["homepage"]}\n<b>Author: </b>{detail["author"].replace("<", "").replace(">", "")}\n<b>Tags:</b><code>{tags}</code>\n<b>Latest Version: </b><code>{detail["versions"][-1]}</code>',
                                parse_mode="html",
                                reply_markup=naz())
            except:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🏘", callback_data="['home']"))
                markup.add(types.InlineKeyboardButton("🔄 Попробовать еще раз", callback_data="['find']"))
                bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f'<b>Простите но такое библиотека не найдено :(</b>',
                                parse_mode="HTML",
                                reply_markup=markup)
        elif call.data == "['home']":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id , text=ret_welcome(call.message.from_user.first_name, requests.get(main).json()["total"]), parse_mode="Markdown", reply_markup=popular())
        elif call.data == "['find']":
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id , text="""**🔍 Найти**

Напишите имя библиотеку которую вы хотите найти в нижнем регистре!

Например: `angular, vue, react ...`""", parse_mode="Markdown", reply_markup=naz())
            bot.register_next_step_handler(msg, find)
        elif call.data == "['author']":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id , text="Support @murodov_azizmurod", parse_mode="Markdown", reply_markup=naz())

    
def find(message):
    detail = requests.get(main+str(message.text).lower()).json()
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🏘", callback_data="['home']"))
        markup.add(types.InlineKeyboardButton("🔄 Попробовать еще раз", callback_data="['find']"))
        bot.reply_to(message, text=f'<b>Name:</b> {detail["name"].title() or "Not Found"}\n<b>Description:</b> <code>{detail["description"] or "Not Found"}</code> \nRepository: <a href=\"{detail["repository"]["url"] or "Not Found"}\">{detail["repository"]["url"] or "Not Found"}</a>\n<b>Home Page: </b> {detail["homepage"] or "Not Found"}\n<b>Author: </b>{detail["author"].replace("<", "").replace(">", "") or "Not Found"}\n<b>Latest Version: </b><code>{detail["versions"][-1] or "Not Found"}</code>', reply_markup=markup, parse_mode="html")
    except:
        bot.reply_to(message,
                        text=f'<b>Простите но такое библиотека не найдено :(</b>',
                        parse_mode="HTML",
                        reply_markup=naz())


if __name__ == "__main__":
    bot.polling(none_stop=True)
