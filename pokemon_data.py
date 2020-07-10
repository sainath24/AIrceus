from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import movedex
import typedex

def getActivePokemon(browser):

    start = time.time()

    actions = ActionChains(browser)
    active_pokemon = None
    active_pokemon = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.NAME, "chooseDisabled")))#browser.find_element_by_name('chooseDisabled')

    # print('\nActive Pokemon text:' + active_pokemon.text)

    if 'active' in active_pokemon.get_attribute('value').split(','):
        pokemon = {}

        actions.move_to_element(active_pokemon).perform()

        pokemon['element'] = active_pokemon

        # time.sleep(3)

        stats = browser.find_element_by_class_name('tooltip')
        name_level = stats.find_element_by_xpath('.//h2')
        type_list = name_level.find_elements_by_xpath('.//img')
        name_level = name_level.text.split(' ')

        name = ''
        print('\nNAME_LEVEL', str(name_level))
        # for i in range(len(name_level) - 1):
        #     name+= name_level[i] + ' '
        # name = name[:len(name)-1] #Name of pokemon
        pokemon['name'] = name_level[0]
        print('\nNAME', pokemon['name'])
        # print('Name:' + name)

        # level = int(name_level[-1][1:]) #level
        level = 0
        for j in range(1, len(name_level)):
            if name_level[j][0] == 'L' and (len(name_level[j]) == 3 or len(name_level[j]) == 4 ):
                level = int(name_level[j][1:])
        # print('\nLEVEL', level)
        pokemon['level'] = level
        # print('Level:' + str(level))
        p_type = []
        for t in type_list:
            if t.get_attribute('alt') != 'M' and t.get_attribute('alt') != 'F':
                p_type.append(typedex.getTypeOhe(t.get_attribute('alt')))

        pokemon['type'] = p_type
        # print('Type:' + str(p_type))


        stats = stats.find_elements_by_xpath('.//p')
        
        for i in range(len(stats)):
            if i==0: #hp
                hp = float(stats[i].text.split('%')[0][4:])
                pokemon['hp'] = hp
                # print('Hp:' + str(hp))
            elif i==1: #ability and item
                ability_item = stats[i].text.split('/')
                ability = ability_item[0].split(':')[1] #ability with spaces
                ability = ability[1:-1] #remove starting and trailing whitespces

                item = ability_item[1].split(':')[1]
                item = item[1:]

                pokemon['ability'] = ability
                pokemon['item'] = item
                # print('Ability:' + ability + ' Item:' + item)
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

                # print('Stats: ' + str(stats_list))
                
            elif i==3: #moves

                move_start = time.time()

                active_moves = browser.find_elements_by_name('chooseMove')
                moves = []
                for x in active_moves:

                    single_move_start = time.time()

                    element = x
                    x = x.text.split('\n')
                    m = {}
                    m['element'] = element
                    move = x[0]
                    # move_type = x[1]
                    pp_div = element.find_element_by_class_name('pp')
                    try:
                        move_pp = int(pp_div.text.split('/')[0])
                    except:
                        move_pp = 10
                    m['move'] = move
                    # call movedex for deets
                    dex_start = time.time()
                    m['accuracy'],m['power'],m['pp'],m['type'],m['Atk'],m['Def'],m['SpA'],m['SpD'],m['Spe'] = movedex.getMoveDeets(move)
                    print('\nMOVE DEX TIME: ', time.time() -  dex_start)
                    # TODO: use type ohe
                    m['type'] = typedex.getTypeOhe(m['type'])
                    m['pp'] = move_pp
                    moves.append(m)

                    print('\nTIME PER MOVE: ', time.time() - single_move_start)
                
                pokemon['moves'] = moves
                print('\nALL MOVES TIME: ', time.time() - move_start)
                # print('Moves:' + str(moves))
        pokemon['isActive'] = True
        pokemon['isAlive'] = True
    
    else:
        return {'isAlive':False}

    print('\nACTIVE POKEMON TIME: ', time.time() - start )
    
    return pokemon

