import threading
import multiprocessing
import json
import ingestor_tools
import torch
# from multiprocessing import Queue
from config import config

from tqdm import tqdm
from config import config

from Brain import Brain

import logging
import ray
# logging.basicConfig(filename=config['log'], level=logging.DEBUG)
logging.basicConfig(filename='ingestor.log', level=logging.DEBUG)

class Ingestor:
    def __init__(self, data_queue, translator, train, game) -> None:
        self.data_q = data_queue
        self.translator = translator
        self.train = train
        if self.train:
            self.agent = Brain('p1', train = True)
            self.trainer = Brain('p2', train= False)
        else:
            self.agent = Brain('p2', train = False) # AGENT COMES OUT AS p2 WHEN CHALLENGED BY A PLAYER
        self.game = game
        self.switch_queue = []
        self.game_end = False
        self.turn_count = 0
        if train:
            self.trainer_update_frequency = config['trainer_update_frequency']
        self.max_turns = config['max_turns_per_game']
        
    def set_queue(self, data_queue):
        self.data_q = data_queue

    def start(self,threaded = True):
        if threaded:
            ingestor_thread = threading.Thread(target=self.run)
            # ingestor_thread = multiprocessing.Process(target=self.run, args=())
            ingestor_thread.start()
            if self.train:
                ingestor_thread.join() # USED TO EXIT GAME WHEN OVER
        else:
            self.run()
            

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
            if player_identifier == self.agent.player_identifier:
                self.switch_queue.append(player_identifier)
            elif self.train and self.trainer.player_identifier == player_identifier:
                self.switch_queue.append(player_identifier)
        
        return player_identifier

    def weather_change(self, weather):
        weather = weather.split('|')[0]
        weather = weather.replace('\n','')
        self.game.set_weather(weather)

    def side_condition(self, condition, start = True):
        condition = condition.split('|')
        side = condition[0]
        player_identifier = side.split(':')[0]

        condition = condition[1]
        try:
            condition = condition.split(':')[1][1:].lower()
        except Exception as e:
            pass

        condition = condition.replace('\n','')
        condition = condition.replace(" ","").lower()
        condition = condition.encode("ascii", "ignore").decode()

        if start and player_identifier == 'p1':
            self.game.add_p1_base(condition)
        elif not start and player_identifier == 'p1':
            self.game.remove_p1_base(condition)
        elif start and player_identifier == 'p2':
            self.game.add_p2_base(condition)
        elif not start and player_identifier == 'p2':
            self.game.remove_p2_base(condition)


    def choose_switch(self, player_identifier):
        action = None
        if player_identifier == self.agent.player_identifier:
            action = self.agent.get_action(self.game, must_switch= True)
            if self.agent.player_identifier == 'p1':
                action = self.translator.translate(player_identifier, action, self.game.p1_pokemon)
            elif self.agent.player_identifier == 'p2':
                action = self.translator.translate(player_identifier, action, self.game.p2_pokemon)
        elif self.train and player_identifier == self.trainer.player_identifier:
            action = self.trainer.get_action(self.game, must_switch= True)
            action = self.translator.translate(player_identifier, action, self.game.p2_pokemon)

        
        if action!= None: 
            self.translator.write_action_queue(action)
        
    
    def take_decision(self):
        agent_action = self.agent.get_action(self.game, must_switch=False)
        if self.agent.player_identifier == 'p1':
            agent_action = self.translator.translate(self.agent.player_identifier, agent_action, self.game.p1_pokemon)
        elif self.agent.player_identifier == 'p2':
            agent_action = self.translator.translate(self.agent.player_identifier, agent_action, self.game.p2_pokemon)

        self.translator.write_action_queue(agent_action)
        
        if self.train:
            trainer_action = self.trainer.get_action(self.game, must_switch=False)
            trainer_action = self.translator.translate('p2', trainer_action, self.game.p2_pokemon)
            self.translator.write_action_queue(trainer_action)
        
    
    def game_over(self, player_identifier = None, tie = False):
        if tie: # GAME IS A TIE
            self.game.set_tie(tie)
        else:
            if player_identifier.replace('\n','') == 'agent': # TODO: LOOK FOR PROPER NAME
                self.game.set_win('p1')
            else:
                self.game.set_win('p2')
        
        ## CALL AGENT GAME OVER
        self.agent.game_over(self.game)
        self.translator.write_action_queue('game_over')
        self.game_end = True

        # RESET LSTM HIDDEN STATES AFTER GAME OVER
        self.agent.algo.a2c.reset_lstm_hidden_states()
        if self.train:
            self.trainer.algo.a2c.reset_lstm_hidden_states()
        # TODO: HANDLE GAME OVER

    def ingest(self,line):
        if '|request|' in line: # get data about players
            try:
                json_data = json.loads(line[9:])
            except: # NOT A VALID REQUEST WITH POKEMON DATA
                # logging.warning('INVALID JSON: ', line)
                # print('invalid json')
                return 
            # print('JSON: ', json_data, 'hello')
            player = self.pokemon_changes(json_data)
            if len(self.switch_queue) > 0 and player == 'p2': # SOME OR ALL PLAYERS HAVE TO SWITCH
                while len(self.switch_queue) > 0:
                    player_identifier = self.switch_queue.pop(0)
                    self.choose_switch(player_identifier)

            # print(self.game.get_dict())

        elif '|turn|' in line: # take a normal move decision
            self.take_decision()
            self.turn_count +=1
        
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
            self.game_over('trainer') # TODO: TEMP HANDLING ERROR

    def update_trainer_weights(self):
        self.trainer.algo.a2c.load_state_dict(self.agent.algo.a2c.state_dict())

    def update_agent_weights(self, weights):
        self.agent.algo.a2c.load_state_dict(torch.load(config['model']))

    def send_data(self, pipe):
        self.agent.algo.send_data(pipe)
            

    def run(self):
        while self.game_end == False:
            if not self.data_q.empty():
                line = self.data_q.get()
                if '>' == line[0]:
                    # print('Invalid line: ', line)
                    # logging.warning('FOUND INVALID LINE: ', line)
                    position = line.find('|')
                    line = line[position:]
                # if self.train:
                #     logging.info(line)
                self.ingest(line)
            if self.game_end == False and self.train and self.turn_count >= self.max_turns: # MAX TURNS REACHED, END GAME WITH LOSS
                self.game_over('trainer') #TODO: DO NOT PASS TRAINER IN THE FUTURE

        self.game_end = False
        self.turn_count = 0
    
    def kill(self):
        self.game_end = True
                