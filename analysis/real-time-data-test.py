import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QSlider, QLineEdit, QFormLayout, QFileDialog
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


# Optimize all LEDs for best fit
def optimize_leds(target_intensities, leds):
    def error(intensity_factors):
        combined_spectrum = np.zeros_like(target_intensities)
        for factor, (_, max_intensity, center, fwhm, spectrum) in zip(intensity_factors, leds):
            if spectrum is not None:  # Custom or base spectrum
                led_spectrum = spectrum * (factor / max_intensity)
            else:  # Lorentzian-based LED
                led_spectrum = lorentzian(target_intensities, factor, center, fwhm)
            combined_spectrum += led_spectrum
        return np.sum((target_intensities - combined_spectrum) ** 2)

    initial_factors = [led[0] for led in leds]
    bounds = [(0, led[1]) for led in leds]

    result = minimize(error, initial_factors, bounds=bounds, method="SLSQP")
    return result.x if result.success else initial_factors


# Main Application Window
class SpectrumApp(QMainWindow):
    def __init__(self, target_wavelengths, target_intensities, base_wavelengths, base_intensities):
        super().__init__()

        self.target_wavelengths = target_wavelengths
        self.target_intensities = target_intensities

        # Best fit base source to target
        best_fit_factor = optimize_scaling_factor(target_intensities, base_intensities)
        self.base_spectrum = base_intensities * best_fit_factor

        # Store base source and additional LEDs (current_intensity, max_intensity, center, FWHM, spectrum)
        self.leds = [[1.0, 1.0, None, None, self.base_spectrum]]  # Base source

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
        self.max_intensity_input = QLineEdit(self)
        form_layout.addRow("Center Wavelength (nm):", self.center_input)
        form_layout.addRow("FWHM (nm):", self.fwhm_input)
        form_layout.addRow("Max Intensity:", self.max_intensity_input)
        controls_layout.addLayout(form_layout)

        add_led_button = QPushButton("Add LED (Lorentzian)")
        add_led_button.clicked.connect(self.add_led)
        controls_layout.addWidget(add_led_button)

        add_spectrum_button = QPushButton("Add LED (Spectrum File)")
        add_spectrum_button.clicked.connect(self.add_spectrum_led)
        controls_layout.addWidget(add_spectrum_button)

        # Best Fit button
        best_fit_button = QPushButton("Best Fit")
        best_fit_button.clicked.connect(self.best_fit)
        controls_layout.addWidget(best_fit_button)

        # Fit Score label
        self.fit_score_label = QLabel("Fit Score: N/A", self)
        controls_layout.addWidget(self.fit_score_label)

        # Add LED sliders
        self.sliders_layout = QVBoxLayout()
        controls_layout.addLayout(self.sliders_layout)

        layout.addLayout(controls_layout)

        # Add base source slider
        self.add_led_controls(0, base=True)

        # Initial plot
        self.plot_spectrum()

        # Set window properties
        self.setWindowTitle("LED Spectrum Fitting with Best Fit Base")
        self.resize(1200, 800)

    def add_led(self):
        # Get user input for new LED (Lorentzian)
        try:
            center = float(self.center_input.text())
            fwhm = float(self.fwhm_input.text())
            max_intensity = float(self.max_intensity_input.text())
            intensity = 0.1 * max_intensity  # Default initial intensity (10%)
        except ValueError:
            print("Invalid input for center wavelength, FWHM, or max intensity")
            return

        # Add LED parameters
        self.leds.append([intensity, max_intensity, center, fwhm, None])

        # Add slider for the new LED
        self.add_led_controls(len(self.leds) - 1)
        self.plot_spectrum()

    def add_spectrum_led(self):
        # Load spectrum file as new LED
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Spectrum File", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            wavelengths, intensities = load_spectrum_data(file_path)
            if not np.array_equal(wavelengths, self.target_wavelengths):
                raise ValueError("Loaded spectrum wavelengths do not match the target spectrum.")
        except Exception as e:
            print(f"Error loading spectrum file: {e}")
            return

        max_intensity = np.max(intensities)  # Use the actual spectrum as the maximum intensity
        self.leds.append([max_intensity, max_intensity, None, None, intensities])

        # Add slider for the new LED
        self.add_led_controls(len(self.leds) - 1, spectrum_file=True)
        self.plot_spectrum()

    def add_led_controls(self, index, base=False, spectrum_file=False):
        # Add controls for a specific LED
        if base:
            led_label = QLabel(f"Base Source (Best Fit, 100% Intensity):")
        elif spectrum_file:
            led_label = QLabel(f"LED {index}: Custom Spectrum (100% Max)")
        else:
            center, fwhm, max_intensity = self.leds[index][2], self.leds[index][3], self.leds[index][1]
            led_label = QLabel(f"LED {index}: Center={center}nm, FWHM={fwhm}nm, Max={max_intensity:.1f}")

        intensity_slider = QSlider(Qt.Horizontal)
        intensity_slider.setMinimum(0)
        intensity_slider.setMaximum(100)  # Slider in percentage
        intensity_slider.setValue(100)  # Default to 100%
        intensity_slider.valueChanged.connect(lambda value, idx=index: self.update_led_intensity(idx, value))

        self.sliders_layout.addWidget(led_label)
        self.sliders_layout.addWidget(intensity_slider)

    def update_led_intensity(self, index, value):
        # Update the intensity of a specific LED
        self.leds[index][0] = (value / 100.0) * self.leds[index][1]
        self.plot_spectrum()

    def best_fit(self):
        # Optimize all LEDs for best fit
        best_fit_intensities = optimize_leds(self.target_intensities, self.leds)
        for i, intensity in enumerate(best_fit_intensities):
            self.leds[i][0] = intensity  # Update LED intensities
        self.plot_spectrum()

        # Calculate and display fit score
        combined_spectrum = np.zeros_like(self.target_intensities)
        for current_intensity, max_intensity, center, fwhm, spectrum in self.leds:
            if spectrum is not None:
                combined_spectrum += spectrum * (current_intensity / max_intensity)
            else:
                combined_spectrum += lorentzian(self.target_wavelengths, current_intensity, center, fwhm)
        fit_score = np.sum((self.target_intensities - combined_spectrum) ** 2)
        self.fit_score_label.setText(f"Fit Score: {fit_score:.2f}")

    def plot_spectrum(self):
        self.ax.clear()

        # Plot real-time and target spectra
        self.ax.plot(self.target_wavelengths, self.target_intensities, label="Target Spectrum", color="blue", alpha=0.7)

        # Combine LEDs to create a simulated spectrum
        combined_spectrum = np.zeros_like(self.target_intensities)
        for current_intensity, max_intensity, center, fwhm, spectrum in self.leds:
            if spectrum is not None:  # Custom or base spectrum
                led_spectrum = spectrum * (current_intensity / max_intensity)
                label = f"Custom Spectrum ({int((current_intensity / max_intensity) * 100)}%)"
            else:  # Lorentzian-based LED
                led_spectrum = lorentzian(self.target_wavelengths, current_intensity, center, fwhm)
                label = f"LED: {center}nm ({int((current_intensity / max_intensity) * 100)}%)"

            combined_spectrum += led_spectrum
            self.ax.plot(self.target_wavelengths, led_spectrum, linestyle="--", alpha=0.5, label=label)

        # Plot combined spectrum
        self.ax.plot(self.target_wavelengths, combined_spectrum, label="Fitted Spectrum", color="green", alpha=0.8)

        # Difference area
        self.ax.fill_between(self.target_wavelengths, combined_spectrum, self.target_intensities, color="gray", alpha=0.3, label="Difference")

        # Update plot
        self.ax.legend(fontsize=10)
        self.ax.set_title("LED Spectrum Fitting with Best Fit Base", fontsize=14)
        self.ax.set_xlabel("Wavelength (nm)", fontsize=12)
        self.ax.set_ylabel("Intensity", fontsize=12)
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

