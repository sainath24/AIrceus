import threading
import subprocess

class BattleSimulator:
    def __init__(self, data_queue, action_queue, formatid = 'gen4randombattle', p1 = 'agent', p2 = 'trainer') -> None:
        self.data_q = data_queue
        self.action_q = action_queue
        self.formatid = formatid
        self.p1 = p1
        self.p2 = p2
        self.proc = None

    def set_queues(self, data_queue, action_queue):
        self.data_q = data_queue
        self.action_q = action_queue

    def get_action(self):
        while True:
            if not self.action_q.empty():
                action = self.action_q.get()
                if action == 'game_over':
                    break
                self.proc.stdin.write(action)
                self.proc.stdin.flush()

    def write_data_q(self):
        for line in iter(self.proc.stdout.readline, ""):
            self.data_q.put(line)

    def start(self,threaded = True):
        if threaded:
            battlesim = threading.Thread(target = self.run, args = ())
            battlesim.start()
        else:
            self.run()


    def run(self):
        self.proc = subprocess.Popen(['node', 'pokemon-showdown/pokemon-showdown', 'simulate-battle'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

        output_thread = threading.Thread(target=self.write_data_q)
        output_thread.setDaemon(True)
        output_thread.start()

        get_action_thread = threading.Thread(target=self.get_action)
        get_action_thread.setDaemon(True)
        get_action_thread.start()

        start = '>start {"formatid":"' + self.formatid + '"}\n'
        player1 = '>player p1 {"name":"' + self.p1 + '"}\n'
        player2 = '>player p2 {"name":"' + self.p2 + '"}\n'

        self.proc.stdin.write(start)
        self.proc.stdin.flush()
        self.proc.stdin.write(player1)
        self.proc.stdin.flush()
        self.proc.stdin.write(player2)
        self.proc.stdin.flush()

        get_action_thread.join()

    def kill(self):
        self.proc.kill()





        
