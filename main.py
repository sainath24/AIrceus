from BatteSimulator import BattleSimulator
from Ingestor import Ingestor
from Game import Game
from Translator import Translator
from Brain import Brain

from multiprocessing import Queue
from config import config

from tqdm import tqdm

import wandb
if config['use_wandb']:
    wandb.init(project = 'AIrceus_V2.0')

import logging
logging.basicConfig(filename = config['log'], level=logging.DEBUG)

data_queue = None
action_queue = None

if __name__ == "__main__":

    batsim = BattleSimulator(data_queue=data_queue, action_queue= action_queue)
    # brain = Brain(train=True)
    translator = Translator(action_queue=action_queue)
    game = Game()
    ingestor = Ingestor(data_queue=data_queue, translator=translator, train=True, game=game)

    for episode in tqdm(range(config['episodes']), desc='EPISODE'):
        # print('\nEPISODE: ', episode, '\n')
        logging.log(logging.INFO, 'EPISODE ' + str(episode + 1))
        data_queue = Queue()
        action_queue = Queue()
        batsim.set_queues(data_queue, action_queue)
        ingestor.set_queue(data_queue)
        translator.set_queue(action_queue)

        game.reset()

        batsim.start(threaded=True)
        ingestor.start(threaded=False) # WILL NOT PASS HERE UNTIL INGESTOR ENDS
        # batsim.kill()
        if config['use_wandb']:
            wandb.log({'episode': episode})

