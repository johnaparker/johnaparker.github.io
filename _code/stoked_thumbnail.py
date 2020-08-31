import numpy as np
import miepy
import matplotlib.pyplot as plt
import stoked
from topics.photonic_clusters.create_lattice import hexagonal_lattice_layers
import matplotlib as mpl

from numpipe import scheduler, pbar, once
from functools import partial

job = scheduler()
nm = 1e-9
um = 1e-6
us = 1e-6
initial = 600*nm*hexagonal_lattice_layers(9)[:,:2]
Nsteps = 750000
mpl.rc('font', size=12)

def harmonic_force(time, position, orientation, stiffness):
    return -stiffness*position

class nonrec_force(stoked.interactions):
    """
    Pair-wise interaction force
    """
    def __init__(self, A, amplitude, phase, k):
        """
        Arguments:
            force_func     force function of the form F(r[dim]) -> [dim]
        """
        self.A = A
        self.amplitude = np.asarray(amplitude)
        self.phase = np.asarray(phase)
        self.k = k

        self.factor = self.A*np.multiply.outer(self.amplitude, self.amplitude)/2
        self.phase_diff = self.phase[:,np.newaxis] - self.phase[np.newaxis]

    def force(self):
        Nparticles = len(self.position)

        r_ij = self.position[:,np.newaxis] - self.position[np.newaxis]   # N x N x 3
        r = np.linalg.norm(r_ij, axis=-1)
        F_ij = np.zeros_like(r_ij)
        with np.errstate(divide='ignore'):
            F1 = self.factor/r**2*np.sin(self.k*r - self.phase_diff)
            F_ij = -r_ij*F1[...,np.newaxis]

        np.einsum('iix->ix', F_ij)[...] = 0
        F_i = np.sum(F_ij, axis=1)

        return F_i

    def torque(self):
        T_i = np.zeros_like(self.position)
        return T_i

@job.cache
def sim():
    drag = stoked.drag_sphere(75*nm, 8e-4)

    A = 2e-20
    k = 2*np.pi*1.33/(800*nm)

    # sep = 600*nm
    # initial = [[-sep/2, 0, 0], [sep/2, 0, 0]]
    # amplitude = [1,1]
    # phase = [0, .3]

    phase = np.zeros(len(initial), dtype=float)
    amplitude = np.ones(len(initial), dtype=float)

    order = np.arange(len(initial)).astype(int)
    np.random.shuffle(order)
    size = int(len(initial)//4)
    idx1 = order[:size]
    idx2 = order[size:2*size]
    idx3 = order[2*size:3*size]
    idx4 = order[3*size:]

    phase[idx2] = .5
    phase[idx3] = 1
    phase[idx4] = 1.5
    amplitude[idx2] = 1.3
    amplitude[idx3] = 1.6
    amplitude[idx4] = 1.9

    bd = stoked.brownian_dynamics(temperature=300, 
                             dt=5*us,
                             position=initial,
                             drag=drag,
                             force=partial(harmonic_force, stiffness=.3e-8),
                             interactions=[nonrec_force(A, amplitude, phase, k),
                                           stoked.double_layer_sphere(75*nm, -77e-3)])

    yield once(idx2=idx2, idx3=idx3, idx4=idx4)
    for i in pbar(range(Nsteps)):
        if i % 10 == 0:
            yield dict(pos=bd.position)

        bd.step()

@job.plots
def vis():
    var = job.load(sim)
    cmap = mpl.cm.Blues
    cmap = mpl.colors.LinearSegmentedColormap.from_list('simple', ['C0', 'C2', 'C1', 'C3'])

    colors = np.array(['C0']*len(initial), dtype=object)
    colors[var.idx2] = 'C2'
    colors[var.idx3] = 'C1'
    colors[var.idx4] = 'C3'

    fig, ax = plt.subplots(figsize=(6,6))
    for i in range(len(initial)):
        circle = plt.Circle(var.pos[-1,i,:2]/um, 3.5*.075, color=colors[i], fill=True, alpha=.9)
        ax.add_patch(circle)
    ax.autoscale()
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()

    plt.savefig('temp.png')
    plt.savefig('temp.svg')

job.run() 
