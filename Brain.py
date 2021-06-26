import torch
from torch._C import device
import torch.nn as nn
import torch.nn.functional as f
import torch.optim as optim
from torch.distributions import Categorical
from PPO import PPO
from config import config
import state_tools
# import logging
import reward_tools
import wandb
import reward_state_tools


class Brain:
    def __init__(self, player_identifier, train = True) -> None:
        self.player_identifier = player_identifier
        self.train = train 
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.batch_size = config['batch_size']
        self.episode_reward = 0.0
        self.step = 0

        self.enemy_alive = [1] *6

        self.algo = None
        if config['algorithm'] == 'PPO':
            self.algo = PPO(config['batch_size'], config['epochs'], \
                config['state_size'], config['action_size'], config['hidden_size'], config['clip_param'],self.device)


    def update_memory(self, lstm_hidden, action, actor_probs, critic_value, state, critic_state):
        self.algo.insert_value(critic_value)
        log_prob_action = actor_probs.log_prob(action)
        self.algo.insert_state(state)
        self.algo.insert_critic_state(critic_state)
        self.algo.insert_action(action)
        self.algo.insert_log_prob_action(log_prob_action)
        if self.step > 0:
            self.algo.insert_done(torch.tensor(0.0, dtype=torch.float, device=self.device))
        self.algo.insert_lstm_hidden(lstm_hidden)


    def compute_rewards(self, state, game):
        reward, self.enemy_alive = reward_tools.get_reward(state, game, self.enemy_alive)
        # if config['use_wandb']:
        #     wandb.log({'rewards': reward})
        self.episode_reward += reward
        self.algo.insert_reward(reward)
        

    def get_action(self, game, must_switch = False):
        state, invalid_actions = self.create_state(game)
        # state = reward_state_tools.get_state(game, self.player_identifier)
        critic_state = reward_state_tools.get_state(game, self.player_identifier)
        # print('\nSTATE LENGTH: ', state.size())
        # print('\nSTATE: ', state)
        lstm_hidden_to_insert = self.algo.a2c.lstm_hidden#torch.stack(self.algo.a2c.lstm_hidden).detach() # IS A TUPLE OF TENSORS, STACK AS ONE TESNOR IN ORDER TO INSERT INTO REPLAY BUFFER
        state = state.to(self.device)
        with torch.no_grad():
            actor_values, critic_values, _ = self.algo.a2c(state.unsqueeze(0), critic_state.unsqueeze(0))
        # print('ACTION PROBS BEFORE MASK: ' + str(self.player_identifier) + ' ' + str(actor_values))
        # print('MASK:', invalid_actions)
        # INVALID ACTION MASKING
        actor_values_clone = torch.clone(actor_values)
        for i in range(len(invalid_actions)):
            if invalid_actions[i] == 1.0 or (must_switch and i < 4): # ACTION IS INVALID
                actor_values_clone[i] = -1e8
        
        # logging.debug('INVALID ACTIONS MASK: ' + str(self.player_identifier) + ' ' + str(invalid_actions))
        actor_values_clone = f.softmax(actor_values_clone, dim = -1)
        # logging.debug('ACTION PROBS AFTER MASK: ' + str(self.player_identifier) + ' ' + str(actor_values))
        # if self.train:
        # print('action probabilities: ', actor_values_clone)
        actor_probs = Categorical(actor_values_clone)
        action = actor_probs.sample()
        # else:
        # action = torch.argmax(actor_values_clone)
        if self.train:
            if self.step > 0:
                reward_state = reward_state_tools.get_state(game, self.player_identifier)
                self.compute_rewards(reward_state, game)
            self.update_memory(lstm_hidden_to_insert, action, actor_probs, critic_values, state, critic_state)
        
        self.step += 1

        return action.item()

    def create_state(self, game):
        # logging.warning('GAME DICT: ', str(game.get_dict()))
        state = state_tools.get_state(game, self.player_identifier)
        invalid_actions = state_tools.get_invalid_actions(game, self.player_identifier)

        return state, invalid_actions

    def game_over(self, game):
        state, invalid_actions = self.create_state(game)
        self.algo.insert_done(torch.tensor(1.0, dtype=torch.float, device=self.device))
        reward_state = reward_state_tools.get_state(game, self.player_identifier)
        self.compute_rewards(reward_state, game)
        
        if config['use_wandb'] and self.train:
            wandb.log({'episode_rewards': self.episode_reward})
        self.episode_reward = 0
        self.enemy_alive = [1] * 6
        self.step = 0

