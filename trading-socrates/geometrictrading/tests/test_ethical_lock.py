import pytest
import numpy as np
from utils.ethical_lock import EthicalLock
def test_ethical_lock():
    data = {
        'momentum': 0.1, 'volatility': 0.2, 'spectral_phase': 0.3, 'entropy': 0.4,
        'price': np.random.randn(1000), 'state_prob': np.array([0.2, 0.3, 0.2, 0.2, 0.1])
    }
    lock = EthicalLock(data)
    user_input = {'phase': 'ACCUMULATION', 'allocation': [0.7, 0.3]}
    unlocked, message = lock.unlock(user_input)
    assert unlocked or 'Clé géométrique invalide' in message
