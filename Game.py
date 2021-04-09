import logging
class Game:
    def __init__(self) -> None:
        self.weather = ''
        self.p1_base = []
        self.p2_base = []
        self.p1_pokemon = []
        self.p2_pokemon = []
        self.win = ''
        self.tie = False
    
    def set_weather(self, weather):
        self.weather = weather
    
    def set_p1_pokemon(self, p1_pokemon_array):
        self.p1_pokemon = p1_pokemon_array
    def add_p1_pokemon(self, p1_pokemon):
        self.p1_pokemon.append(p1_pokemon)
    
    def set_p2_pokemon(self, p2_pokemon_array):
        self.p2_pokemon = p2_pokemon_array
    def add_p2_pokemon(self, p2_pokemon):
        self.p2_pokemon.append(p2_pokemon)
    
    def add_p1_base(self, item):
        self.p1_base.append(item)
    def remove_p1_base(self, item):
        try:
            self.p1_base.remove(item)
        except Exception as e:
            logging.warning('UNABLE TO FIND BASE CONDITION ' + str(item) + ' in p1_base: ' + str(self.p1_base))

    def add_p2_base(self, item):
        self.p2_base.append(item)
    def remove_p2_base(self, item):
        try:
            self.p2_base.remove(item)
        except Exception as e: # CONDITION NOT FOUND
            logging.warning('UNABLE TO FIND BASE CONDITION ' + str(item) + ' in p2_base: ' + str(self.p2_base))
    
    def set_win(self, player):
        self.win = player
        # GAME OVER
    def set_tie(self, tie):
        self.tie = tie
        # GAME OVER

    def is_new(self):
        if self.p1_pokemon == [] or self.p2_pokemon == []:
            return True
        return False
    
    def get_pokemon_pos(self, pokemon_details, player_identifier):
        if player_identifier == 'p1':
            for i in range(0, len(self.p1_pokemon)):
                if pokemon_details == self.p1_pokemon[i].name:
                    return i
        elif player_identifier == 'p2':
            for i in range(0, len(self.p2_pokemon)):
                if pokemon_details == self.p2_pokemon[i].name:
                    return i
        logging.error('UNABLE TO FIND POKEMON FOR POKEMON DETAILS: ' + str(pokemon_details) + '\n IN POKEMON LIST: ' + str(self.get_dict()))
        return None

    def get_dict(self):
        game = {}
        game['weather'] = self.weather
        game['p1_base'] = self.p1_base
        game['p2_base'] = self.p2_base
        game['p1_pokemon'] = [pokemon.get_dict() for pokemon in self.p1_pokemon]
        game['p2_pokemon'] = [pokemon.get_dict() for pokemon in self.p2_pokemon]
        game['win'] = self.win
        game['tie'] = self.tie
        
        return game

    def reset(self):
        self.weather = ''
        self.p1_base = []
        self.p2_base = []
        self.p1_pokemon = []
        self.p2_pokemon = []
        self.win = ''
        self.tie = False


