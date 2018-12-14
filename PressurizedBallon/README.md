<h3>Indroduction</h3>
Here I present a simple model of a pressurized ballon. This is achived through the numerical integration of "ballon" particles and "gas particles". Each ballon particles is connected to two other ballon particles by a spring potential, the set of all ballon particles is arranged in a circle. The gas particles ineract with the other gas particles through a lenard-jones potential. Finally the ballon and gas particles interact with one and other via a spring potential when they are within a certain charecaristic radius of one and other.

In order to model an inward pressure the value of equilibrium length of the springs connecting the ballons is set to be an order of magnitude smaller than the the initial seperation of the ballon masses. This places an effective pressure along the surface of the ballon.

Additionally due to the large number of particles required to effectivly see pressurization the n-body integrator implimented with the traditional CPython interpriter and numpy prooved to be quite slow. This was remidied using the just-in-time compiler "numba". The effect of this is an approximate 300 times speed improvment over the origional python implimentation.

We start with importing the required libraries. If you do not have numba installed this will fail. The recommended manner of installing numba is through the anaconda python stack, however you may also install it with your operating systems package manager so long as you also have llmv or llvm-lite installed.

<h3>Dependencies</h3>
To run this notebook you will need python 3.6 > and the following modules

    1) numpy
    2) matplotlib
    3) mplEasyAnimate
    4) tqdm
    5) scipy
    6) numba
