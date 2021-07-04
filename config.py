config = {
    'model': 'model.pth',
    'optim': 'optim.pth',
    'log': 'game.log',
    'actor_lr': 1e-4,
    'critic_lr': 1e-3,
    'simulations': 1, # NUMBER OF PARALLEL DATA COLLECTORS
    'episodes': 10, # TOTAL NUMBER OF EPISODES THAT WILL BE EQUALLY SPLIT BETWEEN PARALLEL SIMULTIONS
    'state_size': 182,#840,
    'critic_state_size': 744,
    'action_size': 9,#10,
    'actor_hidden_layers': (512,256), # INPUT AS TUPLE OF NEURONS IN HIDDEN LAYER
    'critic_hidden_layers': (1024,512),
    'use_lstm': False, # BOOLEAN
    'lstm_size': 1,
    'algorithm':'PPO',
    'batch_size': 64,#201,
    # 'num_mini_batches': 5,
    'epochs': 15,
    'clip_param': 0.2,
    'value_loss_coef': 1,
    'entropy_coef' : 1e-2,
    'max_grad_norm' : 50.0,
    'gamma': 0.99,
    'trainer_update_frequency': 4, # IN EPISODES PER SIMULATION PROCESS
    'agent_update_frequency': 2, # IN EPISODES PER SIMULATION PROCESS
    'max_turns_per_game': 200,
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