import torch
from torch._C import device
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self, state_size, critic_state_size, action_size, hidden_size, lstm_size, device):
        super(NeuralNet, self).__init__()
        self.state_size = state_size
        self.critic_state_size = critic_state_size
        self.hidden_size = hidden_size
        self.action_size = action_size
        self.lstm_size = lstm_size
        self.device = device

        self.lstm = nn.LSTM(hidden_size, action_size, lstm_size)
        self.critic_lstm = nn.LSTM(hidden_size, 1, lstm_size)

        self.actor = nn.Sequential(
            nn.Linear(state_size, hidden_size), nn.ReLU()
            # nn.Linear(hidden_size, hidden_size), nn.ReLU(),
            # nn.Linear(hidden_size, hidden_size), nn.ReLU(),
            # nn.Linear(hidden_size, action_size)
        )

        self.critic = nn.Sequential(
            nn.Linear(self.critic_state_size, hidden_size), nn.ReLU()
            # nn.Linear(hidden_size, hidden_size), nn.ReLU(),
            # nn.Linear(hidden_size, hidden_size), nn.ReLU(),
            # nn.Linear(hidden_size, 1)
        )

        self.lstm_hidden = (torch.zeros(self.lstm_size,1,action_size, device=self.device), torch.zeros(self.lstm_size,1,action_size, device=self.device))
        self.critic_lstm_hidden = (torch.zeros(self.lstm_size,1,1, device=self.device), torch.zeros(self.lstm_size,1,1, device=self.device))

    def reset_lstm_hidden_states(self): 
        self.lstm_hidden = (torch.zeros(self.lstm_size,1,self.action_size, device=self.device), torch.zeros(self.lstm_size,1,self.action_size, device=self.device))
        self.critic_lstm_hidden = (torch.zeros(self.lstm_size,1,1, device=self.device), torch.zeros(self.lstm_size,1,1, device=self.device))


    def forward(self, nn_input, critic_input, lstm_hidden = None):
        # print('\nCRITIC INPUT SIZE: ', critic_input.size())
        # print('\nNN INPUT SIZE BEFORE CONVERSION: ', nn_input.size())
        # nn_input = nn_input.view(1,1,self.state_size)
        nn_input = nn_input.unsqueeze(1)
        # print('\nSIZE OF INPUT: ', nn_input.size())

        out = self.actor(nn_input)
        
        # if lstm_hidden == None:
        output, self.lstm_hidden = self.lstm(out, self.lstm_hidden)
        #     # print('\nLSTM HIDDEN LEN: ',len(self.lstm_hidden))
        #     # print('\nLSTM HIDDEN SIZE: ', self.lstm_hidden[0].size())
        # else:
        #     # lstm_hidden = lstm_hidden.unsqueeze(0)
        #     # print('\nUPDATE LSTM BEOFRE UNBIND: ', lstm_hidden.size())
        #     # lstm_hidden = torch.unbind(lstm_hidden)
        #     # print('\nLEN OF UPDATE LSTM AFTER UNBIND: ', len(lstm_hidden))
        #     # print('\nUPDATE LSTM AFTER UNBIND: ', lstm_hidden[0].size(), lstm_hidden[1].size())
        #     # lstm_hidden = [x.unbind() for x in lstm_hidden]
        #     output, hidden = self.lstm(out, lstm_hidden)
        
        # print('\nLSTM OUTPUT: ', output.size())
        actor_output = output.squeeze()
        # print('\nLSTM OUTPUT AFTER SQUEEZE: ', actor_output.size())
        critic_input = critic_input.unsqueeze(1)
        # print('\nCRITIC INPUT SIZE after unsqueeze: ', critic_input.size())
        critic_output = self.critic(critic_input)
        # print('\nCRITIC OUTPUT SIZE AFTER NN: ', critic_output.size())
        critic_output, self.critic_lstm_hidden = self.critic_lstm(critic_output, self.critic_lstm_hidden)
        # print('\nCRITIC OUTPUT SIZE AFTER LSTM: ', critic_output.size())
        critic_output = critic_output.squeeze()
        if critic_output.size() == torch.Size([]): # NO DIMENSION, ADD DIMENSION
            critic_output = critic_output.view(1)
        else:
            critic_output = critic_output.unsqueeze(1)

        # print('CRITIC_OUTPUT: ', critic_output.size())

        return actor_output, critic_output, self.lstm_hidden