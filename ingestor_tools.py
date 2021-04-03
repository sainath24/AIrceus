from Move import Move
from Pokemon import Pokemon
import subprocess
import json
import logging
from config import config
# logging.basicConfig(filename= config['log'], level=logging.DEBUG)

def get_move_data(move_id):
    ''' get rest of the move data from moves.js'''
    removed_unicode = False
    while True:
        if len(move_id) == 1:
            break
        command = ['node', './get_move_data.js', move_id +'\n']
        proc = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        try:
            out_dict = json.loads(out)
            break
        except Exception as e:
            logging.warning('UABLE TO FIND MOVE ' + str(move_id))
            if removed_unicode == False: # TRY REMOVING UNICODE CHARACTERS
                move_id = move_id.encode("ascii", "ignore").decode()
                removed_unicode = True
            else:
                move_id = move_id[:-1]
    
    out_dict['name'] = move_id
    if 'hiddenpower' in move_id:
        out_dict['name'] = 'hiddenpower'

    if out_dict['accuracy'] == True:
        out_dict['accuracy'] = 100
    if out_dict['target'] == 'self':
        out_dict['enemy_stat_changes'] = {}
        if 'boosts' in out_dict.keys():
            out_dict['user_stat_changes'] = out_dict['boosts']
        else:
            out_dict['user_stat_changes'] = {}
    elif 'self' in out_dict.keys(): # self stat change
        # print('\n\nboost testing', out_dict['self'], '\n\n')
        try:
            out_dict['user_stat_changes'] = out_dict['self']['boosts']
        except Exception as e:
            out_dict['user_stat_changes'] = {}
        out_dict['enemy_stat_changes'] = {}
    
    else:
        out_dict['user_stat_changes'] = {}
        if 'boosts' in out_dict.keys():
            out_dict['enemy_stat_changes'] = out_dict['boosts']
        else:
            out_dict['enemy_stat_changes'] = {}

    return out_dict

def create_move(move_json):
    '''Update single move_json to a proper move dict to create Move object'''
    move_name = ''.join(filter(str.isalpha, move_json['id']))
    move_dict = get_move_data(move_name)
    # move_json['name'] = move_dict['name']
    move_json['name'] = move_name
    move_json['type'] = move_dict['type']
    move_json['accuracy'] = move_dict['accuracy']
    move_json['basePower'] = move_dict['basePower']
    move_json['user_stat_changes'] = move_dict['user_stat_changes']
    move_json['enemy_stat_changes'] = move_dict['enemy_stat_changes']

    return Move(move_json)
    
def get_active_moves(moves_json):
    ''' use moves_json and return list of 4 Move objects'''
    moves = []
    for move_json in moves_json:
        move = create_move(move_json)
        moves.append(move)
    return moves

def update_active_moves(game, pos, moves_json, player_identifier, maybe_trapped):
    ''' update already existing moves '''
    updated_moves = []
    if player_identifier == 'p1':
        for move_json in moves_json:
            move_name = ''.join(filter(str.isalpha, move_json['id']))
            position = game.p1_pokemon[pos].get_move_position(move_name)
            if position != None:
                updated_moves.append(position)
                try:
                    game.p1_pokemon[pos].moves[position].pp = move_json['pp']
                except Exception as e: # NO PP IN JSON
                    pass
                try:
                    game.p1_pokemon[pos].moves[position].disabled = move_json['disabled']
                except Exception as e: # NO DISABLED IN JSON
                    game.p1_pokemon[pos].moves[position].disabled = False
                try:
                    game.p1_pokemon[pos].moves[position].trapped = move_json['trapped']
                except Exception as e: # NOT TRAPPED
                    game.p1_pokemon[pos].moves[position].trapped = False
            
        for i in range(4): # SET DIABLED MOVES IF ANY, ALL NON UPDATED MOVES ARE DISABLED
            if i not in updated_moves:
                game.p1_pokemon[pos].moves[i].disabled = True
            if maybe_trapped:
                game.p1_pokemon[pos].moves[i].trapped = True

    elif player_identifier == 'p2':
        updated_moves = []
        for move_json in moves_json:
            move_name = ''.join(filter(str.isalpha, move_json['id']))
            position = game.p2_pokemon[pos].get_move_position(move_name)
            if position != None:
                updated_moves.append(position)
                try:
                    game.p2_pokemon[pos].moves[position].pp = move_json['pp']
                except Exception as e: # NO PP IN JSON
                    pass
                try:
                    game.p2_pokemon[pos].moves[position].disabled = move_json['disabled']
                except Exception as e: # NO DISABLED IN JSON
                    game.p2_pokemon[pos].moves[position].disabled = False
                try:
                    game.p2_pokemon[pos].moves[position].trapped = move_json['trapped']
                except Exception as e: # NOT TRAPPED
                    game.p2_pokemon[pos].moves[position].trapped = False
            
        for i in range(4): # SET DIABLED MOVES IF ANY, ALL NON UPDATED MOVES ARE DISABLED
            if i not in updated_moves:
                game.p2_pokemon[pos].moves[i].disabled = True
            if maybe_trapped:
                game.p1_pokemon[pos].moves[i].trapped = True

