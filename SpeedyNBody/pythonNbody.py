import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mplEasyAnimate import animation
from tqdm import tqdm
from scipy.special import comb
from scipy.special import factorial
from numba import njit, jit

G = 4*np.pi**2 # AU^3 yr^-2 Msolar^-1

def rk4(y0, h, ID, pList, massList):
    k1 = h*nbody(y0, ID, pList, massList)
    k2 = h*nbody(y0+k1/2, ID, pList, massList)
    k3 = h*nbody(y0+k2/2, ID, pList, massList)
    k4 = h*nbody(y0+k3, ID, pList, massList)
    return y0 + (k1/6)+(k2/3)+(k3/3)+(k4/6)


def nbody(I0, ID, pList, massList):
    dydt = np.zeros(6)
    dydt[:3] = I0[3:]
    m = massList[ID]
    for i in range(len(pList)):
        if ID != i:
            r = pList[i, :3] - I0[:3]
            rmag = np.sqrt(r[0]**2+r[1]**2+r[2]**2)
            if rmag > 0.5:
                rhat = r/rmag
                AMag = (G*massList[i])/((rmag)**2)
                dydt[3:] += AMag*rhat

    return dydt

def int_n_model(y0, massList, h, tf=1.0):
    ts = np.arange(0.0, tf, h)
    ys = np.zeros(shape=(ts.shape[0]+1, y0.shape[0], y0.shape[1]))
    ys[0] = y0
    for i in tqdm(range(ts.shape[0])):
        for ID in range(len(ys[i])):
            ys[i+1][ID] = rk4(ys[i, ID], h, ID, ys[i], massList)
    return ts, ys

def make_initial_conditions(n):
    I0 = np.zeros(shape=(n, 6))
    I0[:, :3] = np.random.uniform(size=(n, 3), low=-10, high=10)
    I0[:, 3:] = np.random.normal(size=(n, 3))
    return I0

def plot_system(state):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(state[:, 0], state[:, 1], 'o')
    ax.quiver(state[:, 0], state[:, 1], state[:, 3], state[:, 4])
    return fig, ax

def animate_system(filename, state, fps=30, skip=1):
    anim = animation(filename, fps=fps)

    for i, y in tqdm(enumerate(state), total=state.shape[0]):
        if i%skip == 0:
            fig, ax = plot_system(y)
            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 15)
            anim.add_frame(fig)
            plt.close(fig)

    anim.close()
    del(anim)


if __name__ == '__main__':
    n = 100
    I0 = make_initial_conditions(n)
    massList = np.ones(shape=(n,))

    ts, ys = int_n_model(I0, massList, 0.01, tf=10.0)
    animate_system('Animations/PythonAnimation.mp4', ys, skip=5)
