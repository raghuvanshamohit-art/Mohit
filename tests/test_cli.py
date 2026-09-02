import os

from dyncorr.cli import main


def test_list_presets(capsys):
    rc = main(["list-presets"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "gold" in out
    assert "us_treasury_10y" in out


def test_run_end_to_end(tmp_path, capsys):
    outdir = tmp_path / "out"
    rc = main([
        "run",
        "--params", "gold", "us_treasury_10y", "inflation",
        "--method", "rolling", "--window", "60",
        "--outdir", str(outdir),
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Static (full-sample) correlation matrix" in out
    assert "Dynamic correlation summary" in out

    for name in [
        "dynamic_correlation.csv",
        "static_correlation.csv",
        "current_correlation_matrix.csv",
        "summary.csv",
        "dynamic_correlation.png",
        "current_correlation_heatmap.png",
    ]:
        assert (outdir / name).exists(), f"missing {name}"


def test_run_ewma_no_plots(tmp_path):
    outdir = tmp_path / "out2"
    rc = main([
        "run",
        "--params", "gold", "sp500",
        "--method", "ewma", "--halflife", "20",
        "--no-plots", "--outdir", str(outdir),
    ])
    assert rc == 0
    assert (outdir / "dynamic_correlation.csv").exists()
    assert not (outdir / "dynamic_correlation.png").exists()


def test_run_rejects_unknown_param(tmp_path):
    try:
        main(["run", "--params", "gold", "not_a_real_param",
              "--outdir", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code != 0
    else:  # pragma: no cover
        assert False, "expected SystemExit for unknown parameter"


def test_run_pairs_filter(tmp_path):
    outdir = tmp_path / "out3"
    rc = main([
        "run",
        "--params", "gold", "us_treasury_10y", "sp500",
        "--pairs", "gold~us_treasury_10y",
        "--no-plots", "--outdir", str(outdir),
    ])
    assert rc == 0
    import pandas as pd

    roll = pd.read_csv(outdir / "dynamic_correlation.csv", index_col=0)
    assert list(roll.columns) == ["gold~us_treasury_10y"]
