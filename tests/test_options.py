"""Offline tests for the options module: Black-Scholes, implied-vol inversion,
HV-rank, ATM chain metrics, and the structure suggestion."""

import math

import numpy as np
import pandas as pd

from vcp_screener.options import (
    OptionsConfig,
    bs_delta,
    bs_price,
    hv_rank,
    implied_vol,
    option_metrics,
    suggest_structure,
)


def test_bs_put_call_parity():
    S, K, T, r, sig = 1000.0, 1000.0, 0.25, 0.065, 0.30
    c = bs_price(S, K, T, r, sig, call=True)
    p = bs_price(S, K, T, r, sig, call=False)
    # c - p == S - K*exp(-rT)
    assert abs((c - p) - (S - K * math.exp(-r * T))) < 1e-6


def test_implied_vol_roundtrip():
    S, K, T, r, sig = 1000.0, 1050.0, 0.20, 0.065, 0.42
    price = bs_price(S, K, T, r, sig, call=True)
    iv = implied_vol(price, S, K, T, r, call=True)
    assert abs(iv - sig) < 1e-3


def test_implied_vol_below_intrinsic_is_nan():
    # A price below intrinsic value can't be inverted.
    S, K, T, r = 1000.0, 800.0, 0.10, 0.065
    assert math.isnan(implied_vol(150.0, S, K, T, r, call=True))  # intrinsic ~200


def test_bs_delta_ranges():
    assert 0.45 < bs_delta(100, 100, 0.25, 0.065, 0.3, call=True) < 0.65
    assert bs_delta(200, 100, 0.25, 0.065, 0.3, call=True) > 0.95    # deep ITM
    assert bs_delta(50, 100, 0.25, 0.065, 0.3, call=True) < 0.10     # deep OTM


def test_hv_rank():
    rng = np.random.default_rng(0)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 400)))
    df = pd.DataFrame({"Close": close}, index=pd.bdate_range("2023-01-02", periods=400))
    hv, rank = hv_rank(df, OptionsConfig())
    assert hv > 0
    assert 0 <= rank <= 100


def _synthetic_chain(spot=1000.0, iv=0.30, r=0.065):
    today = pd.Timestamp("2026-01-01")
    near = today + pd.Timedelta(days=10)   # dte 10 -> below min_dte, skipped
    far = today + pd.Timedelta(days=35)    # dte 35 -> chosen
    rows = []
    for expiry in (near, far):
        T = (expiry - today).days / 365.0
        for K in [960, 980, 1000, 1020, 1040]:
            for typ, call in (("CE", True), ("PE", False)):
                px = bs_price(spot, K, T, r, iv, call)
                oi = 1000 if K == 1000 else 300
                vol = 200 if K == 1000 else 40
                rows.append({"Symbol": "TEST", "Expiry": expiry, "Strike": float(K),
                             "OptType": typ, "Settle": px, "OI": oi, "Volume": vol})
    return today, pd.DataFrame(rows)


def test_option_metrics_recovers_iv_and_expiry():
    today, chain = _synthetic_chain(spot=1000.0, iv=0.30)
    m = option_metrics(chain, 1000.0, today, OptionsConfig(min_dte=25))
    assert m["dte"] == 35                       # skipped the 10-day expiry
    assert m["atm_strike"] == 1000.0
    assert abs(m["atm_iv"] - 0.30) < 0.01       # IV recovered from settle prices
    assert m["liquid"] is True
    expected = 0.30 * math.sqrt(35 / 365.0)
    assert abs(m["exp_move_pct"] - expected) < 0.005


def test_suggest_structure():
    cfg = OptionsConfig()
    liquid = {"liquid": True, "expiry": pd.Timestamp("2026-02-05"), "dte": 35, "sug_strike": 980.0}
    assert "debit spread" in suggest_structure(liquid, rank=85, cfg=cfg).lower()
    assert "ce" in suggest_structure(liquid, rank=30, cfg=cfg).lower()
    thin = {"liquid": False, "expiry": None, "dte": None, "sug_strike": None}
    assert "thin" in suggest_structure(thin, rank=30, cfg=cfg).lower()
