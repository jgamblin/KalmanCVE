# KalmanCVE

KalmanCVE is a reproducible, data-driven project for forecasting Common Vulnerabilities and Exposures (CVE) counts using the Kalman Filter and time series analysis. The project leverages the [Darts](https://unit8co.github.io/darts/) time series library and public data from the [National Vulnerability Database (NVD)](https://nvd.nist.gov/vuln/data-feeds).

## Project Overview
- **Goal:** Provide transparent, robust, and regularly updated forecasts of CVE counts for recent and upcoming years (2023, 2024, 2025).
- **Approach:** Each year has a dedicated Jupyter notebook that loads, cleans, and aggregates NVD data, fits a Kalman Filter model, and generates monthly forecasts. Diagnostics and validation steps are included for transparency.
- **Data Source:** NVD JSONL export (see [NVD Data Feeds](https://nvd.nist.gov/vuln/data-feeds)).
- **Forecasting Library:** [Darts](https://unit8co.github.io/darts/)
- **Visualization:** Matplotlib, pandas, and Darts built-in plotting.

## Notebooks
- `Kalman_2023.ipynb`: Forecasts and validates CVE counts for 2023.
- `Kalman_2024.ipynb`: Forecasts and validates CVE counts for 2024.
- `Kalman_2025.ipynb`: Forecasts and validates CVE counts for 2025. **This notebook updates every 6 hours.**

Each notebook includes:
- Data loading and validation
- Aggregation and exploratory analysis
- Model fitting and forecasting
- Diagnostics and visualizations
- Validation against actuals (where available)

## Usage
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Download the latest NVD data:**
   - Place the `nvd.jsonl` file in the project root directory.
3. **Open a notebook:**
   - Use JupyterLab, VS Code, or another compatible environment.
   - Run all cells in the desired notebook (e.g., `Kalman_2025.ipynb`).

## File Descriptions
- `Kalman_2023.ipynb`, `Kalman_2024.ipynb`, `Kalman_2025.ipynb`: Main forecasting notebooks for each year.
- `nvd.jsonl`: NVD data export (required for analysis).
- `requirements.txt`: Python dependencies.
- `forecast_plot.png`: Example output plot (optional).
- `LICENSE`: Project license (NIST data is public domain).

## Notes
- The 2025 notebook is scheduled to update every 6 hours to reflect the latest available data.
- All code is designed for reproducibility and transparency. See notebook markdown cells for detailed explanations.

## License
- NVD data is provided by NIST and is in the public domain. See: https://www.nist.gov/open/license
- Project code is licensed under the terms in `LICENSE`.