def getInactivePokemon(browser):
    my_pokemon = []
    actions = ActionChains(browser)
    switch_pokemon_list = WebDriverWait(browser, 60).until(EC.presence_of_all_elements_located((By.NAME, "chooseSwitch")))#browser.find_elements_by_name('chooseSwitch')
    for i in range(len(switch_pokemon_list)):
        pokemon = {}

        actions.move_to_element(switch_pokemon_list[i]).perform()
        pokemon['element'] = switch_pokemon_list[i]

        stats = browser.find_element_by_class_name('tooltip')
        name_level = stats.find_element_by_xpath('.//h2')
        type_list = name_level.find_elements_by_xpath('.//img')
        name_level = name_level.text.split(' ')

        # name = ''
        # for i in range(len(name_level) - 1):
        #     name+= name_level[i] + ' '
        # name = name[:len(name)-1] #Name of pokemon
        pokemon['name'] = name_level[0]
        # print('Name:' + name)

        # level = int(name_level[1][1:]) #level
        level = 0
        for j in range(1, len(name_level)):
            # if name_level[j][0] == 'L' and (len(name_level[j]) == 3 or len(name_level[j]) == 4 ):
            #     level = int(name_level[1][1:])
            try:
                level = int(name_level[j][1:])
            except:
                print('\nnot level\n')
        pokemon['level'] = level
        # print('Level:' + str(level))
        p_type = []
        for t in type_list:
            if t.get_attribute('alt') != 'M' and t.get_attribute('alt') != 'F':
                p_type.append(typedex.getTypeOhe(t.get_attribute('alt')))

        pokemon['type'] = p_type
        # print('Type:' + str(p_type))


        stats = stats.find_elements_by_xpath('.//p')
        
        for i in range(len(stats)):
            if i==0: #hp
                hp = float(stats[i].text.split('%')[0][4:])
                pokemon['hp'] = hp
                # print('Hp:' + str(hp))
            elif i==1: #ability and item
                ability_item = stats[i].text.split('/')
                ability = ability_item[0].split(':')[1] #ability with spaces
                ability = ability[1:-1] #remove starting and trailing whitespces

                item = ability_item[1].split(':')[1]
                item = item[1:]

                pokemon['ability'] = ability
                pokemon['item'] = item
                # print('Ability:' + ability + ' Item:' + item)
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

                # print('Stats: ' + str(stats_list))
                
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
                    m['accuracy'],m['power'],m['pp'],m['type'],m['Atk'],m['Def'],m['SpA'],m['SpD'],m['Spe'] = movedex.getMoveDeets(moves[i])

                    m['type'] = typedex.getTypeOhe(m['type'])
                    mov.append(m)

                pokemon['moves'] = mov

                # print('Moves:' + str(moves))
            elif i==4: #modified stats
                print('Stats Modified:' + stats[i].text)
        pokemon['isActive'] = False
        pokemon['isAlive'] = True
        my_pokemon.append(pokemon)
    return my_pokemon

