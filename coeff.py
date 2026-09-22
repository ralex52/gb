import numpy as np
import sys
from functions import array2file
from functions import arrays2file
from functions import text2file
from functions import save_plot
from functions import save_triple_plot

# Get complex refraction index from n, tan delta
# Return complex(n, kappa) = n + i*kappa
def get_complex_n(n, tan_delta):
    n = np.asarray(n)
    tan_delta = np.asarray(tan_delta)
    eps1 = n**2 
    eps11 = eps1 * tan_delta
    kappa = 0.5 * eps11 / n
    return n + 1j * kappa

# Switch power array to dB
def power2db(arr):
    arr = np.array(arr)
    return 10 * np.log10(arr)

# Switch amplitude array to dB
def ampl2db(arr):
    arr = np.array(arr)
    return 20 * np.log10(arr)

#
def decompose_polarization(X, k, n):
    k0 = np.linalg.norm(k)
    k = k / k0

    Angle0rad = np.acos (n @ k);
    Angle0 = np.degrees (Angle0rad)
    
    s_dir = np.cross(k, n)

    if np.linalg.norm(s_dir) < 1e-8:
        X_s = X
        X_p = np.array([0,0,0])
        return X_s, X_p
    s_dir /= np.linalg.norm(s_dir)
    p_dir = np.cross(s_dir, k)
    p_dir /= np.linalg.norm(p_dir)
    
    X_s_mag = np.dot(X, s_dir)
    X_p_mag = np.dot(X, p_dir)
    
    X_s = X_s_mag * s_dir
    X_p = X_p_mag * p_dir
    return Angle0, X_s, X_p

# GET reflection and transmission coefficients for a specific angle
# Units: Hz, Meters, Degrees
# DielWidthArray - width for each layer
# DielRefrComArray - all layers
# Input and output media: 1.0+0.0j
def refltransm(AngDeg,BeamF,DielWidthArray,DielRefrComArray,polarization='S'):
    """
    DielRefrComArray: array of complex n (n + 1j*kappa).
                    [0] - input (vacuum), [1:-1] - layers, [-1] - output (vacuum)
    DielWidthArray: array of layer width
    polarization: 'S', 'TE' (Perpendicular) or Any other (Parallel)
    """
    if len(DielWidthArray) != len(DielRefrComArray):
        sys.exit("The array sizes do not match")

    # Input output n:
    DielRefrComArray = np.concatenate(([1.0+0.0j], DielRefrComArray, [1.0+0.0j]))
    
    c = 299792458.0;
    # Eta0 = 376.7303;
    wavelength = c / BeamF;
    n0 = 1.0 + 0.0j
    ns = 1.0 + 0.0j
    theta0 = np.radians(AngDeg)
    
    # Complex cos (snell law)
    # n0 * sin(theta0) = n_i * sin(theta_i)
    sin_theta0 = np.sin(theta0)
    
    # Complex cos array
    # cos(theta) = sqrt(1 - sin^2(theta))
    cos_theta = np.sqrt(1 - (n0 * sin_theta0 / DielRefrComArray)**2 + 0j)

    # Admittance (η)
    if polarization.upper() == 'S' or polarization.upper() == 'TE':
        eta = DielRefrComArray * cos_theta
    else:
        eta = DielRefrComArray / cos_theta

    # Transfer matrix
    M = np.identity(2, dtype=complex)
    
    # Internal layers (from 1 to N-1)
    for i in range(1, len(DielRefrComArray) - 1):
        d = DielWidthArray[i-1]
        # phase delay: 2*pi*n*d*cos(theta)/lambda
        # decay (image part of n)
        phi = (2 * np.pi * DielRefrComArray[i] * d * cos_theta[i]) / wavelength
        
        # matrix for each layer
        # print(f"{phi} {eta}")
        
        Mi = np.array([
            [np.cos(phi),          -1j/eta[i] * np.sin(phi)],
            [-1j * eta[i] * np.sin(phi), np.cos(phi)]
        ], dtype=complex)
        
        M = M @ Mi

    # Amplitide coefficients
    eta_inc = eta[0]
    eta_sub = eta[-1]
    
    m11, m12, m21, m22 = M[0,0], M[0,1], M[1,0], M[1,1]
    
    # Reflection and transmission coefficients
    r = (m11 * eta_inc + m12 * eta_inc * eta_sub - m21 - m22 * eta_sub) / \
        (m11 * eta_inc + m12 * eta_inc * eta_sub + m21 + m22 * eta_sub)
    t = (2 * eta_inc) / (m11 * eta_inc + m12 * eta_inc * eta_sub + m21 + m22 * eta_sub)

    # Power coefficients: R, T, A
    R = np.abs(r)**2
    T = np.abs(t)**2 * np.real(eta_sub) / np.real(eta_inc)
    A = 1 - R - T  # Absorbance
    return r, t, R, T, A

