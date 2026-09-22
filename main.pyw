# Gaussian beam reflection and transmission
#
# (c) Alexander Ryabov, IAP RAS, 2026
# 
# Test: python version 3.14.2
#
import tkinter as tk
import os
import sys
import ctypes
import threading
from datetime import datetime
from gb import gb

FontSize = 11
FontSizeHead = 14
EntryWidth=27
LabelWidth=19
ButtonWidth = 12
TextWidth=38
log_buffer = []

def Help():
    full_path = os.path.join(".", "help.pdf")
    if os.path.exists(full_path):
        os.startfile(full_path) #Windows
    else:
        print("Help not found")

def get_dpi_scaling():
    # scale factor (1.25 for 125%)
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    except:
        return 1.0

def monitor(root,txt,btn1):
    while log_buffer:
        message = log_buffer.pop(0) # Extract line
        if message[:3] != "RUN":
            btn1.config(state="normal")
        txt.delete("1.0", "4.0")
        txt.insert("1.0", f"{message}\n")
    root.after(100, lambda: monitor(root,txt,btn1))

def Run(root,txt,btn1):
    global timestamp
    global BeamPolarisation
    global BeamRadius
    global BeamFrquency
    global DielRefr 
    global DielWidth
    global DielTanD
    global DielRotX
    global DielRotY
    global ParamDistanceIncl
    global ParamDistanceRefl
    global ParamDistanceTran
    global ParamMeshSize
    global ParamMeshStep

    txt.delete("1.0", tk.END)
    txt.insert("1.0", "START OK\n \n \n")
    txt.update_idletasks()
    print(f"\nSTART OK")
    
    global timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_name = f"run_{timestamp}"
    print(f"Creating DIR: {dir_name}")
    full_path = os.path.join(".", dir_name)

    # makedirs
    try:
        os.makedirs(full_path, exist_ok=True)
        print(f"Created directory: {full_path}")
        #return full_path
    except Exception as e:
        print(f"Filesystem error: {e}")
        return None
    log_name = f"run_{timestamp}/log.txt"
    full_path_log = os.path.join(".", log_name)
    with open(full_path_log, 'w', encoding='utf-8') as f:
        f.write(f"Beam:\n")
        f.write(f"Raduis (mm): {BeamRadius.get()}\n")
        f.write(f"Frequency (GHz): {BeamFrquency.get()}\n")
        f.write(f"Dielectric layers:\n")
        f.write(f"Refraction ind.: {DielRefr.get()}\n")
        f.write(f"Width (mm): {DielWidth.get()}\n")
        f.write(f"Diel. loss tan: {DielTanD.get()}\n")
        f.write(f"Rotation X (deg): {DielRotX.get()}\n")
        f.write(f"Rotation Y (deg): {DielRotY.get()}\n")
        f.write(f"Parameters:\n")
        f.write(f"Incl. distance, mm: {ParamDistanceIncl.get()}\n")
        f.write(f"Refl. distance, mm: {ParamDistanceRefl.get()}\n")
        f.write(f"Tran. distance, mm: {ParamDistanceTran.get()}\n")
        f.write(f"Mesh size, mm: {ParamMeshSize.get()}\n")
        f.write(f"Mesh step, mm: {ParamMeshStep.get()}\n")
    print(f"Data saved to {full_path_log}")
    DielRefrArray = [float(x) for x in DielRefr.get().split(",")]
    DielWidthArray = [0.001*float(x) for x in DielWidth.get().split(",")]
    DielTanDArray = [float(x) for x in DielTanD.get().split(",")]
    DielRefrArrayNum = len(DielRefrArray)
    DielWidthArrayNum = len(DielWidthArray)
    DielTanDArrayNum = len(DielTanDArray)
    BeamF = 1.0e9 * BeamFrquency.get();
    BeamR = 0.001 * BeamRadius.get();
    RotX = DielRotX.get()
    RotY = DielRotY.get()
    DistanceIncl = 0.001 * ParamDistanceIncl.get()
    DistanceRefl = 0.001 * ParamDistanceRefl.get()
    DistanceTran = 0.001 * ParamDistanceTran.get()
    MeshSize = 0.001 * ParamMeshSize.get()
    MeshStep = 0.001 * ParamMeshStep.get()

    btn1.config(state="disabled")

    args1 = (timestamp,BeamF,BeamR,DielWidthArray,DielRefrArray,DielTanDArray,\
       RotX,RotY,DistanceIncl,DistanceRefl,DistanceTran,\
       MeshSize, MeshStep, log_buffer)

    thread = threading.Thread(target=gb, args=args1, daemon=True)
    thread.start()
    monitor(root,txt,btn1)

