# THIS FILE GENERATES REWARDs GIVEN OLD AND NEW STATES

def genReward(old_state, new_state, game):
    #MY POKEMON
    mhp = ((new_state[0] - old_state[0])) * 1.5
    #STATS START AT 38
    matk = (new_state[38] - old_state[38])
    mdef = (new_state[39] - old_state[39])
    mspa = (new_state[40] - old_state[40])
    mspd = (new_state[41] - old_state[41])
    mspe = (new_state[42] - old_state[42])

    mstat = matk + mdef + mspa + mspd + mspe
    tm = (mhp + mstat) * 1.25

    # ENEMY POKEMON starts at 147
    ehp =  ((new_state[147] - old_state[147])) / 0.75
    # ENEMY STATS START AT 187
    eatk = ((new_state[187] - old_state[187]))
    edef = ((new_state[188] - old_state[188]))
    espa = ((new_state[189] - old_state[189]))
    espd = ((new_state[190] - old_state[190]))
    espe = ((new_state[191] - old_state[191]))

    estat = (eatk + edef + espa + espd + espe) * 20

    te = (ehp + estat) * 2

    total = tm + te

    if game['active'] == False:
        if game['my_pokemon'] > 0 and game['enemy_pokemon'] == 0: # AI WON
            total += 1.5*total
        
        elif game['my_pokemon'] == 0 and game['enemy_pokemon'] > 0: # AI LOST
            total -= 1.5*total

        else:
            total+= 0.5*total

    return total