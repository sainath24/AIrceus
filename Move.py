class Move:
    def __init__(self, move_json = None) -> None:
        if move_json != None:
            self.name = move_json['name']
            self.type = move_json['type']
            self.target = move_json['target']
            self.accuracy = move_json['accuracy']
            self.base_power = move_json['base_power']
            self.max_pp = move_json['max_pp']
            self.current_pp = move_json['current_pp']
            self.disabled = move_json['disabled']
            self.user_stat_changes = move_json['user_stat_changes']
            self.enemy_stat_changes = {'atk':1, 'def':1, 'spe':1, 'spa':1, 'spd': 1}
    
    def set_current_pp(self, pp):
        self.current_pp = pp
    
    def set_user_stat_changes(self, user_stat_changes_dict):
        self.user_stat_changes = user_stat_changes_dict
    
    def set_enemy_stat_changes(self, enemy_stat_changes_dict):
        self.enemy_stat_changes = enemy_stat_changes_dict
    
    def set_type(self, type):
        self.type = type