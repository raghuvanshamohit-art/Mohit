import numpy as np
import pandas as pd
import pytest

from dyncorr.data import apply_transform, build_panel, generate_synthetic, load_csv
from dyncorr.presets import PRESETS, resolve


def test_apply_transform_variants():
    s = pd.Series([1.0, 2.0, 4.0], name="x")
    assert apply_transform(s, "level").tolist() == [1.0, 2.0, 4.0]
    assert apply_transform(s, "diff").dropna().tolist() == [1.0, 2.0]
    assert apply_transform(s, "returns").dropna().tolist() == [1.0, 1.0]
    lg = apply_transform(s, "log_returns").dropna()
    assert lg.iloc[0] == pytest.approx(np.log(2))
    z = apply_transform(s, "zscore")
    assert z.mean() == pytest.approx(0.0, abs=1e-9)
    with pytest.raises(ValueError):
        apply_transform(s, "bogus")


def test_generate_synthetic_deterministic():
    a = generate_synthetic(["gold", "us_treasury_10y"], seed=42)
    b = generate_synthetic(["gold", "us_treasury_10y"], seed=42)
    pd.testing.assert_frame_equal(a, b)
    assert list(a.columns) == ["gold", "us_treasury_10y"]
    # Rates stay non-negative; gold (a price) stays positive.
    assert (a["us_treasury_10y"] >= 0).all()
    assert (a["gold"] > 0).all()


def test_synthetic_gold_rates_correlation_is_time_varying():
    from dyncorr.correlation import rolling_correlation

    panel = build_panel(["gold", "us_treasury_10y"], source="synthetic")
    roll = rolling_correlation(panel.transformed, window=90)["gold~us_treasury_10y"]
    early = roll.dropna().iloc[:200].mean()
    late = roll.dropna().iloc[-200:].mean()
    # By construction gold's rate loading rises from negative to positive.
    assert late - early > 0.3


def test_build_panel_auto_transforms():
    panel = build_panel(["gold", "us_treasury_10y", "inflation"], source="synthetic")
    assert panel.transforms["gold"] == "log_returns"
    assert panel.transforms["us_treasury_10y"] == "diff"
    assert panel.transforms["inflation"] == "diff"
    # Transformed frame has no NaNs after dropna and 3 columns.
    assert panel.transformed.isna().sum().sum() == 0
    assert panel.transformed.shape[1] == 3


def test_build_panel_forced_transform():
    panel = build_panel(["gold", "sp500"], source="synthetic", transform="returns")
    assert set(panel.transforms.values()) == {"returns"}


def test_load_and_build_from_csv(tmp_path):
    idx = pd.bdate_range("2021-01-01", periods=120)
    rng = np.random.default_rng(1)
    shocks = rng.standard_normal(120) * 0.01
    # Build two price paths whose *returns* are mirror images -> corr ~ -1.
    df = pd.DataFrame(
        {
            "date": idx,
            "AAA": 10 * np.exp(np.cumsum(shocks)),
            "BBB": 20 * np.exp(np.cumsum(-shocks)),
        }
    )
    p = tmp_path / "prices.csv"
    df.to_csv(p, index=False)

    loaded = load_csv(str(p))
    assert list(loaded.columns) == ["AAA", "BBB"]

    panel = build_panel(["AAA", "BBB"], source="csv", csv_path=str(p),
                        transform="returns")
    # Mirror-image returns -> strongly negative correlation.
    from dyncorr.correlation import static_correlation

    corr = static_correlation(panel.transformed)
    assert corr.loc["AAA", "BBB"] < -0.9

    with pytest.raises(KeyError):
        build_panel(["AAA", "ZZZ"], source="csv", csv_path=str(p))


def test_presets_resolve_and_aliases():
    assert resolve("gold").key == "gold"
    assert resolve("US Treasuries").key == "us_treasury_10y"
    assert resolve("bund").key == "euro_treasury_10y"
    assert resolve("jgb").key == "yen_treasury_10y"
    assert resolve("totally-unknown") is None
    # Every preset has a valid transform and source.
    for p in PRESETS.values():
        assert p.source in {"fred", "yahoo"}
        assert p.transform in {"diff", "returns", "log_returns", "level"}
