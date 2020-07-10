import torch
import torch.nn as nn
import torch.nn.functional as f
import gen_state
import numpy as np

class Brain(nn.Module):
    def __init__(self,device,epsilon = 0.2):
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

        # if (1-0.24 * active_moves)/pokemon_count < 0.24:
        #     proba = [0.24] * active_moves
        #     print('\nDEBUG RANDOM PROBA MOVES: ', proba)
        #     proba_switch = [(1-0.24 * active_moves)/pokemon_count] * pokemon_count
        #     print('\nDEBUG RANDOM PROBA SWITCH: ', proba_switch)
        #     proba.extend(proba_switch)
        # elif active_moves == 0 and pokemon_count == 1:
        #     proba = [1]
        #     print('\nDEBUG RANDOM PROBA MOVES: ', proba)

        # elif pokemon_count == 1 and active_moves != 0:
        #     proba = [1/active_moves] * active_moves
        #     print('\nDEBUG RANDOM PROBA MOVES: ', proba)
        #     proba_switch = [0]
        #     print('\nDEBUG RANDOM PROBA SWITCH: ', proba_switch)
        #     proba.extend(proba_switch)
        # else:
        #     proba = [1/actions] * actions



        # print('\nDEBUG RANDOM PROBA: ', proba)

        random_action  = np.random.choice(range(actions))
        best_action = qvalues.argmax()

        should_explore = np.random.choice([0, 1], p=[1-epsilon, epsilon])
        if should_explore == 0:
            return best_action, False
        else:
            return random_action, True
    
def update_move_switch_networks(nn_action,superstate, action,reward, is_done, next_superstate, agent, target_network, device, gamma = 0.99):
    loss = 0
    if action == 0: # UPDATE MOVE NETWORK
        move_state = gen_state.generateStateForMoveChooser(superstate['state'],True) if superstate['must_switch'] == False else gen_state.generateStateForMoveChooser(superstate['state'],False)
        q_values = agent.forwardMove(move_state)
        q_value = q_values[nn_action]
        print('\nDEBUG MOVE CHOSEN: ', nn_action)
        print('\DEBUG MOVE Q VALUES: ',q_values)
        # print('\nNEXT SUPERSTATE LENGTH(1076):',len(next_superstate['state']))
        next_state = gen_state.generateStateForMoveChooser(next_superstate['state'],True) if next_superstate['must_switch'] == False else gen_state.generateStateForMoveChooser(next_superstate['state'],False)
        # print('\nDEBUG NEXT STATE:', next_state)
        # print('\nDEBUG NEXT STATE LENGTH(1074):', len(next_state))
        next_q = target_network.forwardMove(next_state)
        next_q = gamma * max(next_q)

        if is_done:
            next_q = (next_q * 0) + reward
        else:
            next_q = reward + next_q

        loss = (q_value - next_q.detach()) **2
        loss.backward()
        print('\nDEBUG: MOVE LOSS BACKWARD DONE: ', loss)
        #TODO: DO OPTIMISER ACTIONS - NO NEED USE SAME OPTIMIZER

    else: # UPDATE SWITCH NETWORK
        switch_state = gen_state.generateStateforSwitchChooser(superstate['state'],True) if superstate['must_attack'] == False else gen_state.generateStateforSwitchChooser(superstate['state'],False)
        q_values = agent.forwardSwitch(switch_state)
        q_value = q_values[nn_action]
        print('\nDEBUG SWITCH CHOSEN: ', nn_action)
        print('\DEBUG SWITCH Q VALUES: ',q_values)
        next_state = gen_state.generateStateforSwitchChooser(next_superstate['state'],True) if next_superstate['must_attack'] == False else gen_state.generateStateforSwitchChooser(next_superstate['state'],False) 
        next_q = target_network.forwardSwitch(next_state)
        next_q = gamma * max(next_q)

        if is_done:
            next_q = (next_q * 0) + reward
        else:
            next_q = reward + next_q

        loss = (q_value - next_q.detach()) **2
        loss.backward()
        print('\nDEBUG: SWITCH LOSS BACKWARD DONE: ', loss)
        #TODO: DO OPTIMISER ACTIONS  - NO NEED USE SAME OPTIMIZER
    
    return loss

    
    

def compute_loss(nn_actions,superstates,actions, rewards, is_done, next_superstates, agent, target_network, device, gamma = 0.99):
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

        # TODO: UNCOMMENT TO TRAIN FINAL NETWORK
        # print(superstates[i]['must_switch'],superstates[i]['must_attack'])
        q_values, move_qvalue, switch_qvalue = agent.startForward(superstate,superstates[i]['must_switch'],superstates[i]['must_attack'])
        # print('\nTENSOORRRRR???!!! RESPONSE\n')
        # print(q_values)
        q_value = q_values[action]

        print('\DEBUG FINAL Q VALUES: ',q_values)
        print('\DEBUG FINAL DECISION: ',action)
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

        diff = (q_value - next_q.detach()) **2

        diff.backward()
        print('\nFINAL DECISION LOSS: ', diff)

        switch_move_loss = update_move_switch_networks(nn_actions[i],superstates[i],action,reward,is_done[i],next_superstates[i],agent,target_network,device)
        # diff += ((q_value - next_q.detach()) **2) * ((next_q.detach() - q_value)/abs((q_value - next_q.detach()))) # Try to maintain negative loss as negative

        # print('\nDIFF:', diff)
        # torch.cat(agent_qs,q_value)
        # torch.cat(target_qs,next_q)

        # print('\nAGENTS_QS:' , agent_qs)
        # print('\nTARGET_QS:' , target_qs)

    # diff = diff/len(superstates)
    # print('\FINAL DIFF:', diff)
    # print('\nGONNA CALCULATE LOSS\n')
    # agent_qs = torch.tensor(agent_qs,device=device,dtype=torch.float)
    # target_qs = torch.tensor(target_qs,device=device, dtype=torch.float)

    loss = diff

    return loss



