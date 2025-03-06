import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import pandas as pd

# Variables to fill in
# path is the path where the data folder will be located.
root = r"C:\My Documents\data"

# name is the name of the folder where the .CSV files are located.
name = "example_data"

# peaks are the peaks to be integrated. They are given as a dictionary with the peak names as keys and tuples containing start time and end time as the values.
peaks = {"Peak1": (2.4, 2.8), 
         "Peak2": (3.9, 4.1),
         "Peak3": (4.8, 5.1)}

# If you want to zoom in the graphs, specify x_axis and y_axis. If you want default zoom, set them to None
x_axis = None
y_axis = (-1000, 200000)

# interval is used to create the x-axis for the dataframe. If there is no need for this, set it to 1
interval = 0.5


def closest(lst, K):
    """
    Determines the closest value in array lst to value K.
    
    Args:
        lst: A list of values
        K: One numer to find closest value to
    Returns:
        idx: The closest number in the list to K
    """
    idx = (np.abs(lst - K)).argmin()
    return idx
 
def get_data(data_file):
    """
    Reads the csv-file and returns numpy arrays for the time axis and signal axis
    
    Args:
        data_file: The path to the data file to open
    Returns:
        time_axis: A numpy array of all time points of the chromatogram
        signal_axis: A numpy array of all signal points of the chromatogram
    """
    with open(data_file) as f:
        all_lines = f.readlines()
    length = len(all_lines)
    time_axis = []
    signal_axis = []
    for i in range(2,length):
        line = all_lines[i].split(",")
        time = float(line[1])
        if time not in time_axis:
            time_axis.append(time)
            signal_axis.append(float(line[2]))    
        else:
            continue
    time_axis = np.array(time_axis)
    signal_axis = np.array(signal_axis)    
    return time_axis, signal_axis

def integrate (start, finish, time_axis, signal_axis):
    """
    Calculates the integral under a peak
    
    Args:
        start: Start time of the peak
        finish: End time of the peak
        time_axis: Numpy array of the time points
        signal_axis: Numpy array of the signal points
    Returns:
        area: Area of the peak
        baseline: List of y coordinates under the peak
    """
    for i, time_point in enumerate(time_axis):
        if time_point == start:
            start = i
        if time_point == finish:
            finish = i
    y_start = signal_axis[start]
    y_finish = signal_axis[finish]
    x_start = time_axis[start]
    x_finish = time_axis[finish]
    dy = y_finish-y_start
    dx = x_finish-x_start
    b = dy/dx
    a = y_start-(x_start*b)
    signal_minus_baseline=[]
    baseline = []
    for i, signal in enumerate(signal_axis):
        signal_minus_baseline.append(signal_axis[i]-(time_axis[i]*b+a))
        baseline.append(time_axis[i]*b+a)
        
    area = np.trapz(signal_minus_baseline[start:finish], time_axis[start:finish])
    
    return area, baseline
    
def color_peak(time_axis, signal_axis, baseline, start, finish):
    """
    Colors the integrated peaks from the constructed baseline upwards.
    
    Args:
        time_axis: Numpy array of the time points
        signal_axis: Numpy array of the signal points
        baseline: List of y coordinates under the peak
        start: Start time of the peak
        finish: End time of the peak
    """
    start = closest(time_axis, start)
    finish = closest(time_axis, finish)
    plt.fill_between(time_axis, signal_axis, baseline, where = (time_axis > time_axis[start]) & (time_axis <= time_axis[finish]))
    
def data_analysis(folder, results_folder, file, peaks):
    """
    Performs the analysis on a single data file.
    
    Args:
        folder: Path of the root folder
        results_folder: Path of the folder where the results will be
        file: Name of the data file
        peaks: A dictionary with the peak names as keys and tuples containing start time and end time as the values
    Returns:
        areas: A list of integrals per peak
    """
    path = os.path.join(folder, file)
    time_axis, signal_axis = get_data(path)
    plt.figure(figsize=(20,6))
    if x_axis:
        plt.xlim(x_axis)
    if y_axis:
        plt.ylim(y_axis)
    plt.plot(time_axis, signal_axis, color='k', linewidth = 0.3)
    areas = []
    for peak in peaks:
        time_range = peaks[peak]
        area, baseline = integrate(time_range[0], time_range[1], time_axis, signal_axis)
        areas.append(area)
        color_peak(time_axis, signal_axis, baseline, time_range[0], time_range[1])
    name = file.replace(".CSV", "")
    plt.savefig(os.path.join(results_folder, name + ".png"))
    return areas
    
def main():
    """
    Creates a file results in the given folder and creates pictures of all chromatograms in the results folder, as well as a csv file with all integrated peaks per file.
    """
    folder = os.path.join(root, name)
    start_time = datetime.datetime.now()
    files_in_folder = os.listdir(folder)
    data_points = []
    areas_total = []
    results_folder = os.path.join(folder, "results")
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)
    for i, file in enumerate(files_in_folder):
        if file.endswith(".CSV"):
            print(file)
            data_points.append(i*interval)
            areas_per_file = data_analysis(folder, results_folder, file, peaks)
            areas_total.append(areas_per_file)
    areas_total = np.array(areas_total)
    df = pd.DataFrame(areas_total)
    df.columns = list(peaks.keys())
    df["Time"] = data_points
    columns = list(df.columns)
    columns.insert(0, columns.pop())
    df = df[columns]
    df.to_csv(os.path.join(results_folder, f"Peak areas {name}.csv"), index=0)
    end_time = datetime.datetime.now()
    print("Run time: ", end_time-start_time)

if __name__ == "__main__":
    main()
