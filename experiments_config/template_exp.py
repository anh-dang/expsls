EXP_GROUPS = {}

benchmarks_list = ["mushrooms", "ijcnn", "rcv1", "synthetic_ls", "synthetic_kappa", "synthetic_test"]

for benchmark in benchmarks_list:
    EXP_GROUPS["exp_%s" % benchmark] = []

opt_list = []
# MAX_EPOCH=20000
# MAX_EPOCH = 7000
MAX_EPOCH = 5000

RUNS = [0,1,2]
# RUNS=[0,1,2,3,4]

# SHB

# for alpha_t in ['CNST', 'EXP']:
for alpha_t in ['CNST']:
    # for c in [2/3, 1/6, 1/10, 1/100]:
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
    # for sls in [False, True]:
    for sls in [False]:
        opt_list += [{'name': 'EXP_SGD',
                      'alpha_t': alphat,
                      'is_sls': sls,
                      'ada': None,
                      'new': True
                      }]

# opt_list += [{'name': 'EXP_SGD',
#                       'alpha_t': "CNST",
#                       'is_sls': False,
#                       'ada': None}]

# ASGD
rhos=[100]
rho = 1

# for rho in rhos:
#     for alphat in [ "DECR"]:
#         for sls in [False, True]:
#             opt_list += [{'name': 'EXP_ACC_SGD',
#                           'alpha_t': alphat,
#                           'rho': rho,
#                           'is_sls': sls
#                           }]

opt_list += [{'name': 'EXP_ACC_SGD',
                'alpha_t': "DECR",
                'rho': rho,
                'is_sls': False
                }]

# opt_list += [{'name': 'EXP_ACC_SGD',
#                 'alpha_t': "CNST",
#                 'rho': rho,
#                 'is_sls': False
#                 }]


for benchmark in benchmarks_list:
    EXP_GROUPS['exp_%s' % benchmark] += hu.cartesian_exp_group(get_benchmark(benchmark, opt_list,
                                                                            #  batch_size=[100,200,250,275,290], 
                                                                             batch_size=[-10/9],
                                                                            #  variance=[0],
                                                                             is_kernelize=1,
                                                                             max_epoch=[MAX_EPOCH],
                                                                             runs=RUNS, 
                                                                            #  kappa=[20,50,100],
                                                                             losses=['logistic_loss']))
                                                                            # losses=['squared_loss', 'logistic_loss']