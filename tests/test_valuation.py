"""Unit tests for the intrinsic-value + pyramiding engine (no network).

Run with:  python -m unittest discover tests   (or)   python tests/test_valuation.py
"""

from __future__ import annotations

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valuation import intrinsic, pyramid
from valuation.engine import value_stock


class TestIntrinsicModels(unittest.TestCase):
    def test_graham_number(self):
        # sqrt(22.5 * 55 * 668) = 909.20...
        self.assertAlmostEqual(intrinsic.graham_number(55, 668), 909.202, places=2)

    def test_graham_number_requires_positive(self):
        self.assertIsNone(intrinsic.graham_number(-1, 668))
        self.assertIsNone(intrinsic.graham_number(55, 0))
        self.assertIsNone(intrinsic.graham_number(None, 668))

    def test_graham_revised(self):
        # 55 * (8.5 + 2*10) * 4.4/4.4 = 55 * 28.5 = 1567.5
        self.assertAlmostEqual(
            intrinsic.graham_revised(55, 0.10, bond_yield=4.4, growth_cap=None),
            1567.5, places=2)

    def test_graham_revised_growth_cap(self):
        # growth 30% capped to 15% -> multiple 8.5 + 2*15 = 38.5
        v = intrinsic.graham_revised(10, 0.30, bond_yield=4.4, growth_cap=0.15)
        self.assertAlmostEqual(v, 10 * 38.5, places=2)

    def test_graham_revised_bond_yield_scaling(self):
        # Doubling the bond yield halves the value.
        base = intrinsic.graham_revised(50, 0.08, bond_yield=4.4, growth_cap=None)
        higher = intrinsic.graham_revised(50, 0.08, bond_yield=8.8, growth_cap=None)
        self.assertAlmostEqual(higher, base / 2, places=4)

    def test_dcf_two_stage_known_value(self):
        # base=100, g=0, tg=0, r=10%, years=1:
        #   stage1 = 100/1.1 = 90.909...
        #   terminal = 100/0.10 = 1000 -> discounted = 1000/1.1 = 909.09...
        v = intrinsic.dcf_two_stage(100, 0.0, 0.10, terminal_growth=0.0, years=1)
        self.assertAlmostEqual(v, 100 / 1.1 + (100 / 0.10) / 1.1, places=4)

    def test_dcf_diverges_guard(self):
        # r <= terminal growth -> undefined
        self.assertIsNone(intrinsic.dcf_two_stage(100, 0.05, 0.03,
                                                  terminal_growth=0.03, years=5))

    def test_earnings_power(self):
        # 55 * 1.1^10 * 20 / 1.12^10
        v = intrinsic.earnings_power(55, 0.10, 0.12, 20, years=10)
        expected = 55 * (1.1 ** 10) * 20 / (1.12 ** 10)
        self.assertAlmostEqual(v, expected, places=2)

    def test_ddm(self):
        # 6 * 1.10 / (0.12 - 0.10) = 6.6 / 0.02 = 330
        self.assertAlmostEqual(intrinsic.ddm_gordon(6, 0.12, 0.10), 330.0, places=4)
        # r <= g -> undefined
        self.assertIsNone(intrinsic.ddm_gordon(6, 0.10, 0.10))


class TestComposite(unittest.TestCase):
    def test_composite_is_median_and_ignores_outlier(self):
        f = intrinsic.Fundamentals(
            eps=55, book_value_per_share=668, growth_rate=0.10,
            dividend_per_share=6, fair_pe=20, current_price=1257.5)
        res = intrinsic.intrinsic_value_estimates(f, margin_of_safety=0.30)
        self.assertEqual(res["num_methods"], 5)
        # median of the five values
        expected = sorted(res["methods"].values())[2]
        self.assertAlmostEqual(res["composite"], expected, places=2)
        # best buy price = composite * (1 - mos)
        self.assertAlmostEqual(res["best_buy_price"],
                               round(res["composite"] * 0.70, 2), places=2)

    def test_verdict_buy_zone(self):
        f = intrinsic.Fundamentals(eps=100, book_value_per_share=100,
                                   growth_rate=0.05, current_price=50)
        res = intrinsic.intrinsic_value_estimates(f)
        self.assertTrue(res["upside"] > 0)
        self.assertIn("BUY ZONE", res["verdict"])

    def test_no_methods_when_no_inputs(self):
        res = intrinsic.intrinsic_value_estimates(intrinsic.Fundamentals())
        self.assertEqual(res["num_methods"], 0)
        self.assertIsNone(res["composite"])
        self.assertIsNone(res["best_buy_price"])

    def test_dcf_prefers_fcf_over_eps(self):
        f = intrinsic.Fundamentals(eps=10, fcf_per_share=20, growth_rate=0.08)
        res = intrinsic.intrinsic_value_estimates(f)
        self.assertEqual(res["dcf_cash_flow_basis"], "fcf_per_share")


