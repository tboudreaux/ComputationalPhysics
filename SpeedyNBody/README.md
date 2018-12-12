<h1>Thomas M. Boudreaux</h1>
<h2>Multiple implimentations of a gravitational Nbody simulation for speed comparisons</h2>


<h3>Introduction</h3>
I implimented a gravitational Nbody simulation in three ways. One in python with numpy, one in python with numba, and one in python with pyCUDA. I found that, as you would expect the numpy implimentation was by far the slowest, (12 minutes to run 100 particles for 1000 timesteps), then the numba implimentation (20 seconds for 100 particles over 1000 timesteps), and the pyCUDA implimentation was the fastest, taking only 1.5 seconds to integrate 100 particles over 1000 timesteps.

If you want to run these you can however you will need CUDA installed and an NVIDIA graphics card. I tested these on a GTX 970.