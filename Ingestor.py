import threading
import json
import ingestor_tools
from queue import Queue
from config import config

from tqdm import tqdm
from config import config

from Brain import Brain

import logging
# logging.basicConfig(filename=config['log'], level=logging.DEBUG)


class Ingestor:
    def __init__(self, data_queue, translator, train, game) -> None:
        self.data_q = data_queue
        self.translator = translator
        self.train = train
        if self.train:
            self.agent = Brain('p1', train = True)
            self.trainer = Brain('p2', train= False)
        else:
            self.agent = Brain('p1', train = False)
        # self.brain = brain
        self.game = game
        self.switch_queue = Queue()
        self.step = 0
        self.episodes_finished = 0
        self.game_end = False
        self.batch_size = config['batch_size']
        if train:
            self.trainer_update_frequency = config['trainer_update_frequency']
        self.progress_bar = tqdm(total=self.batch_size, desc='STEPS TO UPDATE')


    def reset_progress_bar(self):
        self.progress_bar.reset()
        
    def set_queue(self, data_queue):
        self.data_q = data_queue

    def start(self,threaded = True):
        if threaded:
            ingestor_thread = threading.Thread(target=self.run)
            ingestor_thread.start()
            ingestor_thread.join() # USED TO EXIT GAME WHEN OVER
        else:
            self.run()

    def increment_step(self):
        if (self.step + 1) % self.batch_size == 0: # RESET STEP TO 1
            self.step = 1
            self.progress_bar.update(1)
            self.reset_progress_bar()
            self.progress_bar.update(1)
        else:
            self.step += 1
            self.progress_bar.update(1)
            


    def pokemon_changes(self,json): 
        # logging.info(str(json))
        active_moves = None
        maybe_trapped = False
        player_identifier = json['side']['id'] # p1 or p2

        if 'forceSwitch' not in json.keys() and 'wait' not in json.keys(): # GET ACTIVE MOVES
            active_moves = json['active'][0]['moves'] # list of active moves
            try: # active[1] can be maybe_trapped
                maybe_trapped = json['active'][0]['maybeTrapped']
            except Exception as e:
                pass
        
        pokemon_json = json['side']['pokemon']
        if self.game.is_new(): # new game, need all pokemon data
            active_moves = ingestor_tools.get_active_moves(active_moves) # get a Move list of active moves
            pokemons = ingestor_tools.get_pokemon(pokemon_json) # get list of 6 pokemon with no moves for active pokemon
            ## SET GAME VARIABLES
            if player_identifier == 'p1': # player 1
                self.game.set_p1_pokemon(pokemons)
                ingestor_tools.set_active_pokemon_moves(self.game.p1_pokemon[0], active_moves, maybe_trapped)
            elif player_identifier == 'p2': # player 2
                self.game.set_p2_pokemon(pokemons)
                ingestor_tools.set_active_pokemon_moves(self.game.p2_pokemon[0], active_moves, maybe_trapped)
        else: # game is not new, just update variables
            ingestor_tools.update_pokemons_data(self.game, pokemon_json, active_moves, player_identifier, maybe_trapped)
        
        if 'forceSwitch' in json.keys(): # HAVE TO SWITCH, DONT GET ACTIVE MOVES
            self.switch_queue.put(player_identifier)
        
        return player_identifier

    def weather_change(self, weather):
        weather = weather.split('|')[0]
        self.game.set_weather(weather[:-1])

    def side_condition(self, condition, start = True):
        condition = condition.split('|')
        side = condition[0]
        player_identifier = side.split(':')[0]

        condition = condition[1]
        try:
            condition = condition.split(':')[1][1:].lower()
        except Exception as e:
            pass

        condition = condition.replace(" ","").lower()
        condition = condition.encode("ascii", "ignore").decode()

        if start and player_identifier == 'p1':
            self.game.add_p1_base(condition[:-1])
        elif not start and player_identifier == 'p1':
            self.game.remove_p1_base(condition[:-1])
        elif start and player_identifier == 'p2':
            self.game.add_p2_base(condition[:-1])
        elif not start and player_identifier == 'p2':
            self.game.remove_p2_base(condition[:-1])


    def choose_switch(self, player_identifier):
        if player_identifier == 'p1':
            action = self.agent.get_action(self.game, self.step, must_switch= True)
            action = self.translator.translate(player_identifier, action, self.game.p1_pokemon)
        elif player_identifier == 'p2':
            action = self.trainer.get_action(self.game, self.step, must_switch= True)
            action = self.translator.translate(player_identifier, action, self.game.p2_pokemon)

        
        self.translator.write_action_queue(action)

        self.increment_step()
        
    
    def take_decision(self):
        agent_action = self.agent.get_action(self.game, self.step, must_switch=False)
        agent_action = self.translator.translate('p1', agent_action, self.game.p1_pokemon)
        self.translator.write_action_queue(agent_action)
        
        if self.train:
            trainer_action = self.trainer.get_action(self.game, self.step, must_switch=False)
            trainer_action = self.translator.translate('p2', trainer_action, self.game.p2_pokemon)
            self.translator.write_action_queue(trainer_action)
        
        self.increment_step()
    
    def game_over(self, player_identifier = None, tie = False):
        if tie: # GAME IS A TIE
            self.game.set_tie(tie)
        else:
            if player_identifier[:-1] == 'agent': # TODO: LOOK FOR PROPER NAME
                self.game.set_win('p1')
            else:
                self.game.set_win('p2')
        
        ## CALL BRAIN GAME OVER AND PASS STEP
        self.agent.game_over(self.game, self.step)
        self.translator.write_action_queue('game_over')
        self.game_end = True
        # TODO: HANDLE GAME OVER

    def ingest(self,line):
        if '|request|' in line: # get data about players
            json_data = json.loads(line[9:])
            player = self.pokemon_changes(json_data)
            if self.switch_queue.empty() == False and player == 'p2': # SOME OR ALL PLAYERS HAVE TO SWITCH
                while not self.switch_queue.empty():
                    player_identifier = self.switch_queue.get()
                    self.choose_switch(player_identifier)

            # print(self.game.get_dict())

        elif '|turn|' in line: # take a normal move decision
            self.take_decision()
        
        elif '|-weather|' in line: # weather changes
            self.weather_change(line[len('|-weather|'):])
        
        elif '|-sidestart|' in line: # a condition on a player's side has started
            self.side_condition(line[len('|-sidestart|'):], start=True)
        
        elif '|-sideend|' in line: # a condition on a player's side has ended
            self.side_condition(line[len('|-sideend|'):], start= False)
        
        elif '|win|' in line:
            logging.info(line)
            self.game_over(line[len('|win|'):])
        
        elif '|tie' in line and '|tier' not in line:
            logging.info(line)
            self.game_over(tie=True)

        elif '|error' in line:
            logging.error(line)
            self.game_over(tie=True) # TODO: TEMP HANDLING ERROR

    def update_trainer_weights(self):
        self.trainer.algo.a2c.load_state_dict(self.agent.algo.a2c.state_dict())
            

    def run(self):
        if self.train and self.episodes_finished % self.trainer_update_frequency == 0: # UPDATE TRAINER WEIGHTS
            self.update_trainer_weights()
            logging.info('TRAINER WEIGHTS AFTER EPISODE: ' + str(self.episodes_finished))

        while self.game_end == False:
            if not self.data_q.empty():
                line = self.data_q.get()
                # print(line)
                # logging.info(line)
                self.ingest(line)
        self.episodes_finished += 1
        self.game_end = False
        # print('\n INGESTOR GAME OVER \n')
                