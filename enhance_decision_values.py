import type_multiplier
import numpy as np
from move_priority import moves_first, charge_moves_invulnerable, charge_moves_vulnerable, modify_target_stats
import enhance_switch_values

# def updateMove(q_value, prev_superstate, active_pokemon, enemy_pokemon, chosen_move, game):

#     MOVE_FIRST_MUL = 0
#     FAINT_MUL = 0
#     MOVES_FIRST_MUL = 0
#     CHARGE_MUL = 0
#     SAME_TYPE_MUL = 0
#     MODIFY_STATS = 1 # 1 - self, -1 - enemy

#     move_name = chosen_move['move']

#     if move_name.lower() in moves_first:
#         MOVES_FIRST_MUL = 2
#     if move_name.lower() in charge_moves_invulnerable:
#         CHARGE_MUL = 2
#     elif move_name.lower() in charge_moves_vulnerable:
#         CHARGE_MUL = -1

#     if move_name.lower() in modify_target_stats:
#         MODIFY_STATS = -1

#     type1mul = type_multiplier.getMultiplier(chosen_move['type'],enemy_pokemon['type'][0])
#     if len(enemy_pokemon['type']) > 1:
#         type2mul = type_multiplier.getMultiplier(chosen_move['type'],enemy_pokemon['type'][1])
#     else:
#         type2mul = 0

#     if chosen_move['type'] in active_pokemon['type']:
#         if chosen_move['type'] in enemy_pokemon['type']:
#             SAME_TYPE_MUL = np.random.choice([0,-0.5], p = [0.3,0.7])
#         else:
#             SAME_TYPE_MUL = 0.5

#     spd_diff = active_pokemon['SpD'] - (enemy_pokemon['from_spe'] * enemy_pokemon['SpD']) # IF NEGATIVE, ENEMY PROBABLY MOVES FIRST, ELSE AGENT MOVES FIRST

#     hp_damage = 0
#     if prev_superstate != None:
#             hp_damage = prev_superstate[0] - active_pokemon['hp'] # IF > CURRENT_HP, CAN FAINT IF ENEMY MOVES FIRST
    
#     if spd_diff < 0 and hp_damage >= active_pokemon['hp']: # WILL PROBABLY FAINT
#         FAINT_MUL = np.random.choice([0,-1], p = [0.2,0.8])

#     if spd_diff > 0 and hp_damage > active_pokemon['hp'] and chosen_move['power'] > 0:
#         ENEMY_HIT_MUL = np.random.choice([0,1], p = [0.3,0.7])
    
#     elif spd_diff > 0 and hp_damage < active_pokemon['hp']:
#         ENEMY_HIT_MUL = np.random.choice([0.5,1], p = [0.3,0.7])

#     if move_name in charge_moves_vulnerable and hp_damage > active_pokemon['hp']:
#         CHARGE_MUL = -2

#     # if chosen_move['power'] == 0:
#     #         q_value -= 5000/active_pokemon['hp']

#     #TODO: ADJUST Q
#     q_value += 100 * (type1mul + type2mul + SAME_TYPE_MUL + FAINT_MUL + ENEMY_HIT_MUL + CHARGE_MUL)


#     return q_value

# def updateSwitch(q_value,pokemon, enemy_pokemon, game):
#     pokemon_type_adv = enhance_switch_values.getPokemonTypeMult(pokemon,enemy_pokemon)

#     m_val = 0
#     for move in pokemon['moves']:
#         m_val += enhance_switch_values.getMoveMultiplier(move,pokemon,enemy_pokemon,game)


    
#     q_value += 100 * (pokemon_type_adv)






# def updateQ(q_value,prev_superstate, active_pokemon, enemy_pokemon, chosen_switch, chosen_move, game):
#     pass


def getVal(q_values,prev_superstate, active_pokemon, enemy_pokemon, chosen_switch, chosen_move, game):

    hp_damage = 0
    if prev_superstate != None:
        hp_damage = prev_superstate[0] - active_pokemon['hp']
    
    spd_diff = active_pokemon['SpD'] - (enemy_pokemon['from_spe'] * enemy_pokemon['SpD']) # IF NEGATIVE, ENEMY PROBABLY MOVES FIRST, ELSE AGENT MOVES FIRST


    if hp_damage > active_pokemon['hp'] and spd_diff < 0:
        q_values[1] += np.random.choice([50,100], p = [0.4,0.6])
    
    elif hp_damage > active_pokemon['hp'] and spd_diff > 0:
        q_values[0] += np.random.choice([50,100], p = [0.4,0.6])
    
    elif hp_damage < active_pokemon['hp']:
        q_values[0] += np.random.choice([65,85], p = [0.4,0.6])
        q_values[1] += np.random.choice([45,65], p = [0.4,0.6])

    pokemon_type_adv = enhance_switch_values.getPokemonTypeMult(chosen_switch,enemy_pokemon)


    if pokemon_type_adv != 0:
        q_values[0] += active_pokemon['hp']/pokemon_type_adv
        q_values[1] += 100 - active_pokemon['hp']/pokemon_type_adv
    else:
        q_values[0] += active_pokemon['hp']
        q_values[1] += 100 - active_pokemon['hp']


    type1mul = type_multiplier.getMultiplier(chosen_move['type'],enemy_pokemon['type'][0])
    if len(enemy_pokemon['type']) > 1:
        type2mul = type_multiplier.getMultiplier(chosen_move['type'],enemy_pokemon['type'][1])
    else:
        type2mul = 0

    if type1mul == 2 and type2mul != -2 or type2mul == 2 and type1mul != -2: # MOVE IS GOING TO BE EFFECTIVE, WORTH CONSIDERING
        if chosen_move['power'] > 0:
            q_values[0] += np.random.choice([65,85], p = [0.4,0.6])
        else:
            q_values[0] += np.random.choice([20,45], p = [0.4,0.6])

    if pokemon_type_adv > 0:
        q_values[1] += np.random.choice([65,85], p = [0.4,0.6])
    
    return q_values