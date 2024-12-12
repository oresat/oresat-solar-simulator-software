import pandas as pd
import numpy as np


def load_irr_file(input_file):
    """
    read.IRR
    """
    with open(input_file, 'r') as file:
        lines = file.readlines()

    data = []
    for line in lines[2:]:  # jump the first two lines
        line = line.strip()
        if not line:
            continue
        try:
            wavelength, intensity = map(float, line.split())
            data.append((wavelength, intensity))
        except ValueError:
            continue

    df = pd.DataFrame(data, columns=["Wavelength", "Intensity"])
    return df

def interpolate_data(df, min_wavelength=350, max_wavelength=1100, interval=1):
    """
    Interpolates the data to cover the wavelength range [350, 1100] with the specified interval.
    """
    target_wavelengths = np.arange(min_wavelength, max_wavelength + interval, interval)
    interpolated_intensity = np.interp(target_wavelengths, df["Wavelength"], df["Intensity"])

    interpolated_df = pd.DataFrame({"Wavelength": target_wavelengths, "Intensity": interpolated_intensity})
    return interpolated_df


def filter_uv_light(df, uv_min=350, uv_max=400):
    """
    Filters UV light, retaining values only within the range 350-400 nm, and sets the intensity of other wavelengths to 0.
    """
    df["Intensity"] = np.where(
        (df["Wavelength"] >= uv_min) & (df["Wavelength"] <= uv_max),
        df["Intensity"],
        0
    )
    return df


def process_irr_file(input_file, output_file, min_wavelength=350, max_wavelength=1100, interval=1, uv_min=350, uv_max=400):
    """
    Processes the .IRR file: performs interpolation and UV filtering.
    """
    # Load raw data
    raw_data = load_irr_file(input_file)

    # Interpolate to the target wavelength range
    interpolated_data = interpolate_data(raw_data, min_wavelength, max_wavelength, interval)

    # Apply UV light filtering
    filtered_data = filter_uv_light(interpolated_data, uv_min, uv_max)

    # Save the processed data
    filtered_data.to_csv(output_file, index=False)
    return filtered_data


if __name__ == "__main__":
    # Input parameters
    input_file = r"data\solar0.7.IRR"  # Path to the input IRR file
    output_file = r"data\solar0.7_processed.csv"  # Path to the output processed file
    min_wavelength = 350  # Minimum wavelength for interpolation
    max_wavelength = 1100  # Maximum wavelength for interpolation
    interval = 1  # Interval for interpolation
    uv_min = 350  # Minimum wavelength for UV filtering
    uv_max = 1100  # Maximum wavelength for UV filtering

    # Process the file
    processed_data = process_irr_file(input_file, output_file, min_wavelength, max_wavelength, interval, uv_min, uv_max)
    print("Processed Data:")
    print(processed_data)
