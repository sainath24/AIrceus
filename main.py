from BatteSimulator import BattleSimulator
from Ingestor import Ingestor
from Game import Game
from Translator import Translator
from Brain import Brain

from multiprocessing import Queue

data_queue = Queue()
action_queue = Queue()

batsim = BattleSimulator(data_queue=data_queue, action_queue= action_queue)
brain = Brain(train=True)
translator = Translator(action_queue=action_queue)
game = Game()
ingestor = Ingestor(data_queue=data_queue, translator=translator, brain=brain, game=game)

batsim.start(threaded=True)
ingestor.start(threaded=True)

