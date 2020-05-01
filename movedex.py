import pokebase as pb

stat_lookup = {
    'defense' : 'Def',
    'attack' : 'Atk',
    'special-attack' : 'SpA',
    'special-defense' : 'SpD',
    'speed' : 'Spe'
}


def getMoveDeets(move):

    

    stats = {
        'Atk' : 0,
        'Def' : 0,
        'SpA' : 0,
        'SpD' : 0,
        'Spe' : 0
    }
    move = move.lower().replace(' ','-')
    if 'hidden-power' in move:
        move = 'hidden-power'
    print('\nMOVEDEX REQUEST:' + move)
    move = pb.move(move)

    accuracy = move.accuracy
    if accuracy == None:
        accuracy = 100
    
    power = move.power
    if power == None:
        power = 0
    
    pp = move.pp
    
    stat_changes = move.stat_changes

    if len(stat_changes) > 0:
        for change in stat_changes:
            # print(stat_lookup['attack'])
            stats[stat_lookup[str(change.stat)]] = change.change
    # print(stat_changes)

    move_type = str(move.type)
    
    return accuracy,power,pp,move_type,stats['Atk'],stats['Def'],stats['SpA'],stats['SpD'],stats['Spe']
