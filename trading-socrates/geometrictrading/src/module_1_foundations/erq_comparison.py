import numpy as np
def calculate_erq_native_vs_stable(data_i, data_j, data_usd, macro_factor=1.0):
    distance_native = np.sqrt(sum((data_i[k] - data_j[k])**2 for k in ['T', 'V', 'Phi', 'H']))
    distance_stable = np.sqrt(sum((data_i[k] - data_usd[k])**2 for k in ['T', 'V', 'Phi', 'H']))
    return {'native': distance_native, 'stablecoin': distance_stable * macro_factor}
def compare_spot_vs_futures(spot_data, futures_data, macro_factor=1.0):
    erq_spot = calculate_erq_native_vs_stable(spot_data['asset1'], spot_data['asset2'], spot_data['usdt'], macro_factor)
    erq_futures = calculate_erq_native_vs_stable(futures_data['asset1'], futures_data['usdt'], futures_data['usdt'], macro_factor)
    return {'spot': erq_spot, 'futures': erq_futures}
