"""Indian market sectors and their constituent stocks.

The sector definitions below follow the NSE **sectoral indices** (Nifty Bank,
Nifty IT, Nifty Auto, ...). These indices are how the National Stock Exchange
of India officially groups listed companies by sector, so they are the natural
"list of all Indian sectors".

Each stock carries the symbol used by NSE. The ``yahoo_symbol`` is derived by
appending the ``.NS`` suffix that Yahoo Finance uses for NSE-listed equities
(with a couple of hand overrides where the two differ).

``nse.py`` can refresh the constituents live from NSE when the exchange is
reachable; this module is the authoritative bundled fallback (NSE blocks many
datacenter / cloud IP ranges, so a live fetch is not always possible).
"""

from __future__ import annotations

from dataclasses import dataclass, field


# A few NSE symbols need a different Yahoo Finance ticker. Everything else is
# simply "<NSE symbol>.NS".
_YAHOO_OVERRIDES = {
    # symbols with characters that must be preserved verbatim on Yahoo
    "M&M": "M&M.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "L&TFH": "L&TFH.NS",
}


def to_yahoo(nse_symbol: str) -> str:
    """Return the Yahoo Finance ticker for an NSE trading symbol."""
    return _YAHOO_OVERRIDES.get(nse_symbol, f"{nse_symbol}.NS")


@dataclass(frozen=True)
class Stock:
    symbol: str          # NSE trading symbol, e.g. "HDFCBANK"
    name: str            # Company name

    @property
    def yahoo_symbol(self) -> str:
        return to_yahoo(self.symbol)


@dataclass(frozen=True)
class Sector:
    key: str             # short slug, e.g. "bank"
    name: str            # display name, e.g. "Bank"
    nse_index: str       # NSE sectoral index this maps to
    stocks: list = field(default_factory=list)


def _s(pairs):
    return [Stock(sym, name) for sym, name in pairs]


# ---------------------------------------------------------------------------
# Sector -> constituent stocks.
# Constituents follow the composition of each NSE sectoral index.
# ---------------------------------------------------------------------------

