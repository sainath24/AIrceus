import threading

class Ingestor:
    def __init__(self, data_queue, translator, brain, game) -> None:
        self.data_q = data_queue
        self.translator = translator
        self.brain = brain
        self.game = game

    def start(self,threaded = True):
        if threaded:
            ingestor_thread = threading.Thread(target=self.run)
            ingestor_thread.start()
        else:
            self.run()
            
    def run(self):
        while True:
            if not self.data_q.empty():
                line = self.data_q.get()
                print(line)

