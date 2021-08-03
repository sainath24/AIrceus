field = {
    'spikes': 5.0,
    'stealthrock': 3.0,
    'toxicspikes': 2.0
}

def field_score(field_list):
    ''' Input: List of field conditions
        Output: Float score for the combination of conditions
    '''
    out = 1.0
    for f in field_list:
        out*= field[f]
    return out/10
