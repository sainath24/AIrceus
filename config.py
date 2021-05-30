config = {
    'model': 'model.pth',
    'optim': 'optim.pth',
    'log': 'game.log',
    'optim_lr': 1e-5,
    'simulations': 2, # NUMBER OF PARALLEL DATA COLLECTORS
    'episodes': 10, # TOTAL NUMBER OF EPISODES THAT WILL BE EQUALLY SPLIT BETWEEN PARALLEL SIMULTIONS
    'state_size': 157,#840,
    'action_size': 9,#10,
    'hidden_size': 256,
    'lstm_size': 3,
    'algorithm':'PPO',
    'batch_size': 32,#201,
    # 'num_mini_batches': 5,
    'epochs': 15,
    'clip_param': 0.2,
    'value_loss_coef': 1,
    'entropy_coef' : 1e-3,
    'max_grad_norm' : 100.0,
    'gamma': 0.99,
    'trainer_update_frequency': 2, # IN EPISODES PER SIMULATION PROCESS
    'agent_update_frequency': 1, # IN EPISODES PER SIMULATION PROCESS
    'use_wandb': False
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