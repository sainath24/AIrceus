import torch
import torch.optim as optim
import logging
import multiprocessing
from config import config
from NeuralNet import NeuralNet
import wandb
import os
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler
import torch.nn as nn
import torch.nn.functional as f
from torch.distributions.categorical import Categorical
from tqdm import tqdm
import sys


class CentralUpdater:
    def __init__(self, simulations) -> None:
        self.simulations = simulations
        self.pipes = []

        self.states = torch.tensor([])
        self.actions = torch.tensor([])
        self.values = torch.tensor([])
        self.returns = torch.tensor([])
        self.log_prob_actions = torch.tensor([])
        self.dones = torch.tensor([])
        self.hx = torch.tensor([])
        self.cx = torch.tensor([])

        self.batch_size = config['batch_size']
        # self.num_mini_batches = number_mini_batches
        self.epochs = config['epochs']
        self.state_size = config['state_size']
        self.action_size = config['action_size']
        self.hidden_size = config['hidden_size']
        self.clip_param = config['clip_param']
        self.lstm_size = config['lstm_size']
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.model_path = config['model']
        self.optim_path = config['optim']

        self.value_loss_coef = config['value_loss_coef']
        self.entropy_coef = config['entropy_coef']
        self.max_grad_norm = config['max_grad_norm'] ## NOT USED
        self.gamma = config['gamma']

        self.model = NeuralNet(self.state_size, self.action_size, self.hidden_size, self.lstm_size, self.device)
        self.optimiser = optim.Adam(self.model.parameters(), lr=config['optim_lr'])

        self.model.to(self.device)

        
        # if config['use_wandb']:
        #     wandb.init(project = 'AIrceus_V2.0') 
  
        # if config['use_wandb']:
        #     wandb.watch(self.model)

        
        self.load()
    
    def start(self, threaded = True): 
        if threaded: # START AS SEPARATE PROCESS
            process = multiprocessing.Process(target= self.run, args=())
            process.start()
        else:
            self.run()

    def run(self):
        if config['use_wandb']:
            wandb.init(project = 'AIrceus_V2.0') 

        no_updates = (config['episodes']//self.simulations)//config['agent_update_frequency']
        for i in tqdm(range(no_updates), desc='UPDATES'):
            self.wait_for_data() # BLOCKS UNTIL ALL SIMULATIONS HAVE SENT DATA
            
            policy_loss, value_loss = self.update()
            self.send_model()
            if config['use_wandb']:
                wandb.log({'policy_loss': policy_loss, 'value_loss': value_loss})

    def load(self):
        if os.path.isfile(self.model_path):
            print('\nMODEL LOADED')
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.reset_lstm_hidden_states()
        else: # save common model
            torch.save(self.model.state_dict(), self.model_path)

        if os.path.isfile(self.optim_path):
            print('\nOPTIMIZER LOADED')
            self.optimiser.load_state_dict(torch.load(self.optim_path, map_location=self.device))
        else: # save common optim
            torch.save(self.optimiser.state_dict(), self.optim_path)

    def add_pipe(self, pipe):
        self.pipes.append(pipe)
    
    def remove_pipe(self, pipe):
        self.pipes.remove(pipe)
    
    def wait_for_data(self):
        for pipe in self.pipes:
            data = pipe.recv() # GETS DICT
            self.add_data(data)
            del data

    
    def add_data(self, data):
        self.states = torch.cat((self.states, data['states']))
        self.actions = torch.cat((self.actions, data['actions']))
        self.values = torch.cat((self.values, data['values']))
        self.log_prob_actions = torch.cat((self.log_prob_actions, data['log_prob_actions']))
        self.dones = torch.cat((self.dones, data['dones']))
        self.returns = torch.cat((self.returns, data['returns']))
        self.hx = torch.cat((self.hx, data['hx']))
        self.cx = torch.cat((self.cx, data['cx']))


    def send_model(self):
        for pipe in self.pipes:
            pipe.send(1)
            # pipe.send(self.model.state_dict())
    
    def update(self):
        advantages = self.returns - self.values
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-5)

        batch_count = 0.0

        total_value_loss = 0.0
        total_policy_loss = 0.0

        for epoch in range(self.epochs):
            data = self.data_generator(advantages)
            for sample in data:
                batch_count+=1
                lstm_hidden_batch, states_batch, actions_batch, values_batch, returns_batch, \
                    dones_batch, old_action_log_probs_batch, adv_targ = sample

                values, action_log_probs, entropy = self.evaluate(lstm_hidden_batch, states_batch, actions_batch)

                ratio = torch.exp(action_log_probs - old_action_log_probs_batch.detach())
                surr1 = ratio * adv_targ.detach()
                surr2 = torch.clamp(ratio, 1 - self.clip_param, 1 + self.clip_param) * adv_targ.detach()

                policy_loss = -torch.min(surr1, surr2).mean() 

                value_loss = 0.5 * (returns_batch - values).pow(2).mean()

                self.optimiser.zero_grad()
                (value_loss * self.value_loss_coef + policy_loss - entropy * self.entropy_coef).backward()

                nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                self.optimiser.step()

                total_value_loss += value_loss.item()
                total_policy_loss += policy_loss.item()

        num_updates = self.epochs * batch_count
        
        total_policy_loss /= num_updates
        total_value_loss /= num_updates

        logging.info('MODEL UPDATED, policy_loss: ' + str(-total_policy_loss) + ' value_loss: ' + str(total_value_loss))

        self.post_update()
        self.checkpoint()

        return -total_policy_loss, total_value_loss

    def data_generator(self, advantages):
        data_length = self.states.size(0)

        sampler = BatchSampler(SubsetRandomSampler(range(data_length)), self.batch_size, drop_last=False)

        for indices in sampler:
            states_batch = self.states.view(-1, self.state_size)[indices]
            actions_batch = self.actions.view(-1, 1)[indices]
            values_batch = self.values.view(-1, 1)[indices]
            returns_batch = self.returns.view(-1, 1)[indices]
            dones_batch = self.dones.view(-1,1)[indices]
            old_action_log_probs_batch = self.log_prob_actions.view(-1, 1)[indices]
            
            hx_batch = torch.zeros(self.lstm_size, len(indices), self.hidden_size)
            for i in range(self.lstm_size):
                hx_batch[i].copy_(torch.cat(([x[i] for x in self.hx[indices]])))

            cx_batch = torch.zeros(self.lstm_size, len(indices), self.hidden_size)
            for i in range(self.lstm_size):
                cx_batch[i].copy_(torch.cat(([x[i] for x in self.cx[indices]])))

            lstm_hidden_batch = (hx_batch, cx_batch)

            adv_targ = advantages.view(-1,1)[indices]

            yield lstm_hidden_batch, states_batch, actions_batch, values_batch, returns_batch, \
                dones_batch, old_action_log_probs_batch, adv_targ

    def evaluate(self, lstm_hidden_batch, states_batch, actions_batch):
        actor_output, critic_output, lstm_hidden = self.model(states_batch, lstm_hidden_batch)
        
        actor_output = f.softmax(actor_output, dim = -1)

        actor_probs = Categorical(actor_output)
        action_log_probs = actor_probs.log_prob(actions_batch)
        entropy = actor_probs.entropy().mean()

        return critic_output, action_log_probs, entropy

    def post_update(self):
        self.states = torch.tensor([])
        self.actions = torch.tensor([])
        self.values = torch.tensor([])
        self.returns = torch.tensor([])
        self.log_prob_actions = torch.tensor([])
        self.dones = torch.tensor([])
        self.hx = torch.tensor([])
        self.cx = torch.tensor([])

    def checkpoint(self):
        torch.save(self.model.state_dict(), self.model_path)
        torch.save(self.optimiser.state_dict(), self.optim_path)

        