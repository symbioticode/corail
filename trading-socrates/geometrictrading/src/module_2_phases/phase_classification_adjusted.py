def classify_phase_adjusted(state, is_stablecoin=False, macro_adjustment=0.0):
    energy = state['energy'] + macro_adjustment if is_stablecoin else state['energy']
    curvature, velocity = state['curvature'], state['velocity']
    thresholds = {'energy_low': 0.25, 'energy_median': 0.5, 'curvature_low': 0.1, 'curvature_high': 0.7}
    if energy < thresholds['energy_low'] and curvature < thresholds['curvature_low']:
        return 'ACCUMULATION'
    elif velocity > 0 and energy > thresholds['energy_median']:
        return 'EXPANSION'
    elif curvature > thresholds['curvature_high']:
        return 'CLIMAX'
    elif velocity < 0 and energy > thresholds['energy_median']:
        return 'DISTRIBUTION'
    return 'NEUTRAL'
