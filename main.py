import threading
from CentralUpdater import CentralUpdater
from BatteSimulator import BattleSimulator
from Ingestor import Ingestor
from Game import Game
from Translator import Translator
from Brain import Brain

from multiprocessing import Queue
# from queue import Queue
import multiprocessing
from config import config

from tqdm import tqdm
import time
from copy import deepcopy

import wandb
import ray
from ray.test_utils import SignalActor
from ray.util.queue import Queue as rayQ

ray.init()
# import os
# os.environ["WANDB_RUN_GROUP"] = "experiment-" + wandb.util.generate_id()
# if config['use_wandb']:
#     wandb.init(project = 'AIrceus_V2.0')

import logging
logging.basicConfig(filename = config['log'], level=logging.DEBUG)

@ray.remote
class BattleProcess:
    def __init__(self, signal_actor, algorithm, episodes, agent_update_frequency, trainer_update_frequency, rayq, process_id) -> None:
        self.pid = process_id
        self.signal_actor = signal_actor
        self.data_queue = Queue()
        self.action_queue = Queue()

        # self.data_queue = rayQ()
        # self.action_queue = rayQ()

        self.batsim = BattleSimulator(data_queue = self.data_queue, action_queue = self.action_queue)
        self.translator = Translator(action_queue = self.action_queue)
        self.game = Game()
        self.ingestor = Ingestor(data_queue = self.data_queue, translator = self.translator, train=True, game = self.game)
        self.episodes = episodes
        self.agent_update_frequency = agent_update_frequency
        self.trainer_update_frquence = trainer_update_frequency
        self.rayq = rayq
    
    def reset_queue(self):
        self.data_queue = Queue()
        self.action_queue = Queue()
        # self.data_queue = rayQ()
        # self.action_queue = rayQ()
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
                self.ingestor.send_data(self.rayq)
                ray.get(self.signal_actor.wait.remote())
                # weights_done = self.pipe.recv()
                # weights = deepcopy(weights)
                self.ingestor.update_agent_weights(1)
                # del weights
                # logging.info(f'MODEL UPDATED AFTER EPISODE {i+1}')
                
            if (i+1) % self.trainer_update_frquence == 0: # UPDATE TRAINER
                self.ingestor.update_trainer_weights()
                # logging.info(f'Trainer wrights updated after episode {i+1}')
            
            # if config['use_wandb']:
            #     wandb.log({f'episode_{self.pid}': i+1})
            #     wandb.log({f'episode_reward_{self.pid}': self.ingestor.agent.episode_reward})
            self.ingestor.agent.episode_reward = 0
        # self.pipe.close()

if __name__ == "__main__":
    ray_ids = []
    rayq = rayQ()
    signal_actor = SignalActor.remote()
    start = time.time()
    episodes = config['episodes']
    simulations = config['simulations']
    episodes_per_simulation = episodes//simulations
    agent_update_frequency = config['agent_update_frequency']
    trainer_update_frequency = config['trainer_update_frequency']

    updater = CentralUpdater.remote(signal_actor, rayq, simulations)

    ## CREATE SIMULATION PROCESSES
    battle_procs = []
    for i in range(simulations):
        # conn1, conn2 = multiprocessing.Pipe(duplex=True)
        # ray.get(updater.add_pipe.remote(conn1))
        pid = 'p' + str(i)
        battle_procs.append(BattleProcess.remote(signal_actor, config['algorithm'], episodes_per_simulation, agent_update_frequency, trainer_update_frequency, rayq, pid))

    ## START UPDATER
    ray_ids.append(updater.start.remote(threaded=False))

    ## START SIMULATIONS
    for battle_proc in battle_procs:
        ray_ids.append(battle_proc.start.remote(threaded = False))

    # WAIT FOR ALL BATTLE PROCESSES TO GET OVER BEFORE ENDING MAIN
    # for battle_proc in battle_procs:
    #     battle_proc.process.join()
    #     print(f'\n{battle_proc.pid} PROCESS OVER\n')
    done_ids, remaining_ids = ray.wait(ray_ids)
    while len(remaining_ids) !=0:
        done_ids, remaining_ids = ray.wait(remaining_ids)
    
    # ## END
    print(f'\nTRAINING COMPLETED FOR {episodes} EPISODES, PARALLEL SIMULATIONS = {simulations}')
    logging.info(f'\nTRAINING COMPLETED FOR {episodes} EPISODES, PARALLEL SIMULATIONS = {simulations}')
    print(f'TIME TAKEN: {time.time() - start}')
    

