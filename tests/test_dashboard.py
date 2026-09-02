from dyncorr.dashboard import (
    DEFAULT_PARAMS,
    build_dashboard_data,
    render_dashboard,
    write_dashboard,
)
from dyncorr.data import build_panel


def test_build_dashboard_data():
    panel = build_panel(["gold", "us_treasury_10y", "inflation"], source="synthetic")
    data = build_dashboard_data(panel)
    assert data["order"] == ["gold", "us_treasury_10y", "inflation"]
    assert len(data["dates"]) == data["n"]
    for key in data["order"]:
        assert len(data["series"][key]) == data["n"]
        assert key in data["labels"]


def test_render_full_and_partial():
    full = render_dashboard(params=["gold", "us_treasury_10y"], full=True)
    assert full.lstrip().startswith("<!doctype html>")
    assert "__DATA__" not in full  # marker was replaced
    assert "Cross-Asset Correlation Monitor" in full

    partial = render_dashboard(params=["gold", "us_treasury_10y"], full=False)
    assert not partial.lstrip().startswith("<!doctype")
    assert partial.startswith("<title>")


def test_write_dashboard(tmp_path):
    out = tmp_path / "dash.html"
    write_dashboard(str(out), params=DEFAULT_PARAMS[:4])
    html = out.read_text()
    assert len(html) > 5000
    assert "<canvas id=\"line\"" in html
    assert "<canvas id=\"heat\"" in html


def test_dashboard_from_csv(tmp_path):
    import numpy as np
    import pandas as pd

    idx = pd.bdate_range("2021-01-01", periods=120)
    rng = np.random.default_rng(3)
    shocks = rng.standard_normal(120) * 0.01
    pd.DataFrame({
        "date": idx,
        "AAA": 10 * np.exp(np.cumsum(shocks)),
        "BBB": 20 * np.exp(np.cumsum(-shocks)),
    }).to_csv(tmp_path / "p.csv", index=False)

    html = render_dashboard(params=["AAA", "BBB"], csv_path=str(tmp_path / "p.csv"),
                            full=True)
    assert "AAA" in html and "BBB" in html