def getActiveEnemyPokemon(browser):
    pokemon = {}
    actions = ActionChains(browser)
    moved = False
    try:
        divs = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "tooltips")))#browser.find_element_by_class_name('tooltips')
    except:
        print('Enemy active pokemon not found')
        return None

    
    divs = divs.find_elements_by_class_name('has-tooltip')
    for x in divs:
        if x.get_attribute('data-tooltip') == 'activepokemon|1|0':

            # GET STATS
            pokemon['Atk'] = 1.0
            pokemon['Def'] = 1.0
            pokemon['SpA'] = 1.0
            pokemon['SpD'] = 1.0
            pokemon['Spe'] = 1.0

            try:
                status = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "status")))
                bads = WebDriverWait(status, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "bad")))
                for bad in bads:
                    bad_list = bad.text.split('×')
                    bad_amount = float(bad_list[0])
                    bad_stat = bad_list[1][1:]
                    print('ENEMY BAD STAT:' + str(bad_stat) + ' ' + str(bad_amount))
                    pokemon[bad_stat] = bad_amount

            except Exception as e:
                print('\nException, no BAD status found for active enemy pokemon\n')

            try:
                status = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "status")))
                goods = WebDriverWait(status, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "good")))
                for good in goods:
                    good_list = good.text.split('×')
                    print(good_list)
                    good_amount = float(good_list[0])
                    good_stat = good_list[1][1:]
                    print('ENEMY GOOD STAT:' + str(good_stat) + ' ' + str(good_amount))
                    pokemon[good_stat] = good_amount

            except Exception as e:
                print(e)
                print('\nException, no GOOD status found for active enemy pokemon\n')


            actions.move_to_element(x).perform()
            moved = True
            break

    if moved == False:
        print('Enemy active pokemon not found')
        return None

    stats = browser.find_elements_by_class_name('tooltip')
    if len(stats) == 0:
        print('\nENEMY POKEMON NOT FOUND\n')
        return None
    stats = stats[0]
    name_level = stats.find_element_by_xpath('.//h2')
    type_list = name_level.find_elements_by_xpath('.//img')
    name_level = name_level.text.split(' ')

    # name = ''
    # for i in range(len(name_level) - 1):
    #     name+= name_level[i] + ' '
    # name = name[:len(name)-1] #Name of pokemon
    pokemon['name'] = name_level[0]
    # print('Name:' + name)
    level = 0
    for j in range(1, len(name_level)):
        if name_level[j][0] == 'L' and (len(name_level[j]) == 3 or len(name_level[j]) == 4 ):
            level = int(name_level[j][1:])
    # level = int(name_level[1][1:]) #level
    pokemon['level'] = level
    # print('Level:' + str(level))
    p_type = []
    for t in type_list:
        if t.get_attribute('alt') != 'M' and t.get_attribute('alt') != 'F':
            p_type.append(typedex.getTypeOhe(t.get_attribute('alt')))

    pokemon['type'] = p_type
    # print('Type:' + str(p_type))

    stats = stats.find_elements_by_xpath('.//p')

    for i in range(len(stats)):
        if i==0: #hp
            hp = float(stats[i].text.split('%')[0][4:])
            pokemon['hp'] = hp
            # print('Hp:' + str(hp))
        elif i==2: #stats spe 162 to 205 or item
                if stats[i].text[0:3] != 'Spe':
                    pass
                else:
                    s = stats[i].text.split('to')
                    from_spe = int(s[0][4:-1])
                    to_spe = s[1][1:]
                    to_spe = int(to_spe.split(' ')[0])

                    pokemon['from_spe'] = from_spe
                    pokemon['to_spe'] = to_spe

                    # print('Stats: spe ' + str(pokemon['from_spe']) + ' to ' + str(pokemon['to_spe']))

        elif i==3: #stats spe 162 to 205
            if stats[i].text[0:3] != 'Spe':
                pass
            else:
                s = stats[i].text.split('to')
                from_spe = int(s[0][4:-1])
                to_spe = s[1][1:]
                to_spe = int(to_spe.split(' ')[0])

                pokemon['from_spe'] = from_spe
                pokemon['to_spe'] = to_spe

                # print('Stats: Spe ' + str(pokemon['from_spe']) + ' to ' + str(pokemon['to_spe']))
        # TODO: maybe get moves of enemy pokemon

    return pokemon

