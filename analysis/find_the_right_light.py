import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QSlider, QLineEdit, QFormLayout
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Lorentzian function to simulate LED spectrum
def lorentzian(wavelengths, intensity, center, fwhm):
    gamma = fwhm / 2  # Half width at half maximum
    return intensity * gamma**2 / ((wavelengths - center)**2 + gamma**2)


# Load spectral data
def load_spectrum_data(file_path):
    data = pd.read_csv(file_path)
    return data["Wavelength"].values, data["Intensity"].values


# Optimize base source scaling
def optimize_scaling_factor(target_intensities, base_intensities):
    def error(scale_factor):
        scaled_base = base_intensities * scale_factor
        return np.sum((target_intensities - scaled_base) ** 2)

    result = minimize(error, x0=1.0, bounds=[(0.1, 10.0)], method="SLSQP")
    return result.x[0] if result.success else 1.0


# Main Application Window
class SpectrumApp(QMainWindow):
    def __init__(self, target_wavelengths, target_intensities, base_wavelengths, base_intensities):
        super().__init__()

        self.target_wavelengths = target_wavelengths
        self.target_intensities = target_intensities

        # Pre-optimize base source scaling
        self.base_intensity_factor = optimize_scaling_factor(target_intensities, base_intensities)
        self.base_spectrum = base_intensities * self.base_intensity_factor

        # Store base source and additional LEDs (intensity, center wavelength, FWHM)
        self.leds = [[1.0, None, None, self.base_spectrum]]  # Base source: [intensity, center, fwhm, spectrum]

        self.initUI()

    def initUI(self):
        # Main widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)

        # Add controls for adding LEDs
        controls_layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.center_input = QLineEdit(self)
        self.fwhm_input = QLineEdit(self)
        form_layout.addRow("Center Wavelength (nm):", self.center_input)
        form_layout.addRow("FWHM (nm):", self.fwhm_input)
        controls_layout.addLayout(form_layout)

        add_led_button = QPushButton("Add LED")
        add_led_button.clicked.connect(self.add_led)
        controls_layout.addWidget(add_led_button)

        # Add LED sliders
        self.sliders_layout = QVBoxLayout()
        controls_layout.addLayout(self.sliders_layout)

        layout.addLayout(controls_layout)

        # Add base source slider
        self.add_led_controls(0, base=True)

        # Initial plot
        self.plot_spectrum()

        # Set window properties
        self.setWindowTitle("LED Spectrum Fitting with Lorentzian Model")
        self.resize(1200, 800)

    def add_led(self):
        # Get user input for new LED
        try:
            center = float(self.center_input.text())
            fwhm = float(self.fwhm_input.text())
            intensity = 0.1  # Default intensity
        except ValueError:
            print("Invalid input for center wavelength or FWHM")
            return

        # Add LED parameters
        self.leds.append([intensity, center, fwhm, None])

        # Add slider for the new LED
        self.add_led_controls(len(self.leds) - 1)
        self.plot_spectrum()

    def add_led_controls(self, index, base=False):
        # Add controls for a specific LED
        if base:
            led_label = QLabel(f"Base Source (Halogen, Initial Fit):")
        else:
            center, fwhm = self.leds[index][1], self.leds[index][2]
            led_label = QLabel(f"LED {index}: Center={center}nm, FWHM={fwhm}nm")

        intensity_slider = QSlider(Qt.Horizontal)
        intensity_slider.setMinimum(0)
        intensity_slider.setMaximum(100)
        intensity_slider.setValue(int(self.leds[index][0] * 100))
        intensity_slider.valueChanged.connect(lambda value, idx=index: self.update_led_intensity(idx, value))

        self.sliders_layout.addWidget(led_label)
        self.sliders_layout.addWidget(intensity_slider)

    def update_led_intensity(self, index, value):
        # Update the intensity of a specific LED
        self.leds[index][0] = value / 100.0
        self.plot_spectrum()

    def plot_spectrum(self):
        self.ax.clear()

        # Plot real-time and target spectra
        self.ax.plot(self.target_wavelengths, self.target_intensities, label="Target Spectrum", color="blue", alpha=0.7)

        # Combine LEDs to create a simulated spectrum
        combined_spectrum = np.zeros_like(self.target_intensities)
        for intensity, center, fwhm, spectrum in self.leds:
            if spectrum is not None:  # Base source
                led_spectrum = intensity * spectrum
            else:  # Custom LED
                led_spectrum = lorentzian(self.target_wavelengths, intensity, center, fwhm)

            combined_spectrum += led_spectrum
            self.ax.plot(self.target_wavelengths, led_spectrum, linestyle="--", alpha=0.5, label=f"LED: {center}nm" if center else "Base Source")

        # Plot combined spectrum
        self.ax.plot(self.target_wavelengths, combined_spectrum, label="Fitted Spectrum", color="green", alpha=0.8)

        # Difference area
        self.ax.fill_between(self.target_wavelengths, combined_spectrum, self.target_intensities, color="gray", alpha=0.3, label="Difference")

        # Update plot
        self.ax.legend(fontsize=10)
        self.ax.set_title("LED Spectrum Fitting with Lorentzian Model", fontsize=14)
        self.ax.set_xlabel("Wavelength (nm)", fontsize=12)
        self.ax.set_ylabel("Intensity (arbitrary units)", fontsize=12)
        self.ax.grid(True)
        self.canvas.draw()


# Main program
if __name__ == "__main__":
    # Load target spectrum
    target_file = "data/reference/Interpolated_Solar_Data.csv"
    target_wavelengths, target_intensities = load_spectrum_data(target_file)

    # Load base source spectrum (halogen)
    base_file = "data/reference/hal100_processed.csv"
    base_wavelengths, base_intensities = load_spectrum_data(base_file)

    # Ensure target and base wavelengths match
    if not np.array_equal(target_wavelengths, base_wavelengths):
        raise ValueError("Target and base source wavelengths do not match!")

    # Launch PyQt5 application
    app = QApplication(sys.argv)
    main_window = SpectrumApp(target_wavelengths, target_intensities, base_wavelengths, base_intensities)
    main_window.show()
    sys.exit(app.exec_())
