import json
import logging
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _get_nested_value(entry, keys, default="Missing_Data"):
    try:
        for key in keys:
            entry = entry[key]
        return entry
    except (KeyError, IndexError, TypeError):
        return default


def download_nvd_data(url: str, dest: str, max_retries: int = 3) -> Path:
    dest_path = Path(dest)
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Downloading NVD data (attempt %d/%d)...", attempt, max_retries)
            urllib.request.urlretrieve(url, dest_path)
            logger.info("Download complete: %s", dest_path)
            return dest_path
        except Exception as e:
            if attempt == max_retries:
                raise RuntimeError(f"Failed to download {url} after {max_retries} attempts: {e}")
            logger.warning("Download attempt %d failed: %s. Retrying...", attempt, e)
            time.sleep(2)
    return dest_path  # unreachable, but satisfies type checker


def load_nvd_jsonl(path: str) -> pd.DataFrame:
    # Despite the .jsonl extension, this file is a JSON array
    with open(path, "r", encoding="utf-8") as f:
        nvd_data = json.load(f)

    if not isinstance(nvd_data, list):
        raise ValueError(f"Expected data to be a list, got {type(nvd_data)}")
    if len(nvd_data) == 0:
        raise ValueError("Loaded data is empty")

    logger.info("Loaded %d CVE records", len(nvd_data))

    rows = []
    for entry in nvd_data:
        rows.append(
            {
                "CVE": _get_nested_value(entry, ["cve", "id"]),
                "Published": _get_nested_value(entry, ["cve", "published"]),
                "AttackVector": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "attackVector"],
                ),
                "AttackComplexity": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "attackComplexity"],
                ),
                "PrivilegesRequired": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "privilegesRequired"],
                ),
                "UserInteraction": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "userInteraction"],
                ),
                "Scope": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "scope"],
                ),
                "ConfidentialityImpact": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "confidentialityImpact"],
                ),
                "IntegrityImpact": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "integrityImpact"],
                ),
                "AvailabilityImpact": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "availabilityImpact"],
                ),
                "BaseScore": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "baseScore"],
                    "0.0",
                ),
                "BaseSeverity": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "cvssData", "baseSeverity"],
                ),
                "ExploitabilityScore": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "exploitabilityScore"],
                ),
                "ImpactScore": _get_nested_value(
                    entry,
                    ["cve", "metrics", "cvssMetricV31", 0, "impactScore"],
                ),
                "CWE": _get_nested_value(
                    entry, ["cve", "weaknesses", 0, "description", 0, "value"]
                ),
                "Description": _get_nested_value(entry, ["cve", "descriptions", 0, "value"], ""),
                "Assigner": _get_nested_value(entry, ["cve", "sourceIdentifier"]),
                "Tag": _get_nested_value(entry, ["cve", "cveTags", 0, "tags"], np.nan),
                "Status": _get_nested_value(entry, ["cve", "vulnStatus"], ""),
            }
        )

    df = pd.DataFrame(rows)
    del rows

    df = df[~df.Status.str.contains("Rejected", na=False)]
    df["Published"] = pd.to_datetime(df["Published"])
    df = df.sort_values(by=["Published"]).reset_index(drop=True)
    df["BaseScore"] = pd.to_numeric(df["BaseScore"], errors="coerce")
    df["BaseScore"] = df["BaseScore"].replace(0, np.nan)

    return df


def clean_nvd_data(
    df: pd.DataFrame, start_date: str, forecast_year: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    year_start = f"{forecast_year}-01-01"
    next_year_start = f"{forecast_year + 1}-01-01"

    training_mask = (df["Published"] > start_date) & (df["Published"] < year_start)
    actuals_mask = (df["Published"] >= year_start) & (df["Published"] < next_year_start)

    training_df = df.loc[training_mask].copy()
    actuals_df = df.loc[actuals_mask].copy()

    return training_df, actuals_df


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Published"] = pd.to_datetime(df["Published"])
    df["Published"] = df["Published"].dt.to_period("M").dt.to_timestamp()

    monthly = df["Published"].groupby(df["Published"]).agg("count")
    monthly_cves = pd.DataFrame(monthly)
    monthly_cves.columns = ["Count"]
    monthly_cves = monthly_cves.reset_index()
    monthly_cves = monthly_cves.rename(columns={"Published": "Month", "Count": "CVEs"})
    monthly_cves["Month"] = pd.to_datetime(monthly_cves["Month"].astype(str))

    monthly_cves = monthly_cves.replace([np.inf, -np.inf], np.nan)
    monthly_cves = monthly_cves.dropna(subset=["CVEs"])
    monthly_cves = monthly_cves[monthly_cves["CVEs"] > 0]
    monthly_cves = monthly_cves.reset_index(drop=True)

    return monthly_cves


def compute_summary_stats(training_df: pd.DataFrame, total_count: int, start_date: str) -> dict:
    from datetime import date as date_cls

    startdate = date_cls.fromisoformat(start_date)
    enddate = date_cls.today()
    num_days = (enddate - startdate).days
    per_day = round(total_count / num_days, 2) if num_days > 0 else 0

    return {
        "Total CVEs": training_df["CVE"].count(),
        "Date Range": (
            f"{training_df['Published'].min().date()} to {training_df['Published'].max().date()}"
        ),
        "Unique Days": training_df["Published"].nunique(),
        "Missing BaseScore": int(training_df["BaseScore"].isnull().sum()),
        "Missing Severity": int(training_df["BaseSeverity"].isnull().sum()),
        "Average CVEs Per Day": per_day,
        "Average CVSS Score": round(float(training_df["BaseScore"].mean()), 2),
    }
