import torch
import type_multiplier
# import logging

ACTIVE_ENEMY_POKEMON_WEIGHT = 1

def get_default_state():
    '''All 0 for fainted pokemon in player's team, not opposition'''
    return torch.zeros(70, dtype=torch.float)

def normalize_score(score, minimum, maximum):
    ''' normalize to range [0,1] '''
    score = (score - minimum)/(maximum - minimum)
    return score

def get_field_score(base):
    ''' calculate score for this pokemon with current #TODO:weather and base conditions'''
    score = 0
    for i in base:
        if i in ['spikes', 'stealthrock', 'toxicspikes']:
            score -=1
        else:
            score += 1 
    
    score = normalize_score(score, minimum= -2.0, maximum= 2.0)
    score = torch.clamp(torch.tensor([score], dtype = torch.float), 0.0, 1.0)
    return score

def get_stats_score(stats):
    ''' compute pokemon stats score '''
    scores = []
    for k,v in stats.items():
        scores.append(normalize_score(v, minimum=0, maximum=1000))
    scores = torch.clamp(torch.tensor(scores, dtype=torch.float), 0.0, 1.0)
    return scores

def get_move_stats_state(move):
    ''' return move stats state'''
    temp_dict = {'atk': 0.0, 'def': 0.0, 'spa': 0.0, 'spd': 0.0, 'spe': 0.0}
    user_stat_changes = []
    enemy_stat_changes = []
    for k,v in move.user_stat_changes.items():
        temp_dict[k] = v
    for k,v in temp_dict.items():
        user_stat_changes.append(normalize_score(v, minimum= -3.0, maximum= 3.0))
    
    temp_dict = {'atk': 0.0, 'def': 0.0, 'spa': 0.0, 'spd': 0.0, 'spe': 0.0}
    for k,v in move.enemy_stat_changes.items():
        temp_dict[k] = v
    for k,v in temp_dict.items():
        enemy_stat_changes.append(normalize_score(v, -3.0, 3.0))
    
    user_stat_changes = torch.tensor(user_stat_changes, dtype= torch.float)
    enemy_stat_changes = torch.tensor(enemy_stat_changes, dtype= torch.float)

    stat_changes = torch.cat((user_stat_changes, enemy_stat_changes))

    return stat_changes


def get_status_score(status):
    ''' compute status score of pokemon '''
    score = 0;
    for i in status:
        score = -1
    
    score = normalize_score(score, -4.0, 4.0)
    score = torch.clamp(torch.tensor([score], dtype=torch.float), 0.0, 1.0)

    return score

def get_pokemon_specific_state(pokemon, base):
    '''retrun pokemon specific information'''
    hp = torch.tensor([normalize_score(pokemon.hp, 0.0, 1.0)], dtype=torch.float)
    # active = torch.tensor([1.0], dtype=torch.float) if pokemon.active else torch.tensor([0.0], dtype = torch.float)
    status = get_status_score(pokemon.status)
    stats = get_stats_score(pokemon.stats)
    field_score = get_field_score(base)

    state = torch.cat((hp, status, stats, field_score))
    return state

def get_pokemon_move_adv(move, enemy_pokemon):

    try:
        pp = float(move.current_pp)/float(move.max_pp)
    except Exception as e: # CAN DIVIDE BY ZERO WHEN USING DEFAULT MOVE
        pp = 0.0

    if enemy_pokemon == None or enemy_pokemon.hp == 0.0 or pp == 0.0 or move.disabled:
        return torch.zeros(1, dtype = torch.float)

    adv = []
    for enemy_type in enemy_pokemon.type:
        multiplier = type_multiplier.getMultiplier(move.type, enemy_type)
        if enemy_pokemon.active:
            multiplier *= ACTIVE_ENEMY_POKEMON_WEIGHT
        adv.append(multiplier)
    avg = torch.tensor(adv, dtype=torch.float).mean().item()
    move_type_adv = torch.tensor(normalize_score(avg, -2.0, 2.0), dtype= torch.float)
    move_type_adv = torch.clamp(move_type_adv, 0.0, 1.0)

    return move_type_adv

def get_invalid_move_specific_state():
    return torch.zeros(1 + 1 + 10, dtype = torch.float)

