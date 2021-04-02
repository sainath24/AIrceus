import torch
import torch.nn as nn
import torch.nn.functional as f
import torch.optim as optim
from torch.distributions import Categorical
from PPO import PPO
from config import config
import state_tools


class Brain:
    def __init__(self, train = True) -> None:
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

    def compute_rewards(self, state, step):
        if step > 0:
            # TODO: COMPUTE ACTUAL REWARDS
            reward = torch.tensor(1.0, dtype=torch.float, device=self.device)
            self.algo.insert_reward(reward, step)
        

    def get_action(self, game, step):
        state, invalid_actions = self.create_state(game)
        # print('\nSTATE LENGTH: ', state.size())
        # print('\nSTATE: ', state)
        actor_values, critic_values = self.algo.a2c(state)

        # TODO: use invalid_actions to mask invalid actions and choose
        actor_probs = Categorical(actor_values)
        action = actor_probs.sample()

        if self.train:
            self.update_memory(action, actor_probs, critic_values, state, step)

        # TODO: COMPUTE REWARDS AND APPEND AT STEP -1
        if (step + 1) % self.batch_size != 0:
            self.compute_rewards(state, step-1)

        return action.item()

    def create_state(self, game):
        state = state_tools.get_state(game)
        invalid_actions = state_tools.get_invalid_actions(game)

        return state, invalid_actions

    def update(self, step):
        if (step + 1) % self.batch_size == 0: # TIME TO UPDATE
            policy_loss, value_loss = self.algo.update()
            # TODO: wandb log these

    def game_over(self, game, step):
        # TODO: COMPUTE LAST REWARDS AND APPEND AT STEP -1
        state, invalid_actions = self.create_state(game)
        if (step + 1) % self.batch_size != 0:
            self.algo.insert_done(torch.tensor(1.0, dtype=torch.float, device=self.device), step-1)
            self.compute_rewards(state, step -1)

        self.update(step)