# Create Arrays for transmit and reflection coefficients
def refltransmArray(timestamp,BeamF,DielWidthArray,DielRefrComArray):
    print(f"refltransmArray start")
    if len(DielWidthArray) != len(DielRefrComArray):
        sys.exit("The array sizes do not match")
    AngleArrayDeg = np.arange(0, 89.99, 0.01)
    #AngleArray = np.pi/180 * AngleArrayDeg;
    AngleArrayNum = len(AngleArrayDeg);
    #array2file(timestamp, "Angles.txt", AngleArrayDeg)
    
    tPerpArray = np.zeros(AngleArrayNum, dtype=complex);
    tParalArray = np.zeros(AngleArrayNum, dtype=complex);
    rPerpArray = np.zeros(AngleArrayNum, dtype=complex);
    rParalArray = np.zeros(AngleArrayNum, dtype=complex);
    TPerpArray = np.zeros(AngleArrayNum);
    TParalArray = np.zeros(AngleArrayNum);
    RPerpArray = np.zeros(AngleArrayNum);
    RParalArray = np.zeros(AngleArrayNum);
    APerpArray = np.zeros(AngleArrayNum);
    AParalArray = np.zeros(AngleArrayNum);
    for i in range(AngleArrayNum):
        AngDeg = AngleArrayDeg[i];
        r, t, R, T, A = refltransm(AngDeg,BeamF,DielWidthArray,DielRefrComArray,polarization='S')
        tPerpArray[i] = t;
        rPerpArray[i] = r;
        TPerpArray[i] = T;
        RPerpArray[i] = R;
        APerpArray[i] = A;
        r, t, R, T, A = refltransm(AngDeg,BeamF,DielWidthArray,DielRefrComArray,polarization='P')
        tParalArray[i] = t;
        rParalArray[i] = r;
        TParalArray[i] = T;
        RParalArray[i] = R;
        AParalArray[i] = A;
    return AngleArrayDeg, tPerpArray, tParalArray, rPerpArray, rParalArray,\
           TPerpArray, TParalArray, RPerpArray, RParalArray, APerpArray, AParalArray

# Calculate Reflection & Transmission for each component
# kx, ky - Arrays of kx & ky values
# Fx0, Fy0, Fz0 - 2D Arrays of FFT spectrum
# n0 - Normal vector to the dielectric surface
def GB_Refl_Transm(BeamF, kxArr, kyArr, Fx0, Fy0, Fz0, n0,\
                   DistanceIncl,DistanceRefl,DistanceTran,\
                   AngleArray, tPerpArray, tParalArray, rPerpArray, rParalArray):
    n = 1;
    c = 299792458;
    k0 = 2 * np.pi * BeamF / c * n;
    FTx = np.zeros_like(Fx0, dtype=complex)
    FTy = np.zeros_like(Fy0, dtype=complex)
    FTz = np.zeros_like(Fz0, dtype=complex)
    FRx = np.zeros_like(Fx0, dtype=complex)
    FRy = np.zeros_like(Fy0, dtype=complex)
    FRz = np.zeros_like(Fz0, dtype=complex)

    PlaneWaveCount = 0
    
    for kxi in range(len(kxArr)):
        for kyi in range(len(kyArr)):
            kx = kxArr[kxi];
            ky = kyArr[kyi];
            if np.hypot(kx,ky) > 0.95*k0:
                continue
            PlaneWaveCount = PlaneWaveCount + 1
            kz = np.sqrt (k0**2 - kx**2 - ky**2);
            k = np.array([kx, ky, kz])
            F0 = np.array([Fx0[kxi,kyi], Fy0[kxi,kyi], Fz0[kxi,kyi]])

            #Angle0, F0perp, F0paral = decompose_polarization(F0, k, n0)
            k = k / np.linalg.norm(k)

            if n0 @ k <= 0:
                continue
            Angle0rad = np.acos (n0 @ k);
            Angle0 = np.degrees (Angle0rad)
            if Angle0<0 or Angle0>90:
                print(f"WARN Angle 0-90: {Angle0:.{2}f}")
            # Normal incidence flag (dont decompose to Perp & Paral)
            Flag_Norm_Inc = False
    
            n1 = np.cross(k, n0) #n1=s_dir

            if np.linalg.norm(n1) < 1e-8:
                Flag_Norm_Inc = True
                F0perp = F0
                F0paral = np.array([0,0,0])
            else:
                n1 /= np.linalg.norm(n1)
                n2 = np.cross(n1, k) #n2=p_dir
                n2 /= np.linalg.norm(n2)
    
                F0perp = np.dot(F0, n1)
                F0paral = np.dot(F0, n2)
 
            #F0perp_Arr(kxi,kyi) = F0perp;
            #F0paral_Arr(kxi,kyi) = F0paral;
            
            # Find Index and angle in coefficents arrays
            idx = np.abs(AngleArray - Angle0).argmin()# Find index
            # val = arr[idx] # Nearest array value (dont need)
            FRperp  = rPerpArray[idx]  * F0perp;   # Reflected
            FRparal = rParalArray[idx] * F0paral;  # Reflected
            FTperp  = tPerpArray[idx]  * F0perp;   # Transmitted
            FTparal = tParalArray[idx] * F0paral;  # Transmitted

            # Convert to Fr & Ft
            Fr = FRperp * n1 + FRparal * n2;
            Ft = FTperp * n1 + FTparal * n2;
            #Normal incidence
            if Flag_Norm_Inc:
                Fr = FRperp
                Ft = FTperp

            # Phase shift
            zPhaseShiftR = np.exp(1j*(kz*(DistanceIncl+DistanceRefl)));
            zPhaseShiftT = np.exp(1j*(kz*(DistanceIncl+DistanceTran)));
            Fr = zPhaseShiftR * Fr
            Ft = zPhaseShiftT * Ft

            # Result Arr:
            FTx[kxi,kyi] = Ft[0]
            FTy[kxi,kyi] = Ft[1]
            FTz[kxi,kyi] = Ft[2]
            FRx[kxi,kyi] = Fr[0]
            FRy[kxi,kyi] = Fr[1]
            FRz[kxi,kyi] = Fr[2]
    #print(f"GB_Refl_Transm end")
    return FTx,FTy,FTz,FRx,FRy,FRz,PlaneWaveCount
