import torch
from torch.distributions.categorical import Categorical
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as f
from NeuralNet import NeuralNet
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler
import wandb
import logging

import os
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

        self.model_path = config['model']
        self.optim_path = config['optim']
        self.max_grad_norm = config['max_grad_norm']


        self.states = torch.zeros(self.batch_size, self.state_size, device=self.device)
        self.actions = torch.zeros(self.batch_size, 1, device=self.device)
        self.rewards = torch.zeros(self.batch_size, 1, device=self.device)
        self.values = torch.zeros(self.batch_size, 1, device=self.device)
        self.returns = torch.zeros(self.batch_size, 1, device= self.device)
        self.log_prob_actions = torch.zeros(self.batch_size,1, device=self.device)
        self.dones = torch.zeros(self.batch_size, 1, device=self.device)
        # self.lstm_hidden = torch.zeros(self.batch_size, 2, 1 ,1, self.hidden_size, device = self.device)
        self.hx = torch.zeros(self.batch_size,self.hidden_size, device = self.device)
        self.cx = torch.zeros(self.batch_size,self.hidden_size, device = self.device)

        self.a2c = NeuralNet(self.state_size, self.action_size, self.hidden_size, self.device)
        self.optimiser = optim.Adam(self.a2c.parameters(), lr=config['optim_lr'])

        self.value_loss_coef = config['value_loss_coef']
        self.entropy_coef = config['entropy_coef']
        self.max_grad_norm = config['max_grad_norm'] ## NOT USED
        self.gamma = config['gamma']
        
        self.a2c.to(self.device)
        if config['use_wandb']:
            wandb.watch(self.a2c)
        
        self.load()

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
    
    def insert_lstm_hidden(self, lstm_hidden, step):
        self.hx[step].copy_(lstm_hidden[0].detach().squeeze())
        self.cx[step].copy_(lstm_hidden[1].detach().squeeze())
        # self.lstm_hidden[step].copy_(lstm_hidden)
    
    def load(self):
        if os.path.isfile(self.model_path):
            print('\n\nMODEL LOADED')
            self.a2c.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.a2c.reset_lstm_hidden_states()

        if os.path.isfile(self.optim_path):
            print('\n\nOPTIMIZER LOADED')
            self.optimiser.load_state_dict(torch.load(self.optim_path, map_location=self.device))
    
    def checkpoint(self):
        torch.save(self.a2c.state_dict(), self.model_path)
        torch.save(self.optimiser.state_dict(), self.optim_path)

    def calculate_returns(self):
        # TODO: IMPLEMENT GAE
        self.returns[-1] = self.values[-1]
        for i in reversed(range(self.rewards.size(0) - 1)):
            self.returns[i] = self.rewards[i] + (1 - self.dones[i]) * self.gamma * self.returns[i+1] 

    def update(self):
        self.calculate_returns()
        advantages = self.returns[:-1] - self.values[:-1]
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-5)

        total_value_loss = 0.0
        total_policy_loss = 0.0

        for epoch in range(self.epochs):
            data = self.data_generator(advantages)
            for sample in data:
                lstm_hidden_batch, states_batch, actions_batch, values_batch, rewards_batch, \
                    dones_batch, old_action_log_probs_batch, adv_targ = sample

                values, action_log_probs, entropy = self.evaluate(lstm_hidden_batch, states_batch, actions_batch)

                ratio = torch.exp(action_log_probs - old_action_log_probs_batch.detach())
                surr1 = ratio * adv_targ.detach()
                surr2 = torch.clamp(ratio, 1 - self.clip_param, 1 + self.clip_param) * adv_targ.detach()

                policy_loss = -torch.min(surr1, surr2).mean() 

                value_loss = 0.5 * (rewards_batch - values).pow(2).mean()

                self.optimiser.zero_grad()
                (value_loss * self.value_loss_coef + policy_loss - entropy * self.entropy_coef).backward()

                nn.utils.clip_grad_norm_(self.a2c.parameters(), self.max_grad_norm)
                self.optimiser.step()

                total_value_loss += value_loss.item()
                total_policy_loss += policy_loss.item()

        num_updates = self.epochs * self.num_mini_batches
        
        total_policy_loss /= num_updates
        total_value_loss /= num_updates

        logging.info('MODEL UPDATED, policy_loss: ' + str(total_policy_loss) + ' value_loss: ' + str(total_value_loss))

        self.post_update()
        self.checkpoint()

        return total_policy_loss, total_value_loss

    def data_generator(self, advantages):
        mini_batch_size = self.batch_size // self.num_mini_batches

        sampler = BatchSampler(SubsetRandomSampler(range(self.batch_size - 1)), mini_batch_size, drop_last=True)

        for indices in sampler:
            states_batch = self.states[:-1].view(-1, self.state_size)[indices]
            actions_batch = self.actions[:-1].view(-1, 1)[indices]
            values_batch = self.values[:-1].view(-1, 1)[indices]
            rewards_batch = self.rewards[:-1].view(-1, 1)[indices]
            dones_batch = self.dones[:-1].view(-1,1)[indices]
            old_action_log_probs_batch = self.log_prob_actions[:-1].view(-1, 1)[indices]
            # lstm_hidden_batch = self.lstm_hidden[:-1].view(-1, 1, mini_batch_size, self.lstm_hidden.size(-1))[indices]
            # lstm_hidden_batch = self.lstm_hidden[:-1][indices]
            hx_batch = self.hx[:-1].view(-1, self.hidden_size)[indices].unsqueeze(0)
            cx_batch = self.cx[:-1].view(-1, self.hidden_size)[indices].unsqueeze(0)
            lstm_hidden_batch = (hx_batch, cx_batch)

            adv_targ = advantages.view(-1,1)[indices]

            yield lstm_hidden_batch, states_batch, actions_batch, values_batch, rewards_batch, \
                dones_batch, old_action_log_probs_batch, adv_targ

    def evaluate(self, lstm_hidden_batch, states_batch, actions_batch):
        actor_output, critic_output, lstm_hidden = self.a2c(states_batch, lstm_hidden_batch)
        
        actor_output = f.softmax(actor_output, dim = -1)

        actor_probs = Categorical(actor_output)
        action_log_probs = actor_probs.log_prob(actions_batch)
        entropy = actor_probs.entropy().mean()

        return critic_output, action_log_probs, entropy
    
    def post_update(self):
        self.states[0].copy_(self.states[-1])
        self.actions[0].copy_(self.actions[-1])
        self.rewards[0].copy_(self.rewards[-1])
        self.values[0].copy_(self.values[-1])
        self.log_prob_actions[0].copy_(self.log_prob_actions[-1])
        self.dones[0].copy_(self.dones[-1])
        # self.lstm_hidden[0].copy_(self.lstm_hidden[-1])
        self.hx[0].copy_(self.hx[-1])
        self.cx[0].copy_(self.cx[-1])

        


