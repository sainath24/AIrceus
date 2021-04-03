config = {
    'model': 'model.pth',
    'optim': 'optim.pth',
    'log': 'game.log',
    'optim_lr': 1e-4,
    'episodes': 5,
    'state_size': 840,
    'action_size': 10,
    'hidden_size':128,
    'algorithm':'PPO',
    'batch_size': 6,
    'num_mini_batches': 2,
    'epochs': 5,
    'clip_param': 0.2,
    'value_loss_coef': 1,
    'entropy_coef' : 1e-2,
    'max_grad_norm' : 0.0, # NOT USED
    'gamma': 0.99,
    'trainer_update_frequency': 5 # IN EPOCHS
    ## TODO: ADD REST OF THE CONFIG AND SET PARAMS
}