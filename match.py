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
superstates = []
next_superstates = []
pokemon_actions = []
rewards = []
is_done = []

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('\nDEVICE: ' + str(device) + '\n')

agent = brains.Brain(device=device)
target_network = brains.Brain(device=device)

browser = webdriver.Edge('C:/Users/saina/Files/projects/PokemonShowdownAI/edge_driver/msedgedriver.exe')
browser.get('https://play.pokemonshowdown.com/')

actions = ActionChains(browser)

login_button = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.NAME, "login")))#browser.find_element_by_name('login')
login_button.click() #click login button

username = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, "username")))#browser.find_element_by_name('username')
username.send_keys('saroja')
username.send_keys(Keys.ENTER) #login with a name


def randomBattle():

    battle_type_button = WebDriverWait(browser,30).until(browser.find_element_by_name('format'))
    battle_type_button.click()
    gen4_button = WebDriverWait(browser,30).until(browser.find_elements_by_name('selectFormat'))

    for button in gen4_button:
        # print('\n' + button.get_attribute('value'))
        if button.get_attribute('value') == 'gen4randombattle':
            button.click()
            break

    time.sleep(2)
    # start battle with random opponet
    battle_button = WebDriverWait(browser,5).until(browser.find_element_by_name('search'))
    battle_button.click() #iniate gen 4 random battle

def challengeUser(username):
    # TODO: Complete functionality
    find_user_button = browser.find_element_by_name('finduser')
    find_user_button.click()
    username = browser.find_element_by_name('data')
    username.send_keys(username)
    username.send_keys(Keys.ENTER)

# ACCEPT CHALLENGE WHILE TESTING
accept_challenge_button = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.NAME, "acceptChallenge")))#browser.find_element_by_name('acceptChallenge')
accept_challenge_button.click()

time.sleep(3) # LET WEBPAGE LOAD IRRESPECTIVE OF EXPLICIT WAITS

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
    'error' : 'nil' # CAN BE USED TO FIND LAST ERROR 
}

# TODO:
# MAKE INITIAL STATE
# LET AI MAKE THE FIRST MOVE OUTSIDE THE MAIN WHILE
active_moves = pd.getCurrentActiveMoves(browser) 
isSwitchPossible = pd.isSwitchPossible(browser)

must_attack = True if isSwitchPossible == False else False
must_switch = False

state = {}
state['must_attack'] = must_attack
state['must_switch'] = must_switch
state['state'] = gen_state.generateSuperState(active_pokemon,active_moves,my_pokemon,opp_pokemon,game)
superstates.append(state)


# AI MAKES FIRST MOVE HERE
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

print('\nDECISIONNNNN:' + str(decision))

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