def get_move_specific_state(move):
    '''return move specific state'''
    try:
        pp = float(move.current_pp)/float(move.max_pp)
    except Exception as e: # CAN DIVIDE BY ZERO WHEN USING DEFAULT MOVE
        pp = 0.0
    if pp == 0.0 or move.disabled:
        return get_invalid_move_specific_state()

    base_power = torch.clamp(torch.tensor([normalize_score(move.base_power, 0.0, 500.0)], dtype=torch.float), 0.0, 1.0)
    accuracy = torch.clamp(torch.tensor([normalize_score(move.accuracy, 0.0, 100.0)], dtype=torch.float), 0.0, 1.0)
    stats_change = get_move_stats_state(move)

    state = torch.cat((base_power, accuracy, stats_change))

    return state

def get_active_pokemon_move_state(moves, enemy_pokemon):
    move_state = torch.tensor([])
    for move in moves:
        move_state = torch.cat((move_state, get_move_specific_state(move)))
        move_adv = torch.tensor([get_pokemon_move_adv(move, enemy_pokemon)], dtype= torch.float)
        move_state = torch.cat((move_state, move_adv))

    return move_state


def get_pokemon_type_adv(pokemon, enemy_pokemon):
    '''compare pokemon type with enemy pokemon type'''
    pokemon_type_adv = []
    if enemy_pokemon == None or enemy_pokemon.hp == 0.0: # ENEMY HAS FAINTED
        return 0 # TODO: TEMP TO GET ONLY OPP ACTIVE POKEMON TYPE ADV
    
    ## POKEMON TYPE ADVANTAGE
    for poke_type in pokemon.type:
        for enemy_type in enemy_pokemon.type:
            multiplier = type_multiplier.getMultiplier(poke_type, enemy_type)
            if enemy_pokemon.active:
                multiplier *= ACTIVE_ENEMY_POKEMON_WEIGHT
            pokemon_type_adv.append(multiplier)
    
    avg = torch.tensor(pokemon_type_adv, dtype=torch.float).mean().item()
    pokemon_type_adv = torch.tensor(normalize_score(avg, -2.0, 2.0), dtype= torch.float)
    # pokemon_type_adv = torch.tensor(normalize_score(avg, -2.66, 2.66), dtype= torch.float) # BECAUSE ACITVE ENEMY WEIGHT = 3
    pokemon_type_adv = torch.clamp(pokemon_type_adv, 0.0, 1.0).item()
    return pokemon_type_adv

def get_active_pokemon(pokemon_list):
    ''' Return position of active pokemon in list, if none return -1'''
    for i in range(len(pokemon_list)):
        if pokemon_list[i].active:
            return i
    return -1

def get_default_fainted_pokemon():
    return torch.zeros(8 + 1 + (13*4), dtype=torch.float)

def get_active_pokemon_state(pokemon, enemy_pokemon, base):
    '''Generate state for active pokemon'''
    if pokemon == None: # No active pokemo
        state = get_default_fainted_pokemon()
        return state
    
    pokemon_specific_state = get_pokemon_specific_state(pokemon, base)
    type_adv = torch.tensor([get_pokemon_type_adv(pokemon, enemy_pokemon)], dtype=torch.float)
    move_state = get_active_pokemon_move_state(pokemon.moves, enemy_pokemon)

    state = torch.cat((pokemon_specific_state, type_adv, move_state))

    return state

def get_inactive_move_state(move, enemy_pokemon):
    try:
        pp = float(move.current_pp)/float(move.max_pp)
    except Exception as e: # CAN DIVIDE BY ZERO WHEN USING DEFAULT MOVE
        pp = 0.0
    if pp == 0.0 or move.disabled:
        return None

    move_adv = get_pokemon_move_adv(move, enemy_pokemon).item()

    if move_adv == -2:
        return None

    stats_state = get_move_stats_state(move)
    stats_score = stats_state.sum().item()
    stats_score = normalize_score(stats_score,0.0, 10.0)

    score = move_adv + (move.base_power / 120.0) +  (move.accuracy / 100.0) + stats_score
    score = normalize_score(score, 0, 4)

    state = torch.tensor([score], dtype= torch.float)
    return state


