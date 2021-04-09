import logging
class Translator:
    def __init__(self, action_queue, for_websocket = False) -> None:
        self.action_q = action_queue
        self.for_websocket = for_websocket

    def get_switch_name(self, pokemon_list, position):
        name = pokemon_list[position].name
        name = name.split(',')[0].lower()
        name = name.encode("ascii", "ignore").decode()

        return name

    def get_move_name(self, pokemon_list, position):
        move_name = None
        for pokemon in pokemon_list:
            if pokemon.active and pokemon.hp != 0.0: # ACTIVE POKEMON
                move_name = pokemon.moves[position].name
        
        if move_name == None:
            logging.error('MOVE NAME NOT FOUND AT POSITION ' + str(position) + 'FOR POKEMON: ' + str(pokemon.get_dict()))
        return move_name


    def translate(self, player_identifier, action, pokemon_list):
        output = '>' + player_identifier
        if self.for_websocket:
            output = '|/choose'
        if action < 4: # MOVE
            output = output + ' move ' + str(self.get_move_name(pokemon_list, int(action))) + '\n'
        else: # SWITCH
            if self.for_websocket:
                output = '|/switch ' + str(self.get_switch_name(pokemon_list, int(action) - 4)) + '\n'
            else:
                output = output + ' switch ' + str(self.get_switch_name(pokemon_list, int(action) - 4)) + '\n'


        # logging.warning('ACTION: ' + str(output))
        return output

    def write_action_queue(self,action):
        self.action_q.put(action)

    def set_queue(self, action_queue):
        self.action_q = action_queue