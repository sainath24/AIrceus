from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pokemon_data as pd

my_pokemon = []
opp_pokemon = None



browser = webdriver.Edge('C:/Users/saina/Files/projects/PokemonShowdownAI/edge_driver/msedgedriver.exe')
browser.get('https://play.pokemonshowdown.com/')

actions = ActionChains(browser)

browser.implicitly_wait(60)
login_button = browser.find_element_by_name('login')
login_button.click() #click login button

username = browser.find_element_by_name('username')
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
accept_challenge_button = browser.find_element_by_name('acceptChallenge')
time.sleep(5)
accept_challenge_button.click()


active_pokemon = pd.getActivePokemon(browser,actions)
my_pokemon.append(active_pokemon)

inactive_pokemon = pd.getInactivePokemon(browser,actions)
my_pokemon.extend(inactive_pokemon)

print('My_Pokemon: ' + str(my_pokemon))

opp_pokemon = pd.getActiveEnemyPokemon(browser,actions)
print(opp_pokemon)


