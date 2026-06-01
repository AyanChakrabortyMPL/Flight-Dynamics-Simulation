import math
import numpy as np


def ThrustCurve(t, duration, thrust):
    ramp_time = 0.2 * duration
    steady_start = ramp_time

    if t < ramp_time:
        return (thrust / ramp_time) * t  # ramp up
    elif t <= duration:
        return thrust  # steady
    else:
        return 0

def SixDOFDynamics(t_s, StateVector, vehicle):

    dx = np.zeros((12))

    #Unpack State Vector
    u_mps = StateVector[0]
    v_mps = StateVector[1]
    w_mps = StateVector[2]

    p_rps = StateVector[3]
    q_rps = StateVector[4]   
    r_rps = StateVector[5]

    phi_rad = StateVector[6]
    theta_rad = StateVector[7]
    psi_rad = StateVector[8]

    Xword_m = StateVector[9]
    Yword_m = StateVector[10]
    Zword_m = StateVector[11]
    
    #Unpack Vehicle Definitions

    m_kg = vehicle['mass_kg']
    Jxz_kgm2 = vehicle['Jxz_kgm2']
    Jzx_kgm2 = vehicle['Jzx_kgm2']
    Jxx_kgm2 = vehicle['Jxx_kgm2']
    Jyy_kgm2 = vehicle['Jyy_kgm2']
    Jzz_kgm2 = vehicle['Jzz_kgm2']

    #Gravity data 
    gravityZaxis_ms2 = 9.80665

    #Gravity in body axis (Rotation Matrix)

    gravitybodyX_mps2 = -math.sin(theta_rad)*gravityZaxis_ms2
    gravitybodyY_mps2 = math.sin(phi_rad)*math.cos(theta_rad)*gravityZaxis_ms2
    gravitybodyZ_mps2 = math.cos(phi_rad)*math.cos(theta_rad)*gravityZaxis_ms2

    #External Forces

    Fx_b_N = 0
    Fy_b_N = ThrustCurve(t_s, 6, 15000)
    Fz_b_N = -ThrustCurve(t_s, 15, 150000)

    #External Moments

    L_b_kgm2ps2 = ThrustCurve(t_s, 2, 100)
    M_b_kgm2ps2 = 0
    N_b_kgm2ps2 = 0


    #Translational Equations

    #x axis velocity 
    dx[0] = (1/m_kg * Fx_b_N) + gravitybodyX_mps2 - (w_mps * q_rps) + (v_mps*r_rps)

    #y-axis velocity
    dx[1] = (1/m_kg * Fy_b_N) + gravitybodyY_mps2 - (u_mps * r_rps) + (w_mps * p_rps)

    #z-axis velocity
    dx[2] = (1/m_kg * Fz_b_N) + gravitybodyZ_mps2 - (v_mps * p_rps) + (u_mps * q_rps)

    #Rotational Equation

    #Denominator 
    denominator = ((Jxx_kgm2 * Jzz_kgm2) - Jxz_kgm2**2) 

    #Roll Equation (p)
    dx[3] = ((Jxz_kgm2*(Jxx_kgm2-Jyy_kgm2+Jzz_kgm2)*p_rps*q_rps) - ((Jzz_kgm2*(Jzz_kgm2-Jyy_kgm2)+(Jxz_kgm2**2))*q_rps*r_rps) + (Jzz_kgm2*L_b_kgm2ps2) + (Jxz_kgm2*N_b_kgm2ps2))/denominator

    #Pitch Equation (q)
    dx[4] = (((Jzz_kgm2-Jxx_kgm2)*p_rps*r_rps) - (Jxz_kgm2*(p_rps**2 - r_rps**2)) + M_b_kgm2ps2)/Jyy_kgm2

    #Yaw Equation (r)
    dx[5] = (((Jxx_kgm2*(Jxx_kgm2-Jyy_kgm2)+(Jxz_kgm2**2))*p_rps*q_rps) + (Jxz_kgm2*(Jxx_kgm2-Jyy_kgm2+Jzz_kgm2)*q_rps*r_rps) + (Jxz_kgm2*L_b_kgm2ps2) + (Jxx_kgm2*N_b_kgm2ps2))/denominator

    #Kinematic Equation 
    dx[6] = p_rps+math.sin(phi_rad)*math.tan(theta_rad)*q_rps+math.cos(phi_rad)*math.tan(theta_rad)*r_rps
    dx[7] = math.cos(phi_rad)*q_rps-math.sin(phi_rad)*r_rps
    dx[8] = math.sin(phi_rad)/math.cos(theta_rad)*q_rps+math.cos(phi_rad)/math.cos(theta_rad)*r_rps

    cos_phi = math.cos(phi_rad)
    sin_phi = math.sin(phi_rad)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    cos_psi = math.cos(psi_rad)
    sin_psi = math.sin(psi_rad)


    #Position 
    dx[9] = (cos_theta*cos_psi*u_mps)+((-cos_phi*sin_psi)+(sin_phi*sin_theta*cos_psi))*v_mps+((sin_phi*sin_psi)+(cos_phi*sin_theta*cos_psi))*w_mps
    dx[10] = (cos_theta*sin_psi*u_mps)+((cos_phi*cos_psi)+(sin_phi*sin_theta*sin_psi))*v_mps+((-sin_phi*cos_psi)+(cos_phi*sin_theta*sin_psi))*w_mps
    dx[11] = (-sin_theta*u_mps)+(sin_phi*cos_theta*v_mps)+(cos_phi*cos_theta*w_mps)

    return dx

