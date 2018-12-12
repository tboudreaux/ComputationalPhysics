import io
import base64
from IPython.display import HTML
import os
from mplEasyAnimate import animation
from tqdm import tqdm

def display_video(filename):
    if not os.path.exists(filename):
        raise IOError('ERROR! Animation has not been generated to the local directory yet!')
    video = io.open(filename, 'r+b').read()
    encoded = base64.b64encode(video)
    HTML(data='''<video alt="test" controls>
                <source src="data:video/mp4;base64,{0}" type="video/mp4" />
             </video>'''.format(encoded.decode('ascii')))
    return HTML


def make_animation(pos, filename, plt, AutoMinorLocator, step=100):
    anim = animation(filename)
    for i in tqdm(range(110, pos.size, step)):
        fig, ax = plt.subplots(1, 1, figsize=(10, 7))
        ax.axhline(y=0, color='gray', alpha=0.5)
        ax.axhline(y=10, color='gray', alpha=0.5)
        ax.axvline(x=-5, color='gray', alpha=0.5)
        ax.axvline(x=5, color='gray', alpha=0.5)

        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        ax.tick_params(which='both', labelsize=17, direction='in', top=True, right=True)
        ax.tick_params(which='major', length=10, width=1)
        ax.tick_params(which='minor', length=5, width=1)

        ax.set_xlabel('$x$ [m]', fontsize=20)
        ax.set_ylabel('$y$ [m]', fontsize=20)

        ax.plot(pos[i-100:i, 0], pos[i-100:i, 1], 'k')

        anim.add_frame(fig)
        plt.close(fig)
    anim.close()
