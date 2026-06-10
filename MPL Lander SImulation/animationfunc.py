import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def Animate2D(t_s, StateHistory):

    x = StateHistory[9, :]
    z = StateHistory[11, :]

    fig, ax = plt.subplots()

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Z (m)")

    ax.set_xlim(np.min(x)-10, np.max(x)+10)
    ax.set_ylim(np.min(z)-10, np.max(z)+10)

    rocket, = ax.plot([], [], 'o')

    # Timestamp text
    time_text = ax.text(
        0.02, 0.95,
        '',
        transform=ax.transAxes,
        fontsize=12
    )

    def init():
        rocket.set_data([], [])
        time_text.set_text('')
        return rocket, time_text

    def update(frame):

        rocket.set_data([x[frame]], [z[frame]])

        time_text.set_text(
            f'Time = {t_s[frame]:.2f} s'
        )

        return rocket, time_text

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(t_s),
        init_func=init,
        interval=20,
        blit=True
    )

    plt.show()

def PlotVerticalVelocity(t_s, StateHistory):

    z = StateHistory[11, :]

    vertical_velocity = np.gradient(z, t_s)

    plt.figure(figsize=(8,5))

    plt.plot(t_s, vertical_velocity)

    plt.xlabel("Time (s)")
    plt.ylabel("Vertical Velocity (m/s)")
    plt.title("Vertical Velocity vs Time")

    plt.grid(True)

    plt.show()
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec


def PlotFlightPath(t_s, StateHistory, interval=30):
    """
    Live-animates the flight path (side view + 3D) with a time counter.

    Parameters
    ----------
    t_s          : 1-D array of time stamps (s)
    StateHistory : (12, N) state matrix
    interval     : milliseconds between frames
    """
    x = StateHistory[9, :]
    y = StateHistory[10, :]
    z = -StateHistory[11, :]  # flip sign: NED Z points down

    N = len(t_s)

    # ── Pre-compute axis limits so they never rescale ──────────────────────
    pad = lambda lo, hi, f=0.05: (lo - abs(hi - lo) * f, hi + abs(hi - lo) * f)

    xlim2d = pad(x.min(), x.max())
    zlim2d = pad(z.min(), z.max())

    xlim3d = pad(x.min(), x.max())
    ylim3d = pad(y.min(), y.max())
    zlim3d = pad(z.min(), z.max())

    # ── Layout ─────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 6))
    gs = GridSpec(2, 2, figure=fig,
                  height_ratios=[20, 1], hspace=0.35, wspace=0.35)

    ax2d  = fig.add_subplot(gs[0, 0])
    ax3d  = fig.add_subplot(gs[0, 1], projection='3d')
    ax_tb = fig.add_subplot(gs[1, :])   # time-bar row

    # ── 2D side-view setup ─────────────────────────────────────────────────
    ax2d.set_xlim(*xlim2d)
    ax2d.set_ylim(*zlim2d)
    ax2d.set_xlabel("Downrange Distance X (m)")
    ax2d.set_ylabel("Altitude (m)")
    ax2d.set_title("Flight Path – Side View")
    ax2d.grid(True)

    ghost2d,  = ax2d.plot(x, z, color='lightsteelblue', lw=1, ls='--', alpha=0.4)
    line2d,   = ax2d.plot([], [], color='royalblue', lw=2)
    head2d,   = ax2d.plot([], [], 'o', color='royalblue', ms=6)

    # ── 3D setup ───────────────────────────────────────────────────────────
    ax3d.set_xlim(*xlim3d)
    ax3d.set_ylim(*ylim3d)
    ax3d.set_zlim(*zlim3d)
    ax3d.set_xlabel("X – North (m)")
    ax3d.set_ylabel("Y – East (m)")
    ax3d.set_zlabel("Altitude (m)")
    ax3d.set_title("3D Flight Path")
    ax3d.grid(True)

    ax3d.scatter(x[0],  y[0],  z[0],  color='green', s=50, label='Launch',  zorder=5)
    ax3d.scatter(x[-1], y[-1], z[-1], color='red',   s=50, label='Landing', zorder=5)
    ax3d.plot(x, y, z, color='lightsteelblue', lw=1, ls='--', alpha=0.4)
    ax3d.legend(fontsize=8)

    line3d, = ax3d.plot([], [], [], color='royalblue', lw=2)
    head3d, = ax3d.plot([], [], [], 'o', color='royalblue', ms=6)

    # ── Time counter / bar ─────────────────────────────────────────────────
    ax_tb.set_xlim(t_s[0], t_s[-1])
    ax_tb.set_ylim(0, 1)
    ax_tb.set_yticks([])
    ax_tb.set_xlabel("Time (s)", fontsize=9)
    ax_tb.set_title("")

    bar_bg = ax_tb.axhspan(0, 1, color='lightgrey', alpha=0.5)
    bar_fill, = ax_tb.fill([t_s[0], t_s[0], t_s[0], t_s[0]],
                           [0, 0, 1, 1],
                           color='royalblue', alpha=0.6)

    time_text = ax_tb.text(
        0.5, 0.5, f"t = {t_s[0]:.2f} s",
        transform=ax_tb.transAxes,
        ha='center', va='center',
        fontsize=10, fontweight='bold', color='white',
        bbox=dict(boxstyle='round,pad=0.2', fc='royalblue', ec='none')
    )

    fig.suptitle("Live Flight Path", fontsize=13, fontweight='bold')

    # ── Animation update ───────────────────────────────────────────────────
    def update(frame):
        i = frame + 1                   # draw 1..N

        line2d.set_data(x[:i], z[:i])
        head2d.set_data([x[i-1]], [z[i-1]])

        line3d.set_data(x[:i], y[:i])
        line3d.set_3d_properties(z[:i])
        head3d.set_data([x[i-1]], [y[i-1]])
        head3d.set_3d_properties([z[i-1]])

        # progress bar
        t_now = t_s[i-1]
        bar_fill.set_xy([[t_s[0], 0], [t_s[0], 1],
                         [t_now,  1], [t_now,  0]])
        time_text.set_text(f"t = {t_now:.2f} s")

        return line2d, head2d, line3d, head3d, bar_fill, time_text

    ani = animation.FuncAnimation(
        fig, update,
        frames=N,
        interval=interval,
        blit=False,        # blit=True conflicts with 3D axes on some backends
        repeat=False
    )

    plt.tight_layout()
    plt.show()
    return ani   # keep reference so GC doesn't kill it


