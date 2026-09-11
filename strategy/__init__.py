"""Decision engines that turn the investor's framework into numbers.

Three questions from ``docs/investment-framework.md``, made computable:

* ``valuation``  — which stock to buy, and at what price? (intrinsic value,
  margin of safety, a buy / accumulate / hold / avoid verdict, and the growth
  the market is already pricing in).
* ``allocation`` — which asset to sell and which to buy? (counter-trend
  rebalancing back to a target mix, plus a glide path that shifts equity into
  bonds as the goal nears).
* ``pyramid``    — how to add to a winner? (a price-laddered plan that adds on
  the way up but stops once price reaches intrinsic value).

Pure standard library, no third-party dependencies.
"""

from __future__ import annotations

from . import allocation, pyramid, valuation

__all__ = ["valuation", "allocation", "pyramid"]
