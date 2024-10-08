import numpy as np

from dependencies import *

from utils import *
from datasets import *
from objectives import *
import time
from scipy.special import lambertw

def ls_stages(kap, T, c='auto'):

    def stages(kap, T):
        res = np.floor(np.real(lambertw(T*np.log(2)/(2*np.sqrt(kap))))/np.log(np.sqrt(2)))
        return int(res)
    
    I = stages(kap, T)
    if c == 'auto':
        T_0 = 100*np.sqrt(kap)
    else:
        T_0 = int(T*c)
    T_left = T - T_0
    total = sum([2**(i/2) for i in range(1, I+1)])
    ls = [T_0]
    for i in range(1,I+1):
        t = (T_left/total)*(2**(i/2))
        ls.append(int(np.ceil(t)))
    ls_stage = np.cumsum(ls)
    ls_stage[-1] = T
    return ls_stage

def M_ASHB(score_list, closure, D, labels, batch_size=1, max_epoch=100,
            x0=None, mu=0.1,L=0.1, c='auto', beta_const=False, verbose=True, D_test=None, labels_test=None,log_idx=100):
    """
        Multi-stage SHB for solving finite-sum problems
        Closure: a PyTorch-style closure returning the objective value and it's gradient.
        batch_size: the size of minibatches to use.
        D: the set of input vectors (usually X).
        labels: the labels corresponding to the inputs D.
        init_step_size: step-size to use
        n, d: size of the problem
    """
    n = D.shape[0]
    d = D.shape[1]

    m = int(n / batch_size)

    T = m * max_epoch
    T = max_epoch

    if x0 is None:
        x = np.zeros(d)
        x0 = np.zeros(d)
    elif isinstance(x0, np.ndarray) and x0.shape == (d,):
        x = x0.copy()
    else:
        raise ValueError('x0 must be a numpy array of size (d, )')

    
    px=x.copy()

    num_grad_evals = 0
    step_size=1./L
    t=0
    def a(k):
        return 1/((2.0**(k))*L)
    kappa=L/mu
    if T < 2*kappa:
        raise ValueError('T must be greater than 2*kappa,' + str(2*kappa))
    stages = ls_stages(kappa, T, c)
    loss, full_grad = closure(x, D, labels)

    if verbose:
        output = 'Epoch.: %d, Grad. norm: %.2e' % \
                 (0, np.linalg.norm(full_grad))
        output += ', Func. value: %e' % loss
        output += ', Step size: %e' % step_size
        output += ', Num gradient evaluations/n: %f' % (num_grad_evals / n)
        print(output)

    score_dict = {"itr": 0}
    score_dict["n_grad_evals"] = num_grad_evals
    score_dict["n_grad_evals_normalized"] = num_grad_evals / log_idx
    score_dict["train_loss"] = loss
    score_dict["grad_norm"] = np.linalg.norm(full_grad)
    score_dict["train_accuracy"] = accuracy(x, D, labels)
    score_dict["alpha_k"] = a(t)
    score_dict["beta_k"] = (1 - np.sqrt(step_size*mu))**2
    if D_test is not None:
        test_loss = closure(x, D_test, labels_test, backwards=False)
        score_dict["test_loss"] = test_loss
        score_dict["test_accuracy"] = accuracy(x, D_test, labels_test)
    score_list += [score_dict]

    T = stages[-1]
    
    for k in range(max_epoch):
        t_start = time.time()


        if np.linalg.norm(full_grad) <= 1e-12:
            break
        # if np.linalg.norm(full_grad) > 1e20:
        #     break
        if np.isnan(full_grad).any():
            break
        if t >= T:
            break
        # Create Minibatches:


        minibatches = make_minibatches(n, m, batch_size)

        for i in range(m):

            # get the minibatch for this iteration
            indices = minibatches[i]
            # indices=np.array([np.random.randint(low=0,high=n)])
            Di, labels_i = D[indices, :], labels[indices]
            temp = x.copy()
            stage = np.searchsorted(stages, t)
            a_k = a(stage)
            if beta_const:
                b_k = (1 - (1/2)*np.sqrt(mu/(L)))**2
            else:
                b_k = (1 - (1/2)*np.sqrt(a_k*mu))**2
           # compute the loss, gradients
            loss, gk = closure(x, Di, labels_i)
            x -= a_k * gk - b_k * (x - px)
            px = temp
            num_grad_evals = num_grad_evals + batch_size
            

            if (num_grad_evals) % log_idx == 0 or (num_grad_evals) % n== 0:
                t_end=time.time()
                loss, full_grad = closure(x, D, labels)

                if verbose:
                    output = 'Epoch.: %d, Grad. norm: %.2e' % \
                             (int(t*batch_size/n), np.linalg .norm(full_grad))
                    output += ', Func. value: %e' % loss
                    output += ', Step size: %e' % a_k
                    output += ', Num gradient evaluations/n: %f' % (num_grad_evals / log_idx)
                    print(output)

                score_dict = {"itr": (t+1)}
                score_dict["time"]=t_end-t_start
                score_dict["n_grad_evals"] = num_grad_evals
                if batch_size==n:
                    score_dict["n_grad_evals_normalized"] = num_grad_evals / n
                else :
                    score_dict["n_grad_evals_normalized"] = num_grad_evals / log_idx
                score_dict["train_loss"] = loss
                score_dict["grad_norm"] = np.linalg.norm(full_grad)
                score_dict["train_accuracy"] = accuracy(x, D, labels)
                score_dict["alpha_k"] = a_k
                score_dict["beta_k"] = b_k
                if D_test is not None:
                    test_loss = closure(x, D_test, labels_test, backwards=False)
                    score_dict["test_loss"] = test_loss
                    score_dict["test_accuracy"] = accuracy(x, D_test, labels_test)
                score_list += [score_dict]
                if np.linalg.norm(full_grad) <= 1e-12:
                    print("Fast convergence!!")
                    break
                # if np.linalg.norm(full_grad) > 1e20:
                #     print("Divergence!!")
                #     break
                if np.isnan(full_grad).any():
                    print("Nannnn!!")
                    break
            t += 1
            if t >= T:
                break
            t_start=time.time()

    return score_list