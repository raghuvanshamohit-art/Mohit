"""
Calibrate the ExitMantra proxy against real samples.

Usage:
    python3 tools/em_calibrate.py tools/samples.csv

Reads a CSV of real ExitMantra readings (see samples_template.csv), fetches
price data for each ticker, then:
  * checks our 52-week outperformance calc vs ExitMantra's flag,
  * grid-searches the exit-price indicator (supertrend / chandelier + params)
    to best match ExitMantra's shown Exit Price,
  * rebuilds score / rating / zone and reports match rate,
  * profiles Super Performers to infer the extra rule.
"""

from __future__ import annotations
import csv
import sys
import statistics as st

import em_engine as em


def yn(v: str | None) -> bool | None:
    if v is None or str(v).strip() == "":
        return None
    return str(v).strip().lower() in ("y", "yes", "1", "true", "up", "outperformer")


def num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def ret_nbars(series: em.Series, n: int) -> float:
    c = series.c
    return c[-1] / c[-1 - n] - 1 if len(c) > n else c[-1] / c[0] - 1


def load(path: str) -> list[dict]:
    with open(path, newline="") as f:
        return [row for row in csv.DictReader(f) if (row.get("ticker") or "").strip()]


ST_GRID = [("supertrend", p, m) for p in (7, 10, 14) for m in (1.5, 2, 2.5, 3, 3.5, 4)]
CH_GRID = [("chandelier", p, m) for p in (22, 26) for m in (2, 2.5, 3, 3.5, 4)]
GRID = ST_GRID + CH_GRID


def main(path: str) -> None:
    rows = load(path)
    if not rows:
        print("No rows found. Fill in tools/samples.csv first.")
        return

    print(f"Loaded {len(rows)} samples. Fetching Nifty 500 …")
    idx = em.fetch(em.NIFTY500_SYMBOL, rng="2y", interval="1wk")
    idx_ret = ret_nbars(idx, 52)

    # fetch each stock once (weekly 2y)
    data = {}
    for r in rows:
        t = r["ticker"].strip().upper()
        sym = t if "." in t else t + ".NS"
        try:
            data[t] = em.fetch(sym, rng="2y", interval="1wk")
            print(f"  fetched {sym}: {len(data[t].c)} weeks, last {data[t].last_close:.2f}")
        except Exception as e:  # noqa: BLE001
            print(f"  !! {sym}: {e}")

    # -------- Criterion 2: outperformance --------
    print("\n=== Criterion 2: 52-week outperformance vs Nifty 500 ===")
    print(f"Nifty 500 52w return: {idx_ret*100:+.1f}%")
    op_match = op_total = 0
    for r in rows:
        t = r["ticker"].strip().upper()
        if t not in data:
            continue
        my = ret_nbars(data[t], 52) > idx_ret
        their = yn(r.get("outperformer"))
        flag = "" if their is None else ("MATCH" if my == their else "MISMATCH")
        if their is not None:
            op_total += 1
            op_match += (my == their)
        print(f"  {t:14s} stock {ret_nbars(data[t],52)*100:+6.1f}%  -> mine={str(my):5s}"
              f" their={their}  {flag}")
    if op_total:
        print(f"  outperformance match: {op_match}/{op_total}")

    # -------- Criterion 3: calibrate exit price --------
    print("\n=== Criterion 3: calibrating exit-price proxy ===")
    fit_rows = [r for r in rows
                if num(r.get("exit_price")) and r["ticker"].strip().upper() in data]
    if not fit_rows:
        print("  No rows with an exit_price to calibrate against. "
              "Fill exit_price for non-bear-zone stocks.")
    else:
        best = None
        for method, period, mult in GRID:
            errs, cls_ok, cls_tot = [], 0, 0
            for r in fit_rows:
                t = r["ticker"].strip().upper()
                s = data[t]
                lvl, up = em.exit_level(s, method, period, mult)
                cmp = num(r.get("cmp")) or s.last_close
                exit_actual = num(r["exit_price"])
                if lvl and lvl > 0:
                    errs.append(abs(lvl - exit_actual) / exit_actual)
                their_above = yn(r.get("above_exit"))
                if their_above is not None and lvl:
                    cls_tot += 1
                    cls_ok += ((cmp > lvl) == their_above)
            if not errs:
                continue
            med = st.median(errs)
            acc = cls_ok / cls_tot if cls_tot else 0
            cand = (acc, -med, method, period, mult)
            if best is None or cand > best:
                best = cand
        if best:
            acc, negmed, method, period, mult = best
            print(f"  BEST: {method}({period},{mult})  "
                  f"median |err| {(-negmed)*100:.1f}%  class-acc {acc*100:.0f}%")
            print(f"  {'ticker':14s} {'their_exit':>10s} {'my_exit':>10s} {'err%':>7s} {'cmp':>9s}")
            for r in fit_rows:
                t = r["ticker"].strip().upper()
                s = data[t]
                lvl, up = em.exit_level(s, method, period, mult)
                ea = num(r["exit_price"])
                err = abs(lvl - ea) / ea * 100 if lvl else float("nan")
                print(f"  {t:14s} {ea:10.2f} {(lvl or 0):10.2f} {err:6.1f}% "
                      f"{(num(r.get('cmp')) or s.last_close):9.2f}")

    # -------- Rebuild score / rating / zone --------
    print("\n=== Score / Rating / Zone reconstruction ===")
    if fit_rows and best:
        _, _, method, period, mult = best
    else:
        method, period, mult = "supertrend", 10, 3.0
    r_match = r_tot = 0
    for r in rows:
        t = r["ticker"].strip().upper()
        if t not in data:
            continue
        s = data[t]
        ath = yn(r.get("ath_profit"))
        outp = ret_nbars(s, 52) > idx_ret
        lvl, up = em.exit_level(s, method, period, mult)
        cmp = num(r.get("cmp")) or s.last_close
        above = bool(lvl) and cmp > lvl
        if ath is None:
            continue  # need criterion 1 flag to reconstruct
        res = em.score_rating_zone(ath, outp, above)
        their = (r.get("rating") or "").strip().upper()
        flag = "" if not their else ("MATCH" if res["rating"] == their else "MISMATCH")
        if their:
            r_tot += 1
            r_match += (res["rating"] == their)
        print(f"  {t:14s} mine={res['rating']:8s}({res['score']}) zone={res['zone']:5s}"
              f"  their={their or '-':8s}  {flag}")
    if r_tot:
        print(f"  rating match: {r_match}/{r_tot}")

    # -------- Super Performer profiling --------
    print("\n=== Super Performer profile ===")
    sp_yes, sp_no = [], []
    for r in rows:
        t = r["ticker"].strip().upper()
        if t not in data:
            continue
        sp = yn(r.get("super_performer"))
        if sp is None:
            continue
        spread = ret_nbars(data[t], 52) - idx_ret
        (sp_yes if sp else sp_no).append((t, spread))
    if sp_yes:
        print(f"  SP=Y ({len(sp_yes)}): RS-spread avg "
              f"{st.mean(x[1] for x in sp_yes)*100:+.1f}%")
    if sp_no:
        print(f"  SP=N ({len(sp_no)}): RS-spread avg "
              f"{st.mean(x[1] for x in sp_no)*100:+.1f}%")
    print("  (Provide ath_profit + rating so we can test 'SP = all 3 met + strong RS'.)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tools/samples.csv")
