import logging
import warnings
from datetime import date

import click
import numpy as np

from . import __version__
from .config import ForecastConfig
from .data import (
    aggregate_monthly,
    clean_nvd_data,
    compute_summary_stats,
    download_nvd_data,
    load_nvd_jsonl,
)
from .forecast import fit_and_predict, prediction_to_dataframe
from .plot import plot_forecast
from .report import build_validation_table, print_report, save_csv


@click.command()
@click.option("--year", default=date.today().year, help="Forecast year.", show_default=True)
@click.option(
    "--start-date", default="2017-01-01", help="Training data start date.", show_default=True
)
@click.option("--dim-x", default=2, help="Kalman filter state dimension.", show_default=True)
@click.option("--num-samples", default=1000, help="Monte Carlo samples.", show_default=True)
@click.option(
    "--data-url", default="https://nvd.handsonhacking.org/nvd.jsonl", help="NVD JSONL URL."
)
@click.option(
    "--data-file", default=None, type=click.Path(), help="Use local file (skip download)."
)
@click.option(
    "--output-plot", default="forecast_plot.png", help="Plot output path.", show_default=True
)
@click.option("--output-csv", default=None, type=click.Path(), help="Save validation table as CSV.")
@click.option("--no-plot", is_flag=True, help="Skip plot generation.")
@click.option("--verbose", is_flag=True, help="Enable verbose output.")
@click.version_option(version=__version__)
def main(
    year,
    start_date,
    dim_x,
    num_samples,
    data_url,
    data_file,
    output_plot,
    output_csv,
    no_plot,
    verbose,
):
    """Forecast CVE counts using Kalman Filter on NVD data."""
    np.seterr(all="ignore")
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(message)s",
    )
    log = logging.getLogger(__name__)

    config = ForecastConfig(
        data_url=data_url,
        data_file=data_file or "nvd.jsonl",
        start_date=start_date,
        forecast_year=year,
        dim_x=dim_x,
        num_samples=num_samples,
        output_plot=output_plot,
        output_csv=output_csv,
        no_plot=no_plot,
        verbose=verbose,
    )

    if data_file is None:
        download_nvd_data(config.data_url, config.data_file)

    log.info("Loading NVD data...")
    df = load_nvd_jsonl(config.data_file)
    total_count = len(df)

    log.info("Cleaning and splitting data...")
    training_df, actuals_df = clean_nvd_data(df, config.start_date, config.forecast_year)
    del df

    summary = compute_summary_stats(training_df, total_count, config.start_date)

    log.info("Aggregating monthly counts...")
    monthly_cves = aggregate_monthly(training_df)

    if len(monthly_cves) < 24:
        log.warning(
            "Time series is very short (%d months). Results may be unreliable.", len(monthly_cves)
        )

    log.info("Fitting Kalman filter and generating forecast...")
    train_series, pred_series = fit_and_predict(monthly_cves, config)

    predicted_df = prediction_to_dataframe(pred_series)

    validation_df = build_validation_table(predicted_df, actuals_df)
    print_report(validation_df, summary)

    if not config.no_plot:
        log.info("Saving forecast plot to %s", config.output_plot)
        plot_forecast(train_series, pred_series, config.output_plot)

    if config.output_csv:
        log.info("Saving validation table to %s", config.output_csv)
        save_csv(validation_df, config.output_csv)
