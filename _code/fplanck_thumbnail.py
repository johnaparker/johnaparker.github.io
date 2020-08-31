import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
from fplanck import fokker_planck, boundary, gaussian_pdf, harmonic_potential
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
from my_pytools.my_matplotlib.colors import cmap

mpl.rc('font', size=15)
cmap = cmap['parula']

nm = 1e-9
viscosity = 8e-4
radius = 50*nm
drag = 6*np.pi*viscosity*radius

U = harmonic_potential((0,0), 1e-6)
sim = fokker_planck(temperature=300, drag=drag, extent=[600*nm, 600*nm],
            resolution=5*nm, boundary=boundary.reflecting, potential=U)

### time-evolved solution
pdf = gaussian_pdf(center=(-150*nm, -150*nm), width=30*nm)
p0 = pdf(*sim.grid)

Nsteps = 200
time, Pt = sim.propagate_interval(pdf, 2e-3, Nsteps=Nsteps)

### animation
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'), figsize=(6,6))

surf = ax.plot_surface(*sim.grid/nm, Pt[40], cmap=cmap)

ax.set_zlim([0,np.max(Pt)/6])
ax.autoscale(False)

# ax.set(xlabel='x (nm)', ylabel='y (nm)', zlabel='normalized PDF')
kwargs = dict(labelpad=-2, fontsize=16, weight='bold')
ax.set_xlabel('x', **kwargs)
ax.set_ylabel('y', **kwargs)
ax.set_zlabel('PDF', rotation=90, **kwargs)
ax.xaxis.set_ticklabels([])
ax.yaxis.set_ticklabels([])
ax.zaxis.set_ticklabels([])
plt.tight_layout()
# ax.axis('off')
plt.savefig('temp.png', bbox_inches='tight')

plt.show()
