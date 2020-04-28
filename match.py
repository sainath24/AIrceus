from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

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

# battle_type_button = browser.find_element_by_name('format')
# battle_type_button.click()
# gen4_button = browser.find_elements_by_name('selectFormat')

# for button in gen4_button:
#     # print('\n' + button.get_attribute('value'))
#     if button.get_attribute('value') == 'gen4randombattle':
#         button.click()
#         break

    
# challenge = browser.find_element_by_name('makeChallenge')
# challenge.click()

# get first pokemon
first_pokemon = browser.find_element_by_name('chooseDisabled')


if 'active' in first_pokemon.get_attribute('value').split(','):
    pokemon = {}

    time.sleep(3)

    actions.move_to_element(first_pokemon).perform()

    time.sleep(3)

    stats = browser.find_element_by_class_name('tooltip')
    name_level = stats.find_element_by_xpath('.//h2')
    type_list = name_level.find_elements_by_xpath('.//img')
    name_level = name_level.text.split(' ')

    name = ''
    for i in range(len(name_level) - 1):
        name+= name_level[i] + ' '
    name = name[:len(name)-1] #Name of pokemon
    pokemon['name'] = name
    print('Name:' + name)

    level = int(name_level[-1][1:]) #level
    pokemon['level'] = level
    print('Level:' + str(level))
    type = []
    for t in type_list:
        if t.get_attribute('alt') != 'M' and t.get_attribute('alt') != 'F':
            type.append(t.get_attribute('alt'))

    pokemon['type'] = type
    print('Type:' + str(type))


    stats = stats.find_elements_by_xpath('.//p')
    
    for i in range(len(stats)):
        if i==0: #hp
            hp = float(stats[i].text.split('%')[0][4:])
            pokemon['hp'] = hp
            print('Hp:' + str(hp))
        elif i==1: #ability and item
            ability_item = stats[i].text.split('/')
            ability = ability_item[0].split(':')[1] #ability with spaces
            ability = ability[1:-1] #remove starting and trailing whitespces

            item = ability_item[1].split(':')[1]
            item = item[1:]

            pokemon['ability'] = ability
            pokemon['item'] = item
            print('Ability:' + ability + ' Item:' + item)
        elif i==2: #stats
            s = stats[i].text.split('/')
            atk = int(s[0][4:-1])
            deff = int(s[1][5:-1])
            spa = int(s[2][5:-1])
            spd = int(s[3][5:-1])
            spe = int(s[4][5:])
            stats_list = [atk,deff,spa,spd,spe]

            pokemon['Atk'] = atk
            pokemon['Def'] = deff
            pokemon['SpA'] = spa
            pokemon['SpD'] = spd
            pokemon['Spe'] = spe

            print('Stats: ' + str(stats_list))
            
        elif i==3: #moves
            active_moves = browser.find_elements_by_name('chooseMove')
            moves = []
            for x in active_moves:
                x = x.text.split('\n')
                m = {}
                move = x[0]
                move_type = x[1]
                move_pp = int(x[2].split('/')[0])
                m['move'] = move
                m['move_type'] = move_type
                m['move_pp'] = move_pp
                moves.append(m)
            
            pokemon['moves'] = moves
            print('Moves:' + str(moves))
    pokemon['isActive'] = True
    pokemon['isAlive'] = True
    my_pokemon.append(pokemon)

 
switch_pokemon_list = browser.find_elements_by_name('chooseSwitch')


