#include "flag_beamformer.h"
#include <cuComplex.h>

/*
__global__
void beamform(const cuDoubleComplex * data_in,
              const cuDoubleComplex * weights,
              float * data_out) {

	int f = blockIdx.x;
	int b = blockIdx.y;
	int t = threadIdx.x;
	int s = blockIdx.z;
	//int e = threadIdx.y;

	int i = input_idx(s*N_TIME_STI + t,f,0);//int i = input_idx(t,f,e);
	int w = weight_idx(b,f,0);//int w = weight_idx(b,f,e);
	//int c = sample_idx(t,b,f);
	// ************ Complex multiplication *************
	cuDoubleComplex elem_val;
	cuDoubleComplex weight_val;
	cuDoubleComplex new_beam;
	float beam_power;

	int e; // Element index
	float scale = 1.0/N_TIME_STI;
	//New variables//////
	__shared__ float reduced_array[N_STI_BLOC];
	//reduced_array = (float *)malloc(N_TBF*sizeof(float));
	/////////////////////
	new_beam.x = 0.0;
	new_beam.y = 0.0;

	if (t < N_TIME_STI) {

		for (e = 0; e < N_ELE; e++) { // Loop over elements
			elem_val = data_in[i+e];
			weight_val = weights[w+e];
			new_beam = cuCadd(new_beam, cuCmul(elem_val, cuConj(weight_val)));
		}

		beam_power = (float)(cuCmul(new_beam, cuConj(new_beam)).x);
		//beam_power = (float) (cuCmul(data_in[i], cuConj(weights[w])).x);
		atomicAdd(&data_out[output_idx(b,s,f)], beam_power*scale);
	}

	//New code///////////////////////////////////////////////

	//if(t<N_TIME_STI){
	//	reduced_array[t] = beam_power;
	//}
	//else{
	//	reduced_array[t] = 0.0;
	//}
	//__syncthreads();
	//
	//for(int k = blockDim.x/2; k>0; k>>=1){
	//	if(t<k){
	//		reduced_array[t] += reduced_array[t+k];
	//	}
	//	__syncthreads();
	//}
	//if(t == 0){
	//	data_out[output_idx(b,s,f)] = reduced_array[0]*scale;
	//}

	/////////////////////////////////////////////////////////
}
 */



__global__
void beamform(const unsigned char * data_in,
		const cuFloatComplex * weights,
		cuFloatComplex * beamformed) {

	int e = threadIdx.x;
	int t = blockIdx.x;
	int f = blockIdx.y;
	int b = blockIdx.z;
	//

	int i = input_idx(t,f,e);
	int w = weight_idx(b,f,e);
	//int c = sample_idx(t,b,f);
	// ************ Complex multiplication *************
	//cuDoubleComplex elem_val;
	//cuDoubleComplex weight_val;
	//cuDoubleComplex new_beam;

	//float scale = 1.0/N_ELE;
	//New variables//////
	__shared__ cuFloatComplex reduced_mul[N_ELE_BLOC];
	/////////////////////
	//new_beam.x = 0.0;
	//new_beam.y = 0.0;

	//elem_val = data_in[i];
	//weight_val = weights[w];
	//new_beam = cuCmul(elem_val, cuConj(weight_val));

	//New code///////////////////////////////////////////////

	if(e<N_ELE) {
		reduced_mul[e].x = data_in[2*i]   * weights[w].x + data_in[2*i+1] * weights[w].y;
		reduced_mul[e].y = data_in[2*i+1] * weights[w].x - data_in[2*i]   * weights[w].y;
	}
	else {
		reduced_mul[e].x = 0;
		reduced_mul[e].y = 0;
	}
	__syncthreads();

	//atomicAdd(&(beamformed[sample_idx(t,b,f)].x),reduced_mul[e].x);
	//atomicAdd(&(beamformed[sample_idx(t,b,f)].y),reduced_mul[e].y);

	for(int k = blockDim.x/2; k>0; k>>=1){
		if(e<k){
			//reduced_mul[e] = cuCaddf(reduced_mul[e], reduced_mul[e+k]);
			reduced_mul[e].x = reduced_mul[e].x + reduced_mul[e+k].x;
			reduced_mul[e].y = reduced_mul[e].y + reduced_mul[e+k].y;
		}
		__syncthreads();
	}
	if(e == 0){
		beamformed[sample_idx(t,b,f)] = reduced_mul[0];
	}


	/////////////////////////////////////////////////////////
}


