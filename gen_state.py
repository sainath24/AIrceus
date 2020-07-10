# THIS FILE IS GOING TO BE RESPONSIBLE IN GENERATING APPROPRIATE STATES FOR THE NEURAL NETWORKS
# THE CHILD STATES ARE GOING TO BE GENERATED FROM TEH SUPERSTATE
# ACTIVE POKEMON LIST SIZE - 147
# ENEMY POKEMON LIST SIZE - 45
# TOTAL TEAM LIST SIZE - 882
# SUPER STATE LIST SIZE - 1076
import typedex
import pokemon_data as pd
import torch

def getActivePokemonInfo(active_pokemon,active_moves = None):

    null_move = [0] * 26 # To pad moves incase actives moves are less than 4

    if active_pokemon == None:
        null_pokemon = [0] * 147
        # for _ in range(4):
        #     null_pokemon.extend(null_move)
        
        return null_pokemon


    acp = []  # hp,level,type,atk,def,spa,spd,spe,move1,move2,move3,move4
    acp.append(active_pokemon['hp'])
    # print('\nACP:' + str(active_pokemon['hp']))
    acp.append(active_pokemon['level'])
    # print('\nACP:' + str(active_pokemon['level']))

    acp_type = active_pokemon['type'] # Pokemon can have 2 types, if pokemon has only one type, extend list with nil type
    for t in acp_type:
        acp.extend(t)
        # # print('\nACP TYPE LENGTH:' + str(len(acp_type)))
        # print('\nACP:' + str(t))
    if len(acp_type) == 1: # extend with nil type
        # print('\nACP ADD TYPE NIL')
        acp.extend([0] * 18)
        # print('\nACP ADD TYPE NIL DONE')
        # print('\nACP:' + str(typedex.getTypeOhe('nil')))
    
    acp.append(active_pokemon['Atk'])
    # print('\nACP:' + str(active_pokemon['Atk']))
    acp.append(active_pokemon['Def'])
    # print('\nACP:' + str(active_pokemon['Def']))
    acp.append(active_pokemon['SpA'])
    # print('\nACP:' + str(active_pokemon['SpA']))
    acp.append(active_pokemon['SpD'])
    # print('\nACP:' + str(active_pokemon['SpD']))
    acp.append(active_pokemon['Spe'])
    # print('\nACP:' + str(active_pokemon['Spe']))

    acp_moves = []
    moves = active_pokemon['moves']
    if active_moves != None: #ACTIVE POKEMON
        for mdict in moves:
            if mdict['move'] in active_moves:
                if mdict['pp'] > 0:
                    acp_moves.extend(mdict['type'])
                    # print('\nACP:' + str(mdict['type']))
                    acp_moves.append(mdict['accuracy'])
                    # print('\nACP:' + str(mdict['accuracy']))
                    acp_moves.append(mdict['power'])
                    # print('\nACP:' + str(mdict['power']))
                    acp_moves.append(mdict['pp'])
                    # print('\nACP:' + str(mdict['pp']))
                    acp_moves.append(mdict['Atk'])
                    # print('\nACP:' + str(mdict['Atk']))
                    acp_moves.append(mdict['Def'])
                    # print('\nACP:' + str(mdict['Def']))
                    acp_moves.append(mdict['SpA'])
                    # print('\nACP:' + str(mdict['SpA']))
                    acp_moves.append(mdict['SpD'])
                    # print('\nACP:' + str(mdict['SpD']))
                    acp_moves.append(mdict['Spe'])
                    # print('\nACP:' + str(mdict['Spe']))
                else:
                    acp_moves.extend([0]*26)

        for i in range(len(active_moves), 4):
            acp_moves.extend([0]*26)
    
    else: #INAVTIVE POKEMON
        for mdict in moves:
            if mdict['pp'] > 0:
                acp_moves.extend(mdict['type'])
                # print('\nACP:' + str(mdict['type']))
                acp_moves.append(mdict['accuracy'])
                # print('\nACP:' + str(mdict['accuracy']))
                acp_moves.append(mdict['power'])
                # print('\nACP:' + str(mdict['power']))
                acp_moves.append(mdict['pp'])
                # print('\nACP:' + str(mdict['pp']))
                acp_moves.append(mdict['Atk'])
                # print('\nACP:' + str(mdict['Atk']))
                acp_moves.append(mdict['Def'])
                # print('\nACP:' + str(mdict['Def']))
                acp_moves.append(mdict['SpA'])
                # print('\nACP:' + str(mdict['SpA']))
                acp_moves.append(mdict['SpD'])
                # print('\nACP:' + str(mdict['SpD']))
                acp_moves.append(mdict['Spe'])
                # print('\nACP:' + str(mdict['Spe']))
            else:
                acp_moves.extend([0]*26)
        
        for _ in range(len(acp_moves),104):
            acp_moves.append(0)
        # for i in range(len(moves), 4):
        #     acp_moves.extend(null_move)
        
    
    acp.extend(acp_moves) # Add moves to active pokemon state
    # print('\nACP FULL:' + str(acp))
    return acp