def Animate3D(xpos, ypos, zpos, speed=50, fps=120, trail_length=1000):

    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    # Remove bad values (VERY important for your crash issue)
    valid = np.isfinite(xpos) & np.isfinite(ypos) & np.isfinite(zpos)
    xpos, ypos, zpos = xpos[valid], ypos[valid], zpos[valid]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # ---- FIXED CAMERA (stable view, no “dot in center” bug)
    max_range = max(
        xpos.max() - xpos.min(),
        ypos.max() - ypos.min(),
        zpos.max() - zpos.min()
    ) / 2

    mid_x = (xpos.max() + xpos.min()) / 2
    mid_y = (ypos.max() + ypos.min()) / 2
    mid_z = (zpos.max() + zpos.min()) / 2

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title("3D Flight Animation")

    # Objects
    trail, = ax.plot([], [], [], lw=2)
    point, = ax.plot([], [], [], 'ro', markersize=6)

    # ---- FRAME CONTROL (speed works properly here)
    def update(frame):

        i = frame * speed

        if i >= len(xpos):
            i = len(xpos) - 1

        start = max(0, i - trail_length)

        # trail
        trail.set_data(xpos[start:i], ypos[start:i])
        trail.set_3d_properties(zpos[start:i])

        # vehicle
        point.set_data([xpos[i]], [ypos[i]])
        point.set_3d_properties([zpos[i]])

        return trail, point

    ani = FuncAnimation(
        fig,
        update,
        frames=len(xpos) // speed,
        interval=1000 / fps,
        blit=False,
        cache_frame_data=False
    )

    plt.show()

def Animate2D(xpos, zpos, speed=50, fps=60, trail_length=50000):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    # Strip NaN / inf
    valid = np.isfinite(xpos) & np.isfinite(zpos)
    xpos, zpos = xpos[valid], zpos[valid]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlabel("Downrange (m)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("2D Flight Path")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # Fixed axes — sized to the full trajectory
    pad_x = (xpos.max() - xpos.min()) * 0.05 + 1
    pad_z = (zpos.max() - zpos.min()) * 0.05 + 1
    ax.set_xlim(xpos.min() - pad_x, xpos.max() + pad_x)
    ax.set_ylim(min(0, zpos.min() - pad_z), zpos.max() + pad_z)

    # Ground line
    ax.axhline(0, color="saddlebrown", linewidth=1.5, alpha=0.6)

    trail,  = ax.plot([], [], lw=1.5, color="steelblue", alpha=0.6)
    point,  = ax.plot([], [], "ro", markersize=7)
    text    = ax.text(0.02, 0.96, "", transform=ax.transAxes,
                      va="top", fontsize=9, color="gray")

    def update(frame):
        i     = min(frame * speed, len(xpos) - 1)
        start = max(0, i - trail_length)

        trail.set_data(xpos[start:i], zpos[start:i])
        point.set_data([xpos[i]], [zpos[i]])
        text.set_text(f"x={xpos[i]:.0f} m   alt={zpos[i]:.0f} m")
        return trail, point, text

    ani = FuncAnimation(
        fig, update,
        frames=len(xpos) // speed,
        interval=1000 / fps,
        blit=False,
        cache_frame_data=False
    )

    plt.tight_layout()
    plt.show()