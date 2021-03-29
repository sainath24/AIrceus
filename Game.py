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
        self.p1_base.remove(item)

    def add_p2_base(self, item):
        self.p2_base.append(item)
    def remove_p2_base(self, item):
        self.p2_base.remove(item)
    
    def set_win(self, player):
        self.win = player
    def set_tie(self, tie):
        self.tie = tie