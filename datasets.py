import os.path

import numpy

from dependencies import *
from haven import haven_utils as hu


LIBSVM_URL = "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/"
LIBSVM_DOWNLOAD_FN = {"rcv1": "rcv1_train.binary.bz2",
                      "mushrooms": "mushrooms",
                      "a1a": "a1a",
                      "a2a": "a2a",
                      "ijcnn": "ijcnn1.tr.bz2",
                      "w8a": "w8a",
                      "a3a":"a3a",
                      "w1a":"w1a",
                      "news": "news20.binary.bz2",
                      "covtype":"covtype.libsvm.binary.scale.bz2",
                      "phishing": "phishing"}


def load_libsvm(name, data_dir):
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    fn = LIBSVM_DOWNLOAD_FN[name]
    data_path = os.path.join(data_dir, fn)

    if not os.path.exists(data_path):
        url = urllib.parse.urljoin(LIBSVM_URL, fn)
        print("Downloading from %s" % url)
        urllib.request.urlretrieve(url, data_path)
        print("Download complete.")

    X, y = load_svmlight_file(data_path)
    # print(X.shape)
    return [X, y]


def data_load(data_dir, dataset_name, n=0, d=0, margin=1e-6, false_ratio=0, 
              is_subsample=0, is_kernelize=0,
              test_prop=0.2, split_seed=9513451, standardize=False, remove_strong_convexity=False,reuse=True,kappa=None,variance=1e-3):
    L, mu = None, None
    if (dataset_name not in [ 'synthetic','synthetic_ls','synthetic_reg','synthetic_kappa','synthetic_test']):

        # real data
        #         data = pickle.load(open(data_dir + data_name +'.pkl', 'rb'), encoding = "latin1")
        data = load_libsvm(dataset_name, data_dir='./')

        # load real dataset
        A = data[0].toarray()

        print(A.shape)
        print('hi1')
        if dataset_name in ['quantum', 'protein']:
            y = data[1].toarray().ravel()
        else:
            y = data[1]
            
    if dataset_name == "mushrooms":
        y[y==2] = -1

    if dataset_name=="synthetic":
        A, y, w_true = create_dataset(n, d, margin, false_ratio)


    if dataset_name=="synthetic_reg":
        if reuse:
            if os.path.isfile('./synt_reg_%d_%d.pkl'%(n,d)):
                with open('./synt_reg_%d_%d.pkl'%(n,d), 'rb') as handle:
                    res = pickle.load(handle)
                    A, y, w_true =res["A"],res["y"],res["w_true"]
            else:
                A, y, w_true = create_datasetReg(n, d)
                with open('./synt_reg_%d_%d.pkl' % (n, d), 'wb') as handle:
                    pickle.dump({"A":A,"y":y, "w_true":w_true},handle)
        else:
            A, y, w_true = create_datasetReg(n, d)
            with open('./synt_reg_%d_%d.pkl' % (n, d), 'wb') as handle:
                pickle.dump({"A": A, "y": y, "w_true": w_true}, handle)


    if dataset_name=="synthetic_ls":
        if reuse:
            if os.path.isfile('./synt_ls_%d_%d.pkl'%(n,d)):
                with open('./synt_ls_%d_%d.pkl'%(n,d), 'rb') as handle:
                    res = pickle.load(handle)
                    A, y, w_true =res["A"],res["y"],res["w_true"]
            else:
                A, y, w_true = create_datasetLS(n, d)
                with open('./synt_ls_%d_%d.pkl' % (n, d), 'wb') as handle:
                    pickle.dump({"A":A,"y":y, "w_true":w_true},handle)
        else:
            A, y, w_true = create_datasetLS(n, d)
            with open('./synt_ls_%d_%d.pkl' % (n, d), 'wb') as handle:
                pickle.dump({"A": A, "y": y, "w_true": w_true}, handle)
    
    if dataset_name=="synthetic_kappa" or dataset_name=="synthetic_test":
        var = str(variance)
        if reuse:
            if os.path.isfile('./synt_kappa_%d_%d_%.2f_%s.pkl'%(n,d,kappa,var)):
                with open('./synt_kappa_%d_%d_%.2f_%s.pkl'%(n,d,kappa,var), 'rb') as handle:
                    res = pickle.load(handle)
                    A, y, w_true, mu, L = res["A"],res["y"],res["w_true"],res.get('mu'),res.get('L')
            else:
                A, y, w_true, mu, L = create_dataset_kap(n, d, kappa,variance)
                with open('./synt_kappa_%d_%d_%.2f_%s.pkl' % (n, d,kappa,var), 'wb') as handle:
                    pickle.dump({"A":A,"y":y, "w_true":w_true, "mu":mu, "L":L},handle)
        else:
            A, y, w_true, mu, L = create_dataset_kap(n, d, kappa,variance)
            with open('./synt_kappa_%d_%d_%.2f_%s.pkl' % (n, d,kappa,var), 'wb') as handle:
                pickle.dump({"A":A,"y":y, "w_true":w_true, "mu":mu, "L":L},handle)

    if dataset_name == "matrix_fac":
        fname = './' + 'matrix_fac.pkl'
        if not os.path.exists(fname):
            data = generate_synthetic_matrix_factorization_data()
            hu.save_pkl(fname, data)

        A, y = hu.load_pkl(fname)

        # X_train, X_test, y_train, y_test = train_test_split(A, y, test_size=0.2, random_state=9513451)

        # training_set = torch.utils.data.TensorDataset(torch.tensor(X_train, dtype=torch.float), torch.tensor(y_train, dtype=torch.float))
        # test_set = torch.utils.data.TensorDataset(torch.tensor(X_test, dtype=torch.float), torch.tensor(y_test, dtype=torch.float))

    # subsample
    if is_subsample == 1:
        A = A[:n, :]
        y = y[:n]
        

    # split dataset into train and test sets
    if dataset_name in [ 'synthetic','synthetic_ls','synthetic_reg','synthetic_kappa','synthetic_test']:
        X_train, X_test, y_train, y_test = train_test_split(A, y, test_size=test_prop, random_state=split_seed, shuffle=False)
    else:
        X_train, X_test, y_train, y_test = train_test_split(A, y, test_size=test_prop, random_state=split_seed)

    if remove_strong_convexity:
        #for now we do not care about the test set and only focus on changing X_train such that the training objective is not SC
        U, diag, V = np.linalg.svd(X_train)
        min_sing_value = min(diag)
        diag = diag - min_sing_value
        diag = np.diag(diag)
        while diag.shape[0] != U.shape[1]:
            diag = np.append(diag, [np.zeros(diag.shape[1])], axis = 0)
        X_train = np.dot(U, np.dot(diag, V))     
        
    #For now no need to standardize    
    if standardize:
        #remove columns with same value everyhwere
        B = X_train == X_train[0, :]
        C = B.all(axis=0)
        X_train = X_train[:, ~C]
        X_test = X_test[:, ~C]
        
        mean = np.mean(X_train, axis = 0)
        std = np.std(X_train, axis=0)
        #X_train = (X_train - mean)
        #X_test = (X_test - mean)
        #X_train = (X_train - np.mean(X_train, axis = 0))/ np.std(X_train, axis = 0)
        #X_test = (X_test - np.mean(X_train, axis = 0))/ np.std(X_train, axis = 0)

    if is_kernelize == 1:
        sigma_dict = {"mushrooms": 0.5,
                      "w8a":20.0,
                      "rcv1":0.25 ,
                      "ijcnn":0.05}
        # Form kernel
        A_train, A_test = kernelize(X_train, X_test, dataset_name, data_dir=data_dir, sigma=sigma_dict[dataset_name])
    else:
        A_train = X_train
        A_test = X_test

    print('Loaded ', dataset_name, ' dataset.')
    print(A_train.shape)

    return A_train, y_train, A_test, y_test, L, mu


