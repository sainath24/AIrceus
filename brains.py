import torch
import torch.nn as nn
import torch.nn.functional as f
import gen_state
import numpy as np

class Brain(nn.Module):
    def __init__(self,device,epsilon = 0.5):
        super().__init__()
        self.epsilon = epsilon
        self.device = device

        self.movechooser = nn.Sequential(
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

        self.switchchooser = nn.Sequential(
            nn.Linear(1074, 1024),
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
            nn.Linear(263, 512),
            nn.ReLU(),
            nn.Linear(512,512),
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
        move_state = torch.tensor(move_state,device=self.device, dtype=torch.float)
        move_result = self.movechooser(move_state)

        return move_result

    def forwardSwitch(self, switch_state):
        switch_state = torch.tensor(switch_state,device=self.device, dtype=torch.float)
        switch_result = self.switchchooser(switch_state)

        return switch_result

    def forwardFinal(self, final_state):
        final_state = torch.tensor(final_state,device=self.device, dtype=torch.float)
        final_result = self.finalchooser(final_state)

        return final_result
    
    def startForward(self, superstate,must_switch = False, must_attack = False):
        move_state = gen_state.generateStateForMoveChooser(superstate,True) if must_switch == False else gen_state.generateStateForMoveChooser(superstate,False)
        switch_state = gen_state.generateStateforSwitchChooser(superstate,True) if must_attack == False else gen_state.generateStateforSwitchChooser(superstate,False)
        
        move_result = self.forwardMove(move_state) if must_switch == False else torch.tensor([0,0,0,0])
        # print('\nMOVE_CHOOSER_RESULT:' + str(move_result))
        switch_result = self.forwardSwitch(switch_state) if must_attack == False else torch.tensor([0,0,0,0,0,0])
        # print('\nSWITCH_CHOOSER_RESULT:' + str(switch_result))
        final_state = gen_state.generateStateforFinalChooser(move_result.data.cpu().numpy(),switch_result.data.cpu().numpy(),superstate)

        return self.forwardFinal(final_state),move_result,switch_result

    def sample_action(self, qvalues,active_moves, pokemon_count):
        epsilon = self.epsilon
        actions = active_moves + pokemon_count

        random_action  = np.random.choice(actions)
        best_action = qvalues.argmax()

        should_explore = np.random.choice([0, 1], p=[1-epsilon, epsilon])
        if should_explore == 0:
            return best_action, False
        else:
            return random_action, True

def compute_loss(superstates,actions, rewards, is_done, next_superstates, agent, target_network, device, gamma = 0.99):
    # TODO: Write functionality
    agent_qs = []
    target_qs = []
    diff = 0
    agent_qs = torch.tensor(agent_qs, device = device, dtype=torch.float)
    target_qs = torch.tensor(target_qs, device = device, dtype=torch.float)

    # print('\nTENSOORRRRR???!!! ' + str(len(superstates)))
    for i in range(len(superstates)):
        superstate = superstates[i]['state']#torch.tensor(superstates[i]['state'],device=device,dtype=torch.float)
        action = actions[i] #torch.tensor(actions[i],device=device,dtype = torch.float)
        reward = rewards[i]#torch.tensor(rewards[i],device=device,dtype = torch.float)
        next_superstate = next_superstates[i]['state']#torch.tensor(next_superstates[i]['state'],device=device, dtype=torch.float)

        # print(superstates[i]['must_switch'],superstates[i]['must_attack'])
        q_values, move_qvalue, switch_qvalue = agent.startForward(superstate,superstates[i]['must_switch'],superstates[i]['must_attack'])
        # print('\nTENSOORRRRR???!!! RESPONSE\n')
        print(q_values)
        q_value = q_values[action]
        # print('\nQ VALUES:' , q_value)

        next_q_values, next_move_qvalue, next_switch_qvalue = target_network.startForward(next_superstate,next_superstates[i]['must_switch'], next_superstates[i]['must_attack'])
        # print('\nNEXT_Q_VALUES: ', next_q_values)
        next_q = gamma * max(next_q_values)
        # print('\nNEXT Q * GAMME: ', next_q)

        if is_done[i] == True:
            next_q = (next_q * 0) + reward
            # next_q = torch.tensor(rewards, device=device, dtype = torch.float)
        else:
            next_q = reward + next_q
        
        # print('\nREWARD:', reward)
        # print('\nFINAL NEXT Q: ', next_q)

        # diff += (q_value - next_q.detach()) **2
        diff += ((q_value - next_q.detach()) **2) * ((next_q.detach() - q_value)/abs((q_value - next_q.detach()))) # Try to maintain negative loss as negative

        # print('\nDIFF:', diff)
        # torch.cat(agent_qs,q_value)
        # torch.cat(target_qs,next_q)

        # print('\nAGENTS_QS:' , agent_qs)
        # print('\nTARGET_QS:' , target_qs)

    diff = diff/len(superstates)
    # print('\FINAL DIFF:', diff)
    # print('\nGONNA CALCULATE LOSS\n')
    # agent_qs = torch.tensor(agent_qs,device=device,dtype=torch.float)
    # target_qs = torch.tensor(target_qs,device=device, dtype=torch.float)

    loss = diff

    return loss