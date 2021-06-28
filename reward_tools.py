import torch
# import logging

def get_reward(new_state, game, enemy_alive):
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
    new_enemy_alive = [1 if enemy_state[i]>0 else 0 for i in range(0,enemy_state.size(0),62)]
    # print(f'New enemy alive: {new_enemy_alive}')

    reward = sum([a-b for a,b in zip(enemy_alive, new_enemy_alive)]) * 0.5

    # agent_sum = agent_state.sum()
    # enemy_sum = enemy_state.sum()

    # reward = ((agent_weight*agent_sum) - (enemy_weight*enemy_sum)).item()
    if game.tie: # ADD BONUS
        # reward += tie_bonus
        reward = 0.5
        # reward = torch.clamp(torch.tensor(reward), 0.0, 1.0)
        # return reward
        # logging.debug('RECEIVE TIE BONUS')
    elif game.win == 'p1': # AGENT WON
        # logging.debug('RECEIVE WIN BONUS')
        # reward += win_bonus
        reward = 1
        # reward = torch.clamp(torch.tensor(reward), 0.0, 1.0)
        # return reward
    elif game.win == 'p2': # AGENT LOST
        # logging.debug('RECEIVE LOSE BONUS')
        # reward += lose_bonus
        reward = 0
        # reward = torch.clamp(torch.tensor(reward), 0.0, 1.0)
        # return reward
    
    # minimum = -int(new_state.size()[0]/2)
    # maximum = int(new_state.size()[0]/2)
    
    # reward = torch.clamp(torch.tensor(reward), minimum, maximum)
    # reward = (reward - minimum)/(maximum - minimum)

    # logging.debug('REWARD:' + str(reward))
    # print(f'reward: {reward}')
    return torch.tensor(reward, dtype = torch.float), new_enemy_alive
