from Move import Move
from Pokemon import Pokemon
import subprocess
import json

def get_move_data(id):
    ''' get rest of the move data from moves.js'''
    while True:
        if len(id) == 1:
            break
        command = ['node', './get_move_data.js', id +'\n']
        proc = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        try:
            out_dict = json.loads(out)
            break
        except Exception as e:
            id = id[:-1]

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
    move_json['name'] = move_dict['name']
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
        moves.append(create_move(move_json))
    return moves

def update_active_moves(game, pos, moves_json, player_identifier):
    ''' update already existing moves '''
    if player_identifier == 'p1':
        for i in range(len(moves_json)):
            try:
                game.p1_pokemon[pos].moves[i].pp = moves_json[i]['pp']
            except Exception as e: # NO PP IN JSON
                pass
            try:
                game.p1_pokemon[pos].moves[i].disabled = moves_json[i]['disabled']
            except Exception as e: # NO DIABLED IN JSON
                pass
    
    elif player_identifier == 'p2':
        for i in range(len(moves_json)):
            try:
                game.p2_pokemon[pos].moves[i].pp = moves_json[i]['pp']
            except Exception as e: # NO PP IN JSON
                pass
            try:
                game.p2_pokemon[pos].moves[i].disabled = moves_json[i]['disabled']
            except Exception as e: # NO DIABLED IN JSON
                pass

def get_pokemon_data(name):
    ''' get pokemon data from pokedex using name'''
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
            moves.append(Move(move_dict))
        pokemon_json['moves'] = moves

    return Pokemon(pokemon_json)

def get_pokemon(pokemons_json):
    ''' use pokemon_json and return list of 6 Pokemon objects'''
    pokemons = []
    for pokemon_json in pokemons_json:
        pokemons.append(create_pokemon(pokemon_json))

    return pokemons

def set_active_pokemon_moves(pokemon, active_moves):
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

def update_pokemons_data(game, pokemons_json, active_moves, player_identifier):
    '''update pokemon data for a team with pokemons_json'''
    for pokemon_json in pokemons_json:
        position = game.get_pokemon_pos(pokemon_json['details'], player_identifier)
        update_pokemon(game, position, pokemon_json, player_identifier)

        if active_moves != None and player_identifier == 'p1':
            if game.p1_pokemon[position].active == True:
                # game.p1_pokemon[position].set_moves(active_moves)
                update_active_moves(game, position, active_moves, player_identifier)

        elif active_moves != None and player_identifier == 'p2':
            if game.p2_pokemon[position].active == True:
                # game.p2_pokemon[position].set_moves(active_moves)
                update_active_moves(game, position, active_moves, player_identifier)
