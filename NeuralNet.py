import torch
from torch._C import device
import torch.nn as nn
from config import config

class NeuralNet(nn.Module):
    def __init__(self, state_size, critic_state_size, action_size, lstm_size, device):
        super(NeuralNet, self).__init__()
        self.state_size = state_size
        self.critic_state_size = critic_state_size
        self.action_size = action_size
        self.lstm_size = lstm_size
        self.use_lstm = config['use_lstm']
        self.device = device

        actor_hidden_layers = config['actor_hidden_layers']
        critic_hidden_layers = config['critic_hidden_layers']

        actor = [nn.Linear(self.state_size, actor_hidden_layers[0])]
        actor.append(nn.ReLU())

        for i in range(1, len(actor_hidden_layers)):
            actor.append(nn.Linear(actor_hidden_layers[i-1], actor_hidden_layers[i]))
            actor.append(nn.ReLU())

        critic = [nn.Linear(self.critic_state_size, critic_hidden_layers[0])]
        critic.append(nn.ReLU())

        for i in range(1, len(critic_hidden_layers)):
            critic.append(nn.Linear(critic_hidden_layers[i-1], critic_hidden_layers[i]))
            critic.append(nn.ReLU())
        
        if self.use_lstm:
            self.lstm = nn.LSTM(actor_hidden_layers[-1], action_size, lstm_size)
            self.critic_lstm = nn.LSTM(critic_hidden_layers[-1], 1, lstm_size)

            self.lstm_hidden = (torch.zeros(self.lstm_size,1,action_size, device=self.device), torch.zeros(self.lstm_size,1,action_size, device=self.device))
            self.critic_lstm_hidden = (torch.zeros(self.lstm_size,1,1, device=self.device), torch.zeros(self.lstm_size,1,1, device=self.device))

        
        else: # NOT USING LSTM, CONNECT TO OUTPUT LAYER
            actor.append(nn.Linear(actor_hidden_layers[-1], self.action_size))
            critic.append(nn.Linear(critic_hidden_layers[-1], 1))

        self.actor = nn.Sequential(*actor)

        self.critic = nn.Sequential(*critic)

    def reset_lstm_hidden_states(self):
        if self.use_lstm:
            self.lstm_hidden = (torch.zeros(self.lstm_size,1,self.action_size, device=self.device), torch.zeros(self.lstm_size,1,self.action_size, device=self.device))
            self.critic_lstm_hidden = (torch.zeros(self.lstm_size,1,1, device=self.device), torch.zeros(self.lstm_size,1,1, device=self.device))

    def forward(self, nn_input, critic_input, lstm_hidden = None):
        nn_input = nn_input.unsqueeze(1)
        critic_input = critic_input.unsqueeze(1)

        actor_output = self.actor(nn_input)
        critic_output = self.critic(critic_input)

        if self.use_lstm:
            actor_output, self.lstm_hidden = self.lstm(actor_output, self.lstm_hidden)
            critic_output, self.critic_lstm_hidden = self.critic_lstm(critic_output, self.critic_lstm_hidden)

        actor_output = actor_output.squeeze()

        critic_output = critic_output.squeeze()
        if critic_output.size() == torch.Size([]): # NO DIMENSION, ADD DIMENSION
            critic_output = critic_output.view(1)
        else:
            critic_output = critic_output.unsqueeze(1)

        return actor_output, critic_output, self.lstm_hidden