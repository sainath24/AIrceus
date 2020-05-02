import torch
import torch.nn as nn
import torch.nn.functional as f
import gen_state
import numpy as np

class Brain(nn.Module):
    def __init__(self,epsilon = 0.5):
        self.epsilon = epsilon

        self.movechooser = nn.Sequentail(
            nn.Linear(194, 256),
            nn.ReLU(),
            nn.Linear(256,512),
            nn.ReLU(),
            nn.Linear(512,1024),
            nn.ReLU(),
            nn.Linear(1024,1024),
            nn.ReLU(),
            nn.Linear(1024,1024),
            nn.ReLU(),
            nn.Linear(1024,512),
            nn.ReLU(),
            nn.Linear(512,256),
            nn.ReLU(),
            nn.Linear(256,128),
            nn.ReLU(),
            nn.Linear(128,4)
        )

        self.switchchooser = nn.Sequentail(
            nn.Linear(927, 1024),
            nn.ReLU(),
            nn.Linear(1024,1024),
            nn.ReLU(),
            nn.Linear(1024,1024),
            nn.ReLU(),
            nn.Linear(1024,1024),
            nn.ReLU(),
            nn.Linear(1024,512),
            nn.ReLU(),
            nn.Linear(512,256),
            nn.ReLU(),
            nn.Linear(256,128),
            nn.ReLU(),
            nn.Linear(128,6)
        )

        self.finalchooser = nn.Sequential(
            nn.Linear(175, 256),
            nn.ReLU(),
            nn.Linear(256,512),
            nn.ReLU(),
            nn.Linear(512,1024),
            nn.ReLU(),
            nn.Linear(1024,1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512,256),
            nn.ReLU(),
            nn.Linear(256,128),
            nn.ReLU(),
            nn.Linear(128,2)
        )
    
    def forwardMove(self, move_state):
        move_result = self.movechooser(move_result)

        return move_result.data.cpu().numpy()

    def forwardSwitch(self, switch_state):
        switch_result = self.switchchooser(switch_state)

        return switch_result.data.cpu().numpy()

    def forwardFinal(self, final_state):
        final_result = self.finalchooser(final_state)

        return final_result.data.cpu().numpy()
    
    def startForward(self, superstate,must_switch = False, must_attack = False):
        move_state = gen_state.generateStateForMoveChooser(superstate) if must_switch == False else gen_state.generateStateForMoveChooser(None)
        switch_state = gen_state.generateStateforSwitchChooser(superstate) if must_attack == False else gen_state.generateStateforSwitchChooser(None)
        
        move_result = self.forwardMove(move_state) if must_switch == False else [0,0,0,0]
        switch_result = self.forwardSwitch(switch_state) if must_attack == False else [0,0,0,0,0]
        final_state = gen_state.generateStateforFinalChooser(move_result,switch_result,superstate)

        return self.forwardFinal(final_state).data.cpu().numpy,move_result,switch_result

    def sample_action(self, qvalues,active_moves, pokemon_count):
        epsilon = self.epsilon
        actions = active_moves + pokemon_count

        random_action  = np.random.choice(actions)
        best_action = qvalues.argmax()

        should_explore = np.random.choice([0, 1], p=[1-epsilon, epsilon])
        if should_explore == 0:
            return best_action, 0
        else:
            return random_action, 1

def compute_loss(superstates,actions, rewards, is_done, next_superstates, agent, target_network, device, gamma = 0.99):
    # TODO: Write functionality
    agent_qs = []
    target_qs = []
    for i in range(len(superstates)):
        superstate = torch.tensor(superstates[i]['state'],device=device,dtype=torch.float)
        action = torch.tensor(actions[i],device=device,dtype = torch.float)
        reward = torch.tensor(rewards[i],device=device,dtype = torch.float)
        next_superstate = torch.tensor(next_superstates[i]['state'],device=device, dtype=torch.float)

        q_values, move_qvalue, switch_qvalue = agent.startForward(superstate,superstates[i]['must_switch'],superstates[i]['must_attack'])
        q_value = q_values[actions]

        next_q_values = target_network.startForward(next_superstate,next_superstates[i]['must_switch'], next_superstates[i]['must_attack'])
        next_q = gamma * max(next_q_values)

        if is_done[i] == True:
            next_q = rewards
        else:
            next_q = rewards + next_q

        agent_qs.append(q_value)
        target_qs.append(next_q)
    
    agent_qs = torch.tensor(agent_qs,device=device,dtype=torch.float)
    target_qs = torch.tensor(target_qs,device=device, dtype=torch.float)

    loss = torch.mean((agent_qs - target_qs) ** 2)

    return loss
        