def getEnemyPokemonList(browser):
    enemy_pokemon = []
    actions = ActionChains(browser)
    rightbar = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "rightbar")))#browser.find_element_by_class_name('rightbar')
    team = rightbar.find_elements_by_class_name('picon')

    print('\nENEMY POKEMON LIST COUNT:' + str(len(team)))

    faintedCount = 0
    for p in team:
        if 'pokemonicons-pokeball-sheet' in p.get_attribute('style'):
            continue
        pokemon = {}
        hasFainted = False
        actions.move_to_element(p).perform()
        stats = browser.find_element_by_class_name('tooltip')
        name_level = stats.find_element_by_xpath('.//h2')
        type_list = name_level.find_elements_by_xpath('.//img')
        name_level = name_level.text.split(' ')

        pokemon['element'] = p

        # name = ''
        # for i in range(len(name_level) - 1):
        #     name+= name_level[i] + ' '
        # name = name[:len(name)-1] #Name of pokemon
        pokemon['name'] = name_level[0]
        # print('Name:' + name)

        level = 0
        for j in range(1, len(name_level)):
            if name_level[j][0] == 'L' and (len(name_level[j]) == 3 or len(name_level[j]) == 4 ):
                level = int(name_level[j][1:])
        # level = int(name_level[1][1:]) #level
        pokemon['level'] = level
        # print('Level:' + str(level))
        p_type = []
        for t in type_list:
            if t.get_attribute('alt') != 'M' and t.get_attribute('alt') != 'F':
                p_type.append(typedex.getTypeOhe(t.get_attribute('alt')))

        pokemon['type'] = p_type
        # print('Type:' + str(p_type))

        stats = stats.find_elements_by_xpath('.//p')

        for i in range(len(stats)):
            if i==0: #hp
                if 'fainted' in stats[i].text:
                    print('\nEnemy pokemon fainted: ' + str(pokemon['name']))
                    hasFainted = True
                    faintedCount+=1
                    break
                hp = float(stats[i].text.split('%')[0][4:])
                pokemon['hp'] = hp
                # print('Hp:' + str(hp))
            elif i==2: #stats spe 162 to 205 or item
                if stats[i].text[0:4] == 'Item':
                    pass
                else:
                    s = stats[i].text.split('to')
                    from_spe = int(s[0][4:-1])
                    to_spe = s[1][1:]
                    to_spe = int(to_spe.split(' ')[0])

                    pokemon['from_spe'] = from_spe
                    pokemon['to_spe'] = to_spe

                    # print('Stats: spe ' + str(pokemon['from_spe']) + ' to ' + str(pokemon['to_spe']))

            elif i==3: #stats spe 162 to 205
                if stats[i].text[0:3] != 'spe':
                    pass
                else:
                    s = stats[i].text.split('to')
                    from_spe = int(s[0][4:-1])
                    to_spe = s[1][1:]
                    to_spe = int(to_spe.split(' ')[0])

                    pokemon['from_spe'] = from_spe
                    pokemon['to_spe'] = to_spe

                    # print('Stats: spe ' + str(pokemon['from_spe']) + ' to ' + str(pokemon['to_spe']))

            # TODO: maybe get enemey pokemon moves

        if hasFainted == False:
            pokemon['Atk'] = 1.0
            pokemon['Def'] = 1.0
            pokemon['SpA'] = 1.0
            pokemon['SpD'] = 1.0
            pokemon['Spe'] = 1.0
            
    return enemy_pokemon,faintedCount

def getFaintedPokemonNumber(browser):
    faintCount = 0
    fainted_pokemon = WebDriverWait(browser, 60).until(EC.presence_of_all_elements_located((By.NAME, "chooseDisabled")))#browser.find_element_by_name('chooseDisabled')
    actions = ActionChains(browser)
    # print('\nNon Choosable pokemon:' + str(fainted_pokemon.text))

    for p in fainted_pokemon:
        if 'fainted' in p.get_attribute('value').split(','):
            faintCount+=1

    return faintCount

def getCurrentActiveMoves(browser):

    try:
        active_moves = WebDriverWait(browser,5).until(EC.presence_of_all_elements_located((By.NAME,'chooseMove')))
        moves = []
        for x in active_moves:
            x = x.text.split('\n')
            move = x[0]
            moves.append(move)
        
        return moves
    except:
        return None

