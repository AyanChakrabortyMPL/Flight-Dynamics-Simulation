import numpy as np

def EulerIntegration(f, t_s, x0, h_s, vehicle):

    n_states = len(x0)
    x = np.zeros((n_states, len(t_s)))

    x[:, 0] = x0

    for i in range(1, len(t_s)):
        dx = f(t_s[i-1], x[:, i-1], vehicle)
        x[:, i] = x[:, i-1] + h_s * dx

    return t_s, x