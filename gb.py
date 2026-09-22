import sys
import numpy as np
import time
import tkinter as tk
from coeff import get_complex_n
from coeff import refltransmArray
from coeff import GB_Refl_Transm
from coeff import power2db
from coeff import ampl2db
from beam import GB_profile2D
from beam import GB_Lambda
from beam import GB_k0
from beam import direct_fft2
from beam import direct_fft2_th
from beam import inverse_fft2
from functions import array2file
from functions import arrays2file
from functions import array_to_text
from functions import text2file
from functions import save_2d_plot
from functions import save_2d_plot_text
from functions import rotate_x
from functions import rotate_y
from functions import save_double_plot
from functions import save_triple_plot
from functions import integrate_2d
from functions import truncate_centered
from functions import find_max

# All parameters: Hz, m, degrees
# log - text buffer for tkinter GUI
def gb(timestamp,BeamF,BeamR,DielWidthArray,DielRefrArray,DielTanDArray, \
       RotX,RotY,DistanceIncl,DistanceRefl,DistanceTran,MeshSize, MeshStep,\
       log):
    log.append(f"RUN")
    time1 = time.perf_counter()
    # check array size
    if len(DielRefrArray) != len(DielTanDArray):
        log.append(f"STOP\nERR: Arr size")
        return
    if len(DielWidthArray) != len(DielRefrArray):
        log.append(f"STOP\nERR: Arr size")
        return

    # Check BeamR, WL
    L = GB_Lambda(BeamF)
    Lmm = 1000 * L
    print(f"Wavelength, mm: {Lmm}")
    if BeamR < L:
        log.append(f"STOP\nERR: Beam Radius < wavelength")
        return
    if 2*BeamR > MeshSize:
        log.append(f"STOP\nERR: Beam Diam. > Mesh size")
        return

    # Errors & Warnings:
    Warn = ""
    if BeamR < 3*L:
        Warn += "WARN:R<3WL "
    if 4*BeamR > MeshSize:
        Warn += "WARN:4R>Mesh "

    # Complex refraction
    DielRefrComArray = get_complex_n(DielRefrArray, DielTanDArray);
    array_to_text(timestamp, "RefrComplex.dat", DielRefrComArray)

    # Reflection and transmission coefficients
    log.append(f"RUN (1/7) Refl & Transm coeff.")
    time2 = time.perf_counter()
    print(f"refltransmArray")
    AngleArrayDeg, tPerpArray, tParalArray, rPerpArray, rParalArray,\
            TPerpArray, TParalArray, RPerpArray, RParalArray, APerpArray, AParalArray= \
            refltransmArray(timestamp,BeamF,DielWidthArray,DielRefrComArray)
    arrays2file(timestamp, "PowerCoeff.dat", AngleArrayDeg, TPerpArray, RPerpArray, \
                APerpArray, TParalArray, RParalArray, AParalArray);
    text2file(timestamp, "PowerCoeff.txt", "Power coefficients:\n\
0: Angle[deg]\n1: Transmission (TE)\n2: Reflection (TE)\n\
3: Absorption (TE)\n4: Transmission (TM)\n5: Reflection (TM)\n\
6: Absorption (TM)")
    arrays2file(timestamp, "AmplCoeff.dat", AngleArrayDeg, tPerpArray, rPerpArray, \
                tParalArray, rParalArray);
    text2file(timestamp, "AmplCoeff.txt", "Amplitude coefficients:\n\
0: Angle[deg]\n1: Transmission (TE)\n2: Reflection (TE)\n\
3: Transmission (TM)\n4: Reflection (TM)")
    if np.max(np.abs(DielTanDArray)) > 1e-9:
        save_triple_plot(timestamp, "Coeff_TE.png", "TE", "Angle", "Coefficients",\
                     "Transm", "Refr", "Absorp",\
                     AngleArrayDeg, TPerpArray, RPerpArray, APerpArray)
        save_triple_plot(timestamp, "Coeff_TM.png", "TM", "Angle", "Coefficients",
                     "Transm", "Refr", "Absorp",\
                     AngleArrayDeg, TParalArray, RParalArray, AParalArray)
        
        save_triple_plot(timestamp, "Coeff_dB_TE.png", "TE", "Angle", "dB",
                     "Transm", "Refr", "Absorp",\
                     AngleArrayDeg, power2db(TPerpArray), power2db(RPerpArray), power2db(APerpArray))
        save_triple_plot(timestamp, "Coeff_dB_TM.png", "TM", "Angle", "dB",
                     "Transm", "Refr", "Absorp",\
                     AngleArrayDeg, power2db(TParalArray), power2db(RParalArray), power2db(AParalArray))
    else:
        save_double_plot(timestamp, "Coeff_TE.png", "TE", "Angle", "Coefficients",\
                     "Transm", "Refr",\
                     AngleArrayDeg, TPerpArray, RPerpArray)
        save_double_plot(timestamp, "Coeff_TM.png", "TM", "Angle", "Coefficients",
                     "Transm", "Refr",\
                     AngleArrayDeg, TParalArray, RParalArray)
        
        save_double_plot(timestamp, "Coeff_dB_TE.png", "TE", "Angle", "dB",
                     "Transm", "Refr",\
                     AngleArrayDeg, power2db(TPerpArray), power2db(RPerpArray))
        save_double_plot(timestamp, "Coeff_dB_TM.png", "TM", "Angle", "dB",
                     "Transm", "Refr",\
                     AngleArrayDeg, power2db(TParalArray), power2db(RParalArray))
        
    # Create GB Profile E=Ex
    log.append(f"RUN (2/7) GB Profile")
    time3 = time.perf_counter()
    print(f"Create GB profile")
    Ex0Arr, Ey0Arr, Ez0Arr, xArr = GB_profile2D(BeamF,BeamR,MeshSize,MeshStep)
    log.append(f"RUN (2/7) GB Profile Done")
    save_2d_plot_text(timestamp, "BeamEx0", "Beam Ex0", "x, mm", "y, mm", "abs(Ex)",\
                      1000*xArr, 1000*xArr, np.abs(Ex0Arr))
    save_2d_plot_text(timestamp, "BeamEz0", "Beam Ez0", "x, mm", "y, mm", "abs(Ez)",\
                      1000*xArr, 1000*xArr, np.abs(Ez0Arr))

    # Decompose into plane waves
    log.append(f"RUN (3/7) Decompose to PW")
    time4 = time.perf_counter()
    print(f"Decompose into plane waves")
    Fx0, kxArr, kyArr = direct_fft2(Ex0Arr, xArr, xArr)
    Fy0, kxArr, kyArr = direct_fft2(Ey0Arr, xArr, xArr)
    Fz0, kxArr, kyArr = direct_fft2(Ez0Arr, xArr, xArr)

    # Truncate kx ky Fx Fy Fz
    k0 = GB_k0(BeamF)
    for kxi in range(len(kxArr)):
        for kyi in range(len(kyArr)):
            if np.hypot(kxArr[kxi],kyArr[kyi]) > 0.99*k0:
                Fx0[kxi,kyi] = 0
                Fy0[kxi,kyi] = 0
                Fz0[kxi,kyi] = 0
    
    Fx0Trunc, Fy0Trunc, Fz0Trunc, kxArrTrunc =\
              truncate_centered(Fx0,Fy0,Fz0, kxArr, 0.3*k0)
    kxArrTrunc = 1/k0 * kxArrTrunc # normalized to k0
    save_2d_plot_text(timestamp, "BeamFx0", "Beam Fx0", "kx/k0", "ky/k0", "abs(Fx0)",\
                 kxArrTrunc, kxArrTrunc, np.abs(Fx0Trunc))
    save_2d_plot_text(timestamp, "BeamFz0", "Beam Fz0", "kx/k0", "ky/k0", "abs(Fz0)",\
                 kxArrTrunc, kxArrTrunc, np.abs(Fz0Trunc))

    # Compose into Gaussian Beam
    log.append(f"RUN (4/7) Check errors")
    time5 = time.perf_counter()
    print(f"Compose GB from plane waves")
    Ex0ArrTemp, xArrTemp, yArrTemp = inverse_fft2(Fx0, kxArr, kyArr)

    # Max error decompose-compose:
    maxErrEx1 = np.max(np.abs(Ex0ArrTemp-Ex0Arr))
    print(f"Max decompose-compose error Ex (amplitude): {maxErrEx1}")

    # Error decompose-compose center Ex:
    row, col = np.array(Ex0Arr.shape) // 2
    maxErrEx2 = np.abs(Ex0Arr[row, col] - Ex0ArrTemp[row, col])
    print(f"Center decompose-compose error Ex (amplitude): {maxErrEx2}")

    # power diff decompose-compose Ex:
    I0x = np.sum(np.square(np.abs(Ex0Arr)))
    Ix = np.sum(np.square(np.abs(Ex0ArrTemp)))
    print(f"Power Ex0: {I0x} Power ExTemp: {Ix}")

    if maxErrEx1 > 0.1:
        log.append(f"STOP\nERR: max(decompose-compose)>0.1")
        return
    if maxErrEx2 > 0.1:
        log.append(f"STOP\nERR: center(decompose-compose)>0.1")
        return
    if np.abs((Ix-I0x)/I0x) > 0.1:
        log.append(f"STOP\nERR: power(decompose-compose)>0.1")
        return
    if maxErrEx1 > 0.001 or maxErrEx2 > 0.001 or np.abs((Ix-I0x)/I0x) > 0.001:
        Warn += "WARN:0.1% "

    # Rotate oX: Perpendicular (Horizontal, S, TE) Polarization
    n0 = np.array([0, 0, 1], dtype=float)
    n0 = rotate_x(n0, RotX);
    # Rotate oY: Parallel (Vertical, P, TM) Polarization
    n0 = rotate_y(n0, RotY);
    print(f"Vector n0: {n0}")
    array2file(timestamp, "Vector_n0.dat", n0)

    # Calculate Reflection & Transmission for each component
    log.append(f"RUN (5/7) Reflection & Transmission")
    time6 = time.perf_counter()
    print(f"Refl & Transm for each plane wave")
    FTx,FTy,FTz,FRx,FRy,FRz,PW_Count = GB_Refl_Transm(BeamF, kxArr, kyArr, Fx0, Fy0, Fz0,\
                n0, DistanceIncl, DistanceRefl, DistanceTran,\
                AngleArrayDeg, tPerpArray, tParalArray, rPerpArray, rParalArray)
    FTxTrunc, FTyTrunc, FTzTrunc, kxArrTrunc =\
              truncate_centered(FTx,FTy,FTz, kxArr, 0.3*k0)
    FRxTrunc, FRyTrunc, FRzTrunc, kxArrTrunc =\
              truncate_centered(FRx,FRy,FRz, kxArr, 0.3*k0)
    kxArrTrunc = 1/k0 * kxArrTrunc # normalized to k0
    
    save_2d_plot_text(timestamp, "F_Tran_Fx", "Transm Fx", "kx/k0", "ky/k0", "abs(FTx)",\
                 kxArrTrunc, kxArrTrunc, np.abs(FTxTrunc))
    save_2d_plot_text(timestamp, "F_Refl_Fx", "Refl Fx", "kx/k0", "ky/k0", "abs(FRx)",\
                 kxArrTrunc, kxArrTrunc, np.abs(FRxTrunc))
    save_2d_plot_text(timestamp, "F_Tran_Fy", "Transm Fy", "kx/k0", "ky/k0", "abs(FTy)",\
                 kxArrTrunc, kxArrTrunc, np.abs(FTyTrunc))
    save_2d_plot_text(timestamp, "F_Refl_Fy", "Refl Fy", "kx/k0", "ky/k0", "abs(FRy)",\
                 kxArrTrunc, kxArrTrunc, np.abs(FRyTrunc))
    save_2d_plot_text(timestamp, "F_Tran_Fz", "Transm Fz", "kx/k0", "ky/k0", "abs(FTz)",\
                 kxArrTrunc, kxArrTrunc, np.abs(FTzTrunc))
    save_2d_plot_text(timestamp, "F_Refl_Fz", "Refl Fz", "kx/k0", "ky/k0", "abs(FRz)",\
                 kxArrTrunc, kxArrTrunc, np.abs(FRzTrunc))
    print(f"Plane wave count: {PW_Count}")

    # Compose Ex Ey Ez for Refl & Transm
    time7 = time.perf_counter()
    print(f"Compose GB from plane wave")
    # inverse_fft2(spectrum, kx, ky)
    log.append(f"RUN (6/7) Compose Ex")
    ExT, xArr, yArr = inverse_fft2(FTx, kxArr, kyArr)
    ExR, xArr, yArr = inverse_fft2(FRx, kxArr, kyArr)
    save_2d_plot_text(timestamp, "E_Tran_Ex", "Transm Ex", "x, mm", "y, mm", "abs(Ex)",\
                 1000*xArr, 1000*yArr, np.abs(ExT))
    save_2d_plot_text(timestamp, "E_Refl_Ex", "Refl Ex", "x, mm", "y, mm", "abs(Ex)",\
                 1000*xArr, 1000*yArr, np.abs(ExR))
    log.append(f"RUN (6/7) Compose Ey")
    EyT, xArr, yArr = inverse_fft2(FTy, kxArr, kyArr)
    EyR, xArr, yArr = inverse_fft2(FRy, kxArr, kyArr)
    save_2d_plot_text(timestamp, "E_Tran_Ey", "Transm Ey", "x, mm", "y, mm", "abs(Ey)",\
                 1000*xArr, 1000*yArr, np.abs(EyT))
    save_2d_plot_text(timestamp, "E_Refl_Ey", "Refl Ey", "x, mm", "y, mm", "abs(Ey)",\
                 1000*xArr, 1000*yArr, np.abs(EyR))
    log.append(f"RUN (6/7) Compose Ez")
    EzT, xArr, yArr = inverse_fft2(FTz, kxArr, kyArr)
    EzR, xArr, yArr = inverse_fft2(FRz, kxArr, kyArr)
    save_2d_plot_text(timestamp, "E_Tran_Ez", "Transm Ez", "x, mm", "y, mm", "abs(Ez)",\
                 1000*xArr, 1000*yArr, np.abs(EzT))
    save_2d_plot_text(timestamp, "E_Refl_Ez", "Refl Ez", "x, mm", "y, mm", "abs(Ez)",\
                 1000*xArr, 1000*yArr, np.abs(EzR))
    # XY grid for debug
    arrays2file(timestamp, "XY.dat", xArr, yArr)

    # Integrals & Max locate
    log.append(f"RUN (7/7) Integrals")
    time8 = time.perf_counter()

    ExT_max_x, ExT_max_y = find_max (ExT, xArr, yArr)
    ExR_max_x, ExR_max_y = find_max (ExR, xArr, yArr)
    ExT_max_x = 1000 * ExT_max_x
    ExT_max_y = 1000 * ExT_max_y
    ExR_max_x = 1000 * ExR_max_x
    ExR_max_y = 1000 * ExR_max_y

    print(f"Integrals")
    I0x = np.sum(np.square(np.abs(Ex0Arr)))
    I0y = np.sum(np.square(np.abs(Ey0Arr)))
    I0z = np.sum(np.square(np.abs(Ez0Arr)))
    
    ITx = np.sum(np.square(np.abs(ExT)))
    ITy = np.sum(np.square(np.abs(EyT)))
    ITz = np.sum(np.square(np.abs(EzT)))
    
    IRx = np.sum(np.square(np.abs(ExR)))
    IRy = np.sum(np.square(np.abs(EyR)))
    IRz = np.sum(np.square(np.abs(EzR)))
    
    TotalPow = I0x + I0y + I0z
    TotalTr = (ITx + ITy + ITz) / TotalPow
    TotalR = (IRx + IRy + IRz) / TotalPow
    TotalL = 1.0 - TotalR - TotalTr
    print(f"Norm. beam power (E): 1.0 Reflected: {TotalR} Transmitted: {TotalTr} Lost:{TotalL}")
    I0x = np.sum(np.square(np.abs(Fx0)))
    I0y = np.sum(np.square(np.abs(Fy0)))
    I0z = np.sum(np.square(np.abs(Fz0)))
    
    ITx = np.sum(np.square(np.abs(FTx)))
    ITy = np.sum(np.square(np.abs(FTy)))
    ITz = np.sum(np.square(np.abs(FTz)))
    
    IRx = np.sum(np.square(np.abs(FRx)))
    IRy = np.sum(np.square(np.abs(FRy)))
    IRz = np.sum(np.square(np.abs(FRz)))
    
    TotalPow = I0x + I0y + I0z
    TotalTr = (ITx + ITy + ITz) / TotalPow
    TotalR = (IRx + IRy + IRz) / TotalPow
    TotalL = 1.0 - TotalR - TotalTr
    print(f"Norm. beam power (F): 1.0 Reflected: {TotalR} Transmitted: {TotalTr} Lost:{TotalL}")
    text2file(timestamp, "Integrals.txt", "Power radiated: 1.0"+\
              "\nPower Reflected: "+f"{TotalR}"+\
              "\nPower Transmitted: "+f"{TotalTr}"+\
              "\nPower lost: "+f"{TotalL}"+\
              "\nReflected max XY (mm): "+f"{ExR_max_x:.{2}f}, {ExR_max_y:.{2}f}"+\
              "\nTransmitted max XY (mm): "+f"{ExT_max_x:.{2}f}, {ExT_max_y:.{2}f}"+\
              "\n")
    time9 = time.perf_counter()
    time_total = time9 - time1
    time1 = time2 - time1;
    time2 = time3 - time2;
    time3 = time4 - time3;
    time4 = time5 - time4;
    time5 = time6 - time5;
    time6 = time7 - time6;
    time7 = time8 - time7;
    time8 = time9 - time8;
    log.append(f"END in {time_total:.{1}f} second(s)\nWL:" + f"{Lmm:.{1}f}" + \
                        " Spec.num.:" + f"{PW_Count}" + \
                        " T:" + f"{TotalTr:.{2}f}" + \
                        " R:" + f"{TotalR:.{2}f}\n" + Warn)
    print(f"Running time 1: {time1:.1f}s ")
    print(f"Running time 2: {time2:.1f}s ")
    print(f"Running time 3: {time3:.1f}s ")
    print(f"Running time 4: {time4:.1f}s ")
    print(f"Running time 5: {time5:.1f}s ")
    print(f"Running time 6: {time6:.1f}s ")
    print(f"Running time 7: {time7:.1f}s ")
    print(f"Running time 8: {time8:.1f}s ")
    print(f"END\n")
    return 1
