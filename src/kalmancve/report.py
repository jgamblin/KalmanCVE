import numpy as np
import pandas as pd


MONTH_ORDER = [
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
    "Total",
]


def build_validation_table(predicted_df: pd.DataFrame, actuals_df: pd.DataFrame) -> pd.DataFrame:
    actuals_monthly = actuals_df.copy()
    actuals_monthly["Published"] = pd.to_datetime(actuals_monthly["Published"])
    actuals_monthly = (
        actuals_monthly["Published"]
        .groupby(actuals_monthly["Published"].dt.to_period("M"))
        .agg("count")
    )
    actuals_monthly = actuals_monthly.reset_index(name="CVEs Actual")
    actuals_monthly = actuals_monthly.rename(columns={"Published": "Month"})
    actuals_monthly["Month"] = actuals_monthly["Month"].astype(str)
    actuals_monthly["Month"] = pd.to_datetime(actuals_monthly["Month"])
    actuals_monthly["Month"] = actuals_monthly["Month"].dt.month_name()

    validation_df = pd.merge(actuals_monthly, predicted_df, how="outer", on="Month")

    validation_df["Month"] = pd.Categorical(
        validation_df["Month"], categories=MONTH_ORDER, ordered=True
    )
    validation_df = validation_df.sort_values(by="Month")

    validation_df["Difference"] = validation_df["CVEs Actual"] - validation_df["CVEs Predicted"]
    validation_df["CVEs Actual"] = validation_df["CVEs Actual"].fillna(0)
    validation_df["Difference"] = validation_df["Difference"].fillna(0)

    numeric_df = validation_df.select_dtypes(include=np.number)
    total_row = numeric_df.sum()
    validation_df = pd.concat(
        [validation_df, pd.DataFrame(total_row.rename("Total")).T], ignore_index=True
    )
    validation_df["CVEs Actual"] = validation_df["CVEs Actual"].fillna(0)
    validation_df["Difference"] = validation_df["Difference"].fillna(0)

    validation_df["Percentage"] = (
        (validation_df["CVEs Actual"] / validation_df["CVEs Predicted"]) * 100
    ).round(0)
    validation_df["Percentage"] = validation_df["Percentage"].fillna(0)
    validation_df.at[len(validation_df) - 1, "Month"] = "Total"

    return validation_df


def print_report(validation_df: pd.DataFrame, summary: dict) -> None:
    print("\n=== CVE Forecast Summary ===\n")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n=== Forecast vs Actuals ===\n")
    print(validation_df.to_string(index=False))
    print()


def save_csv(validation_df: pd.DataFrame, path: str) -> None:
    validation_df.to_csv(path, index=False)
