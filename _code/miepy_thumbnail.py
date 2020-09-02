import numpy as np
import miepy
from topics.photonic_clusters.create_lattice import hexagonal_lattice_particles
import matplotlib.pyplot as plt
from numpipe import scheduler, pbar
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from my_pytools.my_matplotlib.layout import alpha_labels
from scipy import constants
from scipy.integrate import trapz
from my_pytools.my_matplotlib.plots import colorbar

mpl.rc('font', size=12, family='arial')
mpl.rc('mathtext', default='regular')

job = scheduler()
nm = 1e-9
um = 1e-6

Ag = miepy.materials.Ag()
radius = 150*nm
width = 2500*nm
wavelengths = np.linspace(470*nm, 880*nm, 1000)
energy = constants.h*constants.c/constants.e/wavelengths
separation = 600*nm

source = miepy.sources.gaussian_beam(width=width, polarization=[1,1j], power=1)
source = miepy.sources.plane_wave(polarization=[0,1], amplitude=1e7)
lmax = 3
water = miepy.materials.water()

@job.cache
def fields():
    pos = lattice[:]*600*nm
    # pos -= np.average(pos, axis=0)[np.newaxis]
    cluster = miepy.sphere_cluster(position=pos,
                                   radius=radius,
                                   material=Ag,
                                   source=source,
                                   wavelength=800*nm,
                                   lmax=lmax,
                                   medium=water)

    xmax = 2500*nm
    x = np.linspace(-xmax, xmax, 250)
    y = np.linspace(-xmax, xmax, 250)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    E = cluster.E_field(X, Y, Z)
    Esrc = cluster.E_source(X, Y, Z)
    # enhance = np.linalg.norm(E, axis=0)/np.linalg.norm(Esrc, axis=0)
    enhance = np.linalg.norm(E, axis=0)**2

    return dict(enhance=enhance, X=X, Y=Y, E=E)

lattice = hexagonal_lattice_particles(37) 
pos = 600*nm*lattice

@job.plots
def vis():
    from my_pytools.my_matplotlib.colors import cmap
    cmap = cmap['parula']

    fig, ax = plt.subplots(figsize=(6,6))
    var = job.load(fields)
    vmax = np.max(var.enhance)

    idx = var.X**2 + var.Y**2 > (1500*nm + 80*nm)**2
    vmin = np.min(var.enhance)

    for j in range(len(lattice)):
        circle = plt.Circle(pos[j,:2]/nm, 140, color='k', fill=False, lw=1.3)
        ax.add_patch(circle)

    # im = ax.pcolormesh(var.X/nm, var.Y/nm, var.enhance, rasterized=True, cmap=cmap, vmax=vmax, vmin=vmin)
    # im = ax.contourf(var.X/nm, var.Y/nm, var.enhance, rasterized=True, cmap=cmap, vmax=vmax, vmin=vmin)
    im = ax.contourf(var.X/nm, var.Y/nm, var.enhance, rasterized=True, cmap=cmap, levels=np.linspace(vmin, vmax/4, 40))
    skip = 15
    idx = np.s_[::skip,::skip]
    ax.quiver(var.X[idx]/nm, var.Y[idx]/nm, var.E.real[0][idx], var.E.real[1][idx], pivot='mid', alpha=.8)
    # im = ax.contourf(var.X/nm, var.Y/nm, var.enhance, rasterized=True, cmap=cmap, vmax=vmax)
    # plt.colorbar(im, ax=ax, label='field enhancement')
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim([-2500,2500])

    plt.tight_layout(pad=0)
    plt.savefig('temp.png', bbox_inches=0)

job.run()
