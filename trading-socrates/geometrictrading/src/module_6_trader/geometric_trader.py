import numpy as np
from scipy.fft import fft
from .phase_classification_adjusted import classify_phase_adjusted
def futures_geometric_allocation(state, leverage, maturity):
    energy = state['energy'] * leverage
    curvature = state['curvature'] * (1 - maturity/30)
    velocity = state['velocity']
    x, y, z = state['manifold_coords']
    dist_accumulation = np.linalg.norm(np.array([x, y, z]) - np.array([0, 0, 0]))
    dist_climax = np.linalg.norm(np.array([x, y, z]) - np.array([1, 1, 1]))
    threshold_accumulation, threshold_climax = 0.1, 0.9
    if dist_accumulation < threshold_accumulation:
        weight = 1 / (1 + np.exp(-(energy - 0.5)))
    elif dist_climax < threshold_climax:
        weight = 1 - 1 / (1 + np.exp(-(curvature - 0.7)))
    else:
        weight = 0.5 + 0.5 * np.tanh(velocity)
    weight = np.clip(weight, 0.1/leverage, 0.9)
    return weight, 1 - weight
class GeometricTrader:
    def __init__(self, contracts, historical_data, use_futures=False):
        self.contracts = contracts
        self.use_futures = use_futures
        self.manifold = self.compute_manifold(historical_data)
    def compute_manifold(self, data):
        macro_adjustment = 0.1 if self.use_futures else 0.0
        return {
            'T': np.diff(data['price'] - data['basis']) / data['time'],
            'V': data['implied_volatility'] - macro_adjustment,
            'Phi': fft(data['price']).dominant_frequency,
            'H': -np.sum(data['state_prob'] * np.log(data['state_prob']))
        }
    def trade(self, current_state, leverage=1, maturity=30):
        phase = classify_phase_adjusted(current_state, is_stablecoin=self.use_futures)
        allocation = futures_geometric_allocation(current_state, leverage, maturity)
        if self.use_futures and phase == 'CLIMAX':
            allocation = (0.3, 0.7)
        return {'phase': phase, 'allocation': allocation}