for i in range(len(switch_pokemon_list)):
    pokemon = {}

    actions.move_to_element(switch_pokemon_list[i]).perform()

    stats = browser.find_element_by_class_name('tooltip')
    name_level = stats.find_element_by_xpath('.//h2')
    type_list = name_level.find_elements_by_xpath('.//img')
    name_level = name_level.text.split(' ')

    name = ''
    for i in range(len(name_level) - 1):
        name+= name_level[i] + ' '
    name = name[:len(name)-1] #Name of pokemon
    pokemon['name'] = name
    print('Name:' + name)

    level = int(name_level[-1][1:]) #level
    pokemon['level'] = level
    print('Level:' + str(level))
    type = []
    for t in type_list:
        if t.get_attribute('alt') != 'M' and t.get_attribute('alt') != 'F':
            type.append(t.get_attribute('alt'))

    pokemon['type'] = type
    print('Type:' + str(type))


    stats = stats.find_elements_by_xpath('.//p')
    
    for i in range(len(stats)):
        if i==0: #hp
            hp = float(stats[i].text.split('%')[0][4:])
            pokemon['hp'] = hp
            print('Hp:' + str(hp))
        elif i==1: #ability and item
            ability_item = stats[i].text.split('/')
            ability = ability_item[0].split(':')[1] #ability with spaces
            ability = ability[1:-1] #remove starting and trailing whitespces

            item = ability_item[1].split(':')[1]
            item = item[1:]

            pokemon['ability'] = ability
            pokemon['item'] = item
            print('Ability:' + ability + ' Item:' + item)
        elif i==2: #stats
            s = stats[i].text.split('/')
            atk = int(s[0][4:-1])
            deff = int(s[1][5:-1])
            spa = int(s[2][5:-1])
            spd = int(s[3][5:-1])
            spe = int(s[4][5:])
            stats_list = [atk,deff,spa,spd,spe]

            pokemon['Atk'] = atk
            pokemon['Def'] = deff
            pokemon['SpA'] = spa
            pokemon['SpD'] = spd
            pokemon['Spe'] = spe

            print('Stats: ' + str(stats_list))
            
        elif i==3: #moves
            
            mov = []
            moves = stats[i].text.split('•')
            moves = moves[1:] #remove starting null
            for i in range(len(moves)):
                m = {}
                if i + 1 != len(moves):
                    moves[i] = moves[i][1:-1]
                else:
                    moves[i] = moves[i][1:]
                m['move'] = moves[i]
                m['move_type'] = None
                m['move_pp'] = None
                mov.append(m)

            pokemon['moves'] = mov

            print('Moves:' + str(moves))
        elif i==4: #modified stats
            print('Stats Modified:' + stats[i].text)
    pokemon['isActive'] = True
    pokemon['isAlive'] = True
    my_pokemon.append(pokemon)


print('My_Pokemon: ' + str(my_pokemon))

# get active enemy pokemon
pokemon = {}
divs = browser.find_element_by_class_name('tooltips')
divs = divs.find_elements_by_class_name('has-tooltip')
for x in divs:
    if x.get_attribute('data-tooltip') == 'activepokemon|1|0':
        actions.move_to_element(x).perform()
        break


stats = browser.find_element_by_class_name('tooltip')
name_level = stats.find_element_by_xpath('.//h2')
type_list = name_level.find_elements_by_xpath('.//img')
name_level = name_level.text.split(' ')

name = ''
for i in range(len(name_level) - 1):
    name+= name_level[i] + ' '
name = name[:len(name)-1] #Name of pokemon
pokemon['name'] = name
print('Name:' + name)

level = int(name_level[-1][1:]) #level
pokemon['level'] = level
print('Level:' + str(level))
type = []
for t in type_list:
    if t.get_attribute('alt') != 'M' and t.get_attribute('alt') != 'F':
        type.append(t.get_attribute('alt'))

pokemon['type'] = type
print('Type:' + str(type))


stats = stats.find_elements_by_xpath('.//p')

for i in range(len(stats)):
    if i==0: #hp
        hp = float(stats[i].text.split('%')[0][4:])
        pokemon['hp'] = hp
        print('Hp:' + str(hp))
    elif i==2: #stats spe 162 to 205
        s = stats[i].text.split('to')
        from_spe = int(s[0][4:-1])
        to_spe = int(s[1][1:])

        pokemon['from_spe'] = from_spe
        pokemon['to_spe'] = to_spe

        print('Stats: spe ' + str(pokemon['from_spe']) + ' to ' + str(pokemon['to_spe']))

pokemon['Atk'] = 1.0
pokemon['Def'] = 1.0
pokemon['SpA'] = 1.0
pokemon['SpD'] = 1.0
pokemon['Spe'] = 1.0


status = browser.find_element_by_class_name('status')
bads = browser.find_elements_by_class_name('bad')
for bad in bads:
    bad_list = bad.text.split(x)
    bad_amount = float(bad_list[0])
    bad_stat = bad_list[1].split(';')[1]
    pokemon[bad_stat] = bad_amount

goods = browser.find_elements_by_class_name('good')
for good in goods:
    good_list = good.text.split(x)
    good_amount = float(good_list[0])
    good_stat = good_list[1].split(';')[1]
    pokemon[good_stat] = good_amount

opp_pokemon = pokemon
print(opp_pokemon)


