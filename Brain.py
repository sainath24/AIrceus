import torch
import torch.nn as nn
import torch.nn.functional as f
import torch.optim as optim
from torch.distributions import Categorical
from PPO import PPO
from config import config


class Brain:
    def __init__(self, train = True) -> None:
        self.train = train 
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.algo = None
        if config['algorithm'] == 'PPO':
            self.algo = PPO(config['batch_size'], config['num_mini_batches'], config['epochs'], \
                config['state_size'], config['action_size'], config['hidden_size'], config['clip_param'],self.device)


    def update_memory(self, action, actor_probs, critic_value, state, step):
        log_prob_action = actor_probs.log_prob(action)

        self.algo.insert_state(state, step)
        self.algo.insert_action(action, step)
        self.algo.insert_log_prob_action(log_prob_action)
        self.algo.insert_value(action, critic_value)
        self.algo.insert_done(0, step)

        self.update(step)
        

    def get_action(self, game, step):
        state, invalid_actions = self.create_state(game)
        state = torch.tensor(state, dtype=torch.float, device=self.device)
        actor_values, critic_values = self.PPO.a2c(state)

        # TODO: use invalid_actions to mask invalid actions and choose
        actor_probs = Categorical(actor_values)
        action = actor_probs.sample()

        if self.train:
            self.update_memory(action, actor_probs, critic_values, state, step)

        # TODO: COMPUTE REWARDS AND APPEND AT STEP -1

        return action.item()

    
    def create_state(self, game):
        state = None

        return state

    def update(self, step):
        if step + 1 % config['batch_size'] == 0: # TIME TO UPDATE
            policy_loss, value_loss = self.algo.update()
            # TODO: wandb log these

    def game_over(self, game, step):
        # TODO: COMPUTE LAST REWARDS AND APPEND AT STEP -1
        self.algo.insert_done(1, step-1)

        self.update(step)