SECTORS: "list[Sector]" = [
    Sector("bank", "Bank", "NIFTY BANK", _s([
        ("HDFCBANK", "HDFC Bank"),
        ("ICICIBANK", "ICICI Bank"),
        ("SBIN", "State Bank of India"),
        ("KOTAKBANK", "Kotak Mahindra Bank"),
        ("AXISBANK", "Axis Bank"),
        ("INDUSINDBK", "IndusInd Bank"),
        ("BANKBARODA", "Bank of Baroda"),
        ("PNB", "Punjab National Bank"),
        ("IDFCFIRSTB", "IDFC First Bank"),
        ("AUBANK", "AU Small Finance Bank"),
        ("FEDERALBNK", "Federal Bank"),
        ("CANBK", "Canara Bank"),
    ])),

    Sector("it", "Information Technology", "NIFTY IT", _s([
        ("TCS", "Tata Consultancy Services"),
        ("INFY", "Infosys"),
        ("HCLTECH", "HCL Technologies"),
        ("WIPRO", "Wipro"),
        ("TECHM", "Tech Mahindra"),
        ("LTM", "LTM (formerly LTIMindtree)"),
        ("PERSISTENT", "Persistent Systems"),
        ("COFORGE", "Coforge"),
        ("MPHASIS", "Mphasis"),
        ("OFSS", "Oracle Financial Services Software"),
    ])),

    Sector("auto", "Automobile", "NIFTY AUTO", _s([
        ("MARUTI", "Maruti Suzuki India"),
        ("M&M", "Mahindra & Mahindra"),
        ("TMPV", "Tata Motors Passenger Vehicles"),
        ("TMCV", "Tata Motors (Commercial Vehicles)"),
        ("BAJAJ-AUTO", "Bajaj Auto"),
        ("EICHERMOT", "Eicher Motors"),
        ("HEROMOTOCO", "Hero MotoCorp"),
        ("TVSMOTOR", "TVS Motor Company"),
        ("ASHOKLEY", "Ashok Leyland"),
        ("BHARATFORG", "Bharat Forge"),
        ("BOSCHLTD", "Bosch"),
        ("MRF", "MRF"),
        ("BALKRISIND", "Balkrishna Industries"),
        ("MOTHERSON", "Samvardhana Motherson International"),
        ("TIINDIA", "Tube Investments of India"),
        ("EXIDEIND", "Exide Industries"),
    ])),

    Sector("pharma", "Pharmaceuticals", "NIFTY PHARMA", _s([
        ("SUNPHARMA", "Sun Pharmaceutical Industries"),
        ("DRREDDY", "Dr. Reddy's Laboratories"),
        ("CIPLA", "Cipla"),
        ("DIVISLAB", "Divi's Laboratories"),
        ("LUPIN", "Lupin"),
        ("AUROPHARMA", "Aurobindo Pharma"),
        ("ZYDUSLIFE", "Zydus Lifesciences"),
        ("TORNTPHARM", "Torrent Pharmaceuticals"),
        ("ALKEM", "Alkem Laboratories"),
        ("GLENMARK", "Glenmark Pharmaceuticals"),
        ("BIOCON", "Biocon"),
    ])),

    Sector("fmcg", "FMCG", "NIFTY FMCG", _s([
        ("HINDUNILVR", "Hindustan Unilever"),
        ("ITC", "ITC"),
        ("NESTLEIND", "Nestle India"),
        ("VBL", "Varun Beverages"),
        ("BRITANNIA", "Britannia Industries"),
        ("TATACONSUM", "Tata Consumer Products"),
        ("DABUR", "Dabur India"),
        ("GODREJCP", "Godrej Consumer Products"),
        ("MARICO", "Marico"),
        ("COLPAL", "Colgate-Palmolive (India)"),
        ("UBL", "United Breweries"),
        ("PGHH", "Procter & Gamble Hygiene"),
        ("EMAMILTD", "Emami"),
        ("RADICO", "Radico Khaitan"),
        ("BALRAMCHIN", "Balrampur Chini Mills"),
    ])),

    Sector("metal", "Metal", "NIFTY METAL", _s([
        ("TATASTEEL", "Tata Steel"),
        ("HINDALCO", "Hindalco Industries"),
        ("JSWSTEEL", "JSW Steel"),
        ("VEDL", "Vedanta"),
        ("ADANIENT", "Adani Enterprises"),
        ("JINDALSTEL", "Jindal Steel & Power"),
        ("HINDZINC", "Hindustan Zinc"),
        ("SAIL", "Steel Authority of India"),
        ("NMDC", "NMDC"),
        ("APLAPOLLO", "APL Apollo Tubes"),
        ("NATIONALUM", "National Aluminium"),
        ("JSL", "Jindal Stainless"),
        ("WELCORP", "Welspun Corp"),
        ("HINDCOPPER", "Hindustan Copper"),
        ("RATNAMANI", "Ratnamani Metals & Tubes"),
    ])),

    Sector("realty", "Realty", "NIFTY REALTY", _s([
        ("DLF", "DLF"),
        ("LODHA", "Macrotech Developers (Lodha)"),
        ("GODREJPROP", "Godrej Properties"),
        ("OBEROIRLTY", "Oberoi Realty"),
        ("PHOENIXLTD", "The Phoenix Mills"),
        ("PRESTIGE", "Prestige Estates Projects"),
        ("BRIGADE", "Brigade Enterprises"),
        ("SOBHA", "Sobha"),
        ("ANANTRAJ", "Anant Raj"),
        ("RAYMOND", "Raymond"),
    ])),

    Sector("energy", "Energy", "NIFTY ENERGY", _s([
        ("RELIANCE", "Reliance Industries"),
        ("NTPC", "NTPC"),
        ("POWERGRID", "Power Grid Corporation of India"),
        ("ONGC", "Oil & Natural Gas Corporation"),
        ("COALINDIA", "Coal India"),
        ("IOC", "Indian Oil Corporation"),
        ("BPCL", "Bharat Petroleum Corporation"),
        ("ADANIGREEN", "Adani Green Energy"),
        ("TATAPOWER", "Tata Power Company"),
        ("ADANIPOWER", "Adani Power"),
    ])),

    Sector("media", "Media & Entertainment", "NIFTY MEDIA", _s([
        ("ZEEL", "Zee Entertainment Enterprises"),
        ("SUNTV", "Sun TV Network"),
        ("PVRINOX", "PVR INOX"),
        ("NAZARA", "Nazara Technologies"),
        ("NETWORK18", "Network18 Media & Investments"),
        ("SAREGAMA", "Saregama India"),
        ("DISHTV", "Dish TV India"),
        ("HATHWAY", "Hathway Cable & Datacom"),
    ])),

    Sector("psu_bank", "PSU Bank", "NIFTY PSU BANK", _s([
        ("SBIN", "State Bank of India"),
        ("BANKBARODA", "Bank of Baroda"),
        ("PNB", "Punjab National Bank"),
        ("CANBK", "Canara Bank"),
        ("UNIONBANK", "Union Bank of India"),
        ("INDIANB", "Indian Bank"),
        ("BANKINDIA", "Bank of India"),
        ("MAHABANK", "Bank of Maharashtra"),
        ("CENTRALBK", "Central Bank of India"),
        ("IOB", "Indian Overseas Bank"),
        ("UCOBANK", "UCO Bank"),
        ("PSB", "Punjab & Sind Bank"),
    ])),

    Sector("private_bank", "Private Bank", "NIFTY PRIVATE BANK", _s([
        ("HDFCBANK", "HDFC Bank"),
        ("ICICIBANK", "ICICI Bank"),
        ("KOTAKBANK", "Kotak Mahindra Bank"),
        ("AXISBANK", "Axis Bank"),
        ("INDUSINDBK", "IndusInd Bank"),
        ("IDFCFIRSTB", "IDFC First Bank"),
        ("FEDERALBNK", "Federal Bank"),
        ("BANDHANBNK", "Bandhan Bank"),
        ("RBLBANK", "RBL Bank"),
        ("CUB", "City Union Bank"),
    ])),

    Sector("financial_services", "Financial Services", "NIFTY FINANCIAL SERVICES", _s([
        ("HDFCBANK", "HDFC Bank"),
        ("ICICIBANK", "ICICI Bank"),
        ("AXISBANK", "Axis Bank"),
        ("KOTAKBANK", "Kotak Mahindra Bank"),
        ("SBIN", "State Bank of India"),
        ("BAJFINANCE", "Bajaj Finance"),
        ("BAJAJFINSV", "Bajaj Finserv"),
        ("JIOFIN", "Jio Financial Services"),
        ("HDFCLIFE", "HDFC Life Insurance"),
        ("SBILIFE", "SBI Life Insurance"),
        ("ICICIPRULI", "ICICI Prudential Life Insurance"),
        ("SHRIRAMFIN", "Shriram Finance"),
        ("CHOLAFIN", "Cholamandalam Investment & Finance"),
        ("HDFCAMC", "HDFC Asset Management"),
        ("SBICARD", "SBI Cards & Payment Services"),
        ("PFC", "Power Finance Corporation"),
        ("RECLTD", "REC"),
        ("MUTHOOTFIN", "Muthoot Finance"),
    ])),

    Sector("healthcare", "Healthcare", "NIFTY HEALTHCARE", _s([
        ("SUNPHARMA", "Sun Pharmaceutical Industries"),
        ("CIPLA", "Cipla"),
        ("DRREDDY", "Dr. Reddy's Laboratories"),
        ("DIVISLAB", "Divi's Laboratories"),
        ("APOLLOHOSP", "Apollo Hospitals Enterprise"),
        ("MAXHEALTH", "Max Healthcare Institute"),
        ("FORTIS", "Fortis Healthcare"),
        ("LUPIN", "Lupin"),
        ("ZYDUSLIFE", "Zydus Lifesciences"),
        ("TORNTPHARM", "Torrent Pharmaceuticals"),
        ("ALKEM", "Alkem Laboratories"),
        ("AUROPHARMA", "Aurobindo Pharma"),
        ("BIOCON", "Biocon"),
        ("LALPATHLAB", "Dr. Lal PathLabs"),
        ("SYNGENE", "Syngene International"),
        ("MANKIND", "Mankind Pharma"),
    ])),

    Sector("consumer_durables", "Consumer Durables", "NIFTY CONSUMER DURABLES", _s([
        ("TITAN", "Titan Company"),
        ("HAVELLS", "Havells India"),
        ("VOLTAS", "Voltas"),
        ("CROMPTON", "Crompton Greaves Consumer Electricals"),
        ("DIXON", "Dixon Technologies (India)"),
        ("BLUESTARCO", "Blue Star"),
        ("KAJARIACER", "Kajaria Ceramics"),
        ("WHIRLPOOL", "Whirlpool of India"),
        ("BATAINDIA", "Bata India"),
        ("VGUARD", "V-Guard Industries"),
        ("AMBER", "Amber Enterprises India"),
        ("TTKPRESTIG", "TTK Prestige"),
        ("CERA", "Cera Sanitaryware"),
    ])),

    Sector("oil_gas", "Oil & Gas", "NIFTY OIL & GAS", _s([
        ("RELIANCE", "Reliance Industries"),
        ("ONGC", "Oil & Natural Gas Corporation"),
        ("IOC", "Indian Oil Corporation"),
        ("BPCL", "Bharat Petroleum Corporation"),
        ("GAIL", "GAIL (India)"),
        ("HINDPETRO", "Hindustan Petroleum Corporation"),
        ("ATGL", "Adani Total Gas"),
        ("IGL", "Indraprastha Gas"),
        ("PETRONET", "Petronet LNG"),
        ("GUJENERGY", "Gujarat Energy (formerly Gujarat Gas)"),
        ("OIL", "Oil India"),
        ("MGL", "Mahanagar Gas"),
        ("CASTROLIND", "Castrol India"),
        ("GSPL", "Gujarat State Petronet"),
    ])),
]


def all_sectors() -> "list[Sector]":
    return SECTORS


def unique_symbols() -> "list[str]":
    """All distinct NSE symbols across every sector."""
    seen = {}
    for sec in SECTORS:
        for st in sec.stocks:
            seen.setdefault(st.symbol, st)
    return sorted(seen)


def stock_index():
    """symbol -> Stock (deduplicated)."""
    idx = {}
    for sec in SECTORS:
        for st in sec.stocks:
            idx.setdefault(st.symbol, st)
    return idx
