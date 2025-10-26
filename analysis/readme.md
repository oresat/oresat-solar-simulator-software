python test_linear.py --config red_test.json
python test_linear.py --config gre_test.json
python test_linear.py --config blu_test.json
python test_linear.py --config hal_test.json
python test_linear.py --config uv_test.json





https://docs.google.com/document/d/1bcTt2vkAWG7h-xJZIvkrwsgkZY4AE9e94BsM26iTa2U/edit?tab=t.0
brief overview of what i was trying to do



# **IRR Data Linearity Analysis**

This project implements a linearity analysis tool for `.IRR` spectral data files. It evaluates whether the spectral intensity of different light sources (e.g., red, green, blue, halogen, UV) scales linearly with intensity percentages.

## **Features**
- Supports filtering `.IRR` files by a specified wavelength range.
- Fits a linear model to verify the relationship between spectral intensity and input power percentage.
- Allows dynamic configuration of light source and intensity ranges via JSON configuration files.
- Visualizes the results of the linear analysis with detailed plots.

---

## **Prerequisites**
- Python 3.8 or above
- Required Python libraries:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `scipy`

Install the required libraries using:
```bash
pip install numpy pandas matplotlib scipy
```

---

## **Usage**

### **1. Prepare JSON Configuration Files**
Create JSON files for each light source, specifying the data directory, light source intensity files, and a base intensity file.

Example: `red_test.json`
```json
{
    "base_dir": "data",
    "lights": {
        "red": ["23", "24", "25", "26", "27", "28", "29", "30"]
    },
    "base_intensity": {
        "red": "26"
    }
}
```

Other configuration files (e.g., `gre_test.json`, `blu_test.json`) should follow the same structure, with appropriate light source names and intensity ranges.

---

### **2. Run the Analysis**

Run the analysis for a specific light source using:
```bash
python test_linear.py --config red_test.json
```

Replace `red_test.json` with the appropriate configuration file for the desired light source:
```bash
python test_linear.py --config gre_test.json
python test_linear.py --config blu_test.json
python test_linear.py --config hal_test.json
python test_linear.py --config uv_test.json
```

---

### **3. Outputs**
- **Fitted `k` Values**:
  - The script outputs the fitted `k` values for each intensity level.
- **Linear Model Parameters**:
  - The slope and intercept of the fitted linear model are printed to the console.
- **Visualization**:
  - A plot of `k` vs. intensity is displayed, showing the measured data and the fitted linear trend.

---

## **Project Structure**
- **`test_linear.py`**: Main script for executing the linearity analysis.
- **`data/`**: Directory containing the `.IRR` files for different light sources.
- **JSON Config Files**:
  - Specify the directory, light sources, intensity percentages, and base intensity file.

---

## **Example Output**
Running:
```bash
python test_linear.py --config red_test.json
```

Console output:
```
Fitted k for red: [0.88, 0.92, 0.95, 1.00, 1.03, 1.08, 1.12, 1.15]
Linear Fit Parameters for red: Slope = 0.0123, Intercept = -0.0015
```

Plot:
- A scatter plot showing the measured `k` values vs. intensity.
- A line showing the fitted linear trend \( k = 	ext{slope} \cdot 	ext{intensity} + 	ext{intercept} \).

---

## **Customizing Analysis**
To customize the analysis:
1. Add new `.IRR` files to the `data/` directory.
2. Update the JSON configuration file to include the new intensity percentages and light sources.
3. Run the analysis with the updated configuration.

---

## **Contact**
For questions or issues, please contact the project maintainer.
