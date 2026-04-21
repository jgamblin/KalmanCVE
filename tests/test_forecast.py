import pandas as pd
from darts import TimeSeries

from kalmancve.config import ForecastConfig
from kalmancve.forecast import fit_and_predict, prediction_to_dataframe


class TestFitAndPredict:
    def test_returns_timeseries(self, sample_monthly_df):
        config = ForecastConfig(num_samples=10, forecast_months=12)
        train, pred = fit_and_predict(sample_monthly_df, config)
        assert isinstance(train, TimeSeries)
        assert isinstance(pred, TimeSeries)

    def test_prediction_length(self, sample_monthly_df):
        config = ForecastConfig(num_samples=10, forecast_months=6)
        _, pred = fit_and_predict(sample_monthly_df, config)
        assert len(pred) == 6


class TestPredictionToDataframe:
    def test_output_columns(self, sample_monthly_df):
        config = ForecastConfig(num_samples=10, forecast_months=12)
        _, pred = fit_and_predict(sample_monthly_df, config)
        df = prediction_to_dataframe(pred)
        assert "Month" in df.columns
        assert "CVEs Predicted" in df.columns

    def test_twelve_months(self, sample_monthly_df):
        config = ForecastConfig(num_samples=10, forecast_months=12)
        _, pred = fit_and_predict(sample_monthly_df, config)
        df = prediction_to_dataframe(pred)
        assert len(df) == 12

    def test_month_names(self, sample_monthly_df):
        config = ForecastConfig(num_samples=10, forecast_months=12)
        _, pred = fit_and_predict(sample_monthly_df, config)
        df = prediction_to_dataframe(pred)
        valid_months = {
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        }
        assert set(df["Month"].values).issubset(valid_months)