# ──────────────────────────────────────────────────────────────────────────────

def PlotAllStates(t_s, StateHistory, interval=30):
    """
    Live-animates all 12 states vs time with a shared time counter.

    Parameters
    ----------
    t_s          : 1-D array of time stamps (s)
    StateHistory : (12, N) state matrix
    interval     : milliseconds between frames
    """
    labels = [
        ('u (m/s)',   'Body X Velocity'),
        ('v (m/s)',   'Body Y Velocity'),
        ('w (m/s)',   'Body Z Velocity'),
        ('p (rad/s)', 'Roll Rate'),
        ('q (rad/s)', 'Pitch Rate'),
        ('r (rad/s)', 'Yaw Rate'),
        ('φ (rad)',   'Roll Angle'),
        ('θ (rad)',   'Pitch Angle'),
        ('ψ (rad)',   'Yaw Angle'),
        ('X (m)',     'World X Position'),
        ('Y (m)',     'World Y Position'),
        ('Z (m)',     'World Z Position'),
    ]

    N = len(t_s)

    # ── Pre-compute y-limits ───────────────────────────────────────────────
    def ylim(row, margin=0.08):
        lo, hi = StateHistory[row].min(), StateHistory[row].max()
        span = max(hi - lo, 1e-9)
        return lo - span * margin, hi + span * margin

    # ── Layout: 4×3 grid + time-bar row ───────────────────────────────────
    fig = plt.figure(figsize=(16, 11))
    gs = GridSpec(5, 3, figure=fig,
                  height_ratios=[6, 6, 6, 6, 1],
                  hspace=0.55, wspace=0.38)

    axes = [fig.add_subplot(gs[r, c]) for r in range(4) for c in range(3)]
    ax_tb = fig.add_subplot(gs[4, :])

    lines  = []
    ghosts = []

    for i, (ax, (ylabel, title)) in enumerate(zip(axes, labels)):
        ax.set_xlim(t_s[0], t_s[-1])
        ax.set_ylim(*ylim(i))
        ax.set_title(title, fontsize=9)
        ax.set_xlabel('Time (s)', fontsize=7)
        ax.set_ylabel(ylabel, fontsize=7)
        ax.tick_params(labelsize=7)
        ax.grid(True, linewidth=0.5)

        # ghost trace
        g, = ax.plot(t_s, StateHistory[i, :],
                     color='lightsteelblue', lw=0.8, ls='--', alpha=0.4)
        ghosts.append(g)

        # live trace
        ln, = ax.plot([], [], color='royalblue', lw=1.5)
        lines.append(ln)

    # ── Time bar ───────────────────────────────────────────────────────────
    ax_tb.set_xlim(t_s[0], t_s[-1])
    ax_tb.set_ylim(0, 1)
    ax_tb.set_yticks([])
    ax_tb.set_xlabel("Time (s)", fontsize=9)

    ax_tb.axhspan(0, 1, color='lightgrey', alpha=0.5)
    bar_fill, = ax_tb.fill([t_s[0], t_s[0], t_s[0], t_s[0]],
                           [0, 0, 1, 1],
                           color='royalblue', alpha=0.6)

    time_text = ax_tb.text(
        0.5, 0.5, f"t = {t_s[0]:.2f} s",
        transform=ax_tb.transAxes,
        ha='center', va='center',
        fontsize=10, fontweight='bold', color='white',
        bbox=dict(boxstyle='round,pad=0.2', fc='royalblue', ec='none')
    )

    fig.suptitle('All States vs Time', fontsize=13, fontweight='bold')

    # ── Animation update ───────────────────────────────────────────────────
    def update(frame):
        i = frame + 1
        t_slice = t_s[:i]

        for row, ln in enumerate(lines):
            ln.set_data(t_slice, StateHistory[row, :i])

        t_now = t_s[i-1]
        bar_fill.set_xy([[t_s[0], 0], [t_s[0], 1],
                         [t_now,  1], [t_now,  0]])
        time_text.set_text(f"t = {t_now:.2f} s")

        return lines + [bar_fill, time_text]

    ani = animation.FuncAnimation(
        fig, update,
        frames=N,
        interval=interval,
        blit=False,
        repeat=False
    )

    plt.tight_layout()
    plt.show()
    return ani

