import sys

import json
import logging
import threading
import uuid
from queue import Queue
from threading import Thread
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, Filters, Dispatcher, CallbackQueryHandler, Updater
from telegram.ext import CommandHandler

from chat_manager.chat_manager import ChatManager
from kafka_config import kafka_config
from mq.from_ai_message import from_ai_message
from mq.kafka.kafka_consumer import KafkaConsumer
from mq.kafka.kafka_publisher import KafkaPublisher
from mq.to_ai_message import to_ai_message
from response_model.response_model import ResponseModel, FINAL_ANSWER

async_mode = "gevent"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
thread = None
thread_lock = Lock()
socketio = SocketIO(app, async_mode=async_mode)
TOKEN = "628583227:AAEy67lVCc9iIBK-7aJgZ0XiwrKyW0E7_J4"
rm = ResponseModel()
bot = Bot(TOKEN)
update_queue = Queue()
dispatcher = Dispatcher(bot, update_queue)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

rm = ResponseModel()
update_queue = Queue()

logger = logging.getLogger("logger")
handlerFile = logging.FileHandler("compliance.log")
handlerConsole = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
logger.addHandler(handlerFile)
logger.addHandler(handlerConsole)


consumer = KafkaConsumer(kafka_config, logger)
publisher = KafkaPublisher(kafka_config, logger)


def _filter_user_messages(messages):
    user_messages = []

    for message in messages:
        if message["message_name"] == "ANSWER_TO_USER":
            user_messages.append(message)
    return user_messages


def receive_from_bot(from_bot_message):
    chatid = from_bot_message["uuid"]["chatId"]
    room = manager.chat_room(chatid)

    messages = from_bot_message["messages"]
    user_messages = _filter_user_messages(messages)

    user_messages_str = json.dumps(user_messages)
    all_messages_str = json.dumps(from_bot_message)

    manager.store_message_from_bot(all_messages_str, chatid)
    bot.send_message(chat_id=chatid, text=user_messages_str)
    socketio.emit('my_response', {'data': f'{from_bot_message}', 'count': 0},
                  namespace="/test",
                  room=str(room))

    #if ans == FINAL_ANSWER:
    #    manager.close_bot_session(chatid)


class KafkaListener:
    def poll(self):
        while 1:
            msg = consumer.poll()
            if msg:
                value = msg.value()
                if value:
                    sys.stderr.write("Received from AI: {}.".format(value))
                    from_bot_message = from_ai_message(value)
                    receive_from_bot(from_bot_message)


#  run kafka polling in another thread


listener = KafkaListener()
tr = threading.Thread(target=listener.poll)
tr.setDaemon(True)
tr.start()


def make_to_message(text, chatid):
    return to_ai_message(messageId=uuid.uuid1(), userId=chatid, chatId=chatid, message=text)


def patch_msg_data(data):
    return data.encode("ISO-8859-1").decode()


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=f"Бобро поржаловать")
    keyboard = [[InlineKeyboardButton("Жалоба", callback_data='сбер плохо себя вел'),
                 InlineKeyboardButton("Другое", callback_data='другое')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    manager.start_user_chat(update.message.chat_id)
    socketio.emit('my_response',
                  {'data': 'Server generated VERY SPECIAL event', 'count': 0},
                  namespace='/test')
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    bot.send_message(chat_id=query.message.chat_id, text=query.data)
    process_text(query.message.chat_id, query.data, bot)
    bot.send_message(chat_id=query.mesage.chat_id, text=query.data)


def process_text(chat_id, text, bot):
    room = manager.chat_room(chat_id)
    bot.send_message(chat_id=chat_id, text='чет пришло')
    socketio.emit('broad_response', {'chat_id': chat_id, 'room_id': room},
                  namespace="/test",
                  broadcast=True)
    socketio.emit('my_response', {'data': f'{text}', 'count': 0},
                  namespace="/test",
                  room=str(room))
    if manager.is_bot_session(chat_id):
        manager.store_message_to_bot(text, chat_id)
        message_to_bot_str = json.dumps(make_to_message(text, chat_id))
        logger.info("Try to send to AI: {}.".format(message_to_bot_str))
        publisher.send(json.dumps(message_to_bot_str), chat_id, "compliance")
        bot.send_message(chat_id=chat_id, text='записали в кафку')


def userinput(bot, update):
    chatid = update.message.chat_id
    manager.start_user_chat(chatid)
    process_text(chatid, update.message.text, bot)


start_handler = CommandHandler('start', start)
user_handler = MessageHandler(None, userinput)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(user_handler)
dispatcher.add_handler(CallbackQueryHandler(button))
thread_bot = Thread(target=dispatcher.start, name='dispatcher')
thread_bot.start()




manager = ChatManager()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/admin')
def webhook():
    bot.set_webhook("https://cryptic-savannah-15984.herokuapp.com/" + TOKEN)
    return "WebHOOK connected"


@app.route('/'+TOKEN, methods=['POST', 'GET'])
def foo():
    logger.info("webhook callback")
    update = Update.de_json(json.loads(request.data), bot)
    update_queue.put(update)
    return "OK"


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': patch_msg_data(message['data'])})


@socketio.on('join', namespace='/test')
def join(message):
    room = int(message['room'])
    if manager.operator_join_room(room, request.sid):
        chatid = manager.chat_id(room)
        history = manager.dump_history(chatid)
        join_room(message['room'])
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms())})
        if history:
            emit('my_response',
                 {'data': history})
    else:
        emit('my_response',
             {'data': 'Cannot join non-existent room'})


@socketio.on('leave', namespace='/test')
def leave(message):
    room = int(message['room'])
    if manager.operator_leave_room(room, request.sid):
        leave_room(message['room'])
        emit('my_response',
            {'data': 'In rooms: ' + ', '.join(rooms())})
    else:
        emit('my_response',
             {'data': 'Cannot delete operator from this room'})


@socketio.on('close_room', namespace='/test')
def close(message):
    #TODO - no bot logic here
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.'},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    room = int(message['room'])
    emit('my_response',
         {'data': patch_msg_data(message['data'])},
         room=message['room'])
    chatid = manager.chat_id(room)
    bot.send_message(chat_id=chatid, text=patch_msg_data(message['data']))
    manager.close_bot_session(chatid)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    manager.operator_chats.append(request.sid)
    emit('my_response', {'data': 'Connected', 'count': 0})
    for it in manager.chat_id_to_room_links:
        emit('broad_response_connect', {'chat_id': it["chat_id"], 'room_id': it['room_id']})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    logger.info('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8443, debug=True)

