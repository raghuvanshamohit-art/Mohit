"""Canonical criterion labels and ordering.

These strings are the single source of truth for the checklist. They are kept
byte-for-byte identical to the on-screen VCP checklist the screener is modelled
on, and drive both the evaluation engine and the report column order.
"""

# --- Individual criterion labels (order matters: matches the checklist) ------
C_PRICE_ABOVE_MAS = "Price > 50/150/200 MA"
C_MA_STACK = "MA 50>150>200"
C_MA200_RISING = "200 MA Rising (1M)"
C_MA50_RISING = "50 MA Rising"
C_WITHIN_HIGH = "Within 25% of 52W High"
C_ABOVE_LOW = "30%+ Above 52W Low (Optional)"
C_PRICE_ABOVE_10 = "Price > 10 MA"
C_MIN_PRICE = "Price >= ₹50"
C_WEEKLY_UPTREND = "Weekly Uptrend"
C_MA150_RISING = "150 MA Rising"
C_VOLUME_OK = "Sufficient Volume"
C_RS_STRONG = "RS vs Nifty Strong"
C_NIFTY_UPTREND = "Nifty in Uptrend"
C_VOLATILITY_CONTRACT = "Volatility Contracting"
C_VOLUME_CONTRACT = "Volume Contracting"

# The checklist, in display order.
CRITERIA_ORDER = [
    C_PRICE_ABOVE_MAS,
    C_MA_STACK,
    C_MA200_RISING,
    C_MA50_RISING,
    C_WITHIN_HIGH,
    C_ABOVE_LOW,
    C_PRICE_ABOVE_10,
    C_MIN_PRICE,
    C_WEEKLY_UPTREND,
    C_MA150_RISING,
    C_VOLUME_OK,
    C_RS_STRONG,
    C_NIFTY_UPTREND,
    C_VOLATILITY_CONTRACT,
    C_VOLUME_CONTRACT,
]

# Short column headers for the compact HTML/CSV matrix (same order).
SHORT_HEADERS = {
    C_PRICE_ABOVE_MAS: "Px>50/150/200",
    C_MA_STACK: "50>150>200",
    C_MA200_RISING: "200MA↑",
    C_MA50_RISING: "50MA↑",
    C_WITHIN_HIGH: "≤25% 52WH",
    C_ABOVE_LOW: "≥30% 52WL*",
    C_PRICE_ABOVE_10: "Px>10MA",
    C_MIN_PRICE: "Px≥₹50",
    C_WEEKLY_UPTREND: "Wk Uptrend",
    C_MA150_RISING: "150MA↑",
    C_VOLUME_OK: "Liquidity",
    C_RS_STRONG: "RS Strong",
    C_NIFTY_UPTREND: "Nifty↑",
    C_VOLATILITY_CONTRACT: "Vol'ty↓",
    C_VOLUME_CONTRACT: "Volume↓",
}

# Criteria that do not have to pass for a "FULL VCP SETUP" (marked Optional
# on the checklist).
DEFAULT_OPTIONAL = (C_ABOVE_LOW,)
