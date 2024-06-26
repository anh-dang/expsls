import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import scipy as sc
from dependencies import *


def make_closure(loss_fn, prior_prec=1e-2):
    '''Computes loss and gradient of the loss w.r.t. w
        Parameters:
            loss_fn: the loss function to use (logistic loss, hinge loss, squared error, etc)
            prior_prec: precision of the Gaussian prior (pass 0 to avoid regularization)
        Returns: a closure fn for computing the loss and gradient. '''

    def closure(w, X, y, backwards=True, model=None):
        '''Computes loss and gradient of the loss w.r.t. w
        Parameters:
            w: weight vector
            X: minibatch of input vectors
            y: labels for the input vectors
            prior_prec: precision of the Gaussian prior (pass 0 to avoid regularization)
        Returns: (loss, gradient)'''
        dev = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        # change the Numpy Arrays into PyTorch Tensors
        X = torch.tensor(X, device=dev)
        # Type of X is double, so y must be double.
        y = torch.tensor(y, dtype=torch.double, device=dev)
        w = torch.tensor(w, requires_grad=True, device=dev)

        # Compute the loss.
        loss = loss_fn(w, X, y) + (prior_prec / 2) * torch.sum(w ** 2)

        if backwards:
            # compute the gradient of loss w.r.t. w.
            loss.backward()
            # Put the gradient and loss back into Numpy.
            if torch.cuda.is_available():
                grad = w.grad.detach().cpu().numpy()
            else:
                grad = w.grad.detach().numpy()
            loss = loss.item()

            return loss, grad
        else:
            loss = loss.item()

            return loss

    return closure

# PyTorch Loss Functions

def logistic_loss(w, X, y):
    ''' Logistic Loss'''
    n,d = X.shape
    return torch.mean(torch.log(1 + torch.exp(-torch.mul(y, torch.matmul(X, w)))))

def squared_hinge_loss(w, X, y):
    n,d = X.shape
    '''Squared Hinge Loss '''
    return torch.mean((torch.max( torch.zeros(n,dtype=torch.double) , torch.ones(n,dtype=torch.double) - torch.mul(y, torch.matmul(X, w))))**2 )

def huber_loss(w, X, y, delta=1):
    diff = torch.abs(torch.matmul(X, w) - y)
    #print(torch.where(diff <= delta, 0.5 * diff**2, delta * diff - 0.5 * delta**2))
    return torch.mean(torch.where(diff <= delta, 0.5 * diff**2, delta * diff - 0.5 * delta**2))

def squared_loss(w, X, y):
    # n,d = X.shape
    '''Squared Loss'''
    return 1./2*torch.mean(( y - torch.matmul(X, w) )**2)



def param_l(X,n=1):

    '''Lmin and Lmax in stochastic case'''
    print(X.shape)
    if n==1:
        Ldiag=np.sum(X**2,axis=1)
        print(np.amax(Ldiag),np.amin(Ldiag))
        return np.amax(Ldiag),np.amin(Ldiag)

    '''Lmin and Lmax in deterministic case case'''
    eigvals=sc.linalg.svdvals(np.matmul(X.T,X))
    Lmax,Lmin=1./n * np.amax(eigvals), 1./n * np.amin(eigvals)
    print("Lmax: %f, Lmin: %f, kappa: %f"%(Lmax,Lmin,Lmax/Lmin))
    return Lmax,Lmin


def accuracy(w, X, y):
    pred = np.matmul(X,w)
    y_pred = np.divide(pred, np.abs(pred), out=np.zeros_like(pred), where=np.abs(pred)!=0)
    acc = (y_pred == y).mean()
    
    return acc

class LinearNetwork(nn.Module):
    def __init__(self, input_size, hidden_sizes, output_size, bias=True):
        super().__init__()

        # iterate averaging:
        self._prediction_params = None

        self.input_size = input_size
        if output_size:
            self.output_size = output_size
            self.squeeze_output = False
        else :
            self.output_size = 1
            self.squeeze_output = True

        if len(hidden_sizes) == 0:
            self.hidden_layers = []
            self.output_layer = nn.Linear(self.input_size, self.output_size, bias=bias)
        else:
            self.hidden_layers = nn.ModuleList([nn.Linear(in_size, out_size, bias=bias) for in_size, out_size in zip([self.input_size] + hidden_sizes[:-1], hidden_sizes)])
            self.output_layer = nn.Linear(hidden_sizes[-1], self.output_size, bias=bias)

    def forward(self, x):
        '''
            x: The input patterns/features.
        '''
        x = x.view(-1, self.input_size)
        out = x

        for layer in self.hidden_layers:
            Z = layer(out)
            # no activation in linear network.
            out = Z

        logits = self.output_layer(out)
        if self.squeeze_output:
            logits = torch.squeeze(logits)

        return logits
    
def get_model(model_name):
    if model_name == "matrix_fac_1":
        model = LinearNetwork(6, [1], 10, bias=False)

    elif model_name == "matrix_fac_4":
        model = LinearNetwork(6, [4], 10, bias=False)
    
    elif model_name == "matrix_fac_10":
        model = LinearNetwork(6, [10], 10, bias=False)

    elif model_name == "linear_fac":
        model = LinearNetwork(6, [], 10, bias=False)
    return model