def kernelize(X, X_test, dataset_name, data_dir="./Data", sigma=1.0, kernel_type=0):
    n = X.shape[0]

    fname = data_dir + '/Kernel_' + str(n) + '_' + str(dataset_name) + '.p'

    if os.path.isfile(fname):

        print('Reading file ', fname)
        X_kernel, X_test_kernel = pickle.load(open(fname, "rb"))

    else:
        if kernel_type == 0:
            X_kernel = RBF_kernel(X, X, sigma=sigma)
            X_test_kernel = RBF_kernel(X_test, X, sigma=sigma)
            print('Formed the kernel matrix')
        
        if dataset_name in ["ijcnn"]:
            pickle.dump((X_kernel, X_test_kernel), open(fname, "wb"), protocol=4)
        else:
            pickle.dump((X_kernel, X_test_kernel), open(fname, "wb"))

    return X_kernel, X_test_kernel


def RBF_kernel(A, B, sigma=1.0):
    distance_2 = np.square(metrics.pairwise.pairwise_distances(X=A, Y=B, metric='euclidean'))
    K = np.exp(-1 * np.divide(distance_2, (2 * (sigma ** 2))))

    return K

def create_datasetLS(n,d):
    tW = np.random.rand(d, 1)
    X = np.random.rand(n, d)
    XTX = np.dot(X.T, X)
    # X=np.dot(np.sqrt(1/np.diag(XTX)),X)
    Y = np.matmul(X, tW) + d * np.random.normal(size=(n, 1))
    # Y = np.matmul(X, tW)
    XTY = np.dot(X.T, Y)
    Ws = np.matmul(np.linalg.inv(XTX), XTY)
    return X,Y.reshape(n,),Ws

