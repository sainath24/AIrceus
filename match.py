from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pokemon_data as pd

my_pokemon = []
enemy_pokemon = []
opp_pokemon = None

browser = webdriver.Edge('C:/Users/saina/Files/projects/PokemonShowdownAI/edge_driver/msedgedriver.exe')
browser.get('https://play.pokemonshowdown.com/')

actions = ActionChains(browser)

login_button = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.NAME, "login")))#browser.find_element_by_name('login')
login_button.click() #click login button

username = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, "username")))#browser.find_element_by_name('username')
username.send_keys('saroja')
username.send_keys(Keys.ENTER) #login with a name

# time.sleep(5)

# battle_type_button = browser.find_element_by_name('format')
# battle_type_button.click()
# gen4_button = browser.find_elements_by_name('selectFormat')

# for button in gen4_button:
#     # print('\n' + button.get_attribute('value'))
#     if button.get_attribute('value') == 'gen4randombattle':
#         button.click()
#         break

time.sleep(2)

# start battle with random opponet
# battle_button = browser.find_element_by_name('search')
# battle_button.click() #iniate gen 4 random battle

# challenge known username
# find_user_button = browser.find_element_by_name('finduser')
# find_user_button.click()
# username = browser.find_element_by_name('data')
# username.send_keys('saroja2')
# username.send_keys(Keys.ENTER)
time.sleep(10)
accept_challenge_button = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.NAME, "acceptChallenge")))#browser.find_element_by_name('acceptChallenge')
time.sleep(5)
accept_challenge_button.click()


active_pokemon = pd.getActivePokemon(browser)
my_pokemon.append(active_pokemon)

inactive_pokemon = pd.getInactivePokemon(browser)
my_pokemon.extend(inactive_pokemon)

print('My_Pokemon: ' + str(my_pokemon))

opp_pokemon = pd.getActiveEnemyPokemon(browser)
print(opp_pokemon)

game = {
    'active' : True,
    'forfeit' : False,
    'active_pokemon': 0,
    'active_pokemon_name': active_pokemon['name'],
    'enemy_active_pokemon_name': opp_pokemon['name'],
    'enemy_pokemon': 6,
    'my_pokemon': 6
}

while game['active']:

    if game['my_pokemon'] == 0 or game['enemy_pokemon'] == 0:
        game['active'] = False
        break

    opp_pokemon_new = pd.getActiveEnemyPokemon(browser)
    print('Got enemy opp_pokemon_new')

    if opp_pokemon_new == None or opp_pokemon_new['name'] != opp_pokemon['name']:
        enemy_pokemon,enemyFaintCount = pd.getEnemyPokemonList(browser,actions)
        game['enemy_pokemon'] = 6 - enemyFaintCount
        if game['enemy_pokemon'] == 0:
            game['active'] = False
            break
        opp_pokemon = opp_pokemon_new
        game['enemy_active_pokemon_name'] = opp_pokemon['name']

    
    # TODO:make moves, get updates
    # network makes a 
    print('\nmake move\n')
    time.sleep(40)
    print('\nMove over\n')
    
    # explicitly wait for 
    move_switch = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.NAME, "selectMove")) or EC.presence_of_element_located((By.NAME,"selectSwitch")))#browser.find_element_by_name('selectMove') or browser.find_element_by_name('selectSwitch')
    if move_switch.text == 'Attack': #choose next attack
        print('\nIn attack\n')
        #TODO: get updates, calculate reward
        active_pokemon_new = pd.getActivePokemon(browser)
        # calculate reward
        my_pokemon[game['active_pokemon']] = active_pokemon_new
        print('Active Pokemon:' + str(active_pokemon))
        # TODO: network decides to either switch or attack
        # click based on network, if switch use pokemon['element']
    
    elif move_switch.text == 'Switch': #choose pokemon to switch to
        # check if active pokemon is dead
        print('\nIn Switch\n')
        active_pokemon_new = pd.getActivePokemon(browser)
        if active_pokemon_new['isAlive'] == False: #pokemon has fainted
            # TODO: calculate reward
            # remove active pokemon from list
            my_pokemon.remove(game['active_pokemon'])
            game['my_pokemon']-=1
            if game['my_pokemon'] == 0:
                game['active'] = False
                break
        
        # get updates
        print('POKEMON: ' + active_pokemon_new)
        # TODO: calculate reward from active_pokemon and active_pokemon_new 
        # choose pokemon to switch
        # TODO: neural network chooses switch, switch with pokemon['element']
        print('\nchoose switch\n')
        time.sleep(30)
        print('\nSwitch chosen\n')

if game['active'] == False:
    if game['my_pokemon'] == 0 and game['enemy_pokemon'] > 0:
        print('You lost')
        # TODO: decrease rewards
    
    elif game['my_pokemon'] > 0 and game['enemy_pokemon'] == 0:
        print('You win')
        # TODO: increse reward
    else:
        print('Draw')
        # TODO: manipulate reward, increase by a little

else:
    print('Broke because of some error') 
    # TODO: handle later

# div class controls text Waiting for opponent...
# button name selectMove text Attack
# button name selectSwitch text Switch (After faint or switch)
#   check if active pokemon has fainted and update reward
#   switch pokemon


