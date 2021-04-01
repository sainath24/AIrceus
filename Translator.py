class Translator:
    def __init__(self, action_queue) -> None:
        self.action_q = action_queue

    def translate(self, input):
        pass

    def write_action_queue(self,action):
        self.action_q.put(action)

    def set_queue(self, action_queue):
        self.action_q = action_queue