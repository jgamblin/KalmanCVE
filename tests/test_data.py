import numpy as np
import pandas as pd

from kalmancve.data import _get_nested_value, aggregate_monthly, clean_nvd_data, load_nvd_jsonl


class TestGetNestedValue:
    def test_present_key(self):
        data = {"a": {"b": {"c": 42}}}
        assert _get_nested_value(data, ["a", "b", "c"]) == 42

    def test_missing_key(self):
        data = {"a": {"b": 1}}
        assert _get_nested_value(data, ["a", "x"]) == "Missing_Data"

    def test_custom_default(self):
        data = {}
        assert _get_nested_value(data, ["a"], default="N/A") == "N/A"

    def test_list_index(self):
        data = {"items": [{"name": "first"}, {"name": "second"}]}
        assert _get_nested_value(data, ["items", 1, "name"]) == "second"

    def test_index_out_of_range(self):
        data = {"items": []}
        assert _get_nested_value(data, ["items", 0, "name"]) == "Missing_Data"


class TestLoadNvdJsonl:
    def test_loads_and_filters_rejected(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        assert "Rejected" not in df["Status"].values
        assert len(df) > 0

    def test_correct_columns(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        expected = {"CVE", "Published", "BaseScore", "BaseSeverity", "Status"}
        assert expected.issubset(set(df.columns))

    def test_published_is_datetime(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        assert pd.api.types.is_datetime64_any_dtype(df["Published"])

    def test_sorted_by_published(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        assert df["Published"].is_monotonic_increasing


class TestCleanNvdData:
    def test_splits_training_and_actuals(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        training, actuals = clean_nvd_data(df, "2017-01-01", 2024)
        assert all(training["Published"] < pd.Timestamp("2024-01-01"))
        assert all(actuals["Published"] >= pd.Timestamp("2024-01-01"))
        assert all(actuals["Published"] < pd.Timestamp("2025-01-01"))

    def test_no_overlap(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        training, actuals = clean_nvd_data(df, "2017-01-01", 2024)
        overlap = set(training.index) & set(actuals.index)
        assert len(overlap) == 0


class TestAggregateMonthly:
    def test_output_columns(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        training, _ = clean_nvd_data(df, "2017-01-01", 2024)
        monthly = aggregate_monthly(training)
        assert list(monthly.columns) == ["Month", "CVEs"]

    def test_no_zero_or_nan(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        training, _ = clean_nvd_data(df, "2017-01-01", 2024)
        monthly = aggregate_monthly(training)
        assert not monthly["CVEs"].isnull().any()
        assert (monthly["CVEs"] > 0).all()

    def test_month_is_datetime(self, sample_nvd_file):
        df = load_nvd_jsonl(sample_nvd_file)
        training, _ = clean_nvd_data(df, "2017-01-01", 2024)
        monthly = aggregate_monthly(training)
        assert pd.api.types.is_datetime64_any_dtype(monthly["Month"])
