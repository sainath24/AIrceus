import torch
import logging

def get_reward(new_state, game):
    # NEW STATE HAS SIZE 840, FIRST 420 is agent pokemon, next 420 is enemy pokemon
    # SINCE STATE HAS VALUES OF RANGE [0,1], max is 420, min is 0
    # MAX REWARD IS 420, MIN REWARD IS -420, normalize using these values
    agent_weight, enemy_weight = 1,1
    tie_bonus = (new_state.size()[0]/2)/4
    win_bonus = (new_state.size()[0]/2)/2
    lose_bonus = -win_bonus
    # logging.debug('WIN BONUS:' + str(win_bonus))
    # logging.debug('LOSE BONUS:' + str(lose_bonus))
    # logging.debug('TIE BONUS:' + str(tie_bonus))
    

    agent_state, enemy_state = torch.split(new_state, int(new_state.size()[0]/2))
    # logging.debug('AGENT STATE SIZE: '+ str(agent_state.size()))
    # logging.debug('ENEMY STATE SIZE: ' +  str(enemy_state.size()))

    agent_sum = agent_state.sum()
    enemy_sum = enemy_state.sum()

    reward = ((agent_weight*agent_sum) - (enemy_weight*enemy_sum)).item()
    if game.tie: # ADD BONUS
        reward += tie_bonus
        # logging.debug('RECEIVE TIE BONUS')
    elif game.win == 'p1': # AGENT WON
        # logging.debug('RECEIVE WIN BONUS')
        reward += win_bonus
    elif game.win == 'p2': # AGENT LOST
        # logging.debug('RECEIVE LOSE BONUS')
        reward += lose_bonus
    
    minimum = -int(new_state.size()[0]/2)
    maximum = int(new_state.size()[0]/2)
    
    reward = torch.clamp(torch.tensor(reward), minimum, maximum)
    reward = (reward - minimum)/(maximum - minimum)

    # logging.debug('REWARD:' + str(reward))
    return reward
