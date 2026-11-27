# Digital Signal Processing: Cooley-Tukey Fast Fourier Transform

The Discrete Fourier Transform maps N evenly spaced time-domain samples into frequency components. Direct computation scales as O(N^2) operations.

The Radix-2 Cooley-Tukey Fast Fourier Transform (FFT) splits the signal recursively into even and odd subsets, lowering complexity to O(N log N) via symmetric butterfly computations and twiddle factors.
