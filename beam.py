import numpy as np
import sys

# Ex distribution for GB profile, E=Ex
# E = E0 * w0m/w * exp(-r^2/w^2) * exp(-1j*(k*z+0.5*k*r^2/R-Psi)):
# x,y,z - meters
# w0 - beam radius, m
# f0 - Frequency, Hz
def GB_profile(x, y, z, w0, f0):
    E0 = 1.0;
    n = 1;
    c = 299792458;
    k0 = 2 * np.pi * f0 / c * n;
    Lambda0 = c / f0;
    ZR = np.pi * w0**2 * n / Lambda0;
    r = np.hypot(x,y);
    w = w0 * np.sqrt(1 + z/ZR);
    if np.abs(z) < 1e-6*Lambda0:
        Ex = E0 * w0/w * np.exp(-r**2/w**2);
        Ez = (-1j * 2 * x / (k0 * w**2))  * Ex;
    else:
        R = z * (1+ZR/z)**2;
        Psi = np.atan(z/ZR);
        Ex = E0 * w0/w * np.exp(-r**2 / w**2) * np.exp(-1j*(k0*z+0.5*k0*r**2/R-Psi));
        Ez = (-1j * 2 * x / (k0 * w**2) + 2*x/R)  * Ex;
    Ey = 0;
    return Ex, Ey, Ez

# GB Profile 2D for meshgrid
def GB_profile2D(BeamF,BeamR,MeshSize,MeshStep):
    c = 299792458;
    Lambda0 = c / BeamF;
    xArr = np.arange(-MeshSize/2, MeshSize/2+1e-9*Lambda0, MeshStep);
    x_len = len(xArr)
    # Create 2D arrays
    Ex0Arr = np.zeros((x_len, x_len), dtype=complex)
    Ey0Arr = np.zeros((x_len, x_len), dtype=complex)
    Ez0Arr = np.zeros((x_len, x_len), dtype=complex)
    for xi in range(x_len):
        x = xArr[xi]
        for yi in range(x_len):
            y = xArr[yi]
            Ex0Arr[xi,yi],Ey0Arr[xi,yi],Ez0Arr[xi,yi] = GB_profile(x,y,0, BeamR, BeamF);
    return Ex0Arr, Ey0Arr, Ez0Arr, xArr

def GB_Lambda(BeamF):
    c = 299792458;
    Lambda0 = c / BeamF;
    return Lambda0

def GB_k0(BeamF):
    c = 299792458;
    Lambda0 = c / BeamF;
    k0 = 2 * np.pi * BeamF / c;
    return k0

# 2D FFT
def direct_fft2(data, x, y):
    nx, ny = len(x), len(y)
    dx, dy = x[1] - x[0], y[1] - y[0]
    # Shifted FFT
    spectrum = np.fft.fftshift(np.fft.fft2(data))
    # Generate k = 2*pi * f
    kx = np.fft.fftshift(np.fft.fftfreq(nx, d=dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(ny, d=dy)) * 2 * np.pi
    # kx_grid, ky_grid = np.meshgrid(kx, ky, indexing='ij')
    return spectrum, kx, ky

def direct_fft2_th(data, x, y, container):
    nx, ny = len(x), len(y)
    dx, dy = x[1] - x[0], y[1] - y[0]
    # Shifted FFT
    spectrum = np.fft.fftshift(np.fft.fft2(data))
    # Generate k = 2*pi * f
    kx = np.fft.fftshift(np.fft.fftfreq(nx, d=dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(ny, d=dy)) * 2 * np.pi
    # kx_grid, ky_grid = np.meshgrid(kx, ky, indexing='ij')
    container.append((spectrum, kx, ky))

# 2D iFFT
def inverse_fft2(spectrum, kx, ky):
    nx, ny = len(kx), len(ky)
    dkx = kx[1] - kx[0]
    dky = ky[1] - ky[0]
    # inverted FFT
    data = np.fft.ifft2(np.fft.ifftshift(spectrum))
    # XY grid
    # x_size = 2*pi / dkx
    x = np.fft.fftshift (np.fft.fftfreq(nx, d=dkx / (2 * np.pi)))
    y = np.fft.fftshift (np.fft.fftfreq(ny, d=dky / (2 * np.pi)))
    #x_grid, y_grid = np.meshgrid(np.sort(x), np.sort(y), indexing='ij')
    return data, x, y