def getActiveEnemyPokemonInfo(enemy_pokemon):

    # null_move = typedex.getTypeOhe('nil')
    # null_move.extend([0,0,0,0,0,0,0,0]) # To pad moves incase actives moves are less than 4

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
    print('\nACP LENGTH:' + str(len(acp)))
    
    enp = getActiveEnemyPokemonInfo(enemy_pokemon) # ACTIVE ENEMY POKEMON
    print('\nENP LENGTH:' + str(len(enp)))
    team = [] #ENTIRE TEAM
    print('\nTEAM LENGTH:' + str(len(team)))
    for pokemon in my_pokemon:
        if active_pokemon != None and active_pokemon['name'] != pokemon['name']:
            team.extend(getActivePokemonInfo(pokemon))
        elif active_pokemon != None and active_pokemon['name'] == pokemon['name']:
            team.extend(getActivePokemonInfo(pokemon,active_moves))
        print('\nTEAM LENGTH:' + str(len(team)))
    if len(my_pokemon) < 6:
        print('TEAM LENGTH IS NOT 6:' + str(len(my_pokemon)))
        for _ in range(len(team),882):
            team.append(0)
        # team.extend(getActivePokemonInfo(None))
        print('\nTEAM LENGTH:' + str(len(team)))

    print('\nTEAM LENGTH:' + str(len(team)))

    my_pokemon_count = game['my_pokemon']
    enemy_pokemon_count = game['enemy_pokemon']
    game_active = game['active']

    print('\nSUPER_STATE_LENGTH: ' + str(len(superState)))
    superState.extend(acp)
    print('\nSUPER_STATE_LENGTH: ' + str(len(superState)))
    superState.extend(enp)
    print('\nSUPER_STATE_LENGTH: ' + str(len(superState)))
    superState.extend(team)
    print('\nSUPER_STATE_LENGTH: ' + str(len(superState)))
    superState.append(my_pokemon_count)
    print('\nSUPER_STATE_LENGTH: ' + str(len(superState)))
    superState.append(enemy_pokemon_count)
    print('\nSUPER_STATE_LENGTH: ' + str(len(superState)))

    return superState

def generateStateForMoveChooser(superState, make = True):
    # REQUIRED: ACTIVE POKEMON, ENEMY POKEMON, MY POKEMON COUNT AND ENEMY POKEMON COUNT
    # ACTIVE POKEMON LIST SIZE - 147
    # ENEMY POKEMON LIST SIZE - 45
    # MY POKEMON COUNT AND ENEMY POKEMON COUNT - 2
    # TOTAL - 194
    if make == False:
        null_state = [0] * 194
        return null_state
        
    # print('\nGENERATEMOVECHOOSER: ',superState)

    state = superState[:192] # ACTIVE POKEMON AND ENEMY ACTIVE POKEMON
    state.append(superState[1074]) # MY POKTMON COUNT
    state.append(superState[1075]) # ENEMY POKEMON COUNT

    # print('\nMOVE_STATE_LENGTH:' + str(len(state)))

    return state

def generateStateforSwitchChooser(superState, make = True):
    # REQUIRED: ACTIVE POKEMON,ENEMY POKEMON, MY TEAM
    # ACTIVE POKEMON - 147
    # ENEMY POKEMON SIZE - 45
    # TEAM SIZE - 882
    # TOTAL - 1074

    if make == False:
        null_state = [0] * 1074
        # for _ in range(1074):
        #     null_state.append(0)
        return null_state

    # print('\nGENERATESWITCHCHOOSER:',superState)
    state = superState[:-2]
    # print('\nSWITCH_STATE_LENGTH:' + str(len(state)))
    return state

def generateStateforFinalChooser(movechooser, switchchooser,superState):
    # REQUIRED: MOVECHOOSER OUTPUT, SWITCHCHOOSER OUTPUT, MY_POKEMON, ENEMY_POKEMON
    # MOVECHOOSER SIZE - 26
    # SWITCH CHOOSER SIZE - 147
    # ACTIVE POKEMON - 43 (EXCLUDING MOVES)
    # ENEMY POKEMON - 45
    # TOTAL - 263
    # ACTIVE MOVES START FROM 43 WITH LENGTH 26

    null_move = typedex.getTypeOhe('nil')
    null_move.extend([0,0,0,0,0,0,0,0])

    chosen_move = movechooser.argmax()
    # print('\nMOVE:' + str(chosen_move))
    if movechooser.tolist() == [0,0,0,0]:
        move = null_move
    else:
        move = superState[(chosen_move * 26) + 43: (chosen_move * 26) + 43 + 26]
    # print('\nMOVE LEN:' + str(len(move)))

    chosen_pokemon = switchchooser.argmax()
    
    # print('\nCHOSEN_POKEMON:' + str(chosen_pokemon))
    if switchchooser.tolist() == [0,0,0,0,0,0]:
        pokemon = [0] * 147
    else:
        pokemon = superState[(chosen_pokemon * 147) + 192: (chosen_pokemon * 147) + 192 + 147]
    # print('\nPOKEMON LEN:' + str(len(pokemon)))

    #ADD ACTIVE POKEMON AND ECTIVE ENEMY POKEMON
    active_pokemon = superState[:43]
    active_enemy_pokemon = superState[147:192]

    state = active_pokemon
    state.extend(active_enemy_pokemon)

    state.extend(move)
    state.extend(pokemon)
    

    state.append(superState[1074])
    state.append(superState[1075])

    return state

