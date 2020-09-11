import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import rc
from my_pytools.my_matplotlib.animation import save_animation
from matplotlib import font_manager as fm, rcParams
import os

fpath = os.path.join(rcParams["datapath"], "/Users/johnparker/Library/Fonts/Hack-Bold.ttf")
prop = fm.FontProperties(fname=fpath, size=18, )

code = """
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-0.5, 0.5, 5000)
y = np.sin(1/x)

plt.fill_between(x, y, where=y>0,
           color='C0', alpha=.8)
plt.fill_between(x, y, where=y<0,
           color='C1', alpha=.8)

plt.plot(x, y)
plt.show()
""".strip()
code += '\n'

fig, ax = plt.subplots(figsize=(6,6))

text = ax.text(-.6, 0.85, '', fontsize=25, va='top',  weight='bold', fontproperties=prop, color='white')
x = np.linspace(-.5, .5, 50000)
y = np.sin(1/x)
ax.axis('off')

line = ax.plot(x, y, lw=.2, color='white')[0]
surf1 = plt.fill_between(x, y, where=y>0, color='C0', alpha=.8)
surf2 = plt.fill_between(x, y, where=y<0, color='C1', alpha=.8)

line.set_visible(False)
surf1.set_visible(False)
surf2.set_visible(False)

def update(i):
    new_code = code[:i] + '|'
    # new_code = '>>> ' + new_code
    # new_code = new_code.replace('\n', '\n>>> ')
    text.set_text(new_code)

    if i > len(code) + 12:
        line.set_visible(True)
        text.set_visible(False)
        surf1.set_visible(True)
        surf2.set_visible(True)

    return text

fig.patch.set_facecolor([.12,]*3)
anim = FuncAnimation(fig, update, len(code)+1+50, interval=50)
save_animation(anim, 'out.mp4', savefig_kwargs={'facecolor':[.12]*3})
