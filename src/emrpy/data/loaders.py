# src/emrpy/data/loaders.py
"""
Data Loading Utilities

Functions for loading CSV and Parquet files with support for pandas or Polars backends,
eager or lazy loading, and optional sampling by fraction or row-count.
"""

from pathlib import Path
from typing import Optional, Union

import pandas as pd
import polars as pl


def load_csv(
    file_path: Union[str, Path],
    engine: str = "polars",
    lazy: bool = False,
    sample_n: Optional[int] = None,
    **kwargs,
) -> Union[pd.DataFrame, pl.DataFrame, pl.LazyFrame]:
    """
    Load a CSV file using pandas or Polars, with optional row-count sampling.

    Parameters:
    -----------
    file_path : str or Path
        Path to the CSV file.
    engine : {'pandas', 'polars'}, default 'polars'
        Which backend to use:
        - 'pandas': calls `pd.read_csv`
        - 'polars': calls `pl.read_csv` (eager) or `pl.scan_csv` (lazy)
    lazy : bool, default False
        If True and engine='polars', returns a `pl.LazyFrame` via `pl.scan_csv`.
        Ignored when engine='pandas'.
    sample_n : int, optional
        Number of rows to load. For pandas, passed as `nrows`; for Polars, as `n_rows`.
        If None, loads the entire file.
    **kwargs
        Passed to the underlying reader.

    Returns:
    --------
    pandas.DataFrame or polars.DataFrame or polars.LazyFrame
        Loaded (and optionally sampled) table.

    Examples:
    ---------
    >>> # Eager pandas
    >>> df = load_csv("data.csv", engine="pandas")
    >>> type(df)
    <class 'pandas.core.frame.DataFrame'>

    >>> # Eager Polars
    >>> df = load_csv("data.csv", engine="polars")
    >>> type(df)
    <class 'polars.internals.frame.DataFrame'>

    >>> # Lazy Polars
    >>> lf = load_csv("data.csv", engine="polars", lazy=True)
    >>> type(lf)
    <class 'polars.lazyframe.LazyFrame'>

    >>> # Sample first 100 rows with Polars
    >>> df = load_csv("data.csv", sample_n=100)
    >>> len(df)
    100
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if engine == "pandas":
        return _load_csv_pandas(file_path, sample_n, **kwargs)
    elif engine == "polars":
        return _load_csv_polars(file_path, lazy, sample_n, **kwargs)
    else:
        raise ValueError(f"Unsupported engine: {engine}. Use 'pandas' or 'polars'")


def load_parquet(
    file_path: Union[str, Path],
    engine: str = "polars",
    lazy: bool = False,
    sample_frac: Optional[float] = None,
    sample_n: Optional[int] = None,
    **kwargs,
) -> Union[pd.DataFrame, "pl.DataFrame", "pl.LazyFrame"]:
    """
    Load a Parquet file using pandas or Polars, with optional row-count sampling.

    Parameters:
    -----------
    file_path : str or Path
        Path to the Parquet file.
    engine : {'pandas', 'polars'}, default 'polars'
        Which backend to use:
        - 'pandas': calls `pd.read_parquet`
        - 'polars': calls `pl.read_parquet` (eager) or `pl.scan_parquet` (lazy)
    lazy : bool, default False
        If True and engine='polars', returns a `pl.LazyFrame` via `pl.scan_parquet`.
        Ignored when engine='pandas'.
    sample_n : int, optional
        Number of rows to load. For pandas, samples after full load; for Polars, as `n_rows`.
        If None, loads the entire file.
    **kwargs
        Passed to the underlying reader.

    Returns:
    --------
    pandas.DataFrame or polars.DataFrame or polars.LazyFrame
        Loaded (and optionally sampled) table.

    Examples:
    ---------
    >>> # Eager pandas
    >>> df = load_parquet("data.parquet", engine="pandas")
    >>> type(df)
    <class 'pandas.core.frame.DataFrame'>

    >>> # Eager Polars
    >>> df = load_parquet("data.parquet", engine="polars")
    >>> type(df)
    <class 'polars.internals.frame.DataFrame'>

    >>> # Lazy Polars
    >>> lf = load_parquet("data.parquet", engine="polars", lazy=True)
    >>> type(lf)
    <class 'polars.lazyframe.LazyFrame'>

    >>> # Sample first 50 rows with Polars
    >>> df = load_parquet("data.parquet", sample_n=50)
    >>> len(df)
    50
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if engine == "pandas":
        return _load_parquet_pandas(file_path, sample_n, **kwargs)
    elif engine == "polars":
        return _load_parquet_polars(file_path, lazy, sample_n, **kwargs)
    else:
        raise ValueError(f"Unsupported engine: {engine}. Use 'pandas' or 'polars'")


