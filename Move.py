class Move:
    def __init__(self, move_json = None) -> None:
        if move_json != None:
            self.name = move_json['name']
            self.type = move_json['type'] #
            self.target = move_json['target']
            self.accuracy = move_json['accuracy'] #
            self.base_power = move_json['basePower'] #
            self.max_pp = move_json['maxpp']
            self.current_pp = move_json['pp']
            self.disabled = move_json['disabled']
            self.user_stat_changes = move_json['user_stat_changes'] ##
            self.enemy_stat_changes = move_json['enemy_stat_changes'] ##
            self.trapped = False
    
    def set_current_pp(self, pp):
        self.current_pp = pp
    
    def set_user_stat_changes(self, user_stat_changes_dict):
        self.user_stat_changes = user_stat_changes_dict
    
    def set_enemy_stat_changes(self, enemy_stat_changes_dict):
        self.enemy_stat_changes = enemy_stat_changes_dict
    
    def set_type(self, type):
        self.type = type

    def get_dict(self):
        move = {}
        move['name'] = self.name 
        move['type'] = self.type
        move['target'] = self.target
        move['accuracy'] = self.accuracy
        move['base_power'] = self.base_power
        move['maxpp'] = self.max_pp
        move['pp'] = self.current_pp 
        move['disabled'] = self.disabled 
        move['user_stat_changes'] = self.user_stat_changes
        move['enemy_stat_changes'] = self.enemy_stat_changes
        move['trapped'] = self.trapped

        return move
