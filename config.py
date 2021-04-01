config = {
    'model': '/model.pth',
    'optim': '/optim.pth',
    'episodes': 1000,
    'state_size': None,
    'action_size': None,
    'hidden_size':None,
    'algorithm':'PPO',
    'batch_size': 1000,
    'num_mini_batches': 100,
    'epochs': 10,
    'clip_param': 0.2,
    'value_loss_ceof': 0.0,
    'entropy_coeff' : 0.0,
    'max_grad_norm' : 0.0
    ## TODO: ADD REST OF THE CONFIG AND SET PARAMS
}