# benchmarks_list = ["mushrooms", "ijcnn", "a1a", "a2a", "w8a", "rcv1", "covtype", "phishing"]
# benchmarks_interpolation_list = ["synthetic_interpolation"]

EXP_KERNEL_CONFIGS={}
EXP_KERNEL_CONFIGS['max_epoch']=2500
EXP_KERNEL_CONFIGS['runs']=[0,1,2]
EXP_KERNEL_CONFIGS['batch_size']=[-2]
EXP_KERNEL_CONFIGS['benchmarks_list']=["mushrooms", "ijcnn", "rcv1"]
EXP_KERNEL_CONFIGS['losses']=["squared_loss"]
EXP_KERNEL_CONFIGS['is_kernelize']=1
opt_list = []

# SHB
for alpha_t in ['CNST']:
    for c in [1]:
        opt_list += [{'name': 'EXP_SHB',
                'alpha_t': alpha_t,
                'method': 'WANG21',
                'is_sls': False,
                'mis_spec': 1.0,
                'ada': None,
                'ld': None,
                'ld_sche': None,
                'c':c
                }]

opt_list += [{'name': 'EXP_SHB',
        'alpha_t': 'EXP',
        'method': 'SEBBOUH',
        'is_sls': False,
        'mis_spec': 1.0,
        'ada': None,
        'ld': None,
        'ld_sche': None,
        'c': 1
        }]

for c in [0.5]:
    opt_list += [{'name': 'Mix_SHB',
                'c':c}]

opt_list += [{'name': 'M_ASHB',
                'I': 4,
                'p': 1,
                'c': 10
                }]

# SGD
for alphat in ["DECR"]:
    opt_list += [{'name': 'EXP_SGD',
                    'alpha_t': alphat,
                    'is_sls': False,
                    'ada': None,
                    'new': True
                    }]
    
# ASGD
rhos=[100]
rho = 1

opt_list += [{'name': 'EXP_ACC_SGD',
                'alpha_t': "DECR",
                'rho': 1,
                'is_sls': False
                }]

EXP_KERNEL_CONFIGS['opt_list'] = opt_list