def _load_csv_pandas(file_path: Path, sample_n: Optional[int], **kwargs) -> pd.DataFrame:
    """
    pandas-based CSV loader with optional nrows sampling.

    Parameters
    ----------
    file_path : Path
        Path to the CSV file.
    sample_n : int or None
        Number of rows to load via `pd.read_csv(nrows=sample_n)`.
    **kwargs
        Passed to `pd.read_csv`.

    Returns
    -------
    pandas.DataFrame
    """

    if sample_n is not None:
        df = pd.read_csv(file_path, nrows=sample_n, **kwargs)
    else:
        df = pd.read_csv(file_path, **kwargs)

    return df


def _load_parquet_pandas(file_path: Path, sample_n: Optional[int], **kwargs) -> pd.DataFrame:
    """
    pandas-based Parquet loader with optional post-load sampling.

    Parameters
    ----------
    file_path : Path
        Path to the Parquet file.
    sample_n : int or None
        If provided, sample up to `sample_n` rows after full load.
    **kwargs
        Passed to `pd.read_parquet`.

    Returns
    -------
    pandas.DataFrame
    """
    # Load the data
    df = pd.read_parquet(file_path, **kwargs)

    # Apply sampling if requested
    if sample_n is not None:
        df = df.sample(n=min(sample_n, len(df)), random_state=42)

    return df


def _load_csv_polars(
    file_path: Path, lazy: bool, sample_n: Optional[int], **kwargs
) -> Union["pl.DataFrame", "pl.LazyFrame"]:
    """
    Polars-based CSV loader with eager or lazy mode and optional n_rows sampling.

    Parameters
    ----------
    file_path : Path
        Path to the CSV file.
    lazy : bool
        If True, uses `pl.scan_csv(n_rows=sample_n)` to produce a LazyFrame.
        Otherwise uses `pl.read_csv(n_rows=sample_n)` for an eager DataFrame.
    sample_n : int or None
        Number of rows to read (`n_rows` parameter).
    **kwargs
        Passed to either `pl.scan_csv` or `pl.read_csv`.

    Returns
    -------
    polars.DataFrame or polars.LazyFrame
    """

    if lazy:
        # Use lazy loading
        # Apply sampling if requested
        if sample_n is not None:
            print(f"Loading first {sample_n} rows lazily from {file_path}")
            df = pl.scan_csv(file_path, n_rows=sample_n, **kwargs)
        else:
            df = pl.scan_csv(file_path, **kwargs)

        return df
    else:
        # Eager loading
        if sample_n is not None:
            df = pl.read_csv(file_path, n_rows=sample_n, **kwargs)
        else:
            df = pl.read_csv(file_path, **kwargs)

        return df


def _load_parquet_polars(
    file_path: Path, lazy: bool, sample_n: Optional[int], **kwargs
) -> Union[pl.DataFrame, pl.LazyFrame]:
    """
    Polars-based Parquet loader with eager or lazy mode and optional n_rows sampling.

    Parameters
    ----------
    file_path : Path
        Path to the Parquet file.
    lazy : bool
        If True, uses `pl.scan_parquet(n_rows=sample_n)` to produce a LazyFrame.
        Otherwise uses `pl.read_parquet(n_rows=sample_n)` for an eager DataFrame.
    sample_n : int or None
        Number of rows to read (`n_rows` parameter).
    **kwargs
        Passed to either `pl.scan_parquet` or `pl.read_parquet`.

    Returns
    -------
    polars.DataFrame or polars.LazyFrame
    """

    if lazy:
        # Use lazy loading
        # Apply sampling if requested
        if sample_n is not None:
            print(f"Loading first {sample_n} rows lazily from {file_path}")
            df = pl.scan_parquet(file_path, n_rows=sample_n, **kwargs)
        else:
            df = pl.scan_parquet(file_path, **kwargs)

        return df
    else:
        # eager loading
        if sample_n is not None:
            df = pl.read_parquet(file_path, n_rows=sample_n, **kwargs)
        else:
            df = pl.read_parquet(file_path, **kwargs)

        return df
