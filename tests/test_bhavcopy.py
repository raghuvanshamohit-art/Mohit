"""Offline tests for the NSE Bhavcopy provider: format parsing, per-symbol
stacking, and split/bonus back-adjustment. No network is used -- the provider's
per-day cache is pre-seeded with synthetic day-files."""

import os
import zipfile

import numpy as np
import pandas as pd
import pytest

from vcp_screener.bhavcopy import BhavcopyProvider, _back_adjust


# --------------------------------------------------------------------------- #
# Format parsing
# --------------------------------------------------------------------------- #
def test_normalize_udiff_format():
    prov = BhavcopyProvider(cache_dir="unused", series=("EQ",))
    raw = pd.DataFrame({
        "TckrSymb": ["RELIANCE", "TCS", "SOMEBOND"],
        "SctySrs": ["EQ", "EQ", "GS"],           # GS should be filtered out
        "OpnPric": [100.0, 200.0, 99.0],
        "HghPric": [105.0, 205.0, 99.0],
        "LwPric": [98.0, 198.0, 99.0],
        "ClsPric": [103.0, 202.0, 99.0],
        "PrvsClsgPric": [99.0, 199.0, 99.0],
        "TtlTradgVol": [1000, 2000, 5],
    })
    out = prov._normalize_cm(raw, pd.Timestamp("2024-08-01").date())
    assert set(out["Symbol"]) == {"RELIANCE", "TCS"}
    assert out.loc[out["Symbol"] == "RELIANCE", "Close"].iloc[0] == 103.0
    assert (out["Date"] == pd.Timestamp("2024-08-01")).all()


def test_normalize_legacy_format():
    prov = BhavcopyProvider(cache_dir="unused", series=("EQ",))
    raw = pd.DataFrame({
        "SYMBOL": ["INFY"],
        "SERIES": ["EQ"],
        "OPEN": [1500.0], "HIGH": [1520.0], "LOW": [1490.0], "CLOSE": [1510.0],
        "PREVCLOSE": [1495.0], "TOTTRDQTY": [123456],
    })
    out = prov._normalize_cm(raw, pd.Timestamp("2024-06-28").date())
    assert out["Symbol"].iloc[0] == "INFY"
    assert out["Close"].iloc[0] == 1510.0
    assert out["Volume"].iloc[0] == 123456


def test_normalize_index():
    raw = pd.DataFrame({
        "Index Name": ["Nifty 50", "Nifty Bank"],
        "Open Index Value": [22000.0, 47000.0],
        "High Index Value": [22150.0, 47200.0],
        "Low Index Value": [21950.0, 46800.0],
        "Closing Index Value": [22100.0, 47100.0],
    })
    row = BhavcopyProvider._normalize_index(raw, pd.Timestamp("2024-08-01").date())
    assert row["Close"] == 22100.0
    assert row["High"] == 22150.0


# --------------------------------------------------------------------------- #
# Split / bonus back-adjustment
# --------------------------------------------------------------------------- #
def test_back_adjust_handles_5_for_1_split():
    # 10 days at ~500, then a 5:1 split: price falls to ~100 and NSE reports an
    # adjusted prev-close (= prior close / 5).
    dates = pd.bdate_range("2024-01-01", periods=12)
    close = np.array([500, 505, 510, 508, 512, 515, 518, 520, 522, 525,  # pre-split
                      105, 106], dtype=float)                            # post-split
    prevc = np.concatenate([[500.0], close[:9], [525.0 / 5.0], [105.0]])
    vol = np.concatenate([np.full(10, 100_000.0), np.full(2, 500_000.0)])  # ~5x after
    df = pd.DataFrame(
        {"Open": close, "High": close * 1.01, "Low": close * 0.99,
         "Close": close, "PrevClose": prevc, "Volume": vol},
        index=dates,
    )
    adj = _back_adjust(df, min_gap=0.10)

    # No artificial ~80% cliff remains: adjusted day-to-day returns stay small.
    rets = adj["Close"].pct_change().dropna().abs()
    assert rets.max() < 0.05
    # Pre-split closes are scaled down onto the post-split basis (~1/5).
    assert 95 < adj["Close"].iloc[0] < 110
    # Traded value (price x volume) is preserved across the adjustment.
    pre = df["Close"] * df["Volume"]
    post = adj["Close"] * adj["Volume"]
    assert np.allclose(pre.to_numpy(), post.to_numpy(), rtol=1e-6)


def test_back_adjust_ignores_dividend_sized_gaps():
    dates = pd.bdate_range("2024-01-01", periods=6)
    close = np.array([200, 201, 202, 203, 204, 205], dtype=float)
    # A ~1.5% dividend adjustment in prev-close should NOT trigger adjustment.
    prevc = np.array([200, 200, 201, 202 * 0.985, 203, 204], dtype=float)
    df = pd.DataFrame(
        {"Open": close, "High": close, "Low": close, "Close": close,
         "PrevClose": prevc, "Volume": np.full(6, 1000.0)},
        index=dates,
    )
    adj = _back_adjust(df, min_gap=0.10)
    assert np.allclose(adj["Close"].to_numpy(), close)   # untouched


# --------------------------------------------------------------------------- #
# End-to-end stacking via the per-day cache (no network)
# --------------------------------------------------------------------------- #
def _seed_cache(cache_dir, days):
    """Write synthetic per-day cache files exactly like the provider would."""
    os.makedirs(cache_dir, exist_ok=True)
    for d, rows in days.items():
        rows.to_csv(os.path.join(cache_dir, f"cm_{d:%Y%m%d}.csv"), index=False)


def test_get_many_stacks_from_cache(tmp_path, monkeypatch):
    cache = tmp_path / "bhav"
    dates = pd.bdate_range("2024-07-01", periods=5)
    day_files = {}
    for i, dt in enumerate(dates):
        day_files[dt.date()] = pd.DataFrame({
            "Date": [dt, dt],
            "Symbol": ["AAA", "BBB"],
            "Open": [100 + i, 50 + i], "High": [101 + i, 51 + i],
            "Low": [99 + i, 49 + i], "Close": [100 + i, 50 + i],
            "PrevClose": [100 + i, 50 + i], "Volume": [1000, 2000],
        })
    _seed_cache(str(cache), day_files)

    prov = BhavcopyProvider(cache_dir=str(cache), history_days=30)
    # Neutralize the trading calendar + network so only cached days are used.
    monkeypatch.setattr(prov, "_date_range", lambda: [d.date() for d in dates])
    monkeypatch.setattr(prov, "_prefetch", lambda days: None)

    out = prov.get_many(["AAA", "BBB", "CCC"])
    assert out["CCC"] is None                    # not present -> None
    assert list(out["AAA"].columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert len(out["AAA"]) == 5
    assert out["AAA"]["Close"].iloc[-1] == 104
