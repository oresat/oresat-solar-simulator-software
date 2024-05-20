# Spectrometer Irradiance Analysis

This script processes irradiance data files and classifies the solar simulation accuracy based on IEC 60904-9.

## Usage

1. Capture an Episodic Spectra file using a SpectraWiz spectrometer.
2. Export the Episodic Spectra file to a group of *.irr* files using SpectraWiz.
3. Put all of the *.irr* files into a data folder.
4. Run the script with the path to your data folder as an argument:
   ```sh
   python spectrometer_time_graph.py /path/to/data/folder
   ```

## Visualization

The script generates a plot showing the irradiance over time for different wavelength ranges. The background color of the plot segments indicates the accuracy classification:
- **A+:** Light blue
- **A:** Light green
- **B:** Yellow
- **C:** Orange
- **D:** Red

![Graphical Example](spectrometer-time-graph-example.png)

## TODO

- Better documentation of usage of SpectraWiz
- Documentation of SpectraWiz capture and export process, including screenshots.
