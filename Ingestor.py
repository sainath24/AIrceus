import threading
import json
import ingestor_tools
from queue import Queue

class Ingestor:
    def __init__(self, data_queue, translator, brain, game) -> None:
        self.data_q = data_queue
        self.translator = translator
        self.brain = brain
        self.game = game
        self.switch_queue = Queue()

    def start(self,threaded = True):
        if threaded:
            ingestor_thread = threading.Thread(target=self.run)
            ingestor_thread.start()
        else:
            self.run()

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
            
    def ingest(self,line):
        if '|request|' in line: # get data about players
            json_data = json.loads(line[9:])
            player = self.pokemon_changes(json_data)
            if self.switch_queue.empty() == False and player == 'p2': # SOME OR ALL PLAYERS HAVE TO SWITCH
                while not self.switch_queue.empty():
                    player_identifier = self.switch_queue.get()
                    self.choose_switch(player_identifier)

            print(self.game.get_dict())

        elif '|turn|' in line: # take a normal move decision
            self.take_decision()
        
        elif '|-weather|' in line: # weather changes
            self.weather_change(line[len('|-weather|'):])

    def choose_switch(self, player_identifier):
        # USE BRAIN TO CHOOSE SWITCH
        switch_pokemon = 2
        action = '>' + player_identifier + ' switch ' + str(switch_pokemon) + '\n'
        self.translator.write_action_queue(action)

    def take_decision(self):
        # USE BRAIN TO DECIDE AND TRANSLATOR TO TRANSLATE
        # action = brain.get_action(game)
        # action = translator.translate(action)
        # translator.write_action_queue(action)

        # FOR TEST
        action = '>p1 move 1\n'
        self.translator.write_action_queue(action)
        action = '>p2 move 1\n'
        self.translator.write_action_queue(action)
            
    def run(self):
        while True:
            if not self.data_q.empty():
                line = self.data_q.get()
                print(line)
                self.ingest(line)



