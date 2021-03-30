class Pokemon:
    def __init__(self, pokemon_json = None) -> None:
        if pokemon_json != None:
            self.name = pokemon_json['details']
            self.type = pokemon_json['types'] # List of types
            self.active = pokemon_json['active'] # boolean
            self.hp = pokemon_json['hp'] # hp in percentage
            self.status = pokemon_json['status'] # list of status 
            self.stats = pokemon_json['stats']
            self.base_ability = pokemon_json['baseAbility']
            self.item = pokemon_json['item']
            # self.ability = pokemon_json['ability']
            self.moves = pokemon_json['moves'] ##

    def add_move(self, move):
        self.moves.append(move)

    def set_moves(self, moves):
        self.moves = moves
    
    def remove_move(self, move):
        self.moves.remove(move)
    
    def update_stats(self, stats):
        self.stats = stats
    
    def get_dict(self):
        pokemon = {}
        pokemon['name'] = self.name
        pokemon['type'] = self.type
        pokemon['active'] = self.active
        pokemon['hp'] = self.hp
        pokemon['status'] = self.status 
        pokemon['stats'] = self.stats
        pokemon['base_ability'] = self.base_ability
        pokemon['item'] = self.item 

        pokemon['moves'] = [move.get_dict() for move in self.moves]

        return pokemon