def main():
    global timestamp
    global BeamPolarisation
    global BeamRadius
    global BeamFrquency
    global BeamPolarisation
    global DielRefr 
    global DielWidth
    global DielTanD
    global DielRotX
    global DielRotY
    global ParamDistanceIncl
    global ParamDistanceRefl
    global ParamDistanceTran
    global ParamMeshSize
    global ParamMeshStep

    # Nice fonts
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()
    
    # Create the main window
    root = tk.Tk()
    scale = get_dpi_scaling()
    root.title("Gaussian beam reflection and transmission")

    # Main frame
    main_frame = tk.Frame(root)
    main_frame.pack(padx=30, pady=30)

    r = 0

    # Beam
    label = tk.Label(main_frame, text="Beam:", font=("Arial", FontSizeHead))
    label.grid(row=r, column=0, columnspan=2, pady=(0, 5), sticky="ew")

    r += 1

    label1 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Radius w₀ (mm): ", font=("Arial", FontSize))
    label1.grid(row=r, column=0, pady=2)
    BeamRadius = tk.DoubleVar()
    BeamRadius.set(12)
    entry1 = tk.Entry(main_frame, width=EntryWidth, textvariable=BeamRadius)
    entry1.grid(row=r, column=1, pady=2)

    r += 1

    label2 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Frequency (GHz): ", font=("Arial", FontSize))
    label2.grid(row=r, column=0, pady=2)
    BeamFrquency = tk.DoubleVar()
    BeamFrquency.set(100)
    entry2 = tk.Entry(main_frame, width=EntryWidth, textvariable=BeamFrquency)
    entry2.grid(row=r, column=1, pady=2)

    r += 1
    
    # Dielectric
    label = tk.Label(main_frame, text="Dielectric layers:", font=("Arial", FontSizeHead))
    label.grid(row=r, column=0, columnspan=2, pady=(10, 5), sticky="ew")

    r += 1

    label1 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Refraction ind.: ", font=("Arial", FontSize))
    label1.grid(row=r, column=0, pady=2)
    DielRefr = tk.StringVar()
    DielRefr.set("2.0, 3.0")
    entry1 = tk.Entry(main_frame, width=EntryWidth, textvariable=DielRefr)
    entry1.grid(row=r, column=1, pady=2)

    r += 1

    label2 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Width (mm): ", font=("Arial", FontSize))
    label2.grid(row=r, column=0, pady=2)
    DielWidth = tk.StringVar()
    DielWidth.set("0.25, 4.0")
    entry2 = tk.Entry(main_frame, width=EntryWidth, textvariable=DielWidth)
    entry2.grid(row=r, column=1, pady=2)

    r += 1

    label3 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Diel. loss tan.: ", font=("Arial", FontSize))
    label3.grid(row=r, column=0, pady=2)
    DielTanD = tk.StringVar()
    DielTanD.set("0.0001, 0.0001")
    entry3 = tk.Entry(main_frame, width=EntryWidth, textvariable=DielTanD)
    entry3.grid(row=r, column=1, pady=2)

    r += 1

    label4 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Rotation X (deg): ", font=("Arial", FontSize))
    label4.grid(row=r, column=0, pady=2)
    DielRotX = tk.DoubleVar()
    entry4 = tk.Entry(main_frame, width=EntryWidth, textvariable=DielRotX)
    entry4.grid(row=r, column=1, pady=2)

    r += 1

    label5 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Rotation Y (deg): ", font=("Arial", FontSize))
    label5.grid(row=r, column=0, pady=2)
    DielRotY = tk.DoubleVar()
    entry5 = tk.Entry(main_frame, width=EntryWidth, textvariable=DielRotY)
    entry5.grid(row=r, column=1, pady=2)

    r += 1
                
    # Parameters
    label = tk.Label(main_frame, text="Parameters:", font=("Arial", FontSizeHead))
    label.grid(row=r, column=0, columnspan=2, pady=(10, 5), sticky="ew")

    r += 1
                
    label1 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Incl. distance, mm: ", font=("Arial", FontSize))
    label1.grid(row=r, column=0, pady=2)
    ParamDistanceIncl = tk.DoubleVar()
    ParamDistanceIncl.set(50)
    entry1 = tk.Entry(main_frame, width=EntryWidth, textvariable=ParamDistanceIncl)
    entry1.grid(row=r, column=1, pady=2)

    r += 1

    label2 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Refl. distance, mm: ", font=("Arial", FontSize))
    label2.grid(row=r, column=0, pady=2)
    ParamDistanceRefl = tk.DoubleVar()
    ParamDistanceRefl.set(50)
    entry2 = tk.Entry(main_frame, width=EntryWidth, textvariable=ParamDistanceRefl)
    entry2.grid(row=r, column=1, pady=2)

    r += 1

    label3 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Tran. distance, mm: ", font=("Arial", FontSize))
    label3.grid(row=r, column=0, pady=2)
    ParamDistanceTran = tk.DoubleVar()
    ParamDistanceTran.set(50)
    entry3 = tk.Entry(main_frame, width=EntryWidth, textvariable=ParamDistanceTran)
    entry3.grid(row=r, column=1, pady=2)

    r += 1

    label4 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Mesh size, mm: ", font=("Arial", FontSize))
    label4.grid(row=r, column=0, pady=2)
    ParamMeshSize = tk.DoubleVar()
    ParamMeshSize.set(100.0)
    entry4 = tk.Entry(main_frame, width=EntryWidth, textvariable=ParamMeshSize)
    entry4.grid(row=r, column=1, pady=2)

    r += 1

    label5 = tk.Label(main_frame, width=LabelWidth, anchor="e", text="Mesh step, mm: ", font=("Arial", FontSize))
    label5.grid(row=r, column=0, pady=2)
    ParamMeshStep = tk.DoubleVar()
    ParamMeshStep.set(0.2)
    entry5 = tk.Entry(main_frame, width=EntryWidth, textvariable=ParamMeshStep)
    entry5.grid(row=r, column=1, pady=2)

    r += 1

    button_container = tk.Frame(main_frame)
    button_container.grid(row=r, column=0, columnspan=2, sticky="ew", pady=(10, 5))

    btn1 = tk.Button(button_container, width=ButtonWidth, text="Start", command=lambda: Run(root,txt,btn1))
    btn1.pack(side="left", padx=10)

    btn2 = tk.Button(button_container, width=ButtonWidth, text="Help", command=Help)
    btn2.pack(side="left", padx=5)
    
    r += 1
                
    txt = tk.Text(main_frame, height=3, width=TextWidth)
    txt.grid(row=r, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")

    txt.insert("1.0", "\n")
    txt.insert("2.0", "\n")
    txt.insert("3.0", "")

    # Start the event loop
    root.mainloop()
    
if __name__ == "__main__":
    main()

