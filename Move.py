from config import default_move
class Move:
    def __init__(self, move_json = None) -> None:
        if move_json != None:
            self.name = move_json['name']
            try:
                self.type = move_json['type'] #
            except:
                self.type = default_move['type']
            try:
                self.target = move_json['target']
            except:
                self.target = default_move['target']
            try:
                self.accuracy = move_json['accuracy'] #
            except:
                self.accuracy = default_move['accuracy']
            try:
                self.base_power = move_json['basePower'] #
            except:
                self.base_power = default_move['basePower']
            try:
                self.max_pp = move_json['maxpp']
            except:
                self.max_pp = default_move['maxpp']
            try:
                self.current_pp = move_json['pp']
            except:
                self.current_pp = default_move['pp']
            try:
                self.disabled = move_json['disabled']
            except:
                self.disabled = False
            try:
                self.user_stat_changes = move_json['user_stat_changes'] ##
            except:
                self.user_stat_changes = default_move['user_stat_changes']
            try:
                self.enemy_stat_changes = move_json['enemy_stat_changes'] ##
            except:
                self.enemy_stat_changes = default_move['enemy_stat_changes']
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
