import pandas as pd

from kalmancve.report import build_validation_table


def _make_predicted_df():
    months = [
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
    ]
    return pd.DataFrame(
        {
            "Month": months,
            "CVEs Predicted": [3000 + i * 50 for i in range(12)],
        }
    )


def _make_actuals_df(months=6):
    dates = pd.date_range("2024-01-10", periods=months * 30, freq="D")
    return pd.DataFrame(
        {
            "Published": dates,
            "CVE": [f"CVE-2024-{i:05d}" for i in range(len(dates))],
            "BaseScore": [7.0] * len(dates),
            "BaseSeverity": ["HIGH"] * len(dates),
        }
    )


class TestBuildValidationTable:
    def test_has_percentage_column(self):
        predicted = _make_predicted_df()
        actuals = _make_actuals_df()
        result = build_validation_table(predicted, actuals)
        assert "Percentage" in result.columns
        assert "Precentage" not in result.columns

    def test_has_total_row(self):
        predicted = _make_predicted_df()
        actuals = _make_actuals_df()
        result = build_validation_table(predicted, actuals)
        assert "Total" in result["Month"].values

    def test_row_count(self):
        predicted = _make_predicted_df()
        actuals = _make_actuals_df()
        result = build_validation_table(predicted, actuals)
        assert len(result) == 13  # 12 months + total

    def test_no_nan_in_actuals(self):
        predicted = _make_predicted_df()
        actuals = _make_actuals_df(months=3)
        result = build_validation_table(predicted, actuals)
        assert not result["CVEs Actual"].isnull().any()

    def test_difference_calculation(self):
        predicted = _make_predicted_df()
        actuals = _make_actuals_df()
        result = build_validation_table(predicted, actuals)
        data_rows = result[result["Month"] != "Total"]
        for _, row in data_rows.iterrows():
            if row["CVEs Actual"] > 0 and row["CVEs Predicted"] > 0:
                expected_diff = row["CVEs Actual"] - row["CVEs Predicted"]
                assert row["Difference"] == expected_diff
