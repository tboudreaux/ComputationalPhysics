import numpy as np
import matplotlib.pyplot as plt
from mplEasyAnimate import animation
from tqdm import tqdm
from numba import njit, jit
from pycuda.compiler import SourceModule
import pycuda.driver as cuda
import pycuda.autoinit

mod = SourceModule("""
    __device__ void vecAdd(double* result, double* A, double B, int sizeA){
	for (int i = 0; i < sizeA; i++){
		result[i] = A[i]+B;
	}
    }

    __device__ void vecMult(double* result, double* A, double B, int sizeA){
	for (int i = 0; i < sizeA; i++){
		result[i] = A[i]*B;
	}
    }

    __device__ void vecDiv(double* result, double* A, double B, int sizeA){
	for (int i = 0; i < sizeA; i++){
		result[i] = A[i]/B;
	}
    }

    __device__ void elementWiseAdd(double* result, double* A, double* B, int size){
	for (int i = 0; i < size; i++){
		result[i] = A[i]+B[i];
	}
    }

    __device__ void model(double* dydt, double* y0, int ID, double* pList, int bodies){
	double G = 4*3.1415*3.1415;
	double* r = new double [3];
	double rmag = 0;
	double rtemp = 0;

	for (int i = 0; i < 3; i++){
		dydt[i] = y0[i+3];
                dydt[i+3] = 0;
		r[i] = 0;
	}
	dydt[6] = 0;

	for (int body = 0; body < bodies; body++){
                rmag = 0;
		if (ID != body){
			for (int i = 0; i < 3; i++){
				// pList[body*7+i] for i in range(0, 3) access the position vec
				//      for each body
				rtemp = pList[body*7+i]-y0[i];
				rmag += rtemp*rtemp;
				r[i] = rtemp;
			}
			rmag = sqrt(rmag);
			if (rmag > 0.5){
				for (int i = 3; i < 6; i++){
					// pList[body*7+6] access the mass for each body
					dydt[i] += ((G*pList[body*7+6])/((rmag*rmag)))*(r[i-3]/rmag);
				}

			}
		}
	}
	delete[] r;
    }

    __device__ void rk4(double* y0, double* result, float h, int ID, double* pList, int bodies){
	double k1[7];
	double k2[7];
	double k3[7];
	double k4[7];

	double y1[7];
	double y2[7];
	double y3[7];

	model(k1, y0, ID, pList, bodies);
	vecMult(k1, k1, h, 7);
	vecDiv(y1, k1, 2, 7);
	elementWiseAdd(y1, y0, y1, 7);

        model(k2, y1, ID, pList, bodies);
	vecMult(k2, k2, h, 7);
	vecDiv(y2, k2, 2, 7);
	elementWiseAdd(y2, y0, y2, 7);

        model(k3, y2, ID, pList, bodies);
	vecMult(k3, k3, h, 7);
	elementWiseAdd(y3, y0, k3, 7);

        model(k4, y3, ID, pList, bodies);
	vecMult(k4, k4, h, 7);

	vecDiv(y1, k1, 6, 7);
	elementWiseAdd(result, y0, y1, 7);

	vecDiv(y1, k2, 3, 7);
	elementWiseAdd(result, result, y1, 7);

	vecDiv(y1, k3, 3, 7);
	elementWiseAdd(result, result, y1, 7);

	vecDiv(y1, k4, 6, 7);
	elementWiseAdd(result, result, y1, 7);
    }


    __global__ void time_step(double* ys, float h, int bodies, int timestep, int panel_size, int TILELENGTH){
            __shared__ double tys[7];

        int body = blockIdx.x*TILELENGTH + threadIdx.x;

        if (body < bodies){
            rk4(ys+timestep*panel_size+body*7, tys, h, body, ys+timestep*panel_size, bodies);
                    for (int j = 0; j < 7; j++){
                            // assign those values to the state array
                            ys[(timestep+1)*panel_size+body*7+j] = tys[j];
                    }
            }
    }
  """)


def int_n_model(y0, h, tf=1.0):
    ts = np.arange(0.0, tf, h)
    ys = np.zeros(shape=(ts.shape[0]+1, y0.shape[0], y0.shape[1]))
    bodies = ys.shape[1]
    model_size = 7
    timesteps = ts.shape[0]
    panel_size = bodies*model_size
    ys[0] = y0

    ys = np.resize(ys, panel_size*timesteps)
    ys = ys.astype(np.float64)
    ys_gpu_ptr = cuda.mem_alloc(ys.nbytes)
    cuda.memcpy_htod(ys_gpu_ptr, ys)

    TILELENGTH = 10

    time_step = mod.get_function("time_step")
    for i in tqdm(range(ts.shape[0])):
           time_step(ys_gpu_ptr, np.float32(h), np.int32(bodies), np.int32(i), np.int32(panel_size), np.int32(TILELENGTH), block=(bodies, 1, 1))
    ys_fetch = np.empty_like(ys)
    cuda.memcpy_dtoh(ys_fetch, ys_gpu_ptr)
    ys_fetch = np.resize(ys_fetch, (timesteps, bodies, model_size))
    return ts, ys_fetch

def make_initial_conditions(n):
    I0 = np.zeros(shape=(n, 7))
    I0[:, :3] = np.random.uniform(size=(n, 3), low=-10, high=10)
    I0[:, 3:6] = np.random.normal(size=(n, 3))
    I0[:, 6] = np.ones(shape=(n,))
    return I0

def plot_system(state, save=False):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(state[:, 0], state[:, 1], 'o')
    ax.quiver(state[:, 0], state[:, 1], state[:, 3], state[:, 4])
    if save:
        plt.savefig('Figures/System.pdf', bbox_inches='tight')
    else:
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

    ts, ys = int_n_model(I0, 0.01, tf=100.0)
    animate_system('Animations/CUDAAnimation.mp4', ys, skip=5)