class TestPyramidValue(unittest.TestCase):
    def test_levels_and_prices(self):
        plan = pyramid.build_pyramid(1000, margin_of_safety=0.30, tranches=3,
                                     step=0.10, weighting="increasing")
        prices = [t["price"] for t in plan["tranches"]]
        self.assertEqual(prices, [700.0, 600.0, 500.0])  # 30/40/50% discounts
        discounts = [t["discount_to_intrinsic"] for t in plan["tranches"]]
        self.assertEqual(discounts, [30.0, 40.0, 50.0])

    def test_weights_sum_to_one(self):
        for scheme in ("increasing", "equal", "decreasing"):
            plan = pyramid.build_pyramid(1000, tranches=4, weighting=scheme)
            total = sum(t["weight"] for t in plan["tranches"])
            self.assertAlmostEqual(total, 1.0, places=6)

    def test_increasing_weights_are_bigger_when_cheaper(self):
        plan = pyramid.build_pyramid(1000, tranches=3, weighting="increasing")
        w = [t["weight"] for t in plan["tranches"]]
        self.assertLess(w[0], w[-1])  # deepest tranche is largest

    def test_weighted_average_entry(self):
        plan = pyramid.build_pyramid(1000, margin_of_safety=0.30, tranches=3,
                                     step=0.10, weighting="increasing")
        # prices 700/600/500 with weights 1/6, 2/6, 3/6
        expected = (700 * 1 + 600 * 2 + 500 * 3) / 6
        self.assertAlmostEqual(plan["summary"]["avg_entry_price"], round(expected, 2), places=2)

    def test_share_sizing_within_capital(self):
        plan = pyramid.build_pyramid(1000, tranches=3, weighting="equal",
                                     capital=30000)
        s = plan["summary"]
        self.assertLessEqual(s["planned_cost"], 30000 + 1e-6)
        self.assertEqual(
            s["planned_shares"], sum(t["shares"] for t in plan["tranches"]))
        # whole shares only
        for t in plan["tranches"]:
            self.assertEqual(t["shares"], int(t["shares"]))

    def test_triggered_flag(self):
        plan = pyramid.build_pyramid(1000, margin_of_safety=0.30, tranches=2,
                                     current_price=650)
        # first tranche at 700 is at/above current 650 -> triggered
        self.assertTrue(plan["tranches"][0]["triggered"])
        # second tranche at 600 is below current -> not yet
        self.assertFalse(plan["tranches"][1]["triggered"])

    def test_invalid_intrinsic_raises(self):
        with self.assertRaises(ValueError):
            pyramid.build_pyramid(0)
        with self.assertRaises(ValueError):
            pyramid.build_pyramid(1000, tranches=0)


class TestPyramidTrend(unittest.TestCase):
    def test_prices_step_up(self):
        plan = pyramid.build_trend_pyramid(100, tranches=3, step=0.10,
                                           weighting="decreasing")
        prices = [t["price"] for t in plan["tranches"]]
        self.assertEqual(prices, [100.0, 110.0, 120.0])

    def test_decreasing_weights_taper(self):
        plan = pyramid.build_trend_pyramid(100, tranches=3, weighting="decreasing")
        w = [t["weight"] for t in plan["tranches"]]
        self.assertGreater(w[0], w[-1])  # base is largest, adds taper

    def test_trailing_stop_present(self):
        plan = pyramid.build_trend_pyramid(100, tranches=2, trail_pct=0.10)
        self.assertAlmostEqual(plan["tranches"][0]["trailing_stop"], 90.0, places=2)


class TestEngine(unittest.TestCase):
    def test_manual_report_no_network(self):
        rep = value_stock(symbol="RELIANCE", auto=False, eps=55,
                          book_value_per_share=668, growth_rate=0.10,
                          dividend_per_share=6, fair_pe=20, current_price=1257.5,
                          capital=100000, tranches=3)
        self.assertEqual(rep["stock"]["symbol"], "RELIANCE.NS")
        self.assertGreater(rep["intrinsic"]["composite"], 0)
        self.assertEqual(rep["pyramid"]["mode"], "value_accumulate")
        # supplied inputs are tagged as supplied
        self.assertEqual(rep["inputs"]["eps"]["source"], "supplied")

    def test_overrides_win_over_defaults(self):
        rep = value_stock(auto=False, eps=10, growth_rate=0.08,
                          discount_rate=0.15, years=5)
        self.assertEqual(rep["inputs"]["discount_rate"]["value"], 0.15)
        self.assertEqual(rep["inputs"]["discount_rate"]["source"], "supplied")
        self.assertEqual(rep["inputs"]["years"]["value"], 5)

    def test_trend_mode_uses_entry(self):
        rep = value_stock(auto=False, eps=65, growth_rate=0.10, fair_pe=24,
                          current_price=1500, pyramid_mode="trend",
                          weighting="decreasing", tranches=3)
        self.assertEqual(rep["pyramid"]["mode"], "trend_pyramid")
        self.assertEqual(rep["pyramid"]["tranches"][0]["price"], 1500.0)

    def test_warns_when_insufficient(self):
        rep = value_stock(auto=False)  # no inputs at all
        self.assertTrue(any("No intrinsic-value model" in w for w in rep["warnings"]))
        self.assertIsNone(rep["pyramid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
