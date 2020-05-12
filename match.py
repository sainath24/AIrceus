from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pokemon_data as pd
import gen_state
import brains
import gen_reward
import torch




my_pokemon = []
enemy_pokemon = []
opp_pokemon = None
active_pokemon = None
superstates = []
next_superstates = []
pokemon_actions = []
rewards = []
is_done = []
active_moves = []

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('\nDEVICE: ' + str(device) + '\n')

agent = brains.Brain(device=device).to(device)
target_network = brains.Brain(device=device).to(device)

opt = torch.optim.Adam(agent.parameters(),lr = 1e-4)

def randomBattle(browser):

    actions = ActionChains(browser)

    battle_type_button = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.NAME, "format")))
    battle_type_button.click()
    time.sleep(2)
    gen4_button = WebDriverWait(browser,30).until(EC.presence_of_all_elements_located((By.NAME, "selectFormat")))

    for button in gen4_button:
        print('\n' + button.get_attribute('value'))
        if button.get_attribute('value') == 'gen4randombattle':
            print('\nGEN 4 BUTTON\n')
            # button.click()
            actions.move_to_element(button).perform()
            actions.click().perform()
            time.sleep(2)
            break

    time.sleep(2)
    # start battle with random opponet
    battle_button = WebDriverWait(browser,5).until(EC.presence_of_element_located((By.NAME, "search")))
    battle_button.click() #iniate gen 4 random battle

def challengeUser(username):
    # TODO: Complete functionality
    find_user_button = browser.find_element_by_name('finduser')
    find_user_button.click()
    username = browser.find_element_by_name('data')
    username.send_keys(username)
    username.send_keys(Keys.ENTER)

def makeMove(state): # RETURNS ACTION
    # AI MAKES MOVE HERE
    global my_pokemon
    global active_pokemon
    global active_moves

    decision_q,move_q,switch_q = agent.startForward(state['state'],state['must_switch'],state['must_attack'])
    decision_q = decision_q.data.cpu().numpy()
    move_chosen = move_q.argmax()
    switch_chosen = switch_q.argmax()

    active_move_len = 0 if active_moves == None else len(active_moves)

    decision, explore = agent.sample_action(decision_q,active_move_len,len(my_pokemon))

    if explore:
        # CONVERT RESULT TO PROPER DECISION
        print('CHOSEN TO EXPLORE')
        if decision < active_move_len:
            move_chosen = decision
            decision = 0
        else:
            switch_chosen = decision - active_move_len - 1
            decision = 1

    # pokemon_actions.append(decision)

    print('\nDECISIONNNNN:' + str(decision))

    if decision == 0:
        if state['must_switch'] == True:
            print('\nTRYING TO MOVE WHEN MUST SWITCH\n')
            # game['active'] = False
            # game['my_pokemon'] = 0
            game['error'] = 'TRIED TO MOVE WHEN MUST HAVE SWITCHED'
            game['invalid_decision'] = True
        else:
            print('\nMOVE CHOSEN INDEX: ' + str(move_chosen))
            moves = active_pokemon['moves']
            if moves[move_chosen]['move'] not in active_moves:
                print('\nCHOSEN MOVE IS NOT ACTIVE\n')
                # game['active'] = False
                # game['my_pokemon'] = 0
                game['error'] = 'CHOSEN MOVE IS NOT ACTIVE'
                game['invalid_decision'] = True
            else:
                move = moves[move_chosen]
                print('\nCHOSEN MOVE: ' + str(move))
                element = pd.getMoveElement(browser,move)
                if element != None:
                    element.click()
                else:
                    print('\nCHOSEN MOVE DOES NOT EXIST\n')
                    # game['active'] = False
                    # game['my_pokemon'] = 0
                    game['error'] = 'CHOSEN DECISION DOES NOT EXIST'
                    game['invalid_decision'] = True
    else:
        if state['must_attack'] == True:
            print('\nTRIED TO SWITCH WHEN MUST ATTACK\n')
            # game['active'] = False
            # game['my_pokemon'] = 0
            game['error'] = 'RIED TO SWITCH WHEN MUST ATTACK'
            game['invalid_decision'] = True
        else:
            print('\nCHOSEN INDEX:' + str(switch_chosen))
            print('\nMY_POKEMON LENGTH:' + str(len(my_pokemon)))
            
            print('\nACTIVE POKEMON:' + str(active_pokemon))
            if switch_chosen >= len(my_pokemon):
                print('\nCHOSEN POKEMON DOES NOT EXIST\n')
                # game['active'] = False
                # game['my_pokemon'] = 0
                game['error'] = 'CHOSEN POKEMON DOES NOT EXIST'
                game['invalid_decision'] = True
            else:
                switch_pokemon = my_pokemon[switch_chosen]
                print('\nCHOSEN MY_POKEMON: ' + str(switch_pokemon))
                # print('\nMATCH CHOSEN SWITCH: ' + str(my_pokemon[switch_chosen]))
                if state['must_switch'] == False and switch_pokemon['name'] == active_pokemon['name']:
                    print('\nSWITCHED TO SAME ACTIVE POKEMON\n')
                    moves = active_pokemon['moves']
                    move = moves[move_chosen]
                    print('\nCHOSEN MOVE:' + str(move))
                    element = pd.getMoveElement(browser,move)
                    if element != None:
                        element.click()
                    else:
                        print('\nCHOSEN MOVE DOES NOT EXIST\n')
                        # game['active'] = False
                        # game['my_pokemon'] = 0
                        game['error'] = 'CHOSEN DECISION DOES NOT EXIST'
                        game['invalid_decision'] = True

                else:
                    element = pd.getSwitchElement(browser,switch_pokemon)
                    if element != None:
                        element.click()
                        active_pokemon = switch_pokemon
                        game['active_pokemon'] = active_pokemon
                    else:
                        print('\nCHOSEN POKEMON DOES NOT EXIST\n')
                        # game['active'] = False
                        # game['my_pokemon'] = 0
                        game['error'] = 'CHOSEN DECISION DOES NOT EXIST'
                        game['invalid_decision'] = True

    return decision

