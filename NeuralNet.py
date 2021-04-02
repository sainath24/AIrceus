import torch
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self, state_size, action_size, hidden_size):
        super(NeuralNet, self).__init__()
        self.actor = nn.Sequential(
            nn.Linear(state_size, hidden_size), nn.Tanh(),
            nn.Linear(hidden_size, hidden_size), nn.Tanh(),
            nn.Linear(hidden_size, action_size)
        )

        self.critic = nn.Sequential(
            nn.Linear(state_size, hidden_size), nn.Tanh(),
            nn.Linear(hidden_size, hidden_size), nn.Tanh(),
            nn.Linear(hidden_size, 1)
        )

    def forward(self, input):
        actor_output = self.actor(input)
        critic_output = self.critic(input)

        return actor_output, critic_output