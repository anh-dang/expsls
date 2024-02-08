from haven import haven_utils as hu
import itertools
import numpy as np


def get_benchmark(benchmark,
                  opt_list,
                  batch_size=[1, 100, -1],
                  runs=[0, 1, 2, 3, 4],
                  max_epoch=[50],
                  losses=["logistic_loss", "squared_loss", "squared_hinge_loss"],
                  kappa=[100],
                  variance=None,
                  is_kernelize=None,
                  ):
    if benchmark == "mushrooms":
        return {"dataset": ["mushrooms"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 0.01,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs,
                "is_kernelize": is_kernelize}

    elif benchmark == "ijcnn":
        return {"dataset": ["ijcnn"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 0.01,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs,
                "is_kernelize": is_kernelize}

    elif benchmark == "a1a":
        return {"dataset": ["a1a"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 0.01,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}

    elif benchmark == "a2a":
        return {"dataset": ["a2a"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 1. / 2300,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}

    elif benchmark == "w8a":
        return {"dataset": ["w8a"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 1. / 50000,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}

    elif benchmark == "covtype":
        return {"dataset": ["covtype"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 1. / 500000,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}

    elif benchmark == "phishing":
        return {"dataset": ["phishing"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 1e-4,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}

    elif benchmark == "rcv1":
        return {"dataset": ["rcv1"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 0.01,
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs,
                "is_subsample": 1,
                "subsampled_n": 10000,
                "is_kernelize": is_kernelize}

    elif benchmark == "synthetic_interpolation":
        return {"dataset": ["synthetic"],
                "loss_func": losses,
                "opt": opt_list,
                "regularization_factor": 0.01,
                "margin": [0.1],
                "false_ratio": [0, 0.1, 0.2],
                "n_samples": [10000],
                "d": [200],
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}
    
    elif benchmark == "synthetic_ls":
        return {"dataset": ["synthetic_ls"],
                "loss_func": ["squared_loss"],
                "opt": opt_list,
                "regularization_factor": 0.,
                "n_samples": [10000],
                "d": [20],
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}

    elif benchmark == "synthetic_reg":
        return {"dataset": ["synthetic_reg"],
                "loss_func": ["logistic_loss"],
                "opt": opt_list,
                "regularization_factor": 1. / 10000,
                "n_samples": [10000],
                "d": [20],
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs}
    
    elif benchmark == "synthetic_kappa":
        return {"dataset": ["synthetic_kappa"],
                "loss_func": ["squared_loss"],
                "opt": opt_list,
                "regularization_factor": 0.,
                "n_samples": [10000],
                "d": [20],
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs,
                "kappa":kappa,
                "variance":variance,
                }
    
    elif benchmark == "synthetic_test":
        return {"dataset": ["synthetic_test"],
                "loss_func": ["squared_loss"],
                "opt": opt_list,
                "regularization_factor": 0.,
                "n_samples": [300],
                "d": [10],
                "batch_size": batch_size,
                "max_epoch": max_epoch,
                "runs": runs,
                "kappa":kappa,
                "variance":variance,
                }

    else:
        print("Benchmark unknown")
        return


EXP_GROUPS = {}

#
# # benchmarks_list = ["mushrooms", "ijcnn", "a1a", "a2a", "w8a", "rcv1", "covtype", "phishing"]
# # benchmarks_interpolation_list = ["synthetic_interpolation"]
#

benchmarks_list = ["mushrooms", "ijcnn", "rcv1", "synthetic_ls", "synthetic_kappa", "synthetic_test"]

for benchmark in benchmarks_list:
    EXP_GROUPS["exp_%s" % benchmark] = []

opt_list = []
# MAX_EPOCH=20000
# MAX_EPOCH = 7000
MAX_EPOCH = 500

RUNS = [0,1,2]
# RUNS=[0,1,2,3,4]

# SHB

# for alpha_t in ['CNST', 'EXP']:
for alpha_t in ['CNST']:
    for c in [2/3, 1/6, 1/10, 1/100]:
    # for c in [1]:
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

# opt_list += [{'name': 'EXP_SHB',
#         'alpha_t': 'EXP',
#         'method': 'SEBBOUH',
#         'is_sls': False,
#         'mis_spec': 1.0,
#         'ada': None,
#         'ld': None,
#         'ld_sche': None,
#         'c': 1
#         }]

# for c in [0.5]:
#     opt_list += [{'name': 'Mix_SHB',
#                 'c':c}]

# opt_list += [{'name': 'M_ASHB',
#                 'I': 4,
#                 'p': 1,
#                 'c': 10
#                 }]

# SGD
# for alphat in ["DECR"]:
#     # for sls in [False, True]:
#     for sls in [False]:
#         opt_list += [{'name': 'EXP_SGD',
#                       'alpha_t': alphat,
#                       'is_sls': sls,
#                       'ada': None,
#                       'new': True
#                       }]

opt_list += [{'name': 'EXP_SGD',
                      'alpha_t': "CNST",
                      'is_sls': False,
                      'ada': None}]

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

# opt_list += [{'name': 'EXP_ACC_SGD',
#                 'alpha_t': "DECR",
#                 'rho': rho,
#                 'is_sls': False
#                 }]

# opt_list += [{'name': 'EXP_ACC_SGD',
#                 'alpha_t': "CNST",
#                 'rho': rho,
#                 'is_sls': False
#                 }]


for benchmark in benchmarks_list:
    EXP_GROUPS['exp_%s' % benchmark] += hu.cartesian_exp_group(get_benchmark(benchmark, opt_list,
                                                                             batch_size=[100,200,250,275,290], 
                                                                            #  batch_size=[-10/9],
                                                                             variance=[0],
                                                                            #  is_kernelize=0,
                                                                             max_epoch=[MAX_EPOCH],
                                                                             runs=RUNS, 
                                                                             kappa=[20,50,100],
                                                                             losses=['squared_loss']))
                                                                            # losses=['squared_loss', 'logistic_loss']