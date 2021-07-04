status = {
    'psn':13.0,
    'tox':13.0,
    'brn':11.0,
    'par':7.0,
    'slp':5.0,
    'frz':3.0,
    'confusion':2.0,
    'fnt': 0.0,
}

def status_score(status_list):
    ''' Input: List of statuses
        Output: Float score for the combination of statuses
    '''
    out = 1.0
    for s in status_list:
        out*= status[s]
    return out/10
