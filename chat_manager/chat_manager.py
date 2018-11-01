
class ChatManager:
    def __init__(self):
        self.chats = 0
        self.operator_chats = []
        self.user_chats = {}
        self.rooms = {}
        self.room_identifiers = 0


    def is_user_chat_started(self, chat_id):
        return chat_id in self.user_chats

    def is_operator_listening(self, chat_id):
        return self.user_chats[chat_id]["operators"]

    def store_message(self, msg, chat_id, bot= False):
        if self.user_chats[chat_id]["store_history"]:
            if bot:
                prefix = "Ответ бота: "
            else:
                prefix = "Юзер пишет: "
            self.user_chats[chat_id]["history"].append(prefix + msg)

    def start_user_chat(self, chat_id):
        if not chat_id in self.user_chats:
            self.room_identifiers += 1
            # do we need to drop history storage then?
            self.user_chats.update({chat_id: {"store_history": True, "chat_room": self.room_identifiers, "bot": True, "history":[], "operators":[]}})
            self.rooms.update({self.room_identifiers: {"chat_id": chat_id, "operators": []}})

    def is_user_chat_closed(self, chat_id):
        return not self.user_chats[chat_id]["available"]

    def close_user_chat(self, chat_id):
        self.user_chats[chat_id]["available"] = False

    def get_history(self, chat_id):
        return "\n".join(self.user_chats[chat_id]["history"])

    def dump_history(self, chat_id):
        history = ""
        if self.user_chats[chat_id]["store_history"]:
            history = self.get_history(chat_id)
        return history

    def chat_room(self, chat_id):
        return self.user_chats[chat_id]["chat_room"]

    def chat_id(self, chat_room):
        return self.rooms[chat_room]["chat_id"]

    def close_bot_session(self, chat_id):
        self.user_chats[chat_id]["bot"] = False

    def is_bot_session(self, chat_id):
        return self.user_chats[chat_id]["bot"]

    def operator_join_room(self, room, op_id):
        if room in self.rooms:
            self.rooms[room]["operators"].append(op_id)
            chat_id = self.rooms[room]["chat_id"]
            self.user_chats[chat_id]["operators"].append(op_id)
            return True
        return False

    def operator_leave_room(self, room, op_id):
        if room in self.rooms and op_id in self.rooms[room]['operators']:
            self.rooms[room]['operators'].remove(op_id)
            chat_id = self.rooms[room]["chat_id"]
            self.user_chats[chat_id]["operators"].remove(op_id)
            return True
        return False

    @property
    def chat_id_to_room_links(self):
        res = []
        for k, v in self.user_chats.items():
            res.append({"chat_id":k, "room_id": v["chat_room"]})
        return res
