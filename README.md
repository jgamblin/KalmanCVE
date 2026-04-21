# KalmanCVE

KalmanCVE forecasts Common Vulnerabilities and Exposures (CVE) counts using the Kalman Filter and time series analysis. It uses the [Darts](https://unit8co.github.io/darts/) library and public data from the [National Vulnerability Database (NVD)](https://nvd.nist.gov/vuln/data-feeds).

## Overview

- **Goal:** Provide transparent, robust, and regularly updated forecasts of CVE counts.
- **Data Source:** NVD JSONL export (public domain, provided by NIST).
- **Model:** Kalman Filter via Darts `KalmanForecaster`.
- **Automation:** GitHub Actions runs the forecast every 6 hours and commits the updated plot.

## Installation

```bash
pip install .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Download NVD data and run forecast for the current year
kalmancve

# Use a local data file
kalmancve --data-file nvd.jsonl

# Forecast a specific year with verbose output
kalmancve --year 2025 --verbose

# Save validation table as CSV
kalmancve --data-file nvd.jsonl --output-csv results.csv

# Skip plot generation
kalmancve --data-file nvd.jsonl --no-plot
```

### Options

```
--year INTEGER          Forecast year (default: current year)
--start-date TEXT       Training data start date (default: 2017-01-01)
--dim-x INTEGER         Kalman filter state dimension (default: 2)
--num-samples INTEGER   Monte Carlo samples (default: 1000)
--data-url TEXT         NVD JSONL URL
--data-file PATH        Use local file (skip download)
--output-plot PATH      Plot output path (default: forecast_plot.png)
--output-csv PATH       Save validation table as CSV
--no-plot               Skip plot generation
--verbose               Enable verbose output
--version               Show version
```

## Output

The tool prints a validation table comparing predicted vs actual CVE counts by month, and generates a forecast plot (`forecast_plot.png`).

## Testing

```bash
pytest
```

## Files

- `src/kalmancve/` — Python package with CLI, data loading, forecasting, reporting, and plotting modules.
- `notebooks/` — Archive of original Jupyter notebooks (2023, 2024, 2025).
- `forecast_plot.png` — Latest forecast visualization (updated every 6 hours by CI).

## License

- NVD data is provided by NIST and is in the public domain. See: https://www.nist.gov/open/license
- Project code is licensed under the terms in `LICENSE` (Apache 2.0).
