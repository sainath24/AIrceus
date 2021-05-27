import torch
from torch.distributions.categorical import Categorical
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as f
from NeuralNet import NeuralNet
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler
import wandb
# import logging

import os
from config import config

class PPO:
    def __init__(self, batch_size, epochs, state_size, action_size, hidden_size, clip_param, device) -> None:
        self.batch_size = batch_size
        self.epochs = epochs
        self.state_size = state_size
        self.action_size = action_size
        self.hidden_size = hidden_size
        self.lstm_size = config['lstm_size']
        self.clip_param = clip_param
        self.device = device

        self.model_path = config['model']
        self.optim_path = config['optim']
        self.max_grad_norm = config['max_grad_norm']

        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.returns = []
        self.log_prob_actions = []
        self.dones = []
        self.hx = []
        self.cx = []

        self.a2c = NeuralNet(self.state_size, self.action_size, self.hidden_size, self.lstm_size, self.device)
        self.optimiser = optim.Adam(self.a2c.parameters(), lr=config['optim_lr'])

        self.gamma = config['gamma']
        
        self.a2c.to(self.device)
        
        self.load()

    def insert_state(self, state):
        self.states.append(state.detach())

    def insert_action(self, action):
        self.actions.append(action.detach())

    def insert_reward(self, reward):
        self.rewards.append(reward.detach())

    def insert_value(self, value):
        self.values.append(value.detach())

    def insert_log_prob_action(self, prob):
        self.log_prob_actions.append(prob.detach())

    def insert_done(self, done):
        self.dones.append(done.detach())
    
    def insert_lstm_hidden(self, lstm_hidden):
        self.hx.append(lstm_hidden[0].detach())
        self.cx.append(lstm_hidden[1].detach())
    
    def load(self):
        if os.path.isfile(self.model_path):
            print('\nMODEL LOADED')
            self.a2c.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.a2c.reset_lstm_hidden_states()

        if os.path.isfile(self.optim_path):
            print('\nOPTIMIZER LOADED')
            self.optimiser.load_state_dict(torch.load(self.optim_path, map_location=self.device))

    def calculate_returns(self):
        # TODO: IMPLEMENT GAE
        self.returns = torch.zeros(len(self.rewards))
        self.returns[-1] = self.rewards[-1]
        for i in reversed(range(len(self.rewards) - 1)):
            self.returns[i] = self.rewards[i] + (1 - self.dones[i]) * self.gamma * self.returns[i+1]

    def send_data(self, rayq):
        # CALCULATE RETURNS
        self.calculate_returns()
        # STACK ALL TENSORS BEFORE SENDING
        self.states = torch.stack((self.states))
        self.actions = torch.stack((self.actions))
        self.values = torch.stack((self.values))
        self.log_prob_actions = torch.stack((self.log_prob_actions))
        self.dones = torch.stack((self.dones))
        self.hx = torch.stack((self.hx))
        self.cx = torch.stack((self.cx))

        # PUT DATA IN A DICT TO SEND
        data = {
            'states': self.states,
            'actions': self.actions,
            'values': self.values,
            'log_prob_actions': self.log_prob_actions,
            'dones': self.dones,
            'returns': self.returns,
            'hx': self.hx,
            'cx': self.cx
        }

        # pipe.send(data)
        rayq.put(data)
        del data

        self.post_update()
    
    def post_update(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.returns = []
        self.log_prob_actions = []
        self.dones = []
        self.hx = []
        self.cx = []

        

        