def playReturn(done,must_attack = False,must_switch = False): # RETURN FUNCTION FOR PLAY
    # CREATE FINAL STATE
    global active_moves
    global opp_pokemon
    global active_pokemon
    global my_pokemon
    global game
    global browser

    # opp_pokemon = pd.getActiveEnemyPokemon(browser) #FAILS TO GET SPEED STATS SOMETIMES, SO REPEATING HERE
    state = {}
    state['must_switch'] = must_switch
    state['must_attack'] = must_attack
    state['state'] = gen_state.generateSuperState(active_pokemon,active_moves,my_pokemon,opp_pokemon,game)
    next_superstates.append(state)

    #GENERATE REWARDS
    reward = gen_reward.genReward(superstates[-1]['state'],state['state'],game)
    rewards.append(reward)

    return state, reward, done

def play(): # RETURN STATE, REWARD, IS_DONE
    global opp_pokemon
    global active_pokemon
    global my_pokemon
    global browser
    global active_moves

    print('\nSEARCHING FOR CONTROLS\n')
    while True:
        try:
            controls = WebDriverWait(browser,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "controls")))
            if len(controls) > 0 and 'Waiting for opponent...' in controls[0].text:
                # print('\nENEMY HAS NOT MADE A MOVE\n')
                pass
            else:
                print('\nENEMY MADE A MOVE\n')
                break
        except:
            print('\nCONTROLS NOT FOUND\n')
            break

    print('\nWAITING FOR ANIMATIONS\n')
    time.sleep(6) # WAIT FOR ANIMATIONS TO GET OVER
    print('\nDONE WAITING FOR ANIMATIONS\n')

    # HANDLE MOVES SUCH AS U-TURN WHERE ENEMY HAS TO SWITCH AFTER MOVE
    uturn_count = 0
    while True:
        try:
            controls = WebDriverWait(browser,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "controls")))
            if len(controls) > 0 and 'Waiting for opponent...' in controls[0].text:
                # print('\nENEMY HAS NOT SWITCHED YET\n')
                uturn_count+=1
            else:
                print('\nENEMY MADE A MOVE\n')
                break
        except:
            print('\nCONTROLS NOT FOUND\n')
            break
    if uturn_count > 0:
        time.sleep(3) # WAIT FOR POKEMON TO SWITCH
    
    if game['active']:

        if game['my_pokemon'] == 0 or game['enemy_pokemon'] == 0:
            print('\nPLAY: SOMEONE LOST ALL POKEMON\n')
            game['active'] = False
            return playReturn(True)

        opp_pokemon_new = pd.getActiveEnemyPokemon(browser)
        print('Got enemy opp_pokemon_new')

        if opp_pokemon_new == None or (opp_pokemon_new != None and opp_pokemon == None) or (opp_pokemon_new['name'] != opp_pokemon['name']):
            enemy_pokemon,enemyFaintCount = pd.getEnemyPokemonList(browser)
            print('\nEnemy Faint Count:' + str(enemyFaintCount))
            game['enemy_pokemon'] = 6 - enemyFaintCount
            print('\nENEMY POKEMON COUNT:' + str(game['enemy_pokemon']) )
            opp_pokemon = opp_pokemon_new
            # opp_pokemon = pd.getActiveEnemyPokemon(browser)
            game['enemy_active_pokemon'] = opp_pokemon
            if game['enemy_pokemon'] == 0: # AI WON
                game['active'] = False
                return playReturn(True)
            # game['enemy_active_pokemon_name'] = opp_pokemon['name']


        active_moves = pd.getCurrentActiveMoves(browser) # INITIALISE OUTSIDE AS THIS WILL BE USED LATER TO MAKE A STATE
        isSwitchPossible = pd.isSwitchPossible(browser) # IS SWITCHING TO A DIFFERENT POKEMON POSSIBLE OR NOT
        print('\n IS SWITCH POSSIBLE:' + str(isSwitchPossible))
        # THIS IS JUST FOR TESTING TO CHOOSE A MOVE MANUALLY

        if isSwitchPossible == False and active_moves == None: # GAME OVER
            print('\nSWITCH NOT POSSIBLE AND ACTIVE MOVES NOT FOUND\n')
            if game['my_pokemon'] > 1: # OPPONENT FORFEITED
                game['enemy_pokemon'] = 0
                game['forfeit'] = True
            else: # AI LOST
                game['my_pokemon'] = 0
            game['active'] = False
            return playReturn(True)

        must_attack = True if isSwitchPossible == False else False
        must_switch = False
        
        move_switch = WebDriverWait(browser, 100).until(lambda browser : browser.find_elements(By.NAME,"selectMove") or browser.find_elements(By.NAME,"selectSwitch"))#browser.find_element_by_name('selectMove') or browser.find_element_by_name('selectSwitch')
        if len(move_switch) == 0:
            # ERROR, 
            game['error'] = 'ERROR: UNABLE TO FIND MOVE/SWITCH BUTTONS'
            return playReturn()
        move_switch = move_switch[0] #PREVIOUS LINE RETURNS A LIST
        
        active_pokemon_new = None
        
        if move_switch.text == 'Attack': #CAN ATTACK OR SWITCH IF SWITCHING IS POSSIBLE
            active_moves = pd.getCurrentActiveMoves(browser) # MOVES WHICH CAN USED 
            print('\nACTIVE MOVES: ' + str(active_moves))
            print('\nIn attack\n')
            if isSwitchPossible == True: # GET FROM SWITCH BAR
                # active_pokemon_new = pd.getActivePokemon(browser) #new state of active pokemon
                active_pokemon = pd.getActivePokemon(browser)
            else: # GET MODIFIED STATS AND HEALTH ALONE
                # active_pokemon_new = active_pokemon
                active_pokemon['hp'],active_pokemon['Atk'],active_pokemon['Def'],active_pokemon['SpA'],active_pokemon['SpD'],active_pokemon['Spe'] = pd.getActiveModifiedStatsAndHpFromSprite(browser)
            game['active_pokemon'] = active_pokemon
            # active_pokemon = active_pokemon_new
            print('Active Pokemon:' + str(active_pokemon))
        
        elif move_switch.text == 'Switch': #MUST SWITCH
            # check if active pokemon is dead
            print('\nIn Switch\n')
            must_switch = True
            active_pokemon_new = pd.getActivePokemon(browser)
            if active_pokemon_new['isAlive'] == False: #pokemon has fainted
                # remove active pokemon from list
                my_pokemon = [pokemon for pokemon in my_pokemon if active_pokemon == None or pokemon['name'] != active_pokemon['name']]
                game['my_pokemon'] =  len(my_pokemon)
                game['active_pokemon'] = None
                active_pokemon = None
                # print('\nAlive pokemon:' + str(game['my_pokemon']))
                if game['my_pokemon'] == 0:
                    print('\nIN SWITCH IS CAUSING THE GAME TO END\n')
                    game['active'] = False #GAME IS OVER
                    return playReturn(True)
            
            # get updates
            print('POKEMON: ' + str(active_pokemon))

            #THIS EXISTS TO ONLY MANUALLY SWITCH WHILE TESTING
            print('\nCHOOSE SWITCH\n')

        print('\nMAKE MOVE\n')
        # time.sleep(20)
        # print('\nMOVE OVER\n')

        return playReturn(False,must_attack,must_switch)
    else:
        print('\nIN PLAY GAME IS NOT ACTIVE\n')
        print('ERROR:' + str(game['error']))
        return playReturn(True)


