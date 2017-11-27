# -*- coding: utf-8 -*-
import telebot
import config
import bpnz
from apscheduler.schedulers.background import BackgroundScheduler

#bot object
bot = telebot.TeleBot(config.token) 

#Cron object
scheduler = BackgroundScheduler()
scheduler.start()

#start
@bot.message_handler(commands=["start"])
def handle_text(message):
    scheduler.add_job(lambda: bpnz.parser(message, bot, config.url_index), 'cron', minute='*/15', id=str(message.from_user.id), replace_existing=True)
#stop
@bot.message_handler(commands=["stop"])
def handle_text(message):
   scheduler.remove_job(str(message.from_user.id))

#send message
@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.from_user.id, message.text)

#main
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)


