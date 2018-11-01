FINAL_ANSWER = "Ваше обращение зарегистрировано, удачного дня\n"

class Node:
    def __init__(self, text):
        self.children = {}


class UserNode(Node):
    def __init__(self, text):
        super(UserNode, self).__init__(text)
        self.text_to_fit = text

    def add(self, text):
        node = BotNode(text)
        self.children.update({text: node})
        return node

    def match(self, text):
        return text == self.text_to_fit


class BotNode(Node):
    def __init__(self, text):
        super(BotNode, self).__init__(text)
        self.question = text
    def add(self, text):
        node = UserNode(text)
        self.children.update({text:node})
        return node

class DialogTree:
    def __init__(self, text):
        self.root = UserNode(text)

    def run(self):
        node = self.root
        while node.children:
            if isinstance(node, UserNode):
                node = list(node.children.values())[0]
                yield node.question
            elif isinstance(node, BotNode):
                text = yield
                match = False
                for tmp in node.children.values():
                    if tmp.match(text):
                        match = True
                        node = tmp
                        break
                if not match:
                    yield FINAL_ANSWER
        yield FINAL_ANSWER



dt = DialogTree("сбер не оч")
fq = dt.root.add("вы уверены?")
fu = fq.add("да")
fq.add("нет")
sec_q = fu.add("точно?")
sec_q.add("нет")
sec_u = sec_q.add("да")
thrd_bot = sec_u.add("точно-преточно?")
thrd_bot.add("да")
thrd_bot.add("нет")



class ResponseModel:
    def __init__(self):
        self.possible_answers = {"сбер плохо себя вел": dt}
        self.answer_map = {}

    def answer(self, text, chat_id):
        scen = self.answer_map.get(chat_id)
        if not scen:
            tree = self.possible_answers.get(text)
            if not tree:
                return FINAL_ANSWER
            else:
                scen = dt.run()
                self.answer_map.update({chat_id: scen})
                return next(scen)
        else:
            next(scen)
            return scen.send(text)




if __name__=="__main__":
    rm = ResponseModel()
    print(rm.answer("сбер плохо себя вел", 1))
    print(rm.answer("да", 1))
    print(rm.answer("да", 1))
    print(rm.answer("нет", 1))