game_count = 12
win_count = 0
loss_count = 12

agent.load_state_dict(torch.load('pokAImon' + str(game_count) + '.pt'))


while game_count < 13:

    my_pokemon = []
    enemy_pokemon = []
    opp_pokemon = None
    active_pokemon = None
    superstates = []
    next_superstates = []
    pokemon_actions = []
    rewards = []
    is_done = []
    active_moves = []

    target_network.load_state_dict(agent.state_dict())

    browser = webdriver.Edge('C:/Users/saina/Files/projects/PokemonShowdownAI/edge_driver/msedgedriver.exe')
    browser.get('https://play.pokemonshowdown.com/')

    actions = ActionChains(browser)

    login_button = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.NAME, "login")))#browser.find_element_by_name('login')
    login_button.click() #click login button

    username = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, "username")))#browser.find_element_by_name('username')
    username.send_keys('saroja')
    username.send_keys(Keys.ENTER) #login with a name


    # ACCEPT CHALLENGE WHILE TESTING
    # accept_challenge_button = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.NAME, "acceptChallenge")))#browser.find_element_by_name('acceptChallenge')
    # accept_challenge_button.click()


    randomBattle(browser)
    # time.sleep(3) # LET WEBPAGE LOAD IRRESPECTIVE OF EXPLICIT WAITS

    # GET AI POKEMON LIST AS WELL AS CURRENT ACTIVE POKEMON
    active_pokemon = pd.getActivePokemon(browser)
    my_pokemon.append(active_pokemon)

    inactive_pokemon = pd.getInactivePokemon(browser)
    my_pokemon.extend(inactive_pokemon)

    print('My_Pokemon: ' + str(my_pokemon))

    # GET ACTIVE ENEMY POKEMON
    opp_pokemon = pd.getActiveEnemyPokemon(browser)
    # print(opp_pokemon)

    # GAME OBJECT CONAINS INFO ABOUT CURRENT GAME, yes i know its not an object and its a dictionary
    game = {
        'active' : True,
        'forfeit' : False,
        'active_pokemon': active_pokemon,
        'enemy_active_pokemon': opp_pokemon,
        'enemy_pokemon': 6,
        'my_pokemon': 6,
        'error' : 'nil', # CAN BE USED TO FIND LAST ERROR 
        'invalid_decision' : False
    }


    # MAKE INITIAL STATE
    active_moves = pd.getCurrentActiveMoves(browser) 
    isSwitchPossible = pd.isSwitchPossible(browser)

    must_attack = True if isSwitchPossible == False else False
    must_switch = False


    opp_pokemon = pd.getActiveEnemyPokemon(browser) # FAILS TO GET SPEED SOMETIMES
    state = {}
    state['must_attack'] = must_attack
    state['must_switch'] = must_switch
    state['state'] = gen_state.generateSuperState(active_pokemon,active_moves,my_pokemon,opp_pokemon,game)

    step_count = 0
    refresh_frequency = 6
    loss_history = []
    loss_frequency = 3
    #MAIN GAME CONTROL SYSTEM
    while game['active']:
        step_count +=1
        superstates.append(state)
        start = time.time()
        pokemon_action = makeMove(state)
        print('\n\nMAKE MOVE DURATION: ', time.time() - start)
        pokemon_actions.append(pokemon_action)
        next_state, reward, done = play()
        next_superstates.append(next_state)
        rewards.append(reward)
        if game['invalid_decision'] == True:
            rewards[-1] = rewards[-1] - 500
            print('\nINVALID DECISION REWARD: ',rewards[-1])
            game['invalid_decision'] = False
        is_done.append(done)
        state = next_state
        agent.epsilon = agent.epsilon - (agent.epsilon/100) if agent.epsilon - (agent.epsilon/10000) > 0 else 0.1
        print('\AGENT EPSILON:', agent.epsilon)
        if len(superstates)%3 == 0 or done == True: # CALCULATE LOSS AND CHANGE NETWORK EVERY THREE TURNS
            print('\nCOMPUTING LOSS\n')
            loss = brains.compute_loss(superstates[-3:],pokemon_actions[-3:],rewards[-3:],is_done[-3:],next_superstates[-3:],agent,target_network,device)
            print('LOSSSS:', loss)
            loss.backward()
            opt.step()
            opt.zero_grad()
            print('\nLOSS BACWARD DONE\n')

            if step_count % loss_frequency == 0:
                loss_history.append(loss.data.cpu().item())
                # grad_norm_history.append(grad_norm)

        if step_count % refresh_frequency == 0:  # Load agent weights into target_network
            print('\nREFRESHED\n')
            target_network.load_state_dict(agent.state_dict())

        if done:
            print('\nBREAKING AT DONE:', game)
            break

    # GAME IS NOT ACTIVE ANYMORE, OUTSIDE WHILE
    if game['active'] == False:
        if game['my_pokemon'] == 0 and game['enemy_pokemon'] > 0:
            print('You lost')
        
        elif game['my_pokemon'] > 0 and game['enemy_pokemon'] == 0:
            print('You win')

        else:
            print('Draw')

    else:
        print('Broke because of some error') 
        print(game['error'])
        # TODO: handle later
    game_count+=1

    print('\nERROR: ', game['error'])
    agent_file = 'pokAImon' + str(game_count) + '.pt'

    torch.save(agent.state_dict(), agent_file)
    browser.quit()

#PLAYED N NUMBER OF GAMES