# THIS FILE GENERATES REWARDs GIVEN OLD AND NEW STATES
enemy_num = 6
my_num = 6

def genReward(old_state, new_state, game):
    global enemy_num, my_num
    #MY POKEMON
    # mhp = ((new_state[0] - old_state[0])) * 1.5
    mhp = (new_state[0] - old_state[0])
    mhp = mhp * 0.5 if mhp > 0 else mhp #GAIN IN HP IS REGARDED LOWER SO AS TO NOT SPAM
    #STATS START AT 38
    matk = (new_state[38] - old_state[38])
    mdef = (new_state[39] - old_state[39])
    mspa = (new_state[40] - old_state[40])
    mspd = (new_state[41] - old_state[41])
    mspe = (new_state[42] - old_state[42])

    mstat = matk + mdef + mspa + mspd + mspe
    tm = (mhp + mstat) * 1.25

    if game['switch_count'] > 1:
        tm -= game['switch_count'] * tm/1.25 #CONSECUTIVE SWITCHES LEADS TO PEANLTY

    # ENEMY POKEMON starts at 147
    ehp =  (new_state[147]/1.25 + new_state[147] - old_state[147]) * 2.5
    # ENEMY STATS START AT 187
    eatk = ((new_state[187] - old_state[187]))
    edef = ((new_state[188] - old_state[188]))
    espa = ((new_state[189] - old_state[189]))
    espd = ((new_state[190] - old_state[190]))
    espe = ((new_state[191] - old_state[191]))

    estat = (eatk + edef + espa + espd + espe) * 1.75

    te = (ehp + estat) * 2

    total = tm - te

    total += (enemy_num-game['enemy_pokemon']) * 300 - (my_num-game['my_pokemon']) * 150
    enemy_num = game['enemy_pokemon']
    my_num = game['my_pokemon']

    if game['active'] == False:
        print('\nGAME IS OVER, CALCULATING FINAL REWARD\n')
        print('\nTOTAL ', total)
        if game['my_pokemon'] > 0 and game['enemy_pokemon'] == 0: # AI WON
            total += 2000#abs(4*total)
        
        elif game['my_pokemon'] == 0 and game['enemy_pokemon'] > 0: # AI LOST
            total -= 2000 #abs(3*total)

        else:
            total+= 1000 #abs(2*total)
        print('FINAL REWARD ', total)

    return total/2000
