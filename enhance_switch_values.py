import type_multiplier
import numpy as np

def getPokemonTypeMult(pokemon, enemy_pokemon):
    agent_types = []
    enemy_types = []

    agent_types.append(pokemon['type'][0])
    if len(pokemon['type']) == 2:
        agent_types.append(pokemon['type'][1])
    else:
        agent_types.append([0] * 18)

    if enemy_pokemon != None:
        enemy_types.append(enemy_pokemon['type'][0])
        if len(enemy_pokemon['type']) == 2:
            enemy_types.append(enemy_pokemon['type'][1])
        else:
            enemy_types.append([0] * 18)
    else:
        enemy_types.append([0] * 18)
        enemy_types.append([0] * 18)

    type_mul = 0

    for i in range(len(agent_types)):
        for j in range(len(enemy_types)):
            type_mul += type_multiplier.getMultiplier(agent_types[i], enemy_types[j])

    return type_mul

def getMoveMultiplier(move,pokemon,enemy_pokemon, game):

    SAME_TYPE_MUL = 0
    PP_MUL = 1
    POWER_MUL = 0

    move_value = 100

    if move['power'] == 0:
        POWER_MUL = np.random.choice([-0.5,0])
    else:
        POWER_MUL = move['power']/100
        if POWER_MUL >= 1:
            POWER_MUL = 1.5
        else:
            POWER_MUL = 0.5

    type1_mul = 0
    type2_mul = 0
    if enemy_pokemon != None:
        type1_mul = type_multiplier.getMultiplier(move['type'], enemy_pokemon['type'][0])
        if len(enemy_pokemon['type']) == 2:
            type2_mul = type_multiplier.getMultiplier(move['type'], enemy_pokemon['type'][1])
    
    if type1_mul == 2 and type2_mul != -2 or type2_mul == 2 and type1_mul != -2:
        if move['type'] in pokemon['type']:
            SAME_TYPE_MUL = 0.75

    if move['pp'] == 0:
        PP_MUL = 0
    
    move_value = move_value * (type1_mul + type2_mul + SAME_TYPE_MUL + POWER_MUL) * PP_MUL
    # move_value*= PP_MUL

    if type1_mul == -2 or type2_mul == -2:
        return 0
    
    return move_value

    
def updateQ(q_value, pokemon, enemy_pokemon, game):

    SPEED_MUL = 0

    SPEED_PRIORITY = 10000
    TYPE_PRIORITY = 10000

    pokemon_type_adv = getPokemonTypeMult(pokemon, enemy_pokemon)

    spd_diff = 1
    if enemy_pokemon != None:
        spd_diff = pokemon['SpD'] - (enemy_pokemon['from_spe'] * enemy_pokemon['SpD'])
    if spd_diff <= 0:
        SPEED_MUL = -1.5
    else:
        SPEED_MUL = 1.5

    for move in pokemon['moves']:
        q_value += getMoveMultiplier(move,pokemon,enemy_pokemon,game)
    

    q_value += SPEED_PRIORITY * SPEED_MUL
    q_value += TYPE_PRIORITY * pokemon_type_adv
    q_value -= 100000/pokemon['hp'] * 1.5

    return q_value



def getVal(q_values, active_pokemon,my_pokemon, enemy_pokemon, game):
    for i in range(len(my_pokemon)):
        if active_pokemon != None and my_pokemon[i]['name'] == active_pokemon['name']:
            q_values[i] = -1000000
        else:
            q_values[i] = updateQ(q_values[i],my_pokemon[i],enemy_pokemon,game)

    for i in range(len(my_pokemon),6):
        q_values[i] = -1000000

    return q_values


