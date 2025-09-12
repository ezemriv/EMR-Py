# src/emrpy/visualization/timeseries.py

"""
Time Series Visualization Utilities

Functions for plotting financial and time series data with proper handling
of gaps (as in trading weekends) and discontinuous timestamps.
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd


def plot_timeseries(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    value_col: str = "close",
    segment_col: Optional[str] = None,
    segment_value: Optional[str] = None,
    tick_every: int = 100,
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[Union[str, Path]] = None,
) -> None:
    """
    Plot time series data with continuous bar numbering to avoid trading gaps.

    This function creates a continuous plot by using bar numbers instead of timestamps,
    which eliminates gaps from weekends and holidays in financial data.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the time series data
    timestamp_col : str, default 'timestamp'
        Name of the timestamp column
    value_col : str, default 'close'
        Name of the column containing values to plot
    segment_col : str, optional
        Column name to filter by (e.g., 'Symbol' for stock tickers)
    segment_value : str, optional
        Value to filter on in segment_col (e.g., 'AAPL')
    tick_every : int, default 100
        Show timestamp labels every N bars
    figsize : tuple, default (12, 6)
        Figure size as (width, height)

    Examples:
    ---------
    >>> # Plot AAPL data
    >>> plot_timeseries(
    ...     df=stock_data,
    ...     segment_col='Symbol',
    ...     segment_value='AAPL'
    ... )

    >>> # Plot all data without filtering
    >>> plot_timeseries(df=price_data)
    """
    # # Filter and sort
    # data = df.copy()
    # if segment_col and segment_value:
    #     data = data[data[segment_col] == segment_value].copy()

    # data[timestamp_col] = pd.to_datetime(data[timestamp_col])
    # data = data.sort_values(timestamp_col).reset_index(drop=True)

    # # Create continuous bar numbering
    # data["bar_number"] = range(len(data))

    # # Create plot
    # plt.figure(figsize=figsize)
    # plt.plot(data["bar_number"], data[value_col], lw=1)

    # # Set title and labels
    # title = f"{segment_value} {value_col.title()}" if segment_value else f"{value_col.title()}"
    # plt.title(f"{title} (Trading Bars Only)")
    # plt.xlabel("Bar Number (continuous through trading sessions)")
    # plt.ylabel(f"{value_col.title()}")

    # # Add timestamp ticks
    # if len(data) > tick_every:
    #     tick_positions = data["bar_number"][::tick_every]
    #     tick_labels = data[timestamp_col].dt.strftime("%Y-%m-%d %H:%M")[::tick_every]
    #     plt.xticks(tick_positions, tick_labels, rotation=45)

    # plt.tight_layout()
    # if save_path:
    #     plt.savefig(save_path)
    # plt.show()

    data = df.copy()
    if segment_col and segment_value:
        data = data[data[segment_col] == segment_value].copy()

    data[timestamp_col] = pd.to_datetime(data[timestamp_col])
    data = data.sort_values(timestamp_col).reset_index(drop=True)
    data["bar_number"] = range(len(data))

    plt.figure(figsize=figsize)
    plt.plot(data["bar_number"], data[value_col], lw=1)
    title = f"{segment_value} {value_col.title()}" if segment_value else value_col.title()
    plt.title(f"{title} (Continuous)")
    plt.xlabel("Bar Number (continuous)")
    plt.ylabel(value_col.title())

    if len(data) > tick_every:
        ticks = data["bar_number"][::tick_every]
        labels = data[timestamp_col].dt.strftime("%Y-%m-%d %H:%M")[::tick_every]
        plt.xticks(ticks, labels, rotation=45)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()
