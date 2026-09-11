"""Tests for the strategy engines (stdlib unittest, zero dependencies).

Run:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from strategy import allocation, pyramid, valuation
from strategy.valuation import Stage


class TestValuation(unittest.TestCase):
    def test_zero_growth_matches_perpetuity(self):
        # No explicit growth and terminal growth 0 → a simple perpetuity:
        # year-1 cash flow is base (grown 0%), value = base / discount.
        v = valuation.intrinsic_value(10.0, [Stage(0.0, 1)], 0.0, 0.10)
        # One explicit year (10/1.1) + terminal (10/0.10 discounted one year).
        expected = 10.0 / 1.1 + (10.0 / 0.10) / 1.1
        self.assertAlmostEqual(v.intrinsic_value, expected, places=6)
        self.assertAlmostEqual(v.intrinsic_value, 100.0, places=6)  # == base/discount

    def test_higher_discount_lowers_value(self):
        # The shop example: raise the discount rate, value must fall.
        cheap = valuation.intrinsic_value(50.0, [Stage(0.12, 10)], 0.04, 0.10)
        dear = valuation.intrinsic_value(50.0, [Stage(0.12, 10)], 0.04, 0.14)
        self.assertGreater(cheap.intrinsic_value, dear.intrinsic_value)

    def test_terminal_must_be_below_discount(self):
        with self.assertRaises(ValueError):
            valuation.intrinsic_value(50.0, [Stage(0.1, 5)], 0.12, 0.10)

    def test_margin_of_safety_and_verdict(self):
        iv = 100.0
        self.assertAlmostEqual(valuation.margin_of_safety(iv, 60.0), 0.40)
        self.assertIn("BUY", valuation.verdict(0.40))
        self.assertIn("ACCUMULATE", valuation.verdict(0.15))
        self.assertIn("HOLD", valuation.verdict(0.0))
        self.assertIn("AVOID", valuation.verdict(-0.25))

    def test_value_stock_sets_price_fields(self):
        v = valuation.value_stock(50.0, [Stage(0.12, 10)], 0.04, 0.11, price=500.0)
        self.assertIsNotNone(v.margin_of_safety)
        self.assertIsNotNone(v.verdict)
        self.assertEqual(v.price, 500.0)

    def test_implied_growth_round_trips(self):
        # Price a stock at a known growth, then recover that growth from price.
        g_true = 0.18
        price = valuation.intrinsic_value(
            40.0, [Stage(g_true, 8)], 0.04, 0.12
        ).intrinsic_value
        g_back = valuation.implied_growth(40.0, price, 8, 0.04, 0.12)
        self.assertIsNotNone(g_back)
        self.assertAlmostEqual(g_back, g_true, places=3)

    def test_required_return(self):
        self.assertAlmostEqual(valuation.required_return(0.07, 0.05), 0.12)


class TestAllocation(unittest.TestCase):
    def test_profiles_sum_to_one(self):
        for name, mix in allocation.PROFILES.items():
            self.assertAlmostEqual(sum(mix.values()), 1.0, places=6, msg=name)

    def test_rebalance_trims_winner_adds_to_loser(self):
        # Equity ran up to 75% vs a 65% target → SELL equity; bonds lag → BUY.
        holdings = {"equity": 750_000, "gold": 150_000, "bonds": 100_000}
        actions = {a.asset: a for a in allocation.rebalance(
            holdings, allocation.PROFILES["balanced"], band=0.02)}
        self.assertEqual(actions["equity"].side, "SELL")
        self.assertEqual(actions["bonds"].side, "BUY")
        # Total bought ≈ total sold (rebalance is cash-neutral within rounding).
        sold = sum(a.amount for a in actions.values() if a.side == "SELL")
        bought = sum(a.amount for a in actions.values() if a.side == "BUY")
        self.assertAlmostEqual(sold, bought, places=2)

    def test_band_holds_small_drift(self):
        holdings = {"equity": 660_000, "gold": 150_000, "bonds": 190_000}
        actions = allocation.rebalance(
            holdings, allocation.PROFILES["balanced"], band=0.05)
        self.assertTrue(all(a.side == "HOLD" for a in actions))

    def test_glide_shifts_equity_to_bonds(self):
        base = allocation.PROFILES["aggressive"]
        near = allocation.glide_targets(base, years_to_goal=3)
        self.assertLess(near["equity"], base["equity"])
        self.assertGreater(near["bonds"], base["bonds"])
        self.assertAlmostEqual(near["gold"], base["gold"], places=6)  # gold steady
        self.assertAlmostEqual(sum(near.values()), 1.0, places=6)

    def test_glide_noop_when_far(self):
        base = allocation.PROFILES["balanced"]
        self.assertEqual(allocation.glide_targets(base, 20), allocation.normalize(base))

    def test_new_money_only_buys_and_spends_full_amount(self):
        holdings = {"equity": 750_000, "gold": 150_000, "bonds": 100_000}
        actions = allocation.invest_new_money(
            holdings, allocation.PROFILES["balanced"], amount=100_000)
        self.assertTrue(all(a.side in ("BUY", "HOLD") for a in actions))
        self.assertAlmostEqual(sum(a.amount for a in actions), 100_000, places=2)
        # Bonds are most underweight here, so they should get the most cash.
        top = max(actions, key=lambda a: a.amount)
        self.assertEqual(top.asset, "bonds")


class TestPyramid(unittest.TestCase):
    def test_rungs_stop_at_intrinsic_value(self):
        plan = pyramid.pyramid_plan(
            entry_price=100, intrinsic_value=130, budget=100_000,
            tranches=10, step=0.08, cap=1.0)
        self.assertTrue(all(r.price <= 130 for r in plan.rungs))
        self.assertLess(len(plan.rungs), 10)  # some rungs dropped above value
        self.assertGreater(plan.uninvested, 0)

    def test_avg_cost_below_entry_times_last_price(self):
        # Decaying sizes keep average cost below the final rung price.
        plan = pyramid.pyramid_plan(
            entry_price=100, intrinsic_value=200, budget=100_000,
            tranches=5, step=0.08, decay=0.65)
        last_price = plan.rungs[-1].price
        self.assertLess(plan.final_avg_cost, last_price)
        self.assertAlmostEqual(plan.deployed, 100_000, places=2)

    def test_no_buy_above_ceiling(self):
        plan = pyramid.pyramid_plan(
            entry_price=150, intrinsic_value=130, budget=50_000)
        self.assertEqual(plan.rungs, [])
        self.assertIn("do not buy", plan.note)
        self.assertEqual(plan.uninvested, 50_000)

    def test_budget_fully_deployed_when_all_rungs_fit(self):
        plan = pyramid.pyramid_plan(
            entry_price=100, intrinsic_value=1000, budget=80_000,
            tranches=4, step=0.05)
        self.assertEqual(len(plan.rungs), 4)
        self.assertAlmostEqual(plan.deployed, 80_000, places=2)
        self.assertAlmostEqual(plan.uninvested, 0.0, places=2)


if __name__ == "__main__":
    unittest.main()
