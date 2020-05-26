# EXPERIENCE REPLAY
# ORDER IN WHICE DATA IS SAVED
# SUPERSTATE
# ACTION
# NN_ACTION - ACTION CHOSEN BY MOVE/SWITCH NETWORK
# REWARD
# NEXT_SUPERSTATE
# ISDONE

import pickle
import numpy as np

class expr_replay():
    def __inti__(self,filename, max_records = 50000):
        self.filename = filename
        self.max_records = max_records
        try:
            with open(filename,'wb') as file:
                file.close()
        except:
            print('\nEXP REPLAY: UNABLE TO OPEN/CREATE FILE')
    
    def addReplay(self,superstate,action,nn_action,reward,next_superstate,isdone):
        data = []
        try:
            with open(self.filename,'wb') as file:
                data = pickle.load(file)
                if data == []:
                    data = [superstate,action,nn_action,reward,next_superstate,isdone]
                else:
                    data[0].append(superstate)
                    data[1].append(action)
                    data[2].append(nn_action)
                    data[3].append(reward)
                    data[4].append(next_superstate)
                    data[5].append(isdone)
                if len(data) > self.max_records: # CUT EXCESSIVE RECORDS FROM THE STARTING
                    data[0] = data[0][len(data) - self.max_records:]
                    data[1] = data[1][len(data) - self.max_records:]
                    data[2] = data[2][len(data) - self.max_records:]
                    data[3] = data[3][len(data) - self.max_records:]
                    data[4] = data[4][len(data) - self.max_records:]
                    data[5] = data[5][len(data) - self.max_records:]
                pickle.dump(data,file)
                file.close()
        except:
            print('\nEXP REPLAY: UNABLE TO WRITE REPLAY INFO TO FILE')

    def getReplay(self, batch_size = 16): # RETURN REPLAY INFORMATION
        superstates,actions,nn_actions,rewards,next_superstates,isdone = [],[],[],[],[],[]
        try:
            with open(self.filename,'rb') as file:
                data = pickle.load(file)
                chosen_replays = np.random.randint(low=0, high=len(data[0]), size=batch_size)
                for i in chosen_replays:
                    superstates.append(data[0][i])
                    actions.append(data[1][i])
                    nn_actions.append(data[2][i])
                    rewards.append(data[3][i])
                    next_superstates.append(data[4][i])
                    isdone.append(data[5][i])
                file.close()
        except:
            print('\nEXP REPLAY: UNABLE TO GET REPLAYS')
        
        return superstates,actions,nn_actions,rewards,next_superstates,isdone


