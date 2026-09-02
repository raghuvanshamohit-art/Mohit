import numpy as np
import pandas as pd
import pytest

from dyncorr.correlation import (
    correlation_summary,
    dynamic_correlation,
    ewma_correlation,
    matrix_as_of,
    rolling_correlation,
    static_correlation,
)


@pytest.fixture
def sample():
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2020-01-01", periods=300)
    a = rng.standard_normal(300)
    # b starts perfectly anti-correlated with a, then flips to correlated.
    b = np.concatenate([-a[:150], a[150:]]) + 0.01 * rng.standard_normal(300)
    c = rng.standard_normal(300)
    return pd.DataFrame({"a": a, "b": b, "c": c}, index=idx)


def test_static_correlation_shape_and_diagonal(sample):
    corr = static_correlation(sample)
    assert corr.shape == (3, 3)
    assert np.allclose(np.diag(corr.values), 1.0)
    assert corr.loc["a", "b"] == pytest.approx(corr.loc["b", "a"])


def test_rolling_correlation_columns_and_bounds(sample):
    roll = rolling_correlation(sample, window=40)
    assert set(roll.columns) == {"a~b", "a~c", "b~c"}
    vals = roll["a~b"].dropna()
    assert (vals.abs() <= 1.0 + 1e-9).all()
    # First window-1 rows are NaN.
    assert roll["a~b"].iloc[:39].isna().all()
    assert not np.isnan(roll["a~b"].iloc[40])


def test_rolling_detects_regime_flip(sample):
    roll = rolling_correlation(sample, window=40)
    early = roll["a~b"].iloc[40:120].mean()
    late = roll["a~b"].iloc[220:].mean()
    assert early < -0.5  # anti-correlated regime
    assert late > 0.5    # correlated regime


def test_rolling_window_validation(sample):
    with pytest.raises(ValueError):
        rolling_correlation(sample, window=1)


def test_ewma_correlation_bounds(sample):
    ewma = ewma_correlation(sample, halflife=20)
    vals = ewma["a~b"].dropna()
    assert (vals.abs() <= 1.0 + 1e-9).all()
    with pytest.raises(ValueError):
        ewma_correlation(sample, halflife=0)


def test_dynamic_dispatch(sample):
    assert dynamic_correlation(sample, method="rolling", window=30).shape[1] == 3
    assert dynamic_correlation(sample, method="ewma", halflife=15).shape[1] == 3
    with pytest.raises(ValueError):
        dynamic_correlation(sample, method="nope")


def test_pairs_filter(sample):
    roll = rolling_correlation(sample, window=30, pairs=[("a", "c")])
    assert list(roll.columns) == ["a~c"]
    with pytest.raises(KeyError):
        rolling_correlation(sample, window=30, pairs=[("a", "z")])


def test_matrix_as_of(sample):
    m_roll = matrix_as_of(sample, method="rolling", window=50)
    assert m_roll.shape == (3, 3)
    assert np.allclose(np.diag(m_roll.values), 1.0)
    m_ewma = matrix_as_of(sample, method="ewma", halflife=20)
    assert m_ewma.shape == (3, 3)
    assert np.allclose(np.diag(m_ewma.values), 1.0)
    # As-of the last date, rolling matrix ~ correlation of the last window.
    manual = sample.tail(50).corr()
    assert m_roll.loc["a", "b"] == pytest.approx(manual.loc["a", "b"])


def test_correlation_summary(sample):
    roll = rolling_correlation(sample, window=40)
    summary = correlation_summary(roll)
    assert set(summary["pair"]) == {"a~b", "a~c", "b~c"}
    # a~b swings the most (it flips sign); it should rank first.
    assert summary.iloc[0]["pair"] == "a~b"
    assert (summary["swing"] >= 0).all()
