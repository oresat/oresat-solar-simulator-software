import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import json
import argparse


# defination of different range of light
WAVELENGTH_RANGES = {
    "red": (600, 660),
    "gre": (480, 600),
    "blu": (420, 520),
    "hal": (0, 900),
    "uv": (350, 400)
}


def parse_intensity_range(intensity_range):
    """
    Parse intensity range from JSON, supporting both ranges and specific values.
    """
    parsed_intensities = []
    for item in intensity_range:
        if "-" in item:
            start, end = map(int, item.split("-"))
            parsed_intensities.extend(range(start, end + 1))
        else:
            parsed_intensities.append(int(item))
    return parsed_intensities


def load_and_filter_irr(file_path, min_wavelength, max_wavelength):
    """
    Load .IRR file and filter by wavelength range.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()
    data = []
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            continue
        try:
            values = [float(x) for x in line.split()]
            if len(values) == 2:
                data.append(values)
        except ValueError:
            continue
    df = pd.DataFrame(data, columns=["Wavelength (nm)", "Intensity (W/m^2/nm)"], dtype=float)
    filtered_df = df[(df["Wavelength (nm)"] >= min_wavelength) & (df["Wavelength (nm)"] <= max_wavelength)]
    return filtered_df["Wavelength (nm)"].values, filtered_df["Intensity (W/m^2/nm)"].values


def verify_global_linear_relationship(file_paths, base_file_path, intensities, light_name):
    """
    Verify linear relationship between intensity and spectral distribution.
    """
    min_wavelength, max_wavelength = WAVELENGTH_RANGES[light_name]  # gain range of wavelength

    # load base file
    _, base_intensity = load_and_filter_irr(base_file_path, min_wavelength, max_wavelength)

    all_data = []
    valid_intensities = []

    for i, file_path in enumerate(file_paths):
        if os.path.exists(file_path):
            _, intensity = load_and_filter_irr(file_path, min_wavelength, max_wavelength)
            all_data.append(intensity)
            valid_intensities.append(intensities[i])

    intensity_matrix = np.array(all_data)

    def linear_model(k, a):
        return k * a

    fitted_k = []
    for i, intensity in enumerate(valid_intensities):
        y = intensity_matrix[i, :]
        x = base_intensity
        popt, _ = curve_fit(linear_model, x, y)
        fitted_k.append(popt[0])

    def linear_intensity_model(intensity, a, b):
        return a * intensity + b

    popt, _ = curve_fit(linear_intensity_model, valid_intensities, fitted_k)
    linear_fit = [linear_intensity_model(i, *popt) for i in valid_intensities]

    plt.figure(figsize=(8, 6))
    plt.scatter(valid_intensities, fitted_k, label="Measured k", color="blue")
    plt.plot(valid_intensities, linear_fit, label=f"Fitted Line: k = {popt[0]:.2f} * intensity + {popt[1]:.2f}",
             color="green")
    plt.title(f"Linearity of k vs Intensity ({light_name}_analysis)")
    plt.xlabel("Intensity (%)")
    plt.ylabel("Fitted k")
    plt.legend()
    plt.grid()
    plt.show()

    return fitted_k, popt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze light source linearity with configurable JSON files.")
    parser.add_argument("--config", type=str, required=True, help="Path to the JSON configuration file.")
    args = parser.parse_args()

    config_path = args.config
    with open(config_path, "r") as file:
        config = json.load(file)

    base_dir = config["base_dir"]
    lights = config["lights"]
    base_intensity = config["base_intensity"]

    for light, intensity_range in lights.items():
        intensities = parse_intensity_range(intensity_range)  # Parse ranges into individual intensity values
        file_paths = [os.path.join(base_dir, f"{light}{intensity}.IRR") for intensity in intensities]
        base_file_path = os.path.join(base_dir, f"{light}{base_intensity[light]}.IRR")

        fitted_k, linear_params = verify_global_linear_relationship(
            file_paths, base_file_path, intensities, light_name=light
        )
        print(f"Fitted k for {light}: {fitted_k}")
        print(f"Linear Fit Parameters for {light}: Slope = {linear_params[0]:.2f}, Intercept = {linear_params[1]:.2f}")
