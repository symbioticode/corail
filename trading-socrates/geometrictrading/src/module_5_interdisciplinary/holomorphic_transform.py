import numpy as np
def holomorphic_transform(z1, z2, hbar_r=np.pi/np.e):
    transform = z1/z2 + (z1*z2)**(hbar_r/(2*np.pi))
    return transform