def create_datasetReg(n,d):
    tW = np.random.rand(d, 1)
    tW = tW / np.sqrt(np.dot(tW.T, tW).squeeze())
    X = np.random.rand(n, d)
    X = 2 * X - 1
    Y = np.matmul(X, tW) + 100 * np.random.normal(size=(n, 1))
    Y = 1. / (1 + np.exp(-Y))
    Y = 2 * (Y > 0.5) - 1
    return X,Y.reshape(n,),tW

def create_dataset(n, d, gamma=0, false_ratio=0):
    # create synthetic dataset using the python utility
    # X, y = datasets.make_classification(n_samples=n, n_features=d,n_informative = d, n_redundant = 0, class_sep = 2.0 )
    # convert into -1/+1
    # y = 2 * y - 1

    # create linearly separable dataset with margin gamma
    # w_star = np.random.random((d,1))
    w_star = np.random.normal(0, 1, (d, 1))
    # normalize w_star
    # w_star = w_star / np.linalg.norm(w_star)

    num_positive = 0
    num_negative = 0
    count = 0
    nb = 0

    X = np.zeros((n, d))
    y = np.zeros((n))


    while (1):
        nb+=1
        x = np.random.normal(1, 1, (1, d))
        # normalize x s.t. || x ||_2 = 1
        x = x / np.linalg.norm(x)

        temp = np.dot(x, w_star)
        margin = abs(temp)
        sig = np.sign(temp)

        if margin > gamma * np.linalg.norm(w_star):
            #print(count, nb)

            if count % 2 == 0:

                # generate positive
                if sig > 0:
                    X[count, :] = x
                else:
                    X[count, :] = -x
                y[count] = + 1

            else:

                # generate negative
                if sig < 0:
                    X[count, :] = x
                else:
                    X[count, :] = -x
                y[count] = - 1

            count = count + 1

        if count == n:
            break

    flip_ind = np.random.choice(n, int(n * false_ratio))
    y[flip_ind] = -y[flip_ind]

    return X, y, w_star

def create_dataset_kap(n,d,kappa,variance=0):
    min_ei = 10.0
    max_ei = min_ei*kappa
    tW = np.random.rand(d, 1)
    
    q, _ = np.linalg.qr(np.random.rand(d, d))
    eigenvalues = np.linspace(np.sqrt(min_ei*n), np.sqrt(max_ei*n), d)
    D = np.diag(eigenvalues)
    symmetric_part = np.dot(np.dot(q, D), q.T)
    non_symmetric_part = np.random.rand(n-d, d)
    X = np.vstack((symmetric_part, non_symmetric_part))
    
    XTX = np.dot(X.T, X)
    Y = np.matmul(X, tW) + variance * np.random.normal(size=(n, 1))
    XTY = np.dot(X.T, Y)
    Ws = np.matmul(np.linalg.inv(XTX), XTY)
    return X,Y.reshape(n,),Ws,min_ei,max_ei

def generate_synthetic_matrix_factorization_data(xdim=6, ydim=10, nsamples=1000, A_condition_number=1e-10):
	"""
    Generate a synthetic matrix factorization dataset as suggested by Ben Recht.
		See: https://github.com/benjamin-recht/shallow-linear-net/blob/master/TwoLayerLinearNets.ipynb.
	"""
	Atrue = np.linspace(1, A_condition_number, ydim
					   ).reshape(-1, 1) * np.random.rand(ydim, xdim)
	# the inputs
	X = np.random.randn(xdim, nsamples)
	# the y's to fit
	Ytrue = Atrue.dot(X)
	data = (X.T, Ytrue.T)

	return data