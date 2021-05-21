import threading
from CentralUpdater import CentralUpdater
from BatteSimulator import BattleSimulator
from Ingestor import Ingestor
from Game import Game
from Translator import Translator
from Brain import Brain

from multiprocessing import Queue
import multiprocessing
from config import config

from tqdm import tqdm
import time
from copy import deepcopy

import wandb
# import os
# os.environ["WANDB_RUN_GROUP"] = "experiment-" + wandb.util.generate_id()
# if config['use_wandb']:
#     wandb.init(project = 'AIrceus_V2.0')

import logging
logging.basicConfig(filename = config['log'], level=logging.DEBUG)


class BattleProcess:
    def __init__(self, algorithm, episodes, agent_update_frequency, trainer_update_frequency, pipe, process_id) -> None:
        self.pid = process_id
        self.data_queue = Queue()
        self.action_queue = Queue()
        self.batsim = BattleSimulator(data_queue = self.data_queue, action_queue = self.action_queue)
        self.translator = Translator(action_queue = self.action_queue)
        self.game = Game()
        self.ingestor = Ingestor(data_queue = self.data_queue, translator = self.translator, train=True, game = self.game)
        self.episodes = episodes
        self.agent_update_frequency = agent_update_frequency
        self.trainer_update_frquence = trainer_update_frequency
        self.pipe = pipe
    
    def reset_queue(self):
        self.data_queue = Queue()
        self.action_queue = Queue()
        self.batsim.set_queues(self.data_queue, self.action_queue)
        self.ingestor.set_queue(self.data_queue)
        self.translator.set_queue(self.action_queue)
    
    def start(self, threaded = True):
        if threaded:
            self.process = multiprocessing.Process(target=self.run, args=())
            self.process.start()
        else:
            self.run()
        # self.run()

    def run(self):
        if config['use_wandb']:
            wandb.init(project = 'AIrceus_V2.0')
        for i in tqdm(range(self.episodes), desc = f'EPISODES_{self.pid}'): # RUN FOR SPECIFIED NUMBER OF EPISODES
            self.game.reset()
            self.reset_queue()
            self.batsim.start(threaded=True)
            self.ingestor.start(threaded=False) # WILL NOT PASS HERE UNTIL INGESTOR ENDS, ONE EPISODE OVER WHEN THIS ENDS
            if (i+1) % self.agent_update_frequency == 0: # UPDATE AGENT
                self.ingestor.send_data(self.pipe)
                weights_done = self.pipe.recv()
                # weights = deepcopy(weights)
                self.ingestor.update_agent_weights(weights_done)
                # del weights
                # logging.info(f'MODEL UPDATED AFTER EPISODE {i+1}')
                
            if (i+1) % self.trainer_update_frquence == 0: # UPDATE TRAINER
                self.ingestor.update_trainer_weights()
                # logging.info(f'Trainer wrights updated after episode {i+1}')
            
            if config['use_wandb']:
                wandb.log({f'episode_{self.pid}': i+1})
                wandb.log({f'episode_reward_{self.pid}': self.ingestor.agent.episode_reward})
            self.ingestor.agent.episode_reward = 0
        self.pipe.close()

if __name__ == "__main__":
    start = time.time()
    episodes = config['episodes']
    simulations = config['simulations']
    episodes_per_simulation = episodes//simulations
    agent_update_frequency = config['agent_update_frequency']
    trainer_update_frequency = config['trainer_update_frequency']

    updater = CentralUpdater(simulations)

    ## CREATE SIMULATION PROCESSES
    battle_procs = []
    for i in range(simulations):
        conn1, conn2 = multiprocessing.Pipe(duplex=True)
        updater.add_pipe(conn1)
        pid = 'p' + str(i)
        battle_procs.append(BattleProcess(config['algorithm'], episodes_per_simulation, agent_update_frequency, trainer_update_frequency, conn2, pid))

    ## START UPDATER
    updater.start(threaded=True)

    ## START SIMULATIONS
    for battle_proc in battle_procs:
        battle_proc.start(threaded = True)

    ## WAIT FOR ALL BATTLE PROCESSES TO GET OVER BEFORE ENDING MAIN
    for battle_proc in battle_procs:
        battle_proc.process.join()
        print(f'\n{battle_proc.pid} PROCESS OVER\n')
    
    # ## END
    print(f'\nTRAINING COMPLETED FOR {episodes} EPISODES, PARALLEL SIMULATIONS = {simulations}')
    logging.info(f'\nTRAINING COMPLETED FOR {episodes} EPISODES, PARALLEL SIMULATIONS = {simulations}')
    print(f'TIME TAKEN: {time.time() - start}')
    

