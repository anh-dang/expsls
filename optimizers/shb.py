from dependencies import *

from utils import *
from datasets import *
from objectives import *
import time

from optimizers.sls import SLS as SLS

def ld_01(k, esp=1e-8):
    return 0.5*(np.sin(k/1000)+1)

def Exp_SHB(score_list, closure, D, labels,  batch_size=1,max_epoch=100, gamma=None, alpha_t="CNST",
         method=None, x0=None, mu=1,L=1, is_sls=False, c=1.0, verbose=True, D_test=None, labels_test=None, 
         log_idx=100, ada=None, ld=None, ld_sche=None):
    """
        SHB with fixed step size for solving finite-sum problems
        Closure: a PyTorch-style closure returning the objective value and it's gradient.
        batch_size: the size of minibatches to use.
        D: the set of input vectors (usually X).
        labels: the labels corresponding to the inputs D.
        init_step_size: step-size to use
        n, d: size of the problem
    """

    n = D.shape[0]
    d = D.shape[1]
    if mu>L:
        mu = L
 
    m = int(n/batch_size)

    T=m*max_epoch
    T=max_epoch
    alpha=1
    if alpha_t=="EXP":
         alpha=(2*(L/mu)/T)**(1./T)
        # alpha=(1/T)**(1./T)

    if method=='POLYAK':
        gamma = 4/((np.sqrt(L) + np.sqrt(mu))**2)
    elif method=='GHADIMI':
        gamma = 2./L
    elif method=='WANG21':
        gamma = c/L
    elif method=='WANG22':
        gamma = 1./L
    elif method=='ADA':
        gamma = ada
    else:
        gamma = 1./(2*L)
    
    if is_sls:
        gamma=1
        L = 1./(2. * gamma)

    if x0 is None:
        x = np.zeros(d)
        x0 = np.zeros(d)
    elif isinstance(x0, np.ndarray) and x0.shape == (d,):
        x = x0.copy()
    else:
        raise ValueError('x0 must be a numpy array of size (d, )')
    x_prev = x.copy()

    num_grad_evals = 0
    num_func_evals = 0

    loss, full_grad = closure(x, D, labels)

    if verbose:
        output = 'Epoch.: %d, Grad. norm: %.2e' % \
                 (0, np.linalg.norm(full_grad))
        output += ', Func. value: %e' % loss
        output += ', Step size: %e' % gamma
        output += ', Num gradient evaluations/n: %f' % (num_grad_evals / n)
        output += ', Num function evaluations/n: %f' % (num_func_evals / n)
        print(output)

    score_dict = {"itr": 0}
    score_dict["n_func_evals"] = num_func_evals
    score_dict["n_grad_evals"] = num_grad_evals
    score_dict["n_grad_evals_normalized"] = num_grad_evals / n
    score_dict["train_loss"] = loss
    score_dict["grad_norm"] = np.linalg.norm(full_grad)
    score_dict["train_accuracy"] = accuracy(x, D, labels)
    if D_test is not None:
        test_loss = closure(x, D_test, labels_test, backwards=False)
        score_dict["test_loss"] = test_loss
        score_dict["test_accuracy"] = accuracy(x, D_test, labels_test)
    

    t=0
    eta = gamma*alpha
    lrn = gamma*alpha
    lr = lrn
    if method=='ADA':
        if ld_sche == 'osc':
            ldn = ld_01(t)
        elif ld_sche == 'add_osc':
            ldn = ld
        elif ld_sche != None:
            ldn = ld
        else:
            ldn = ld
    else:
        ldn = ((1.- 2*eta*L)/lrn*mu) * (1 - (1 - lrn*mu)**t)
    ld = ldn
    grad_sum = 0
        
    if method=='POLYAK':
        a_k = lr
        b_k = (np.sqrt(L) - np.sqrt(mu))/(np.sqrt(L) + np.sqrt(mu))
    elif method=='GHADIMI':
        a_k = lr
        b_k = mu/L
    elif method=='WANG21':
        a_k = lr
        b_k = (1 - (1/2)*np.sqrt(lr*mu))**2
    elif method=='WANG22':
        a_k = lr
        b_k = (1 - 0.5/(np.sqrt(L/mu)))**2
    elif method=='ADA':
        a_k = lr/(1 + ldn)
        b_k = ld/(1 + ldn)
    else:
        a_k = lr/(1 + ldn)
        b_k = ((1 - lr * mu)/(1 + ldn)) * ld
    
    score_dict["lambda_k"] = ld
    score_dict["alpha_k"] = a_k
    score_dict["beta_k"] = b_k
    score_list += [score_dict]

    for k in range(max_epoch):        
        t_start = time.time()


        
        if np.linalg.norm(full_grad) <= 1e-12:
            break
        if np.linalg.norm(full_grad) > 1e20:
            break
        if np.isnan(full_grad).any():
            break
        if t >= T:
            break
                   
        # Create Minibatches:
        minibatches = make_minibatches(n, m, batch_size)
        for i in range(m):
        # for i in range(1):

            # get the minibatch for this iteration
            indices = minibatches[i]
            # indices = minibatches[np.random.randint(m)]
            Di, labels_i = D[indices, :], labels[indices]

            # compute the loss, gradients
            loss, gk = closure(x, Di, labels_i)
            
            if method == 'ADA':
                lr = eta/np.sqrt(grad_sum) if grad_sum != 0 else eta
                grad_sum += np.linalg.norm(gk)
            else:
                lr = lrn
                if alpha_t=="DECR":
                    lrn=gamma*(1./(t+1))
                else:
                    lrn=gamma*(alpha**(t+1))
            
            
            if method == 'ADA':
                ld = ldn
                if ld_sche == 'osc':
                    ldn = ld_01(t+1)
                elif ld_sche == 'add_osc':
                    ldn += ld_01(t+1)
                elif ld_sche != None:
                    ldn += float(ld_sche)
                else:
                    ldn = ld
            else:
                ld = ldn
                ldn = ((1.- 2*eta*L)/lrn*mu) * (1 - (1 - lrn*mu)**(t+1))
             
            if method=='POLYAK':
                a_k = lr
                b_k = (np.sqrt(L) - np.sqrt(mu))/(np.sqrt(L) + np.sqrt(mu))
            elif method=='GHADIMI':
                a_k = lr
                b_k = mu/L
            elif method=='WANG21':
                a_k = lr
                b_k = (1 - (1/2)*np.sqrt(lr*mu))**2
            elif method=='WANG22':
                a_k = lr
                b_k = (1 - 0.5/(np.sqrt(L/mu)))**2
            elif method=='ADA':
                a_k = lr/(1 + ldn)
                b_k = ld/(1 + ldn)
            else:
                a_k = lr/(1 + ldn)
                b_k = ((1 - lr * mu)/(1 + ldn)) * ld
            temp = x.copy()
            x -= a_k * gk - b_k * (x - x_prev)
            x_prev = temp
            num_grad_evals = num_grad_evals + batch_size

            if is_sls:
                gamma,fv=SLS(x,gk,Di,labels_i,gamma,closure,(x_prev,mu,ld,lr,eta,T))
                num_func_evals+=fv
                # num_grad_evals = num_grad_evals + batch_size
                # lr=lr*alpha**(t+1)

            if (num_grad_evals) % log_idx == 0 or (num_grad_evals) % n== 0:
                t_end = time.time()
                # print(ldn)
                loss, full_grad = closure(x, D, labels)

                if verbose:
                    output = 'Epoch.: %d, Grad. norm: %.2e' % \
                             (int(t*batch_size/n), np.linalg .norm(full_grad))
                    output += ', Func. value: %e' % loss
                    output += ', Step size: %e' % gamma
                    output += ', Num gradient evaluations/%d: %f' % (log_idx,num_grad_evals / log_idx)
                    output += ', Num function evaluations/%d: %f' % (log_idx,num_func_evals / n)
                    print(output)

                score_dict = {"itr": (t+1)}
                score_dict["time"]=t_end-t_start
                score_dict["n_func_evals"] = num_func_evals
                score_dict["n_grad_evals"] = num_grad_evals
                if batch_size==n:
                    score_dict["n_grad_evals_normalized"] = num_grad_evals / n
                else:
                    score_dict["n_grad_evals_normalized"] = num_grad_evals / log_idx

                score_dict["train_loss"] = loss
                score_dict["grad_norm"] = np.linalg.norm(full_grad)
                score_dict["train_accuracy"] = accuracy(x, D, labels)
                score_dict["lambda_k"] = ld
                score_dict["alpha_k"] = a_k
                score_dict["beta_k"] = b_k
                if D_test is not None:
                    test_loss = closure(x, D_test, labels_test, backwards=False)
                    score_dict["test_loss"] = test_loss
                    score_dict["test_accuracy"] = accuracy(x, D_test, labels_test)
                score_list += [score_dict]
                if np.linalg.norm(full_grad) <= 1e-12:
                    print(np.linalg.norm(full_grad))
                    break
                if np.linalg.norm(full_grad) > 1e20:
                    print(np.linalg.norm(full_grad))
                    break
                if np.isnan(full_grad).any():
                    print(full_grad)
                    break
                t_start=time.time()
            t += 1
            if t >= T:
                break

    return score_list