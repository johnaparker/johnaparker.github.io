---
title: "FFT performance using NumPy, PyFFTW, and cuFFT"
excerpt: "Compare the performance of different FFT implementations, using Python"

tags:
  - Performance
  - CUDA

github_url: https://github.com/johnaparker/blog/tree/master/fft_performance
---

## Problem statement
Suppose we want to calculate the fast Fourier transform (FFT) of a two-dimensional image, and we want to make the call in Python and receive the result in a NumPy array.
The easy way to do this is to utilize NumPy's [FFT library](https://numpy.org/doc/stable/reference/routines.fft.html).
Now suppose that we need to calculate many FFTs and we care about performance.
Is NumPy's FFT algorithm the most efficient?
NumPy doesn't use [FFTW](http://www.fftw.org), widely regarded as the fastest implementation.
The [PyFFTW](https://github.com/pyFFTW/pyFFTW) library was written to address this omission. 
FFTs are also efficiently evaluated on GPUs, and the CUDA runtime library [cuFFT](https://developer.nvidia.com/cufft) can be used to calculate FFTs.


For the 2D image, we will use random data of size `n × n` with 32 bit floating point precision
```python
image = np.random.random(size=(n,n)).astype(np.float32)
```
We would like to compare the performance of three different FFT implementations at different image sizes `n`.

## Hardware

The relative performance of the CPU and GPU implementations will depend on the hardware being using. 
This is the hardware I'm using to produce the results in this post:

| **CPU**      | AMD Ryzen 2700X (8 core, 16 thread, 3.7 GHz)          |
| **GPU**      | NVIDIA RTX 2070 Super (2560 CUDA cores, 1.6 Ghz)      |

<br>

## Measuring runtime performance
To measure the runtime performance of a function, we will define `time_function` that calls the function many times, similar to IPython's `timeit`.
`time_function` is written such that it will not run longer than 0.1 seconds or the runtime of a single function call.
```python
def time_function(func, runtime=.1):
    """Time a function by running it repeatedly for at least 'runtime' seconds"""
    start = timer()
    t = 0
    count = 0

    while t < runtime:
        t0 = timer()
        func()
        tf = timer()
        t += tf - t0

        count += 1

    return t/count
```

## NumPy implementation
In NumPy, we can use `np.fft.rfft2` to compute the real-valued 2D FFT of the image:
```python
numpy_fft = partial(np.fft.rfft2, a=image)
numpy_time = time_function(numpy_fft)*1e3  # in ms
```
This measures the runtime in milliseconds. 
This can be repeated for different image sizes, and we will plot the runtime at the end.

## PyFFTW implementation
In PyFFTW, we have to create `pyFFTW.empty_aligned` arrays to store the image and the FFT output.
The FFT is performed by calling `pyfftw.FFTW` on these arrays, and the number of threads can also be specified here (I choose 16 in my case):

```python
### Prepare the image for PyFFTW
a = pyfftw.empty_aligned((n,n), dtype='float32')
b = pyfftw.empty_aligned((a.shape[0], a.shape[1]//2 + 1),  dtype='complex64')
a[...] = image
fft_object = pyfftw.FFTW(a, b, threads=16)  # specify number of CPU threads to use

pyfftw_time = time_function(fft_object)*1e3  # in ms
```

## cuFFT implementation
Finally, we can compute the FFT on the GPU.
This can be done entirely with the CUDA runtime library and the `cufft` library.
In C++, the we can write the function `gpu_fft` to perform the FFT:

```cpp
void gpu_fft(const int dataH, const int dataW, const int iterations) {
    /** 
    * @param dataH image height
    * @param dataW image width
    * @param iterations number of FFT iterations
    **/ 

    // prepare the data
    float *h_Data;
    float *d_Data;
    cuComplex *d_DataSpectrum;

    h_Data = (float *)malloc(dataH*dataW * sizeof(float));
    cudaMalloc((void **)&d_Data, dataH*dataW * sizeof(float));
    cudaMalloc((void **)&d_DataSpectrum,   dataH * (dataW / 2 + 1) * sizeof(cuComplex));

    // generate random image
    for (int i = 0; i < dataH * dataW; i++)
    {
        h_Data[i] = getRand();
    }
    cudaMemcpy(d_Data, h_Data,   dataH*dataW * sizeof(float), cudaMemcpyHostToDevice);

    // create cuFFT plan
    cufftHandle fftPlanFwd;
    cufftPlan2d(&fftPlanFwd, dataH, dataW, CUFFT_R2C);

    // compute iterations of FFT
    for (int i = 0; i < iterations; i++) {
        cufftExecR2C(fftPlanFwd, (cufftReal *)d_Data, (cufftComplex *)d_DataSpectrum);
        cudaDeviceSynchronize();
    }

    // free data
    free(h_Data);
    cufftDestroy(fftPlanFwd);
    cudaFree(d_Data);
    cudaFree(d_DataSpectrum);
}
```
Notice that here we pass in the width and height of the image, and generate the random image in C++. 
That data is then transferred to the GPU.
The `iterations` parameters specifies the number of times we perform the exact same FFT (to measure runtime).
Note that in doing so we are not copying the image from CPU (host) to GPU (device) at each iteration, so the performance measurement does not include the time to copy the image.
Depending on the application, the performance of `cudaMemcpy` may be critical.


This C++ function can be easily exposed to Python using `pybind11` with the following code:
```cpp
PYBIND11_MODULE(fft, m) {
    m.def("gpu_fft", gpu_fft, "dataH"_a, "dataW"_a, "iterations"_a)
}
```
The full code is available on [GitHub]({{ page.github_url }}/fft.cpp).

Then we can measure the performance of this GPU implementation using the `time_function`:

```python
iterations = 10000
cuda_fft = partial(gpu_fft, n, n, iterations)
cuda_time = time_function(cuda_fft)*1e3/iterations  # in ms
```
Here, I chose 10,000 iterations of the FFT, so that `cudaMemcpy` only runs for every 10,000 iterations.
If you choose `iterations=1`, the measured runtime would include memory allocation and deallocation, which may not be needed depending on your application.

## Performance comparison
With all of the functions defined, we can time them at different image sizes `n`:
<figure style="width: 100%; max-width: 100%" class="align-center">
  <img src="/assets/img/posts/fft_performance/fft_benchmark.svg" alt="">
</figure> 
The results on the left show the runtime for each function on a log-log scale.
We can see that for all but the smallest of image sizes, `cuFFT > PyFFTW > NumPy`.
On the right is the speed increase of the cuFFT implementation relative to the NumPy and PyFFTW implementations.
For the largest images, cuFFT is an order of magnitude faster than PyFFTW and two orders of magnitude faster than NumPy.
