import pandas as pd
import pytest

from emrpy.data import load_csv, load_parquet


@pytest.fixture
def tmp_csv(tmp_path):
    df = pd.DataFrame({"a": range(10), "b": list("abcdefghij")})
    path = tmp_path / "test.csv"
    df.to_csv(path, index=False)
    return path, df


@pytest.fixture
def tmp_parquet(tmp_path):
    df = pd.DataFrame({"x": range(20), "y": list(range(20, 40))})
    path = tmp_path / "test.parquet"
    df.to_parquet(path, index=False)
    return path, df


@pytest.mark.parametrize(
    "engine,lazy",
    [
        ("pandas", False),
        ("polars", False),
        ("polars", True),
    ],
)
def test_load_csv_full(tmp_csv, engine, lazy):
    path, orig = tmp_csv
    df = load_csv(path, engine=engine, lazy=lazy)
    # Polars lazy yields LazyFrame, so collect
    if engine == "polars" and lazy:
        df = df.collect()
    # Convert to pandas for easy compare
    pdf = df.to_pandas() if hasattr(df, "to_pandas") else df
    pd.testing.assert_frame_equal(pdf, orig)


@pytest.mark.parametrize(
    "engine,lazy",
    [
        ("pandas", False),
        ("polars", False),
        ("polars", True),
    ],
)
def test_load_csv_sample_n(tmp_csv, engine, lazy):
    path, _ = tmp_csv
    df = load_csv(path, engine=engine, lazy=lazy, sample_n=3)
    if engine == "polars" and lazy:
        df = df.collect()
    # Should have exactly 3 rows
    output = df.to_pandas() if hasattr(df, "to_pandas") else df
    assert len(output) == 3


@pytest.mark.parametrize(
    "engine,lazy",
    [
        ("pandas", False),
        ("polars", False),
        ("polars", True),
    ],
)
def test_load_parquet_full(tmp_parquet, engine, lazy):
    path, orig = tmp_parquet
    df = load_parquet(path, engine=engine, lazy=lazy)
    if engine == "polars" and lazy:
        df = df.collect()
    pdf = df.to_pandas() if hasattr(df, "to_pandas") else df
    pd.testing.assert_frame_equal(pdf, orig)


@pytest.mark.parametrize(
    "engine,lazy",
    [
        ("pandas", False),
        ("polars", False),
        ("polars", True),
    ],
)
def test_load_parquet_sample_n(tmp_parquet, engine, lazy):
    path, _ = tmp_parquet
    df = load_parquet(path, engine=engine, lazy=lazy, sample_n=5)
    if engine == "polars" and lazy:
        df = df.collect()
    output = df.to_pandas() if hasattr(df, "to_pandas") else df
    assert len(output) == 5


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        load_parquet(tmp_path / "does_not_exist.parquet")


def test_invalid_engine(tmp_csv):
    path, _ = tmp_csv
    with pytest.raises(ValueError):
        load_csv(path, engine="csvinator")
    with pytest.raises(ValueError):
        load_parquet(path, engine="fastparquet")
