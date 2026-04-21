import dataclasses
from datetime import date


@dataclasses.dataclass
class ForecastConfig:
    data_url: str = "https://nvd.handsonhacking.org/nvd.jsonl"
    data_file: str = "nvd.jsonl"
    start_date: str = "2017-01-01"
    forecast_year: int = dataclasses.field(default_factory=lambda: date.today().year)
    dim_x: int = 2
    num_samples: int = 1000
    forecast_months: int = 12
    output_plot: str = "forecast_plot.png"
    output_csv: str | None = None
    no_plot: bool = False
    verbose: bool = False
