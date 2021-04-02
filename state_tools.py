import torch
import type_multiplier

def normalize_score(score, minimum, maximum):
    ''' normalize to range [0,1] '''
    score = (score - minimum)/(maximum - minimum)
    return score

def get_field_score(base):
    ''' calculate score for this pokemon with current #TODO:weather and base conditions'''
    score = 0
    for i in base:
        score -=1
    
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
    temp_dict = {'atk:': 0.0, 'def': 0.0, 'spa': 0.0, 'spd': 0.0, 'spe': 0.0}
    user_stat_changes = []
    enemy_stat_changes = []
    for k,v in move.user_stat_changes.items():
        temp_dict[k] = v
    for k,v in temp_dict.items():
        user_stat_changes.append(normalize_score(v, minimum= -3.0, maximum= 3.0))
    
    temp_dict = {'atk:': 0.0, 'def': 0.0, 'spa': 0.0, 'spd': 0.0, 'spe': 0.0}
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
    active = torch.tensor([1.0], dtype=torch.float) if pokemon.active else torch.tensor([0.0], dtype = torch.float)
    status = get_status_score(pokemon.status)
    stats = get_stats_score(pokemon.stats)
    field_score = get_field_score(base)

    state = torch.cat((hp, active, status, stats, field_score))
    return state

def get_pokemon_type_adv(pokemon, enemy_pokemon):
    '''compare pokemon type with enemy pokemon type'''
    pokemon_type_adv = []
    if enemy_pokemon.hp == 0.0: # ENEMY HAS FAINTED
        pokemon_type_adv = torch.tensor([2.0], dtype = torch.float) ## ADD 2.0 if ENEMY FAINTED TO HELP INC AVG
        return None
    
    ## POKEMON TYPE ADVANTAGE
    for poke_type in pokemon.type:
        for enemy_type in enemy_pokemon.type:
            pokemon_type_adv.append(type_multiplier.getMultiplier(poke_type, enemy_type))
    
    avg = torch.tensor(pokemon_type_adv, dtype=torch.float).mean().item()
    pokemon_type_adv = torch.tensor(normalize_score(avg, -2.0, 2.0), dtype= torch.float)
    pokemon_type_adv = torch.clamp(pokemon_type_adv, 0.0, 1.0).item()

    return pokemon_type_adv

def get_pokemon_move_adv(move, enemy_pokemon_list):
    ''' calculate move adv score with respect to all enemy pokemon'''
    move_adv = []
    for pokemon in enemy_pokemon_list:
        if pokemon.hp != 0.0:
            adv = []
            for enemy_type in pokemon.type:
                adv.append(type_multiplier.getMultiplier(move.type, enemy_type))
            avg = torch.tensor(adv, dtype=torch.float).mean().item()
            move_adv.append(avg)
    
    avg = torch.tensor(move_adv, dtype=torch.float).mean().item()
    move_adv = torch.tensor([normalize_score(avg, -2.0, 2.0)], dtype=torch.float)
    move_adv = torch.clamp(move_adv, 0.0, 1.0)

    return move_adv

def get_move_specific_state(move):
    '''return move specific state'''
    base_power = torch.clamp(torch.tensor([normalize_score(move.base_power, 0.0, 500.0)], dtype=torch.float), 0.0, 1.0)
    accuracy = torch.clamp(torch.tensor([normalize_score(move.accuracy, 0.0, 100.0)], dtype=torch.float), 0.0, 1.0)
    pp = float(move.current_pp)/float(move.max_pp)
    pp = torch.tensor([pp], dtype=torch.float)
    disabled = torch.tensor([1.0], dtype = torch.float) if move.disabled else torch.tensor([0.0], dtype = torch.float)
    stats_change = get_move_stats_state(move)

    state = torch.cat((base_power, accuracy, pp, disabled, stats_change))

    return state


def get_pokemon_state(pokemon, enemy_pokemon_list, base, weather = None):
    '''compare pokemon with every enemy'''
    pokemon_state = get_pokemon_specific_state(pokemon, base)

    ## POKEMON TYPE ADVANTAGE
    type_adv = []
    for enemy_pokemon in enemy_pokemon_list:
        pokemon_type_adv = get_pokemon_type_adv(pokemon, enemy_pokemon)
        if pokemon_type_adv != None:
            type_adv.append(pokemon_type_adv)
    avg = torch.tensor(type_adv, dtype=torch.float).mean().item()
    type_adv = torch.tensor([normalize_score(avg, -2.0, 2.0)], dtype=torch.float)
    type_adv = torch.clamp(type_adv, 0.0, 1.0)

    ## MOVE STATE
    move_state = torch.tensor([])
    for move in pokemon.moves:
        move_state = torch.cat((move_state, get_move_specific_state(move)))
        move_state = torch.cat((move_state, get_pokemon_move_adv(move, enemy_pokemon_list)))

    state = torch.cat((pokemon_state, type_adv, move_state))
    
    return state

def get_state(game):
    '''return fully formed state from made using game'''
    p1_pokemon = game.p1_pokemon
    p2_pokemon = game.p2_pokemon
    weather = game.weather # NOT USED
    p1_base = game.p1_base
    p2_base = game.p2_base

    # P1_STATE
    p1_state = torch.tensor([])
    for pokemon in p1_pokemon:
        p1_state = torch.cat((p1_state, get_pokemon_state(pokemon, p2_pokemon, p1_base)))

    # P2_STATE
    p2_state = torch.tensor([])
    for pokemon in p2_pokemon:
        p2_state = torch.cat((p2_state, get_pokemon_state(pokemon, p1_pokemon, p2_base)))

    state = torch.cat((p1_state, p2_state))
    
    return state

def get_invalid_actions(game):
    ''' return listo of invalid actions comprising of invalid active moves and invalid switches'''
    invalid_moves = []
    invalid_switch = [] 
    p1_pokemon = game.p1_pokemon

    for pokemon in p1_pokemon:
        if pokemon.active or pokemon.hp == 0.0:
            invalid_switch.append(1.0)
            if pokemon.active:
                moves = pokemon.moves
                for move in moves:
                    if move.disabled or move.current_pp == 0:
                        invalid_moves.append(1.0)
                    else:
                        invalid_moves.append(0.0)
        else:
            invalid_switch.append(0.0)
    
    invalid_actions = torch.cat((torch.tensor(invalid_moves, dtype=torch.float), torch.tensor(invalid_switch, dtype=torch.float)))

    return invalid_actions