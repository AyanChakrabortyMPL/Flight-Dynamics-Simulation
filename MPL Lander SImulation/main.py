import dynamics as dynamics
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import numpy as np

#Vehicle Physical Definitions

MomentInertia_xx = 500     # roll  — small for a slender rocket (kg·m²)
MomentInertia_yy = 8000    # pitch — large, mass spread along length
MomentInertia_zz = 8000    # yaw   — same as pitch by symmetry

ProductOfInertia_xz = 0
ProductOfInertia_zx = 0


vehicle = {
    'mass_kg': 86,
    'Jxz_kgm2': ProductOfInertia_xz,
    'Jzx_kgm2': ProductOfInertia_zx,
    'Jxx_kgm2': MomentInertia_xx,
    'Jyy_kgm2': MomentInertia_yy,
    'Jzz_kgm2': MomentInertia_zz,
}

#Initialization
u_mps = 0
v_mps = 0
w_mps = 0

p_rps = 0
q_rps = 0  
r_rps = 0

phi_rad = 0*math.pi/180
theta_rad = 0*math.pi/180
psi_rad = 0*math.pi/180

Xworld_m = 0
Yworld_m = 0
Zworld_m = 0

InitalStateVector = np.array([
    u_mps, # x-axis velocity in body frame
    v_mps, # y-axis velocity in body frame
    w_mps, # z-axis velocity in body frame
    p_rps, #roll rate in body frame
    q_rps, #pitch rate in body frame
    r_rps, #yaw rate in body frame
    phi_rad, #roll angle in world frame
    theta_rad, #pitch angle in world frame
    psi_rad, #yaw angle in world frame
    Xworld_m, # x-axis position in world frame
    Yworld_m, # y-axis position in world frame
    Zworld_m  # z-axis position in world frame
])

def EulerForwardIntegration():
    return 0