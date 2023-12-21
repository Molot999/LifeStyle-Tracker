from telebot.types import Message
from config import bot

def delete_message_keyboard(message:Message):
    bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=None)