import math
import numpy as np
import dynamics

"""
Control Systems for the MPL Lander Simulation

We need to test and simulate the dynamics of the control system and we can attempt to do that here. 
These are the steps I think I will take:

Step 1: Implement a flight path, just a straight line at a slope so we dont crash the DCMs
Step 2: Implement the actual controller to follow the flight path I just created, use a simple PID controller. Maybe cascade the PIDs?
Step 3: goon bro idek atp :)
 
"""

def pid_controller(setpoint, current, kp, kd, previous_error, dt):
    error = setpoint - current
    derivative = (error - previous_error) / dt
    output = kp * error + kd * derivative
    return output, error

def FlightPath():
    # A function that will define a flight path for the lander to follow. 

    x0 = 0
    y0 = 0
    z0 = 0

    xf = 0
    yf = 10
    zf = -40

    velocity = 20 

    PointA = np.array([x0,y0,z0])
    PointB = np.array([xf,yf,zf])

    idk = np.linspace(PointA, PointB, num=100, axis=0)

    ControlPath = np.c_[idk, np.full(len(idk), velocity)]


    return ControlPath

FlightProfile = FlightPath()

def TargetPoint(path, CurrentPosition):

    PathPositions = path[:, :3]

    distances = np.linalg.norm(
        PathPositions - CurrentPosition,
        axis=1
    )

    ClosestIndex = np.argmin(distances)

    return path[ClosestIndex]
    

def PositionPID(CurrentState, Target, gains, previous_errors, dt):

    """
    Takes the current positional error and turns that into a angle that the vehicle should continue its path on to hit the target. 
    Its a PD controller with control over the pitch and yaw. 
    I went ahead and set a clamp on the max angle so the simulation doesnt crash due to bad tuning and stuff like that.
    """

    Kp, Kd = gains

    TargetX = Target[0]
    TargetY = Target[1]
    TargetZ = Target[2]

    CurrentX = CurrentState[9]
    CurrentY = CurrentState[10]
    CurrentZ = CurrentState[11]

    prev_x, prev_y, prev_z = previous_errors

    outputx, errorx = pid_controller(TargetX, CurrentX, Kp, Kd, prev_x, dt)
    outputy, errory = pid_controller(TargetY, CurrentY, Kp, Kd, prev_y, dt)
    outputz, errorz = pid_controller(TargetZ, CurrentZ, Kp, Kd, prev_z, dt)

    MAX_ANGLE = np.radians(45)

    desired_theta = np.clip(outputx, -MAX_ANGLE, MAX_ANGLE)  # pitch: fwd/back
    desired_psi   = np.clip(outputy, -MAX_ANGLE, MAX_ANGLE)  # yaw:   lateral

    updated_errors = (errorx, errory, errorz)

    return desired_theta, desired_psi, outputz, updated_errors


def AngularAccelPID(CurrentState, Target, gains, previous_errors, dt):

    """
    Takes the desired angles from above and turns them into angular accelerations. We can then use the torque equation to turn the angular accel into a 
    gimbal command. 
    """

    Kp, Kd = gains

    prevoutput = PositionPID(CurrentState, Target, gains, previous_errors, dt)

    TargetTheta = prevoutput[0]
    TargetPsi = prevoutput[1]

    CurrentTheta = CurrentState[7]
    CurrentPsi = CurrentState[8]

    prev_theta, prev_psi = previous_errors

    alphaTheta, errTheta = pid_controller(TargetTheta,CurrentTheta, Kp, Kd, prev_theta, dt)
    alphaPsi, errPsi = pid_controller(TargetPsi,CurrentPsi, Kp, Kd, prev_psi, dt)

    updated_errors = (errTheta, errPsi)

    return alphaTheta, alphaPsi, updated_errors



def ActuatorPID():

    error = 0 

def ThrottlingPID():

    error = 0