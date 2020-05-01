# THIS FILE IS GOING TO BE RESPONSIBLE IN GENERATING APPROPRIATE STATES FOR THE NEURAL NETWORKS
# THE CHILD STATES ARE GOING TO BE GENERATED FROM TEH SUPERSTATE
# ACTIVE POKEMON LIST SIZE - 147
# ENEMY POKEMON LIST SIZE - 45
# TOTAL TEAM LIST SIZE - 882
# SUPER STATE LIST SIZE - 1077
import typedex

def getActivePokemonInfo(active_pokemon,active_moves = None):

    null_move = typedex.getTypeOhe('nil')
    null_move.extend([0,0,0,0,0,0,0,0]) # To pad moves incase actives moves are less than 4

    if active_pokemon == None:
        null_pokemon = [0,0]
        null_pokemon.extend(typedex.getTypeOhe('nil'))
        null_pokemon.extend(typedex.getTypeOhe('nil'))
        null_pokemon.extend([0,0,0,0,0])
        for _ in range(4):
            null_pokemon.extend(null_move)
        
        return null_pokemon


    acp = []  # hp,level,type,atk,def,spa,spd,spe,move1,move2,move3,move4
    acp.append(active_pokemon['hp'])
    acp.append(active_pokemon['level'])

    acp_type = active_pokemon['type'] # Pokemon can have 2 types, if pokemon has only one type, extend list with nil type
    for t in acp_type:
        acp.extend(t)
    if len(acp_type) == 1: # extend with nil type
        acp.extend(typedex.getTypeOhe('nil'))
    
    acp.append(active_pokemon['Atk'])
    acp.append(active_pokemon['Def'])
    acp.append(active_pokemon['SpA'])
    acp.append(active_pokemon['SpD'])
    acp.append(active_pokemon['Spe'])

    acp_moves = []
    moves = active_pokemon['moves']
    if active_moves != None: #ACTIVE POKEMON
        for mdict in moves:
            if mdict['move'] in active_moves:
                acp_moves.extend(mdict['type'])
                acp_moves.append(mdict['accuracy'])
                acp_moves.append(mdict['power'])
                acp_moves.append(mdict['pp'])
                acp_moves.append(mdict['Atk'])
                acp_moves.append(mdict['Def'])
                acp_moves.append(mdict['SpA'])
                acp_moves.append(mdict['SpD'])
                acp_moves.append(mdict['Spe'])
        for i in range(len(active_moves), 4):
            acp_moves.extend(null_move)
    
    else: #INAVTIVE POKEMON
        for mdict in moves:
            acp_moves.extend(mdict['type'])
            acp_moves.append(mdict['accuracy'])
            acp_moves.append(mdict['power'])
            acp_moves.append(mdict['pp'])
            acp_moves.append(mdict['Atk'])
            acp_moves.append(mdict['Def'])
            acp_moves.append(mdict['SpA'])
            acp_moves.append(mdict['SpD'])
            acp_moves.append(mdict['Spe'])
        for i in range(len(moves), 4):
            acp_moves.extend(null_move)
        
    
    acp.extend(acp_moves) # Add moves to active pokemon state

    return acp

def getActiveEnemyPokemonInfo(enemy_pokemon):

    null_move = typedex.getTypeOhe('nil')
    null_move.extend([0,0,0,0,0,0,0,0]) # To pad moves incase actives moves are less than 4

    if enemy_pokemon == None:
        null_pokemon = [0,0,0,0]
        null_pokemon.extend(typedex.getTypeOhe('nil'))
        null_pokemon.extend(typedex.getTypeOhe('nil'))
        null_pokemon.extend([0,0,0,0,0])
        return null_pokemon

    enp = [] # hp,level,type,atk,def,spa,spd,spe,move1,move2,move3,move4
    enp.append(enemy_pokemon['hp'])
    enp.append(enemy_pokemon['level'])
    enp.append(enemy_pokemon['from_spe'])
    enp.append(enemy_pokemon['to_spe'])


    enp_type = enemy_pokemon['type'] # Pokemon can have 2 types, if pokemon has only one type, extend list with nil type
    for t in enp_type:
        enp.extend(t)
    if len(enp_type) == 1: # extend with nil type
        enp.extend(typedex.getTypeOhe('nil'))

    enp.append(enemy_pokemon['Atk'])
    enp.append(enemy_pokemon['Def'])
    enp.append(enemy_pokemon['SpA'])
    enp.append(enemy_pokemon['SpD'])
    enp.append(enemy_pokemon['Spe'])

    # DONT HAVE ENEMY POKEMON MOVES

    return enp


def generateSuperState(active_pokemon, active_moves, my_pokemon, enemy_pokemon, game):
    superState = []
    # ACTIVE POKEMON DETAILS
    acp =  getActivePokemonInfo(active_pokemon,active_moves) # ACTIVE POKEMON 
    enp = getActiveEnemyPokemonInfo(enemy_pokemon) # ACTIVE ENEMY POKEMON
    team = acp #ENTIRE TEAM
    for pokemon in my_pokemon:
        if active_pokemon['name'] != my_pokemon['name']:
            team.extend(getActivePokemonInfo(pokemon))
    for _ in range(len(my_pokemon),6):
        team.extend(getActivePokemonInfo(None))

    my_pokemon_count = game['my_pokemon']
    enemy_pokemon_count = game['enemy_pokemon']
    game_active = game['active']

    superState.extend(acp)
    superState.extend(enp)
    superState.extend(team)
    superState.append(my_pokemon_count)
    superState.append(enemy_pokemon_count)
    if game_active:
        superState.append(1)
    else:
        superState.append(0)

    return superState

def generateStateForMoveChooser(superState):
    # REQUIRED: ACTIVE POKEMON, ENEMY POKEMON, MY POKEMON COUNT AND ENEMY POKEMON COUNT
    # ACTIVE POKEMON LIST SIZE - 147
    # ENEMY POKEMON LIST SIZE - 45
    # MY POKEMON COUNT AND ENEMY POKEMON COUNT - 2
    # TOTAL - 194

    state = superState[:192] # ACTIVE POKEMON AND ENEMY ACTIVE POKEMON
    state.append(superState[1074]) # MY POKTMON COUNT
    state.append(superState[1075]) # ENEMY POKEMON COUNT

    return state

def generateStateforSwitchChooser(superState):
    # REQUIRED: ENEMY POKEMON, MY TEAM
    # ENEMY POKEMON SIZE - 45
    # TEAM SIZE - 882
    # TOTAL - 927

    state = superState[147:-3]
    return state
