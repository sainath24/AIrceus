class Translator:
    def __init__(self, action_queue) -> None:
        self.action_q = action_queue

    def get_switch_name(self, pokemon_list, position):
        name = pokemon_list[position].name
        name = name.split(',')[0].lower()
        name = name.encode("ascii", "ignore").decode()

        return name

    def translate(self, player_identifier, action, pokemon_list):
        output = '>' + player_identifier
        if action < 4: # MOVE
            output = output + ' move ' + str(int(action) + 1) + '\n'
        else: # SWITCH
            output = output + ' switch ' + str(self.get_switch_name(pokemon_list, int(action) - 4)) + '\n'

        return output

    def write_action_queue(self,action):
        self.action_q.put(action)

    def set_queue(self, action_queue):
        self.action_q = action_queue