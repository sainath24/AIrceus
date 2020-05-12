# # MAIN LOOP THAT PLAYS THE GAME, TECHNICALLY STARTS FROM TURN 2 OF THE GAME
# while game['active']:

#     if game['my_pokemon'] == 0 or game['enemy_pokemon'] == 0:
#         game['active'] = False
#         break

#     opp_pokemon_new = pd.getActiveEnemyPokemon(browser)
#     print('Got enemy opp_pokemon_new')

#     if opp_pokemon_new == None or opp_pokemon_new['name'] != opp_pokemon['name']:
#         enemy_pokemon,enemyFaintCount = pd.getEnemyPokemonList(browser)
#         print('\nEnemy Faint Count:' + str(enemyFaintCount))
#         game['enemy_pokemon'] = 6 - enemyFaintCount
#         print('\nENEMY POKEMON COUNT:' + str(game['enemy_pokemon']) )
#         if game['enemy_pokemon'] == 0: # AI WON
#             game['active'] = False
#             break
#         opp_pokemon = opp_pokemon_new
#         game['enemy_active_pokemon_name'] = opp_pokemon['name']


#     active_moves = pd.getCurrentActiveMoves(browser) # INITIALISE OUTSIDE AS THIS WILL BE USED LATER TO MAKE A STATE
#     isSwitchPossible = pd.isSwitchPossible(browser) # IS SWITCHING TO A DIFFERENT POKEMON POSSIBLE OR NOT
#     print('\n IS SWITCH POSSIBLE:' + str(isSwitchPossible))
#     # THIS IS JUST FOR TESTING TO CHOOSE A MOVE MANUALLY

#     if isSwitchPossible == False and active_moves == None: # GAME OVER
#         if game['my_pokemon'] > 1: # OPPONENT FORFEITED
#             game['enemy_pokemon'] = 0
#             game['forfeit'] = True
#         else: # AI LOST
#             game['my_pokemon'] = 0
#         game['active'] = False
#         break

#     must_attack = True if isSwitchPossible == False else False
#     must_switch = False
    
#     move_switch = WebDriverWait(browser, 100).until(lambda browser : browser.find_elements(By.NAME,"selectMove") or browser.find_elements(By.NAME,"selectSwitch"))#browser.find_element_by_name('selectMove') or browser.find_element_by_name('selectSwitch')
#     if len(move_switch) == 0:
#         # ERROR, 
#         game['error'] = 'ERROR: UNABLE TO FIND MOVE/SWITCH BUTTONS'
#         break
#     move_switch = move_switch[0] #PREVIOUS LINE RETURNS A LIST
    
#     active_pokemon_new = None
    
#     if move_switch.text == 'Attack': #CAN ATTACK OR SWITCH IF SWITCHING IS POSSIBLE
#         active_moves = pd.getCurrentActiveMoves(browser) # MOVES WHICH CAN USED 
#         print('\nACTIVE MOVES: ' + str(active_moves))
#         print('\nIn attack\n')
#         if isSwitchPossible == True: # GET FROM SWITCH BAR
#             active_pokemon_new = pd.getActivePokemon(browser) #new state of active pokemon
#         else: # GET MODIFIED STATS AND HEALTH ALONE
#             active_pokemon_new = active_pokemon
#             active_pokemon_new['hp'],active_pokemon_new['Atk'],active_pokemon_new['Def'],active_pokemon_new['SpA'],active_pokemon_new['SpD'],active_pokemon_new['Spe'] = pd.getActiveModifiedStatsAndHpFromSprite(browser)
#         game['active_pokemon'] = active_pokemon_new
#         print('Active Pokemon:' + str(active_pokemon))
    