# MAIN LOOP THAT PLAYS THE GAME, TECHNICALLY STARTS FROM TURN 2 OF THE GAME
while game['active']:

    if game['my_pokemon'] == 0 or game['enemy_pokemon'] == 0:
        game['active'] = False
        break

    opp_pokemon_new = pd.getActiveEnemyPokemon(browser)
    print('Got enemy opp_pokemon_new')

    if opp_pokemon_new == None or opp_pokemon_new['name'] != opp_pokemon['name']:
        enemy_pokemon,enemyFaintCount = pd.getEnemyPokemonList(browser)
        print('\nEnemy Faint Count:' + str(enemyFaintCount))
        game['enemy_pokemon'] = 6 - enemyFaintCount
        print('\nENEMY POKEMON COUNT:' + str(game['enemy_pokemon']) )
        if game['enemy_pokemon'] == 0: # AI WON
            game['active'] = False
            break
        opp_pokemon = opp_pokemon_new
        game['enemy_active_pokemon_name'] = opp_pokemon['name']


    active_moves = pd.getCurrentActiveMoves(browser) # INITIALISE OUTSIDE AS THIS WILL BE USED LATER TO MAKE A STATE
    isSwitchPossible = pd.isSwitchPossible(browser) # IS SWITCHING TO A DIFFERENT POKEMON POSSIBLE OR NOT
    print('\n IS SWITCH POSSIBLE:' + str(isSwitchPossible))
    # THIS IS JUST FOR TESTING TO CHOOSE A MOVE MANUALLY

    if isSwitchPossible == False and active_moves == None: # GAME OVER
        if game['my_pokemon'] > 1: # OPPONENT FORFEITED
            game['enemy_pokemon'] = 0
            game['forfeit'] = True
        else: # AI LOST
            game['my_pokemon'] = 0
        game['active'] = False
        break

    must_attack = True if isSwitchPossible == False else False
    must_switch = False
    
    move_switch = WebDriverWait(browser, 100).until(lambda browser : browser.find_elements(By.NAME,"selectMove") or browser.find_elements(By.NAME,"selectSwitch"))#browser.find_element_by_name('selectMove') or browser.find_element_by_name('selectSwitch')
    if len(move_switch) == 0:
        # ERROR, 
        game['error'] = 'ERROR: UNABLE TO FIND MOVE/SWITCH BUTTONS'
        break
    move_switch = move_switch[0] #PREVIOUS LINE RETURNS A LIST
    
    active_pokemon_new = None
    
    if move_switch.text == 'Attack': #CAN ATTACK OR SWITCH IF SWITCHING IS POSSIBLE
        active_moves = pd.getCurrentActiveMoves(browser) # MOVES WHICH CAN USED 
        print('\nACTIVE MOVES: ' + str(active_moves))
        print('\nIn attack\n')
        if isSwitchPossible == True: # GET FROM SWITCH BAR
            active_pokemon_new = pd.getActivePokemon(browser) #new state of active pokemon
        else: # GET MODIFIED STATS AND HEALTH ALONE
            active_pokemon_new = active_pokemon
            active_pokemon_new['hp'],active_pokemon_new['Atk'],active_pokemon_new['Def'],active_pokemon_new['SpA'],active_pokemon_new['SpD'],active_pokemon_new['Spe'] = pd.getActiveModifiedStatsAndHpFromSprite(browser)
        game['active_pokemon'] = active_pokemon_new
        print('Active Pokemon:' + str(active_pokemon))
    
    elif move_switch.text == 'Switch': #MUST SWITCH
        # check if active pokemon is dead
        #TODO: SET MUST SWITCH PARAMETER
        print('\nIn Switch\n')
        must_switch = True
        active_pokemon_new = pd.getActivePokemon(browser)
        if active_pokemon_new['isAlive'] == False: #pokemon has fainted
            # remove active pokemon from list
            my_pokemon = [pokemon for pokemon in my_pokemon if pokemon['name'] != active_pokemon['name']]
            game['my_pokemon']-=1
            game['active_pokemon'] = None
            # print('\nAlive pokemon:' + str(game['my_pokemon']))
            if game['my_pokemon'] == 0:
                game['active'] = False #GAME IS OVER
                break
        
        # get updates
        print('POKEMON: ' + str(active_pokemon_new))

        #THIS EXISTS TO ONLY MANUALLY SWITCH WHILE TESTING
        print('\nCHOOSE SWITCH\n')

    print('\nMAKE MOVE\n')
    # time.sleep(20)
    # print('\nMOVE OVER\n')

    state = {}
    state['must_attack'] = must_attack
    state['must_switch'] = must_switch
    state['state'] = gen_state.generateSuperState(active_pokemon,active_moves,my_pokemon,opp_pokemon,game)
    next_superstates.append(state)
    is_done.append(False)

    #GENERATE REWARDS
    reward = gen_reward.genReward(superstates[-1]['state'],state['state'],game)
    rewards.append(reward)

    if len(superstates)%3 == 0: # CALCULATE LOSS AND CHANGE NETWORK EVERY THREE TURNS
        loss = brains.compute_loss(superstates[-1:-4],pokemon_actions[-1:-4],rewards[-1:-4],is_done[-1:-4],next_superstates[-1:-4],agent,target_network,device)
        loss.backward()

    superstates.append(state)

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

# div class controls text Waiting for opponent...
# button name selectMove text Attack
# button name selectSwitch text Switch (After faint or switch)
#   check if active pokemon has fainted and update reward
#   switch pokemon