__global__
void sti_reduction(const cuFloatComplex * beamformed,
		float * data_out) {

	int f = blockIdx.x;
	int b = blockIdx.y;
	int t = threadIdx.x;
	int s = blockIdx.z;

	float beam_power;
	float scale = 1.0/N_TIME_STI;

	//New variable//////
	__shared__ float reduced_array[N_STI_BLOC];
	/////////////////////

	if (t < N_TIME_STI) {
		cuFloatComplex samp = beamformed[sample_idx(s*N_TIME_STI+t,b,f)];
		//beam_power = (float)(cuCmulf(beamformed[sample_idx(s*N_TIME_STI+t,b,f)], cuConjf(beamformed[sample_idx(s*N_TIME_STI+t,b,f)])).x);
		beam_power = samp.x * samp.x + samp.y * samp.y;

		//atomicAdd(&data_out[output_idx(b,s,f)], beam_power*scale);
	}

	//New code///////////////////////////////////////////////

	if(t<N_TIME_STI){
		reduced_array[t] = beam_power;
	}
	else{
		reduced_array[t] = 0.0;
	}
	__syncthreads();

	for(int k = blockDim.x/2; k>0; k>>=1){
		if(t<k){
			reduced_array[t] += reduced_array[t+k];
		}
		__syncthreads();
	}
	if(t == 0){
		data_out[output_idx(b,s,f)] = reduced_array[0]*scale;
	}

	/////////////////////////////////////////////////////////
}


void run_beamformer(unsigned char * data, float * weights, float * out){
	// Specify grid and block dimensions
	dim3 dimBlock(N_STI_BLOC, 1, 1);
	dim3 dimGrid(N_BIN, N_BEAM, N_STI);

	dim3 dimBlock2(N_ELE_BLOC, 1, 1);
	dim3 dimGrid2(N_TIME, N_BIN, N_BEAM);
	
	unsigned char * d_data;
	cuFloatComplex * d_weights;
	cuFloatComplex * d_beamformed;
	float * d_outputs;

	cudaMalloc((void **)&d_data, 2*N_SAMP*sizeof(unsigned char));
	cudaMalloc((void **)&d_weights, N_WEIGHTS*sizeof(cuFloatComplex));
	cudaMalloc((void **)&d_beamformed, N_TBF*sizeof(cuFloatComplex));
	cudaMalloc((void **)&d_outputs, N_OUTPUTS*sizeof(float));

	cudaMemcpyAsync(d_data, data, 2*N_SAMP*sizeof(unsigned char), cudaMemcpyHostToDevice);
	cudaMemcpy(d_weights, weights, N_WEIGHTS*sizeof(cuFloatComplex), cudaMemcpyHostToDevice);

	// Run the beamformer
	beamform<<<dimGrid2, dimBlock2>>>(d_data, d_weights, d_beamformed);
	cudaError_t err_code = cudaGetLastError();
	if (err_code != cudaSuccess) {
		printf("CUDA Error: %s\n", cudaGetErrorString(err_code));
	}

	sti_reduction<<<dimGrid, dimBlock>>>(d_beamformed, d_outputs);
	err_code = cudaGetLastError();
	if (err_code != cudaSuccess) {
		printf("CUDA Error (sti_reduction): %s\n", cudaGetErrorString(err_code));
	}

	cudaMemcpy(out, d_outputs, N_OUTPUTS*sizeof(float),
			cudaMemcpyDeviceToHost);
	cudaFree(d_data);
	cudaFree(d_weights);
	cudaFree(d_outputs);
	cudaFree(d_beamformed);

}
