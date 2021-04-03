import torch
import torch.nn as nn
import torch.nn.functional as f
import torch.optim as optim
from torch.distributions import Categorical
from PPO import PPO
from config import config
import state_tools
import logging
import reward_tools


class Brain:
    def __init__(self, player_identifier, train = True) -> None:
        self.player_identifier = player_identifier
        self.train = train 
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.batch_size = config['batch_size']

        self.algo = None
        if config['algorithm'] == 'PPO':
            self.algo = PPO(config['batch_size'], config['num_mini_batches'], config['epochs'], \
                config['state_size'], config['action_size'], config['hidden_size'], config['clip_param'],self.device)


    def update_memory(self, action, actor_probs, critic_value, state, step):
        if (step + 1) % self.batch_size != 0:
            log_prob_action = actor_probs.log_prob(action)

            self.algo.insert_state(state, step)
            self.algo.insert_action(action, step)
            self.algo.insert_log_prob_action(log_prob_action, step)
            self.algo.insert_value(critic_value, step)
            self.algo.insert_done(torch.tensor(0.0, dtype=torch.float, device=self.device), step)

        self.update(step)

    def compute_rewards(self, state, step, game):
        # TODO: COMPUTE ACTUAL REWARDS
        reward = reward_tools.get_reward(state, game)
        self.algo.insert_reward(reward, step)
        

    def get_action(self, game, step, must_switch = False):
        state, invalid_actions = self.create_state(game)
        # print('\nSTATE LENGTH: ', state.size())
        # print('\nSTATE: ', state)
        actor_values, critic_values = self.algo.a2c(state)
        # logging.debug('ACTION PROBS BEFORE MASK: ' + str(self.player_identifier) + ' ' + str(actor_values))
        
        # INVALID ACTION MASKING
        for i in range(len(invalid_actions)):
            if invalid_actions[i] == 1.0 or (must_switch and i < 4): # ACTION IS INVALID
                actor_values[i] = -1e8
        
        # logging.debug('INVALID ACTIONS MASK: ' + str(self.player_identifier) + ' ' + str(invalid_actions))
        actor_values = f.softmax(actor_values, dim = -1)
        # logging.debug('ACTION PROBS AFTER MASK: ' + str(self.player_identifier) + ' ' + str(actor_values))

        actor_probs = Categorical(actor_values)
        action = actor_probs.sample()

        if self.train:
            self.update_memory(action, actor_probs, critic_values, state, step)
            if step > 0:
                self.compute_rewards(state, step-1, game)
                # TODO: COMPUTE REWARDS AND APPEND AT STEP -1
        
        return action.item()

    def create_state(self, game):
        state = state_tools.get_state(game, self.player_identifier)
        invalid_actions = state_tools.get_invalid_actions(game, self.player_identifier)

        return state, invalid_actions

    def update(self, step):
        if (step + 1) % self.batch_size == 0: # TIME TO UPDATE
            policy_loss, value_loss = self.algo.update()
            # TODO: wandb log these

    def game_over(self, game, step):
        # TODO: COMPUTE LAST REWARDS AND APPEND AT STEP -1
        state, invalid_actions = self.create_state(game)
        # if self.train and (step + 1) % self.batch_size != 0:
        if step>0:
            self.algo.insert_done(torch.tensor(1.0, dtype=torch.float, device=self.device), step-1)
            self.compute_rewards(state, step -1, game)

        self.update(step)

