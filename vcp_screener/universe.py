"""The NSE F&O (Futures & Options) stock universe.

This is a static snapshot of NSE stocks that trade in the derivatives segment.
The exchange revises the list periodically (adds/removes names each expiry
cycle), so treat it as a starting point and refresh it against the current
"Securities in F&O" list on the NSE website when needed.

Symbols are plain NSE trading symbols (no exchange suffix). Data providers add
whatever suffix they need (e.g. ``.NS`` for Yahoo Finance).
"""

from __future__ import annotations

from typing import List

FNO_SYMBOLS: List[str] = [
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENSOL",
    "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ALKEM", "AMBUJACEM", "ANGELONE",
    "APLAPOLLO", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT",
    "ASTRAL", "ATGL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO",
    "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BANDHANBNK", "BANKBARODA",
    "BANKINDIA", "BATAINDIA", "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL",
    "BHEL", "BIOCON", "BOSCHLTD", "BPCL", "BRITANNIA", "BSOFT", "CAMS",
    "CANBK", "CANFINHOME", "CDSL", "CESC", "CGPOWER", "CHAMBLFERT",
    "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CONCOR",
    "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", "DABUR", "DALBHARAT",
    "DEEPAKNTR", "DELHIVERY", "DIVISLAB", "DIXON", "DLF", "DMART",
    "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK", "GAIL",
    "GLENMARK", "GMRAIRPORT", "GNFC", "GODREJCP", "GODREJPROP", "GRANULES",
    "GRASIM", "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC",
    "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HFCL", "HINDALCO", "HINDCOPPER",
    "HINDPETRO", "HINDUNILVR", "HUDCO", "ICICIBANK", "ICICIGI", "ICICIPRULI",
    "IDEA", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIAMART", "INDIGO",
    "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRB", "IRCTC",
    "IRFC", "ITC", "JINDALSTEL", "JIOFIN", "JKCEMENT", "JSL", "JSWENERGY",
    "JSWSTEEL", "JUBLFOOD", "KALYANKJIL", "KEI", "KOTAKBANK", "KPITTECH",
    "LAURUSLABS", "LICHSGFIN", "LICI", "LODHA", "LT", "LTF", "LTIM",
    "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI",
    "MAXHEALTH", "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS",
    "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NBCC",
    "NCC", "NESTLEIND", "NHPC", "NMDC", "NTPC", "NYKAA", "OBEROIRLTY",
    "OFSS", "OIL", "ONGC", "PAGEIND", "PATANJALI", "PAYTM", "PEL",
    "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", "PIIND", "PNB",
    "POLICYBZR", "POLYCAB", "POONAWALLA", "POWERGRID", "PRESTIGE", "PVRINOX",
    "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD",
    "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SJVN",
    "SONACOMS", "SRF", "SUNPHARMA", "SUNTV", "SUPREMEIND", "SYNGENE",
    "TATACHEM", "TATACOMM", "TATACONSUM", "TATAELXSI", "TATAMOTORS",
    "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TIINDIA", "TITAN",
    "TORNTPHARM", "TORNTPOWER", "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO",
    "UNIONBANK", "UNITDSPR", "UPL", "VBL", "VEDL", "VOLTAS", "WIPRO",
    "YESBANK", "ZOMATO", "ZYDUSLIFE",
]


def load_universe(path: str | None = None) -> List[str]:
    """Return the F&O universe.

    If ``path`` is given, read one symbol per line from that file (blank lines
    and ``#`` comments ignored); otherwise return the built-in snapshot.
    """
    if path is None:
        return list(FNO_SYMBOLS)
    symbols: List[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            symbols.append(line.upper())
    return symbols
