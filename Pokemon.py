class Pokemon:

    def __init__(self,name, level, ability,item,stats,moves,modstats = None):
        self.name = name
        self.level = level
        self.ability = ability
        self.item = item
        if modstats != None:
            stats = modstats
        self.atk = stats[0]
        self.deff = stats[1]
        self.spa = stats[2]
        self.spd = stats[3]
        self.spe = stats[4]
        self.moves = {}
        for i in range(len(moves)):
            # TODO: get damage detail of move from pokeapi
            pp = None
            name = moves[i]
            m = {
                'name':moves[i],
                'pp':pp
            }
            self.moves[str('move' + i)] = m