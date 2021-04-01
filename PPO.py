import torch
from torch.distributions.categorical import Categorical
import torch.optim as optim
import torch.nn as nn
from NeuralNet import NeuralNet
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler

from config import config

class PPO:
    def __init__(self, batch_size, number_mini_batches, epochs, state_size, action_size, hidden_size, clip_param, device) -> None:
        self.batch_size = batch_size
        self.num_mini_batches = number_mini_batches
        self.epochs = epochs
        self.state_size = state_size
        self.action_size = action_size
        self.hidden_size = hidden_size
        self.clip_param = clip_param
        self.device = device


        self.states = torch.zeros(self.batch_size, self.state_size, device=self.device)
        self.actions = torch.zeros(self.batch_size, 1, device=self.device)
        self.rewards = torch.zeros(self.batch_size, 1, device=self.device)
        self.values = torch.zeros(self.batch_size, 1, device=self.device)
        self.log_prob_actions = torch.zeros(self.batch_size,1, device=self.device)
        self.dones = torch.zeros(self.batch_size, 1, device=self.device)

        self.a2c = NeuralNet(self.state_size, self.action_size, self.hidden_size)
        self.optimiser = optim.Adam(self.nn.parameters(), lr=1e-4)

        self.value_loss_coef = config['value_loss_coef']
        self.entropy_coef = config['entropy_coeff']
        self.max_grad_norm = config['max_grad_norm'] ## NOT USED
        
        self.a2c.to(self.device)

    def insert_state(self, state, step):
        self.states[step].copy_(state)

    def insert_action(self, action, step):
        self.actions[step].copy_(action)

    def insert_reward(self, reward, step):
        self.rewards[step].copy_(reward)

    def insert_value(self, value, step):
        self.values[step].copy_(value)

    def insert_log_prob_action(self, prob, step):
        self.log_prob_actions[step].copy_(prob)

    def insert_done(self, done, step):
        self.dones[step].copy_(done) 

    def calculate_returns(self):
        # TODO: CALCULATE RETURNS IN REWARDS ITSELF
        pass

    def update(self):
        self.calculate_returns()
        advantages = self.rewards[:-1] - self.values[:-1]

        data = self.data_generator(advantages)

        for epoch in range(self.epochs):

            total_value_loss = 0.0
            total_policy_loss = 0.0

            for sample in data:
                states_batch, actions_batch, values_batch, rewards_batch, \
                    dones_batch, old_action_log_probs_batch, adv_targ = sample

                values, action_log_probs, entropy = self.evaluate(states_batch, actions_batch)

                ratio = torch.exp(action_log_probs - old_action_log_probs_batch)
                surr1 = ratio * adv_targ
                surr2 = torch.clamp(ratio, 1 - self.clip_param, 1 + self.clip_param) * adv_targ

                policy_loss = -torch.min(surr1, surr2).mean() 

                value_loss = 0.5 * (rewards_batch - values).pow(2).mean()

                self.optimiser.zero_grad()
                (value_loss * self.value_loss_coef + policy_loss - entropy * self.entropy_coef).backwards()

                self.optimiser.step()

                total_value_loss += value_loss.item()
                total_policy_loss += policy_loss.item()

        num_updates = self.epochs * self.num_mini_batches
        
        total_policy_loss /= num_updates
        total_value_loss /= num_updates

        return total_policy_loss, total_value_loss

    def data_generator(self, advantages):
        mini_batch_size = self.batch_size // self.num_mini_batches

        sampler = BatchSampler(SubsetRandomSampler(range(self.batch_size)), mini_batch_size, drop_last=True)

        for indices in sampler:
            states_batch = self.states[:-1].view(-1, self.state_size)[indices]
            actions_batch = self.actions[:-1].view(-1, self.action_size)[indices]
            values_batch = self.values[:-1].view(-1, 1)[indices]
            rewards_batch = self.rewards[:-1].view(-1, 1)[indices]
            dones_batch = self.dones[:-1].view(-1,1)[indices]
            old_action_log_probs_batch = self.log_prob_actions[:-1].view(-1, 1)[indices]

            adv_targ = advantages.view(-1,1)[indices]

            yield states_batch, actions_batch, values_batch, rewards_batch, \
                dones_batch, old_action_log_probs_batch, adv_targ

    def evaluate(self, states_batch, actions_batch):
        actor_output, critic_output = self.a2c(states_batch)

        actor_probs = Categorical(actor_output)
        action_log_probs = actor_probs.log_prob(actions_batch)
        entropy = actor_probs.entropy().mean()

        return critic_output, action_log_probs, entropy


