import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import linregress
import matplotlib.pyplot as plt


# Load spectral data
def load_spectrum_data(file_path):
    """
    Load spectral data from a CSV file.
    """
    data = pd.read_csv(file_path)
    return data["Wavelength"].values, data["Intensity"].values


# Define piecewise linear fitting formula
def calculate_intensity(spectrum, intensity, light_type):
    """
    Calculate the actual spectral intensity using a piecewise linear formula (with soft limits).
    """
    if light_type == "hal":
        factor = 0.01 * intensity - 0.09
    elif light_type in ["blu", "gre", "red", "uv"]:
        if intensity > 50:
            intensity = 50
        if light_type == "blu":
            factor = 0.03 * intensity - 0.63
        elif light_type == "gre":
            factor = 0.03 * intensity - 0.49
        elif light_type == "red":
            factor = 0.03 * intensity - 0.68
        elif light_type == "uv":
            factor = 0.03 * intensity - 0.66
    else:
        raise ValueError(f"Unknown light type: {light_type}")

    return factor * spectrum


# Define the error function
def error_function(intensity_factors, target_spectrum, source_spectra, light_types):
    """
    Objective function: calculate the error between the combined spectrum and the target spectrum.
    """
    combined_spectrum = np.zeros_like(target_spectrum)
    for factor, source, light_type in zip(intensity_factors, source_spectra, light_types):
        adjusted_intensity = calculate_intensity(source, factor, light_type)
        combined_spectrum += adjusted_intensity

    error = np.sum((target_spectrum - combined_spectrum) ** 2)
    return error


# Optimize light source intensities
def optimize_light_intensities(target_intensity, source_spectra, light_types, bounds):
    """
    Optimize the light source intensity combination to match the target spectrum.
    """
    initial_factors = [0.5] * len(source_spectra)

    result = minimize(
        error_function,
        initial_factors,
        args=(target_intensity, source_spectra, light_types),
        method='SLSQP',
        bounds=bounds
    )

    return result.x, result.fun


# Main program
if __name__ == "__main__":
    target_file = "data/reference/Interpolated_Solar_Data.csv"
    source_files = [
        "data/reference/red100_processed.csv",
        "data/reference/gre100_processed.csv",
        "data/reference/blu100_processed.csv",
        "data/reference/hal100_processed.csv",
        "data/reference/uv100_processed.csv"
    ]

    light_types = ["red", "gre", "blu", "hal", "uv"]
    bounds = [(0, 100)] * len(light_types)

    wavelengths, target_intensity = load_spectrum_data(target_file)
    source_spectra = [load_spectrum_data(file)[1] for file in source_files]

    scaling_factors = np.linspace(0, 0.6, 20)
    errors = []
    all_intensity_factors = []

    for scale in scaling_factors:
        scaled_target_intensity = target_intensity * scale
        intensity_factors, error = optimize_light_intensities(
            scaled_target_intensity, source_spectra, light_types, bounds
        )
        errors.append(error)
        all_intensity_factors.append(intensity_factors)

    # Linear regression for intensity trends
    intensity_fit_results = []
    for i, light_type in enumerate(light_types):
        y_values = [factors[i] for factors in all_intensity_factors]
        slope, intercept, r_value, p_value, std_err = linregress(scaling_factors, y_values)
        intensity_fit_results.append((light_type, slope, intercept, r_value**2))
        print(f"{light_type} Fit: Intensity = {slope:.4f} * Scaling_Factor + {intercept:.4f}, R^2 = {r_value**2:.4f}")