def get_inactive_pokemon_state(pokemon, enemy_pokemon):

    if pokemon.hp == 0.0:
        return torch.zeros(7, dtype = torch.float)

    type_adv = get_pokemon_type_adv(pokemon, enemy_pokemon)
    status_score = get_status_score(pokemon.status).item()
    stats = get_stats_score(pokemon.stats)

    pokemon_state = torch.tensor([pokemon.hp + type_adv - status_score], dtype = torch.float)

    move_state = torch.tensor([])
    for move in pokemon.moves:
        move_adv = get_inactive_move_state(move, enemy_pokemon)
        if move_adv != None:
            move_state = torch.cat((move_state, move_adv))
    move_score = move_state.sum().item()
    move_state = torch.tensor([move_score], dtype = torch.float)

    state = torch.cat((pokemon_state, move_state, stats)) 

    return state

def get_inactive_team_state(active_pokemon_pos, pokemon_list, enemy_pokemon):
    state = torch.tensor([])
    for i in range(len(pokemon_list)):
        if i != active_pokemon_pos:
            state = torch.cat((state, get_inactive_pokemon_state(pokemon_list[i], enemy_pokemon)))

    return state

def generate_state(pokemon_list, enemy_pokemon_list, agent_base, enemy_base):
    active_pokemon, enemy_pokemon = None, None
    enemy_pos = get_active_pokemon(enemy_pokemon_list)
    if enemy_pos != -1:
        enemy_pokemon = enemy_pokemon_list[enemy_pos]
    active_pos = get_active_pokemon(pokemon_list)
    if active_pos != -1:
        active_pokemon = pokemon_list[active_pos]
    
    active_pokemon_state = get_active_pokemon_state(active_pokemon, enemy_pokemon, agent_base)
    active_enemy_pokemon_state = get_active_pokemon_state(enemy_pokemon, active_pokemon, enemy_base)
    inactive_team_state = get_inactive_team_state(active_pos, pokemon_list, enemy_pokemon)

    state = torch.cat((active_pokemon_state, active_enemy_pokemon_state, inactive_team_state)) # SHOULD BE 157

    # print('\nSTATE LENGTH: ', state.size())
    # print('\nSTATE: ', state)

    return state
    

def get_state(game, player_identifier):
    '''return fully formed state from made using game'''
    p1_pokemon = game.p1_pokemon
    p2_pokemon = game.p2_pokemon
    weather = game.weather # NOT USED
    p1_base = game.p1_base
    p2_base = game.p2_base

    if player_identifier == 'p1': # GENERATE STATE FOR P1
        state = generate_state(p1_pokemon, p2_pokemon, p1_base, p2_base)
    elif player_identifier == 'p2': # GENERATE STATE FOR P2
        state = generate_state(p2_pokemon, p1_pokemon, p2_base, p1_base)
    
    return state

def get_invalid_actions(game, player_identifier):
    ''' return list of invalid actions comprising of invalid active moves and invalid switches'''
    invalid_moves = []
    invalid_switch = [] 
    player_pokemon = None
    if player_identifier == 'p1':
        player_pokemon = game.p1_pokemon
    elif player_identifier == 'p2':
        player_pokemon = game.p2_pokemon

    move_trapped = False
    for pokemon in player_pokemon:
        if pokemon.active == False and pokemon.hp == 0.0:
            invalid_switch.append(1.0)
        elif pokemon.active == False and pokemon.hp > 0.0:
            invalid_switch.append(0.0)
        if pokemon.active: #and pokemon.hp != 0.0:
            moves = pokemon.moves
            for move in moves:
                if move.trapped and pokemon.hp != 0.0: # TRAPPED, CAN ONLY USE THIS MOVE
                    move_trapped = True
                else:
                    pass
                if move.disabled or move.current_pp == 0:
                    invalid_moves.append(1.0)
                else:
                    invalid_moves.append(0.0)
        # else:
        #     invalid_switch.append(0.0)

    if move_trapped: # TRAPPED, HAVE TO ONLY USE THE ONE MOVE
        invalid_switch = [1.0, 1.0, 1.0, 1.0, 1.0,]

    # if len(invalid_moves) == 0: # POKEMON FAINTED, HAVE TO SWITCH
    #     invalid_moves = [1.0, 1.0, 1.0, 1.0]
    
    invalid_actions = torch.cat((torch.tensor(invalid_moves, dtype=torch.float), torch.tensor(invalid_switch, dtype=torch.float)))

    if invalid_actions.size(0) != 9:
        print(f'ERROR IN INVALID ACTIONS: POKEMON: {len(invalid_switch)}, MOVES: {len(invalid_moves)}')
        print(f'GAME DICTIONARY: {game.get_dict()}')

    return invalid_actions