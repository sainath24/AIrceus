# THIS FILE RETURNS MULTIPLIERS FOR TYPES
# HAS 4 MAIN LISTS - SUPER EFFECTIVE, NORMAL, WEAK, NO EFFECT
#
#  
import typedex

EFFECTIVE_MUL = 2
NORMAL_MUL = 1
WEAK_MUL = 0.5
NO_EFFECT_MUL = 0

data = {
    'normal': {
        'effective':[],
        # 'normal':['normal','fighting','flying','poison','ground','bug','fire','water','grass','electric','psychic','ice','dragon','dark','fairy'],
        'weak':['rock','steel'],
        'no_effect':['ghost']
    },
    'fighting': {
        'effective':['normal','rock','steel','dark','ice'],
        # 'normal':[],
        'weak':['flying','poison','psychic','bug','fairy'],
        'no_effect':['ghost']
    },
    'flying': {
        'effective':['fighting','bug','grass'],
        # 'normal':[],
        'weak':['flying','poison','bug','psychic','fairy'],
        'no_effect':[]
    },
    'poison': {
        'effective':['grass','fairy'],
        # 'normal':[],
        'weak':['posion','ground','rock','ghost'],
        'no_effect':['steel']
    },
    'ground': {
        'effective':['fire','electric','posion','rock','steel'],
        # 'normal':[],
        'weak':['grass','bug'],
        'no_effect':['flying']
    },
    'rock': {
        'effective':['fire','ice','flying','bug'],
        # 'normal':[],
        'weak':['fighting','ground','steel'],
        'no_effect':[]
    },
    'bug': {
        'effective':['grass','psychic','dark'],
        # 'normal':[],
        'weak':['fire','fighting','poison','flying','ghost','steel','fairy'],
        'no_effect':[]
    },
    'ghost': {
        'effective':['psychic','ghost'],
        # 'normal':[],
        'weak':['dark'],
        'no_effect':['normal']
    },
    'steel': {
        'effective':['ice','rock','fairy'],
        # 'normal':[],
        'weak':['fire','water','electric','steel'],
        'no_effect':[]
    },
    'fire': {
        'effective':['grass','ice','bug','steel'],
        # 'normal':[],
        'weak':['fire','water','rock','dragon'],
        'no_effect':[]
    },
    'water': {
        'effective':['fire','ground','rock'],
        # 'normal':[],
        'weak':['water','grass','dragon'],
        'no_effect':[]
    },
    'grass': {
        'effective':['water','ground','rock'],
        # 'normal':[],
        'weak':['fire','grass','posion','flying','bug','dragon','steel'],
        'no_effect':[]
    },
    'electric': {
        'effective':['water','flying'],
        # 'normal':[],
        'weak':['electric','grass','dragon'],
        'no_effect':['ground']
    },
    'psychic': {
        'effective':['fighting','poison'],
        # 'normal':[],
        'weak':['psychic','steel'],
        'no_effect':['dark']
    },
    'ice': {
        'effective':['grass','ground','flying','dragon'],
        # 'normal':[],
        'weak':['fire','water','ice','stee'],
        'no_effect':[]
    },
    'dragon': {
        'effective':['dragon'],
        # 'normal':[],
        'weak':['steel'],
        'no_effect':['fairy']
    },
    'dark': {
        'effective':['psychic','ghost'],
        # 'normal':[],
        'weak':['fighting','dark','fairy'],
        'no_effect':[]
    },
    'fairy': {
        'effective':['fighting','dragon','dark'],
        # 'normal':[],
        'weak':['fire','poison','steel'],
        'no_effect':[]
    }
}

def getMultiplier(type1, type2):
    t1 = typedex.getTypeKey(type1)
    t2 = typedex.getTypeKey(type2)

    t1_data = data[t1]
    if t2 in t1_data['effective']:
        return EFFECTIVE_MUL
    elif t2 in t1_data['weak']:
        return WEAK_MUL
    elif t2 in t1_data['no_effect']:
        return NO_EFFECT_MUL
    else:
        return NORMAL_MUL

    return NORMAL_MUL