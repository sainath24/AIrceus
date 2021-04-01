from BatteSimulator import BattleSimulator
from Ingestor import Ingestor
from Game import Game
from Translator import Translator
from Brain import Brain

from multiprocessing import Queue
from config import config

data_queue = None
action_queue = None

batsim = BattleSimulator(data_queue=data_queue, action_queue= action_queue)
brain = Brain(train=True)
translator = Translator(action_queue=action_queue)
game = Game()
ingestor = Ingestor(data_queue=data_queue, translator=translator, brain=brain, game=game)

for episode in range(config['episodes']):
    print('\nEPISODE: ', episode, '\n')
    data_queue = Queue()
    action_queue = Queue()
    batsim.set_queues(data_queue, action_queue)
    ingestor.set_queue(data_queue)
    translator.set_queue(action_queue)

    game.reset()

    batsim.start(threaded=True)
    ingestor.start(threaded=True) # WILL NOT PASS HERE UNTIL INGESTOR ENDS