def isSwitchPossible(browser):
    try: # if pokemon cannot be switch, switch bar will not be visible, get active pokemon from inbattle sprite
        cannot_switch = WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.CLASS_NAME,"switchmenu")))
        if 'cannot switch' in cannot_switch.text:
            return False
        
        return True
    except:
        return False

def getActiveModifiedStatsAndHpFromSprite(browser):
    actions = ActionChains(browser)
    active_pokemon = None
    
    divs = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "tooltips")))
    divs = divs.find_elements_by_class_name('has-tooltip')
    for x in divs:
        if x.get_attribute('data-tooltip') == 'activepokemon|0|0':
            active_pokemon = x
            break

    actions.move_to_element(active_pokemon).perform()

    stats = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "tooltip")))

    stats = stats.find_elements_by_xpath('.//p')

    atk,deff,spa,spd,spe,hp = 0,0,0,0,0,0

    for i in range(len(stats)):
        if 'HP' in stats[i].text:
            hp = float(stats[i].text.split('%')[0][4:])

        elif 'After stat modifiers:' in stats[i].text:
            x = stats[i+1]
            s = x.text.split('/')
            atk = int(s[0][4:-1])
            deff = int(s[1][5:-1])
            spa = int(s[2][5:-1])
            spd = int(s[3][5:-1])
            spe = int(s[4][5:])
            break
    
    return hp,atk,deff,spa,spd,spe

def getActivePokemonElement(browser):
    actions = ActionChains(browser)
    active_pokemon = None
    pokemon = {}
    active_pokemon = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.NAME, "chooseDisabled")))#browser.find_element_by_name('chooseDisabled')

    if 'active' in active_pokemon.get_attribute('value').split(','):
        actions.move_to_element(active_pokemon).perform()

        stats = browser.find_element_by_class_name('tooltip')
        name_level = stats.find_element_by_xpath('.//h2')
        name_level = name_level.text.split(' ')

        # name = ''
        # for i in range(len(name_level) - 1):
        #     name+= name_level[i] + ' '
        # name = name[:len(name)-1] #Name of pokemon
        pokemon[str(name_level[0])] = active_pokemon
    return pokemon


def getSwitchablePokemonElement(browser,pokemon_name):
    switchable_list = getActivePokemonElement(browser)
    actions = ActionChains(browser)
    switch_pokemon_list = WebDriverWait(browser, 60).until(EC.presence_of_all_elements_located((By.NAME, "chooseSwitch")))#browser.find_elements_by_name('chooseSwitch')
    for i in range(len(switch_pokemon_list)):
        actions.move_to_element(switch_pokemon_list[i]).perform()

        stats = browser.find_element_by_class_name('tooltip')
        name_level = stats.find_element_by_xpath('.//h2')
        name_level = name_level.text.split(' ')

        element = switch_pokemon_list[i]

        # name = ''
        # for j in range(len(name_level) - 1):
        #     name+= name_level[j] + ' '
        # name = name[:len(name)-1] #Name of pokemon
        # switchable_list[str(name_level[0])] = element  

        if str(name_level[0]) == pokemon_name:
            return element

    return None

def getMoveElement(browser, move):
    active_moves = getCurrentActiveMoves(browser)
    moves = browser.find_elements_by_name('chooseMove')
    if move['pp'] == 0 or move['move'] not in active_moves:
        print('\nPOKEMONDATA: MOVE NOT IN LIST:' + str(move['move']))
        return None
    for x in moves:
        element = x
        x = x.text.split('\n')
        if move['move'] == x[0]:
            return element

    return None

def getSwitchElement(browser, pokemon):
    switch_pokemon = getSwitchablePokemonElement(browser,pokemon['name'])
    # print('\nSWITCHABLE POKEMON:' + str(switch_pokemon))
    # print('\nCHOSEN SWITCH: ' + str(pokemon))

    return switch_pokemon

    # if pokemon['name'] in switch_pokemon.keys():
    #     print('\nRETURNING SWITCH ELEMENT\n')
    #     return switch_pokemon[pokemon['name']]
    # return None




    

    
    