def get_pokemon_data(name):
    ''' get pokemon data from pokedex using name'''
    removed_unicode = False
    while True:
        if len(name) == 1:
            break
        command = ['node', './get_pokemon_data.js', name + '\n']
        proc = subprocess.Popen(command, shell = True, stdin=subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        try:
            out_dict = json.loads(out)
            break
        except Exception as e:
            logging.warning('UNABLE TO FIND POKEMON:  ' + str(name))
            if removed_unicode == False: # TRY REMOVING UNICODE CHARACTERS
                name = name.encode("ascii", "ignore").decode()
                removed_unicode = True
            else:
                name = name[:-1]

    return out_dict

def get_health_status(pokemon_json):
    condition = pokemon_json['condition'].split(' ')
    # hp
    hp_data = condition[0].split('/')
    if len(hp_data) == 2: # has not fainted yet, get hp as percentage
        hp = float(hp_data[0])/float(hp_data[1])
    else: # fainted
        hp = 0.0
    #status
    status = []
    if len(condition) > 1: # STATUS EXISTS
        for c in range(1, len(condition)):
            status.append(condition[c])
    return hp, status

def create_pokemon(pokemon_json):
    ''' use pokemon_json to create Pokemon object'''
    pokemon_name = ''.join(filter(str.isalpha, pokemon_json['ident'][4:]))
    pokemon_dict = get_pokemon_data(pokemon_name.lower())
    pokemon_json['types'] = pokemon_dict['types']

    # get hp and status info
    hp, status = get_health_status(pokemon_json)
    pokemon_json['hp'] = hp
    pokemon_json['status'] = status

    # moves
    if pokemon_json['active'] == False: # get move info only for inactive pokemon
        moves = []
        for move_name in pokemon_json['moves']:
            move_dict = get_move_data(move_name)
            move_dict['maxpp'] = move_dict['pp']
            move_dict['pp'] = move_dict['pp']
            move_dict['disabled'] = False
            # logging.warning('CREATED INACTIVE POKEMON MOVES WITH DICT: ' + str(move_dict))
            moves.append(Move(move_dict))
        pokemon_json['moves'] = moves
        
    p = Pokemon(pokemon_json)
    return p

def get_pokemon(pokemons_json):
    ''' use pokemon_json and return list of 6 Pokemon objects'''
    pokemons = []
    for pokemon_json in pokemons_json:
        pokemons.append(create_pokemon(pokemon_json))

    return pokemons

def set_active_pokemon_moves(pokemon, active_moves, maybe_trapped):
    if maybe_trapped:
        for i in range(len(active_moves)):
            active_moves[i].trapped = True
        
    pokemon.set_moves(active_moves)

def update_pokemon(game, pos, pokemon_json, player_identifier):
    '''use pokemon_json and update corresponding Pokemon data'''
    if player_identifier == 'p1':
        game.p1_pokemon[pos].active = pokemon_json['active']
        hp, status = get_health_status(pokemon_json)
        game.p1_pokemon[pos].hp = hp
        game.p1_pokemon[pos].status = status
        game.p1_pokemon[pos].stats = pokemon_json['stats']
        game.p1_pokemon[pos].item = pokemon_json['item']

    elif player_identifier == 'p2':
        game.p2_pokemon[pos].active = pokemon_json['active']
        hp, status = get_health_status(pokemon_json)
        game.p2_pokemon[pos].hp = hp
        game.p2_pokemon[pos].status = status
        game.p2_pokemon[pos].stats = pokemon_json['stats']
        game.p2_pokemon[pos].item = pokemon_json['item']

def update_pokemons_data(game, pokemons_json, active_moves, player_identifier, maybe_trapped):
    '''update pokemon data for a team with pokemons_json'''
    for pokemon_json in pokemons_json:
        position = game.get_pokemon_pos(pokemon_json['details'], player_identifier)
        update_pokemon(game, position, pokemon_json, player_identifier)

        if active_moves != None and player_identifier == 'p1':
            if game.p1_pokemon[position].active == True:
                # game.p1_pokemon[position].set_moves(active_moves)
                update_active_moves(game, position, active_moves, player_identifier, maybe_trapped)

        elif active_moves != None and player_identifier == 'p2':
            if game.p2_pokemon[position].active == True:
                # game.p2_pokemon[position].set_moves(active_moves)
                update_active_moves(game, position, active_moves, player_identifier, maybe_trapped)

