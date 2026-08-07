"""NSE F&O (Futures & Options) stock universe.

This is a snapshot of the NSE F&O equity list (stocks on which single-stock
futures/options trade). The list is periodically revised by NSE, so using a
single current snapshot over a multi-year backtest introduces some
survivorship / constituent bias (see README). Symbols are in Yahoo Finance
format (NSE ticker + ".NS").
"""

# ~190 names. Kept as a plain list so it is easy to edit / extend.
FO_SYMBOLS = [
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
    "DEEPAKNTR", "DELHIVERY", "DIVISLAB", "DIXON", "DLF", "DMART", "DRREDDY",
    "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK", "GAIL", "GLENMARK",
    "GMRAIRPORT", "GNFC", "GODREJCP", "GODREJPROP", "GRANULES", "GRASIM",
    "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC", "HDFCBANK",
    "HDFCLIFE", "HEROMOTOCO", "HFCL", "HINDALCO", "HINDCOPPER", "HINDPETRO",
    "HINDUNILVR", "HUDCO", "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA",
    "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIANB", "INDIGO", "INDUSINDBK",
    "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRB", "IRCTC", "IRFC", "ITC",
    "JINDALSTEL", "JIOFIN", "JKCEMENT", "JSWENERGY", "JSWSTEEL", "JUBLFOOD",
    "KALYANKJIL", "KEI", "KOTAKBANK", "KPITTECH", "LAURUSLABS",
    "LICHSGFIN", "LICI", "LODHA", "LT", "LTF", "LTIM", "LTTS", "LUPIN",
    "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MAXHEALTH", "MCX",
    "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN",
    "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NBCC", "NCC", "NESTLEIND", "NHPC",
    "NMDC", "NTPC", "NYKAA", "OBEROIRLTY", "OFSS", "OIL", "ONGC", "PAGEIND",
    "PAYTM", "PEL", "PERSISTENT", "PETRONET", "PFC", "PHOENIXLTD", "PIDILITIND",
    "PIIND", "PNB", "PNBHOUSING", "POLICYBZR", "POLYCAB", "POONAWALLA",
    "POWERGRID", "PRESTIGE", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD",
    "RELIANCE", "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN",
    "SIEMENS", "SJVN", "SONACOMS", "SRF", "SUNPHARMA", "SUNTV", "SUPREMEIND",
    "SYNGENE", "TATACHEM", "TATACOMM", "TATACONSUM", "TATAELXSI", "TATAMOTORS",
    "TATAPOWER", "TATASTEEL", "TATATECH", "TCS", "TECHM", "TIINDIA", "TITAN",
    "TORNTPHARM", "TORNTPOWER", "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO",
    "UNIONBANK", "UNITDSPR", "UPL", "VBL", "VEDL", "VOLTAS", "WIPRO", "YESBANK",
    "ZOMATO", "ZYDUSLIFE",
]

FO_SYMBOLS = sorted(set(FO_SYMBOLS))


def yahoo_symbols():
    """Return Yahoo Finance tickers (NSE ticker + '.NS')."""
    return [f"{s}.NS" for s in FO_SYMBOLS]


if __name__ == "__main__":
    print(f"{len(FO_SYMBOLS)} F&O symbols")
    for s in yahoo_symbols():
        print(s)
