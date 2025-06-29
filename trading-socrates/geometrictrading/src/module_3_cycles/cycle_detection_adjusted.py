from scipy.fft import fft
import numpy as np
def detect_dominant_cycle_adjusted(prices, is_stablecoin=False, macro_trend=None):
    if is_stablecoin and macro_trend is not None:
        prices = prices - macro_trend
    spectrum = fft(prices)
    frequencies = np.fft.fftfreq(len(prices))
    dominant_freq = frequencies[np.argmax(np.abs(spectrum))]
    return 1 / dominant_freq if dominant_freq != 0 else None
