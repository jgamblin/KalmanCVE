import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _make_cve_entry(cve_id, published, base_score=7.5, severity="HIGH", status="Analyzed"):
    return {
        "cve": {
            "id": cve_id,
            "published": published,
            "metrics": {
                "cvssMetricV31": [
                    {
                        "cvssData": {
                            "attackVector": "NETWORK",
                            "attackComplexity": "LOW",
                            "privilegesRequired": "NONE",
                            "userInteraction": "NONE",
                            "scope": "UNCHANGED",
                            "confidentialityImpact": "HIGH",
                            "integrityImpact": "HIGH",
                            "availabilityImpact": "HIGH",
                            "baseScore": base_score,
                            "baseSeverity": severity,
                        },
                        "exploitabilityScore": 3.9,
                        "impactScore": 5.9,
                    }
                ]
            },
            "weaknesses": [{"description": [{"value": "CWE-79"}]}],
            "descriptions": [{"value": "Test vulnerability"}],
            "sourceIdentifier": "test@test.com",
            "cveTags": [],
            "vulnStatus": status,
        }
    }


@pytest.fixture
def sample_nvd_entries():
    entries = []
    idx = 0
    for year in range(2017, 2026):
        for month in range(1, 13):
            for day in [5, 15, 25]:
                idx += 1
                entries.append(
                    _make_cve_entry(
                        f"CVE-{year}-{idx:05d}",
                        f"{year}-{month:02d}-{day:02d}T12:00:00.000",
                        base_score=round(np.random.uniform(3.0, 10.0), 1),
                    )
                )
    # Add one rejected entry to test filtering
    entries.append(_make_cve_entry("CVE-2020-99999", "2020-06-15T12:00:00.000", status="Rejected"))
    return entries


@pytest.fixture
def sample_nvd_file(sample_nvd_entries, tmp_path):
    path = tmp_path / "nvd.jsonl"
    with open(path, "w") as f:
        json.dump(sample_nvd_entries, f)
    return str(path)


@pytest.fixture
def sample_monthly_df():
    dates = pd.date_range("2017-01-01", periods=84, freq="MS")
    counts = np.random.randint(1000, 4000, size=len(dates))
    return pd.DataFrame({"Month": dates, "CVEs": counts})
