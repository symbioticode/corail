import numpy as np
def calculate_erq(data_i, data_j, leverage=1):
    distance = np.sqrt(sum((data_i[k] - data_j[k])**2 for k in ['T', 'V', 'Phi', 'H']))
    return distance * leverage
