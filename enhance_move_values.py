import type_multiplier
import numpy as np
from move_priority import moves_first, charge_moves_invulnerable, charge_moves_vulnerable, modify_target_stats

def updateQ(q_value, pos, prev_superstate, active_pokemon, enemy_pokemon, game):
    ENEMY_FAINT_MUL = 0
    AGENT_FAINT_MUL = 0
    MOVE_REPETITION = 1
    ENEMY_DAMAGE_MUL = 0 # MANIPULATE POWER
    MOVES_FIRST_MUL = 0 #ADD TO ENEMY_FAINT_MUL
    CHARGE_MUL = 0 #ADD TO AGENT FAINT MULTIPLIER
    SAME_TYPE_MUL = 0
    MODIFY_STATS = 1 # 1 - self, -1 - enemy

    ENEMY_FAINT_PRIORITY = 800
    AGENT_FAINT_PRIORITY = 1000
    MOVE_REPETITION_PRIORITY = 60
    ATK_STAT_PRIORITY = 50
    DEF_STAT_PRIORITY = 50
    SPA_STAT_PRIORITY = 50
    SPD_STAT_PRIORITY = 50
    SPE_STAT_PRIORITY = 50

    chosen_move = pos
    move = active_pokemon['moves']

    try:
    
        chosen_move = move[chosen_move]

        move_name = chosen_move['move']

        if move_name.lower() in moves_first:
            MOVES_FIRST_MUL = 2
        if move_name.lower() in charge_moves_invulnerable:
            CHARGE_MUL = 2
        elif move_name.lower() in charge_moves_vulnerable:
            CHARGE_MUL = -2

        if move_name.lower() in modify_target_stats:
            MODIFY_STATS = -1

        type1mul = type_multiplier.getMultiplier(chosen_move['type'],enemy_pokemon['type'][0])
        if len(enemy_pokemon['type']) > 1:
            type2mul = type_multiplier.getMultiplier(chosen_move['type'],enemy_pokemon['type'][1])
        else:
            type2mul = 0

        if chosen_move['type'] in active_pokemon['type']:
            SAME_TYPE_MUL = 0.5

        if prev_superstate != None:
            en_hp_lost = prev_superstate[147] - enemy_pokemon['hp']  # HEALTH LOST BY ENEMY 
            if en_hp_lost <= 0 and move_name == game['previous_move'] and chosen_move['power'] > 0:
                q_value/=1.75

        spd_diff = active_pokemon['SpD'] - (enemy_pokemon['from_spe'] * enemy_pokemon['SpD']) # IF NEGATIVE, ENEMY PROBABLY MOVES FIRST, ELSE AGENT MOVES FIRST
        
        if prev_superstate != None:
            hp_damage = prev_superstate[0] - active_pokemon['hp'] # IF > CURRENT_HP, CAN FAINT IF ENEMY MOVES FIRST
        else:
            hp_damage = 0

        if chosen_move['power'] == 0 and game['previous_move'] == move_name:
            MOVE_REPETITION = game['move_repetition'] + 1
            print('\nENHANCE MOVE Q: INCREASING MOVE_REPETITION, ', MOVE_REPETITION)


        if spd_diff > 0: #and en_hp >= 0: #CAN DEFEAT ENEMY POKEMON
            ENEMY_FAINT_MUL = np.random.choice([0.5,0.1],p = [0.5,0.5])
        
        # if spd_diff < 0 and en_hp >= 0:
        #     ENEMY_FAINT_MUL = np.random.choice([2,4], p = [0.85,0.15])
        
        if active_pokemon['hp'] <= hp_damage: # AGENT POKEMON WILL PROBABLY FAINT
            AGENT_FAINT_MUL = np.random.choice([2,5], p =[0.15,0.85])

        if type1mul == 2 and type2mul != -2 or type2mul == 2 and type1mul != -2:
            if chosen_move['power'] > 0:
                ENEMY_DAMAGE_MUL = 1


        q_value = q_value/MOVE_REPETITION + (ENEMY_FAINT_PRIORITY/enemy_pokemon['hp'] * (ENEMY_FAINT_MUL + MOVES_FIRST_MUL))
        q_value -= (AGENT_FAINT_PRIORITY/active_pokemon['hp'] * (AGENT_FAINT_MUL - CHARGE_MUL))
        q_value += chosen_move['power']/2 + chosen_move['power'] * (ENEMY_DAMAGE_MUL + type1mul + type2mul + SAME_TYPE_MUL)
        
        if chosen_move['power'] == 0:
            q_value -= 5000/active_pokemon['hp']

        if MODIFY_STATS == -1: # AFFECT ENEMY STATS
            q_value += MODIFY_STATS * (ATK_STAT_PRIORITY * chosen_move['Atk'])
            q_value += MODIFY_STATS * (DEF_STAT_PRIORITY * chosen_move['Def'])
            q_value += MODIFY_STATS * (SPA_STAT_PRIORITY * chosen_move['SpA'])
            q_value += MODIFY_STATS * (SPD_STAT_PRIORITY * chosen_move['SpD'])
            q_value += MODIFY_STATS * (SPE_STAT_PRIORITY * chosen_move['Spe'])
        
        else: # AFFECT SELF STATS
            q_value += MODIFY_STATS * (15000/active_pokemon['Atk'] * chosen_move['Atk'])
            q_value += MODIFY_STATS * (15000/active_pokemon['Def'] * chosen_move['Def'])
            q_value += MODIFY_STATS * (15000/active_pokemon['SpA'] * chosen_move['SpA'])
            q_value += MODIFY_STATS * (15000/active_pokemon['SpD'] * chosen_move['SpD'])
            q_value += MODIFY_STATS * (15000/active_pokemon['Spe'] * chosen_move['Spe'])
        
        if chosen_move['pp'] == 0:
            q_value = -100000

    except:
        print('\nUPDATING MOVE Q: MOVE IS NOT ACTIVE/ DOES NOT EXIST\n')
        q_value = -100000

    return q_value


def getVal(q_values, prev_superstate, active_pokemon, enemy_pokemon, game):

    for i in range(len(q_values)):
        q_values[i] = updateQ(q_values[i],i,prev_superstate,active_pokemon,enemy_pokemon,game)
    
    return q_values





        



