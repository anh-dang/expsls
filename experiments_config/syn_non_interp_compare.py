import numpy as np
EXP_SYN_NON_INTERP_COMPARE_CONFIGS={}
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['max_epoch'] = 7000
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['kappa'] =  [1024, 512, 200, 100, 50] #[1024, 512, 256] [200, 100, 50]
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['runs'] = [0,1,2]
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['batch_size'] = [-10/9]
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['benchmarks_list'] = ["synthetic_kappa"]
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['losses'] = ["squared_loss"]
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['is_kernelize'] = 0
EXP_SYN_NON_INTERP_COMPARE_CONFIGS['variance'] = [1e-6, 1e-4, 1e-2, 1] #[1e-2, 1e-4, 1e-5, 1e-6] [1,1e-2,1e-4]
opt_list = []

# for c in ['auto']: #[0.4,0.5,0.25,0.125]:
#     opt_list += [{'name': 'M_ASHB', 'c':c, 'beta_const':False}]

for C in [2, 'max']:
    opt_list += [{'name': 'M_SHB_PAN', 'C':C}]

# opt_list += [{'name': 'EXP_SHB',
#         'alpha_t': 'CNST',
#         'method': 'WANG21',
#         'is_sls': False,
#         'mis_spec': 1.0,
#         'ada': None,
#         'ld': None,
#         'ld_sche': None,
#         'c':1
#         }]

# opt_list += [{'name': 'Mix_SHB', 'c':0.5}]

EXP_SYN_NON_INTERP_COMPARE_CONFIGS['opt_list'] = opt_list