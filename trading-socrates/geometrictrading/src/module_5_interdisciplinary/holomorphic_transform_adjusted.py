import numpy as np
def holomorphic_transform_adjusted(z1, z2, is_stablecoin=False, macro_factor=1.0, hbar_r=np.pi/np.e):
    transform = z1/z2 + (z1*z2)**(hbar_r/(2*np.pi))
    return transform * macro_factor if is_stablecoin else transform