#     elif move_switch.text == 'Switch': #MUST SWITCH
#         # check if active pokemon is dead
#         #TODO: SET MUST SWITCH PARAMETER
#         print('\nIn Switch\n')
#         must_switch = True
#         active_pokemon_new = pd.getActivePokemon(browser)
#         if active_pokemon_new['isAlive'] == False: #pokemon has fainted
#             # remove active pokemon from list
#             my_pokemon = [pokemon for pokemon in my_pokemon if pokemon['name'] != active_pokemon['name']]
#             game['my_pokemon']-=1
#             game['active_pokemon'] = None
#             # print('\nAlive pokemon:' + str(game['my_pokemon']))
#             if game['my_pokemon'] == 0:
#                 game['active'] = False #GAME IS OVER
#                 break
        
#         # get updates
#         print('POKEMON: ' + str(active_pokemon_new))

#         #THIS EXISTS TO ONLY MANUALLY SWITCH WHILE TESTING
#         print('\nCHOOSE SWITCH\n')

#     print('\nMAKE MOVE\n')
#     # time.sleep(20)
#     # print('\nMOVE OVER\n')

#     state = {}
#     state['must_attack'] = must_attack
#     state['must_switch'] = must_switch
#     state['state'] = gen_state.generateSuperState(active_pokemon,active_moves,my_pokemon,opp_pokemon,game)
#     next_superstates.append(state)
#     is_done.append(False)

#     #GENERATE REWARDS
#     reward = gen_reward.genReward(superstates[-1]['state'],state['state'],game)
#     rewards.append(reward)

    # if len(superstates)%3 == 0: # CALCULATE LOSS AND CHANGE NETWORK EVERY THREE TURNS
    #     loss = brains.compute_loss(superstates[-1:-4],pokemon_actions[-1:-4],rewards[-1:-4],is_done[-1:-4],next_superstates[-1:-4],agent,target_network,device)
    #     loss.backward()

    # superstates.append(state)

    # AI MAKES A MOVE
    decision_q,move_q,switch_q = agent.startForward(state['state'],must_switch,must_attack)
    move_chosen = move_q.argmax()
    switch_chosen = switch_q.argmax()

    decision, explore = agent.sample_action(decision_q,len(active_moves),len(my_pokemon))

    if explore:
        # CONVERT RESULT TO PROPER DECISION
        if decision < len(active_moves):
            move_chosen = decision
            decision = 0
        else:
            switch_chosen = len(active_moves) + len(my_pokemon) - decision - 1
            decision = 1

    pokemon_actions.append(decision)
    
    # TODO:FIND THE RIGHT ELEMENT TO CLICK AND THEN CLICK CAUSE DOM CHANGES
    if decision == 0:
        # TODO: CLICK ON MOVE_CHOSEN
        moves = active_pokemon['moves']
        move = moves[move_chosen]
        move['element'].click()
    else:
        # TODO: CLICK ON SWITCH_CHOSEN
        switch = my_pokemon[switch_chosen]
        if switch['name'] == active_pokemon['name']:
            moves = active_pokemon['moves']
            move = moves[move_chosen]
            move['element'].click()
        else:
            switch['element'].click()

    print('\nMOVE OVER\n')
    # AI DECISION ENDS
    # CLICK USING ['element'] might work cause dom might not have refreshed

    # ### IF POKEMON WAS SWITCHED #######
    # active_pokemon = pd.getActivePokemon(browser)
    # game['active_pokemon'] = active_pokemon
    # print('\nSwitched Pokemon:' + str(active_pokemon))

# END OF WHILE

# CREATE FINAL STATE
is_done.append(True)
state = {}
state['must_switch'] = False
state['must_attack'] = False
state['state'] = gen_state.generateSuperState(active_pokemon,active_moves,my_pokemon,opp_pokemon,game)
next_superstates.append(state)

reward = gen_reward.genReward(superstates[-1]['state'],state['state'],game)
rewards.append(reward)

#TODO: CALCULATE LOSS AND ADJUST NETWORK FOR THE LAST TIME FOR THIS GAME
loss = brains.compute_loss(superstates[-1:-4],pokemon_actions[-1:-4],rewards[-1:-4],is_done[-1:-4],next_superstates[-1:-4],agent,target_network,device)
loss.backward()