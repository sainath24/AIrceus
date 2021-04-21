config = {
    'model': 'model.pth',
    'optim': 'optim.pth',
    'log': 'game.log',
    'optim_lr': 1e-3,
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
    'entropy_coef' : 1e-1,
    'max_grad_norm' : 100.0,
    'gamma': 0.99,
    'trainer_update_frequency': 10, # IN EPISODES
    'use_wandb': False
    ## TODO: ADD REST OF THE CONFIG AND SET PARAMS
}

default_move = {
    'name': 'default',
    'type': 'normal',
    'target': 'self',
    'accuracy': 0,
    'basePower': 0,
    'maxpp': 0,
    'pp': 0,
    'disabled': True, 
    'user_stat_changes': {},
    'enemy_stat_changes': {},
    'trapped': False
}

default_pokemon = {
    'details': 'default',
    'types': ['null'],
    'active': False,
    'hp': 0.0,
    'status': ['fnt'],
    'stats': {'atk':0.0, 'def':0.0, 'spa':0.0, 'spd':0.0, 'spe':0.0},
    'baseAbility': 'null',
    'item': 'null',
    'moves': []
}