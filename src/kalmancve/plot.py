import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from darts import TimeSeries


def plot_forecast(train: TimeSeries, pred: TimeSeries, output_path: str) -> None:
    plt.figure(figsize=(16, 12))
    train.plot(lw=3)
    pred.plot(lw=3, label="forecast")
    plt.title("CVE Forecast using Kalman Filter", fontsize=18)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("CVEs", fontsize=14)
    plt.legend(fontsize=14)
    plt.grid(True, alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_diagnostics(monthly_cves, output_path: str | None = None) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    monthly_cves["CVEs"].hist(ax=axes[0], bins=12, color="#1f77b4", edgecolor="black")
    axes[0].set_title("Histogram of Monthly CVEs", fontsize=14)
    axes[0].set_xlabel("CVEs", fontsize=12)
    axes[0].set_ylabel("Frequency", fontsize=12)

    monthly_cves["CVEs"].plot.box(
        ax=axes[1],
        color={
            "boxes": "#1f77b4",
            "whiskers": "#1f77b4",
            "medians": "#ff7f0e",
            "caps": "#1f77b4",
        },
    )
    axes[1].set_title("Boxplot of Monthly CVEs", fontsize=14)
    axes[1].set_ylabel("CVEs", fontsize=12)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150)
    plt.close()
