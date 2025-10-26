import sys
import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QFileDialog, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# adaptive bandpass filter
def dynamic_bandpass_filter(wavelengths, intensities, drop_ratio=0.01):
    max_intensity = np.max(intensities)
    peak_index = np.argmax(intensities)
    peak_wavelength = wavelengths[peak_index]

    threshold = max_intensity * drop_ratio

    # find the lower bound
    lower_bound_index = peak_index
    while lower_bound_index > 0 and intensities[lower_bound_index] > threshold:
        lower_bound_index -= 1
    lower_bound = wavelengths[lower_bound_index]

    # find upper bound
    upper_bound_index = peak_index
    while upper_bound_index < len(wavelengths) - 1 and intensities[upper_bound_index] > threshold:
        upper_bound_index += 1
    upper_bound = wavelengths[upper_bound_index]

    # filter
    filtered_intensities = np.where(
        (wavelengths >= lower_bound) & (wavelengths <= upper_bound),
        intensities,
        0
    )
    return filtered_intensities, (lower_bound, upper_bound, peak_wavelength)


# interpolate
def interpolate_data(wavelengths, intensities, min_wavelength=350, max_wavelength=1100, interval=1):
    target_wavelengths = np.arange(min_wavelength, max_wavelength + interval, interval)
    interp_func = interp1d(wavelengths, intensities, kind="linear", fill_value="extrapolate")
    interpolated_intensities = interp_func(target_wavelengths)
    return target_wavelengths, interpolated_intensities


# WebPlotDigitizer refine
def refine_webplot_data(wavelengths, intensities):
    # 使用小步长补全
    min_wavelength = max(350, wavelengths.min())
    max_wavelength = min(1100, wavelengths.max())
    small_step_wavelengths = np.arange(min_wavelength, max_wavelength, 0.1)
    interp_func = interp1d(wavelengths, intensities, kind="linear", fill_value="extrapolate")
    refined_intensities = interp_func(small_step_wavelengths)
    return small_step_wavelengths, refined_intensities


#  .irr
def load_irr_file(file_path):
    data = pd.read_csv(file_path, skiprows=2, sep='\s+', header=None)
    data.columns = ["Wavelength", "Intensity"]
    return data["Wavelength"].values, data["Intensity"].values


# load WebPlotDigitizer CSV
def load_webplotdigitizer_file(file_path):
    data = pd.read_csv(file_path, header=None)
    data.columns = ["Wavelength", "Intensity"]
    return data["Wavelength"].values, data["Intensity"].values


# main view
class SpectrumApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.target_wavelengths = None
        self.target_intensities = None

        self.initUI()

    def initUI(self):
        # main
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # view the area
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)

        # load button
        button_layout = QHBoxLayout()
        load_irr_button = QPushButton("Load from .irr File")
        load_irr_button.clicked.connect(self.load_irr_data)
        button_layout.addWidget(load_irr_button)

        load_webplot_button = QPushButton("Load from WebPlotDigitizer Result")
        load_webplot_button.clicked.connect(self.load_webplot_data)
        button_layout.addWidget(load_webplot_button)
        layout.addLayout(button_layout)


        self.setWindowTitle("Spectrum Processor with Refinement")
        self.resize(1200, 800)

    def load_irr_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select an .irr File", "", "IRR Files (*.irr)")
        if file_path:
            wavelengths, intensities = load_irr_file(file_path)
            self.process_and_save(wavelengths, intensities, file_path)

    def load_webplot_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a WebPlotDigitizer CSV File", "", "CSV Files (*.csv)")
        if file_path:
            wavelengths, intensities = load_webplotdigitizer_file(file_path)
            # fix
            refined_wavelengths, refined_intensities = refine_webplot_data(wavelengths, intensities)
            self.process_and_save(refined_wavelengths, refined_intensities, file_path)

    def process_and_save(self, wavelengths, intensities, file_path):
        #
        interp_wavelengths, interp_intensities = interpolate_data(wavelengths, intensities)
        filtered_intensities, band_info = dynamic_bandpass_filter(interp_wavelengths, interp_intensities)

        # plot
        self.ax.clear()
        self.ax.plot(interp_wavelengths, interp_intensities, label="Interpolated Spectrum", color="blue")
        self.ax.plot(interp_wavelengths, filtered_intensities, label="Filtered Spectrum", color="green")
        self.ax.axvline(band_info[0], color="orange", linestyle="--", label=f"Lower Bound: {band_info[0]:.1f} nm")
        self.ax.axvline(band_info[1], color="red", linestyle="--", label=f"Upper Bound: {band_info[1]:.1f} nm")
        self.ax.axvline(band_info[2], color="purple", linestyle="--", label=f"Peak: {band_info[2]:.1f} nm")
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Intensity")
        self.ax.legend()
        self.ax.set_title("Processed Spectrum")
        self.ax.grid()
        self.canvas.draw()

        # save
        output_dir = "data/csv"
        os.makedirs(output_dir, exist_ok=True)  # 确保目录存在

        # _processed.csv
        file_name = os.path.basename(file_path)
        if file_name.endswith(".irr"):
            output_file = os.path.join(output_dir, file_name.replace(".irr", "_processed.csv"))
        elif file_name.endswith(".csv"):
            output_file = os.path.join(output_dir, file_name.replace(".csv", "_processed.csv"))
        else:
            output_file = os.path.join(output_dir, file_name + "_processed.csv")  # 默认添加 _processed.csv 后缀

        # DataFrame
        processed_data = pd.DataFrame({
            "Wavelength": interp_wavelengths,
            "Intensity": filtered_intensities
        })

        # CSV
        try:
            processed_data.to_csv(output_file, index=False)
            QMessageBox.information(self, "Success", f"Processed data saved to:\n{output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save processed data:\n{str(e)}")


# 主程序
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SpectrumApp()
    main_window.show()
    sys.exit(app.exec_())
