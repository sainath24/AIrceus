config = {
    'model': 'model.pth',
    'optim': 'optim.pth',
    'log': 'game.log',
    'optim_lr': 1e-4,
    'episodes': 1000,
    'state_size': 840,
    'action_size': 10,
    'hidden_size':128,
    'algorithm':'PPO',
    'batch_size': 200,
    'num_mini_batches': 10,
    'epochs': 5,
    'clip_param': 0.2,
    'value_loss_coef': 1,
    'entropy_coef' : 1e-2,
    'max_grad_norm' : 100.0,
    'gamma': 0.99,
    'trainer_update_frequency': 10, # IN EPISODES
    'use_wandb': True
    ## TODO: ADD REST OF THE CONFIG AND SET PARAMS
}

default_move = {
    'name': 'default',
    'type': 'normal',
    'target': 'self',
    'accuracy': 0,
    'basePower': 0,
    'maxpp': 1,
    'pp': 1,
    'disabled': True, 
    'user_stat_changes': {},
    'enemy_stat_changes': {},
    'trapped': False
}