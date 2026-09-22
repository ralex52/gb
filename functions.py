import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

#save 1D array to file
def array2file(timestamp, filename, data_array):
    filenamefull = f"run_{timestamp}/{filename}"
    try:
        with open(filenamefull, 'w', encoding='utf-8') as f:
            for item in data_array:
                f.write(f"{item}\n")
        #print(f"Data successfully written to file: {filename}")
    except Exception as e:
        print(f"Data write error: {e}")

#save 1D arrays (any number) to file
def arrays2file(timestamp, filename, *arrays):
    filenamefull = f"run_{timestamp}/{filename}"
    with open(filenamefull, 'w', encoding='utf-8') as f:
        # zip(*arrays) pick i-th element
        for row in zip(*arrays):
            line = " ".join(map(str, row))
            f.write(line + "\n")

#save any array (1D, 2D) as text to file
def array_to_text(timestamp, filename, array):
    filenamefull = f"run_{timestamp}/{filename}"
    np.savetxt(filenamefull, array, delimiter=' ', fmt='%.4e')
    #print(f"Array successfully written to file: {filename}")

#save Text to file
def text2file(timestamp, filename, text):
    filenamefull = f"run_{timestamp}/{filename}"
    try:
        with open(filenamefull, 'w', encoding='utf-8') as f:
            f.write(f"{text}\n")
    except Exception as e:
        print(f"Data write error: {e}")

# save XY plot to file .png, .pdf, .jpg
def save_plot(timestamp, filename, title, xlabel, ylabel, x_data, y_data):
    filenamefull = f"run_{timestamp}/{filename}"
    plt.figure()
    plt.plot(x_data, y_data, linestyle='-', color='b', label='Label1')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.savefig(filenamefull, dpi=300)
    #print(f"Image saved {filename}")
    plt.close()

# save XYY plot to file .png, .pdf, .jpg
def save_double_plot(timestamp, filename, title, xlabel, ylabel,\
                     legend1, legend2, x, y1, y2):
    filenamefull = f"run_{timestamp}/{filename}"
    plt.figure(figsize=(8, 5)) 
    plt.plot(x, y1, label=legend1, color='royalblue', linewidth=2)
    plt.plot(x, y2, label=legend2, color='crimson', linewidth=2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.savefig(filenamefull, dpi=300, bbox_inches='tight')
    plt.close()
    #print(f"Image saved {filename}")

# save XYYY plot to file .png, .pdf, .jpg
def save_triple_plot(timestamp, filename, title, xlabel, ylabel,\
                     legend1, legend2, legend3, x, y1, y2, y3):
    filenamefull = f"run_{timestamp}/{filename}"
    plt.figure(figsize=(8, 5)) 
    plt.plot(x, y1, label=legend1, color='royalblue', linewidth=2)
    plt.plot(x, y2, label=legend2, color='crimson', linewidth=2)
    plt.plot(x, y3, label=legend3, color='forestgreen', linewidth=2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.savefig(filenamefull, dpi=300, bbox_inches='tight')
    plt.close()
    #print(f"Image saved {filename}")

# save 2D plot to file .png, .pdf, .jpg
def save_2d_plot(timestamp, filename, title, xlabel, ylabel, zlabel, xArr, yArr, F):
    filenamefull = f"run_{timestamp}/{filename}"
    X, Y = np.meshgrid(xArr, yArr)
    fig, ax = plt.subplots(figsize=(7, 7))
    # Rotate 90 CCW
    im = ax.pcolormesh(X, Y, np.rot90(F), cmap='jet', shading='auto')
    ax.set_aspect('equal', adjustable='box')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    #cb.set_label(zlabel)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(filenamefull, dpi=300, bbox_inches='tight')
    plt.close()
    #print(f"Image saved {filename}")

# save 2D plot and text data to files
def save_2d_plot_text(timestamp, filename, title, xlabel, ylabel, zlabel, xArr, yArr, F):
    filename1 = f"{filename}.png"
    filename2 = f"{filename}.dat"
    filename3 = f"{filename}.txt"
    save_2d_plot(timestamp, filename1, title, xlabel, ylabel, zlabel, xArr, yArr, F)
    array_to_text(timestamp, filename2, F)

# Rotate vector oX
def rotate_x(vector, angle_degrees):
    theta = np.radians(angle_degrees)
    # Matrix for rotating oX
    c, s = np.cos(theta), np.sin(theta)
    R_x = np.array([[1, 0,  0],
                    [0, c, -s],
                    [0, s,  c]])
    return R_x @ vector

# Rotate vector oY
def rotate_y(vector, angle_degrees):
    theta = np.radians(angle_degrees)
    c, s = np.cos(theta), np.sin(theta)
    # Matrix for rotating oY
    R_y = np.array([[ c, 0, s],
                    [ 0, 1, 0],
                    [-s, 0, c]])
    return R_y @ vector

def integrate_2d(z_array, x_grid, y_grid):
    integral_y = np.trapezoid(z_array, y_grid, axis=0)
    total_integral = np.trapezoid(integral_y, x_grid)
    return total_integral

# z1 z2 z3 - 2D Arrays with XY grid: x_grid, x_grid
def truncate_centered(z1,z2,z3, x_grid, x_max):
    x_mask = (x_grid >= -x_max) & (x_grid <= x_max)
    x_grid = x_grid[x_mask]
    z1 = z1[np.ix_(x_mask, x_mask)]
    z2 = z2[np.ix_(x_mask, x_mask)]
    z3 = z3[np.ix_(x_mask, x_mask)]
    return z1, z2, z3, x_grid

# find coordinates of maximum (abs)
def find_max(data, x_axis, y_axis):
    #data=data.T
    data = np.rot90(data) # Rotate 90 CCW
    idx = np.argmax(np.abs(data))
    row, col = np.unravel_index(idx, data.shape)
    return x_axis[col], y_axis[row]
