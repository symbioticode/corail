import numpy as np
def compute_symbiotic_tensor_adjusted(data, is_stablecoin=False, macro_noise=0.0):
    dimensions = ['T', 'V', 'Phi', 'H']
    n = len(dimensions)
    tensor = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dim_i = data[dimensions[i]] - macro_noise if is_stablecoin else data[dimensions[i]]
            dim_j = data[dimensions[j]] - macro_noise if is_stablecoin else data[dimensions[j]]
            tensor[i,j] = np.var(dim_i) if i == j else np.cov(dim_i, dim_j)[0,1]
    return tensor
