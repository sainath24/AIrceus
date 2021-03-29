class Pokemon:
    def __init__(self, pokemon_json = None) -> None:
        if pokemon_json != None:
            self.name = pokemon_json['name']
            self.type = pokemon_json['type']
            self.active = pokemon_json['active']
            self.current_hp = pokemon_json['hp']
            self.status = pokemon_json['status']
            self.stats = pokemon_json['stats']
            self.base_ability = pokemon_json['base_ability']
            self.item = pokemon_json['item']
            self.ability = pokemon_json['ability']
            self.moves = pokemon_json['moves']

    def add_move(self, move):
        self.moves.append(move)
    
    def remove_move(self, move):
        self.moves.remove(move)
    
    def update_stats(self, stats):
        self.stats = stats
    