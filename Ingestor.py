from re import L
import threading
import json
import ingestor_tools
from queue import Queue
from config import config

from tqdm import tqdm
from config import config

import logging
# logging.basicConfig(filename=config['log'], level=logging.DEBUG)


class Ingestor:
    def __init__(self, data_queue, translator, brain, game) -> None:
        self.data_q = data_queue
        self.translator = translator
        self.brain = brain
        self.game = game
        self.switch_queue = Queue()
        self.step = 0
        self.game_end = False
        self.batch_size = config['batch_size']
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
        active_moves = None
        player_identifier = json['side']['id'] # p1 or p2

        if 'forceSwitch' not in json.keys() and 'wait' not in json.keys(): # GET ACTIVE MOVES
            active_moves = json['active'][0]['moves'] # list of active moves
        
        pokemon_json = json['side']['pokemon']
        if self.game.is_new(): # new game, need all pokemon data
            active_moves = ingestor_tools.get_active_moves(active_moves) # get a Move list of active moves
            pokemons = ingestor_tools.get_pokemon(pokemon_json) # get list of 6 pokemon with no moves for active pokemon
            ## SET GAME VARIABLES
            if player_identifier == 'p1': # player 1
                self.game.set_p1_pokemon(pokemons)
                ingestor_tools.set_active_pokemon_moves(self.game.p1_pokemon[0], active_moves)
            elif player_identifier == 'p2': # player 2
                self.game.set_p2_pokemon(pokemons)
                ingestor_tools.set_active_pokemon_moves(self.game.p2_pokemon[0], active_moves)
        else: # game is not new, just update variables
            ingestor_tools.update_pokemons_data(self.game, pokemon_json, active_moves, player_identifier)
        
        if 'forceSwitch' in json.keys(): # HAVE TO SWITCH, DONT GET ACTIVE MOVES
            self.switch_queue.put(player_identifier)
        
        return player_identifier

    def weather_change(self, weather):
        weather = weather.split('|')[0]
        self.game.set_weather(weather)

    def side_condition(self, condition, start = True):
        condition = condition.split('|')
        side = condition[0]
        player_identifier = side.split(':')[0]

        condition = condition[1]
        condition = condition.split(':')[1][1:].lower()

        if start and player_identifier == 'p1':
            self.game.add_p1_base(condition)
        elif not start and player_identifier == 'p1':
            self.game.remove_p1_base(condition)
        elif start and player_identifier == 'p2':
            self.game.add_p2_base(condition)
        elif not start and player_identifier == 'p2':
            self.game.remove_p2_base(condition)


    def choose_switch(self, player_identifier):
        # TODO: USE BRAIN TO CHOOSE SWITCH
        action = self.brain.get_action(self.game, self.step)

        switch_pokemon = 2
        action = '>' + player_identifier + ' switch ' + str(switch_pokemon) + '\n'
        self.translator.write_action_queue(action)

        self.increment_step()
        
        

    def take_decision(self):
        # TODO: USE BRAIN TO DECIDE AND TRANSLATOR TO TRANSLATE
        # action = brain.get_action(game)
        # action = translator.translate(action)
        # translator.write_action_queue(action)
        action = self.brain.get_action(self.game, self.step)
        # FOR TEST
        action = '>p1 move 1\n'
        self.translator.write_action_queue(action)
        action = '>p2 move 1\n'
        self.translator.write_action_queue(action)
        
        self.increment_step()
    
    def game_over(self, player_identifier = None, tie = False):
        if tie: # GAME IS A TIE
            self.game.set_tie(tie)
        else:
            if player_identifier == 'agent': # TODO: LOOK FOR PROPER NAME
                self.game.set_win('p1')
            else:
                self.game.set_win('p2')
        
        ## CALL BRAIN GAME OVER AND PASS STEP
        self.brain.game_over(self.game, self.step)
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
            self.game_over(line[len('|win|'):])
        
        elif '|tie' in line and '|tier' not in line:
            self.game_over(tie=True)

        elif '|error' in line:
            logging.error(line)
            self.game_over(tie=True) # TODO: TEMP HANDLING ERROR
            

    def run(self):
        while self.game_end == False:
            if not self.data_q.empty():
                line = self.data_q.get()
                # print(line)
                logging.info(line)
                self.ingest(line)
        self.game_end = False
        # print('\n INGESTOR GAME OVER \n')
                