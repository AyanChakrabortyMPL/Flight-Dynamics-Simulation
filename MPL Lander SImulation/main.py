import dynamics as sim
import numerical_integration as integrate 
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

u_mps = 0.001
v_mps = 0.001
w_mps = 0.001

p_rps = .001
q_rps = 0.001  
r_rps = 0.001

phi_rad = 0*math.pi/180
theta_rad = 0*math.pi/180
psi_rad = 0*math.pi/180

Xword_m = 0
Yword_m = 0
Zword_m = 0

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
    Xword_m, # x-axis position in world frame
    Yword_m, # y-axis position in world frame
    Zword_m  # z-axis position in world frame
])

InitalStateVector = InitalStateVector.transpose()
n_statevector = InitalStateVector.size


#Simulation Time boundries

tstart = 0.0
tfullsimulation = 405
timeStep = 0.01

#Integration

t_s = np.arange(tstart, tfullsimulation + timeStep, timeStep)
n_timestep = t_s.size 

StateVector = np.empty((n_statevector, n_timestep), dtype=float)

StateVector[:,0] = InitalStateVector 

#Euler integration
t_s, StateVector = integrate.EulerIntegration(sim.SixDOFDynamics, t_s, InitalStateVector, timeStep, vehicle)

# Extract velocities
xpos = StateVector[9, :]
ypos = StateVector[10, :]
zpos = -StateVector[11, :]

# Rotational Equations

# Plot
sim.Animate3D(xpos,ypos,zpos)

# At t=0, with zero initial state, dx should be close to zero
# except for gravity terms. Print dx to verify:
print(sim.SixDOFDynamics(0, np.zeros(12), vehicle))