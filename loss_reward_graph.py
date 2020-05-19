import matplotlib.pyplot as plt
import numpy as np
import pickle

fname = 'loss_reward.dat'
data = []
with open(fname,'rb') as file:
    data = pickle.load(file)


losses = data[0]
rewards = data[1]

for i in range(len(losses)):
    print('\nGAME ', i)
    plt.figure(figsize=[16, 9])
    plt.subplot(1, 2, 1)
    plt.title("loss history - game " + str(i))
    plt.plot(losses[i])
    plt.grid()

    plt.subplot(1, 2, 2)
    plt.title("Mean reward - game " + str(i))
    plt.plot(rewards[i])
    plt.grid()

    plt.show()