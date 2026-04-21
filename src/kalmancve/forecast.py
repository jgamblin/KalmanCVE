import warnings

import pandas as pd
from darts import TimeSeries
from darts.models import KalmanForecaster

from .config import ForecastConfig


def fit_and_predict(
    monthly_cves: pd.DataFrame, config: ForecastConfig
) -> tuple[TimeSeries, TimeSeries]:
    train = TimeSeries.from_dataframe(monthly_cves, "Month", "CVEs")
    model = KalmanForecaster(dim_x=config.dim_x)
    model.fit(train)
    pred = model.predict(n=config.forecast_months, num_samples=config.num_samples)
    return train, pred


def prediction_to_dataframe(pred: TimeSeries) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        darts_df = pred.to_dataframe()

    darts_monthly = darts_df.mean(axis=1).round(0)
    darts_monthly = darts_monthly.to_frame().reset_index()
    darts_monthly = darts_monthly.rename(columns={0: "CVEs Predicted"})
    darts_monthly["Month"] = darts_monthly["Month"].dt.month_name()
    return darts_monthly
