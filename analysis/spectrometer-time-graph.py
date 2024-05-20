import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Load data files
def load_data_files(data_folder):
    return [f for f in os.listdir(data_folder) if f.endswith('.irr')]

# Condense data into specified wavelength ranges
def condense_data(file_path):
    data = pd.read_csv(file_path, skiprows=4, delim_whitespace=True, header=None, names=['Wavelength', 'Intensity'])
    ranges = {
        '400-500': data[(data['Wavelength'] >= 400) & (data['Wavelength'] < 500)]['Intensity'].sum(),
        '500-600': data[(data['Wavelength'] >= 500) & (data['Wavelength'] < 600)]['Intensity'].sum(),
        '600-700': data[(data['Wavelength'] >= 600) & (data['Wavelength'] < 700)]['Intensity'].sum(),
        '700-800': data[(data['Wavelength'] >= 700) & (data['Wavelength'] < 800)]['Intensity'].sum(),
        '800-900': data[(data['Wavelength'] >= 800) & (data['Wavelength'] < 900)]['Intensity'].sum(),
        '900-1100': data[(data['Wavelength'] >= 900) & (data['Wavelength'] <= 1100)]['Intensity'].sum(),
    }
    return ranges

# Classify accuracy based on IEC 60904-9
def classify_accuracy(ranges):
    expected_percentages = {
        '400-500': 18.4,
        '500-600': 19.9,
        '600-700': 18.4,
        '700-800': 14.9,
        '800-900': 12.5,
        '900-1100': 15.9
    }
    total_intensity = sum(ranges.values())
    
    if total_intensity == 0:
        return 'D'  # Return 'D' if total intensity is zero to avoid division by zero
    
    actual_percentages = {key: (value / total_intensity) * 100 for key, value in ranges.items()}
    deviations = [abs((actual_percentages[key] / expected_percentages[key])) for key in ranges]
    max_deviation = max(deviations)
    min_deviation = min(deviations)

    if max_deviation <= 1.125 and min_deviation >= 0.875:
        return 'A+'
    elif max_deviation <= 1.25 and min_deviation >= 0.75:
        return 'A'
    elif max_deviation <= 1.4 and min_deviation >= 0.6:
        return 'B'
    elif max_deviation <= 2.0 and min_deviation >= 0.4:
        return 'C'
    else:
        return 'D'

# Main function to process data files and classify them
def main(data_folder):
    data_files = load_data_files(data_folder)
    data_files.reverse()

    results = []

    for idx, file in enumerate(data_files):
        file_path = os.path.join(data_folder, file)
        ranges = condense_data(file_path)
        accuracy = classify_accuracy(ranges)
        result = {'File': file, 'Time': idx + 1, **ranges, 'Accuracy': accuracy}
        results.append(result)

    df = pd.DataFrame(results)

    # Select only the first 100 rows for plotting
    df = df.head(100)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8))

    for col in ['400-500', '500-600', '600-700', '700-800', '800-900', '900-1100']:
        ax.plot(df['Time'], df[col], label=col)

    # Add background color based on accuracy
    for idx in df.index:
        accuracy = df.loc[idx, 'Accuracy']
        time = df.loc[idx, 'Time']
        if accuracy == 'A+':
            color = 'lightblue'
        elif accuracy == 'A':
            color = 'lightgreen'
        elif accuracy == 'B':
            color = 'yellow'
        elif accuracy == 'C':
            color = 'orange'
        else:
            color = 'red'

        if idx < len(df) - 1:
            next_time = df.loc[idx + 1, 'Time']
        else:
            next_time = time + 1  # For the last segment

        ax.axvspan(time, next_time, facecolor=color, alpha=0.3)

    ax.set_xlabel('File Index')
    ax.set_ylabel('Irradiance (arbitrary units)')
    ax.set_title('Irradiance over Time for Different Wavelength Ranges')
    ax.legend()
    ax.grid(True)

    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <data_folder>")
        sys.exit(1)
    data_folder = sys.argv[1]
    main(data_folder)
