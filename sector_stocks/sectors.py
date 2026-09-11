"""Indian market — 72-sector industry taxonomy and their constituent stocks.

This is a granular industry / sub-sector classification of the Indian market
(72 groups), grounded in the NSE macro-economic → sector → industry structure
and the sub-sectors data providers commonly use. It is deliberately finer than
the ~15 tradeable NSE sectoral indices: e.g. "Auto" is split into Passenger
Vehicles, Two & Three Wheelers, Commercial Vehicles, Tyres, Auto Components and
Batteries & EV.

Each sector rolls up to a ``macro`` economic sector (used for grouping in the
UI). Stocks carry their NSE trading symbol; ``yahoo_symbol`` appends the ``.NS``
suffix Yahoo Finance uses for NSE equities.

Constituent lists are representative liquid names per industry, not exhaustive
index memberships. ``nse.py`` can refresh live from NSE where reachable; NSE
blocks most datacenter IPs, so this bundled list is the working fallback.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Yahoo tickers that differ from "<NSE symbol>.NS" go here. In practice NSE
# symbols map directly (the client URL-encodes characters like "&" / "-").
_YAHOO_OVERRIDES: "dict[str, str]" = {
    # Yahoo carries these only on BSE (.BO), not NSE (.NS).
    "SPICEJET": "SPICEJET.BO",
}


def to_yahoo(nse_symbol: str) -> str:
    return _YAHOO_OVERRIDES.get(nse_symbol, f"{nse_symbol}.NS")


@dataclass(frozen=True)
class Stock:
    symbol: str
    name: str

    @property
    def yahoo_symbol(self) -> str:
        return to_yahoo(self.symbol)


@dataclass(frozen=True)
class Sector:
    key: str            # short slug
    name: str           # industry / sub-sector display name
    macro: str          # macro-economic sector it rolls up to
    stocks: list = field(default_factory=list)


def _s(pairs):
    return [Stock(sym, name) for sym, name in pairs]


# Ordered list of macro sectors (controls grouping order in the UI).
MACROS = [
    "Financials",
    "Information Technology",
    "Consumer Discretionary",
    "Consumer Staples",
    "Healthcare",
    "Energy & Utilities",
    "Metals & Mining",
    "Chemicals",
    "Construction & Materials",
    "Industrials",
    "Telecom, Media & Hospitality",
    "Diversified & Others",
]


# ---------------------------------------------------------------------------
# The 72 sectors.
# ---------------------------------------------------------------------------
SECTORS: "list[Sector]" = [

    # ===================== FINANCIALS (10) =====================
    Sector("banks_private", "Banks – Private", "Financials", _s([
        ("HDFCBANK", "HDFC Bank"), ("ICICIBANK", "ICICI Bank"), ("KOTAKBANK", "Kotak Mahindra Bank"),
        ("AXISBANK", "Axis Bank"), ("INDUSINDBK", "IndusInd Bank"), ("IDFCFIRSTB", "IDFC First Bank"),
        ("FEDERALBNK", "Federal Bank"), ("BANDHANBNK", "Bandhan Bank"), ("RBLBANK", "RBL Bank"),
        ("CUB", "City Union Bank"), ("KARURVYSYA", "Karur Vysya Bank"), ("J&KBANK", "J&K Bank"),
    ])),
    Sector("banks_psu", "Banks – Public Sector", "Financials", _s([
        ("SBIN", "State Bank of India"), ("BANKBARODA", "Bank of Baroda"), ("PNB", "Punjab National Bank"),
        ("CANBK", "Canara Bank"), ("UNIONBANK", "Union Bank of India"), ("INDIANB", "Indian Bank"),
        ("BANKINDIA", "Bank of India"), ("MAHABANK", "Bank of Maharashtra"), ("CENTRALBK", "Central Bank"),
        ("IOB", "Indian Overseas Bank"), ("UCOBANK", "UCO Bank"), ("PSB", "Punjab & Sind Bank"),
    ])),
    Sector("sfb_mfi", "Small Finance & Microfinance", "Financials", _s([
        ("AUBANK", "AU Small Finance Bank"), ("UJJIVANSFB", "Ujjivan Small Finance Bank"),
        ("EQUITASBNK", "Equitas Small Finance Bank"), ("CREDITACC", "CreditAccess Grameen"),
        ("FUSION", "Fusion Finance"), ("SPANDANA", "Spandana Sphoorty"),
        ("SURYODAY", "Suryoday Small Finance Bank"), ("UTKARSHBNK", "Utkarsh Small Finance Bank"),
    ])),
    Sector("nbfc", "NBFC – Lending & Diversified", "Financials", _s([
        ("BAJFINANCE", "Bajaj Finance"), ("BAJAJFINSV", "Bajaj Finserv"), ("JIOFIN", "Jio Financial"),
        ("CHOLAFIN", "Cholamandalam Investment"), ("SHRIRAMFIN", "Shriram Finance"),
        ("MUTHOOTFIN", "Muthoot Finance"), ("MANAPPURAM", "Manappuram Finance"),
        ("SBICARD", "SBI Cards"), ("LTF", "L&T Finance"), ("PFC", "Power Finance Corp"),
        ("RECLTD", "REC"), ("IREDA", "IREDA"), ("POONAWALLA", "Poonawalla Fincorp"),
        ("ABCAPITAL", "Aditya Birla Capital"),
    ])),
    Sector("housing_finance", "Housing Finance", "Financials", _s([
        ("BAJAJHFL", "Bajaj Housing Finance"), ("LICHSGFIN", "LIC Housing Finance"),
        ("PNBHOUSING", "PNB Housing Finance"), ("CANFINHOME", "Can Fin Homes"), ("HUDCO", "HUDCO"),
        ("AAVAS", "Aavas Financiers"), ("HOMEFIRST", "Home First Finance"), ("APTUS", "Aptus Value Housing"),
        ("REPCOHOME", "Repco Home Finance"), ("INDIASHLTR", "India Shelter Finance"),
    ])),
    Sector("life_insurance", "Life Insurance", "Financials", _s([
        ("LICI", "Life Insurance Corp"), ("HDFCLIFE", "HDFC Life"), ("SBILIFE", "SBI Life"),
        ("ICICIPRULI", "ICICI Prudential Life"), ("MFSL", "Max Financial Services"),
    ])),
    Sector("general_insurance", "General & Health Insurance", "Financials", _s([
        ("ICICIGI", "ICICI Lombard"), ("GICRE", "GIC Re"), ("NIACL", "New India Assurance"),
        ("STARHEALTH", "Star Health Insurance"), ("GODIGIT", "Go Digit General Insurance"),
    ])),
    Sector("amc", "Asset Management", "Financials", _s([
        ("HDFCAMC", "HDFC AMC"), ("NAM-INDIA", "Nippon Life India AMC"), ("UTIAMC", "UTI AMC"),
        ("ABSLAMC", "Aditya Birla Sun Life AMC"), ("360ONE", "360 ONE WAM"),
    ])),
    Sector("capital_markets", "Capital Markets & Exchanges", "Financials", _s([
        ("BSE", "BSE"), ("MCX", "Multi Commodity Exchange"), ("CDSL", "Central Depository (CDSL)"),
        ("ANGELONE", "Angel One"), ("IEX", "Indian Energy Exchange"), ("CAMS", "Computer Age Mgmt (CAMS)"),
        ("KFINTECH", "KFin Technologies"), ("MOTILALOFS", "Motilal Oswal"), ("NUVAMA", "Nuvama Wealth"),
        ("IIFL", "IIFL Finance"),
    ])),
    Sector("fintech_internet", "Fintech, Payments & Internet", "Financials", _s([
        ("ETERNAL", "Eternal (Zomato)"), ("SWIGGY", "Swiggy"), ("NYKAA", "FSN E-Commerce (Nykaa)"),
        ("PAYTM", "One97 (Paytm)"), ("POLICYBZR", "PB Fintech (Policybazaar)"), ("INDIAMART", "IndiaMART"),
        ("CARTRADE", "CarTrade Tech"), ("JUSTDIAL", "Just Dial"), ("MOBIKWIK", "One MobiKwik"),
        ("DELHIVERY", "Delhivery"),
    ])),

    # ===================== INFORMATION TECHNOLOGY (3) =====================
    Sector("it_services", "IT Services & Consulting", "Information Technology", _s([
        ("TCS", "Tata Consultancy Services"), ("INFY", "Infosys"), ("HCLTECH", "HCL Technologies"),
        ("WIPRO", "Wipro"), ("TECHM", "Tech Mahindra"), ("LTM", "LTM (formerly LTIMindtree)"),
        ("MPHASIS", "Mphasis"), ("COFORGE", "Coforge"), ("PERSISTENT", "Persistent Systems"),
        ("LTTS", "L&T Technology Services"), ("KPITTECH", "KPIT Technologies"), ("BSOFT", "Birlasoft"),
        ("CYIENT", "Cyient"), ("SONATSOFTW", "Sonata Software"), ("MASTEK", "Mastek"),
    ])),
    Sector("software_products", "Software Products & Platforms", "Information Technology", _s([
        ("OFSS", "Oracle Financial Services"), ("TATAELXSI", "Tata Elxsi"), ("INTELLECT", "Intellect Design"),
        ("NEWGEN", "Newgen Software"), ("HAPPSTMNDS", "Happiest Minds"), ("RATEGAIN", "RateGain Travel"),
        ("MAPMYINDIA", "C.E. Info (MapmyIndia)"), ("ZAGGLE", "Zaggle Prepaid"), ("NAZARA", "Nazara Technologies"),
        ("ROUTE", "Route Mobile"),
    ])),
    Sector("ems", "Electronics Manufacturing (EMS)", "Information Technology", _s([
        ("DIXON", "Dixon Technologies"), ("KAYNES", "Kaynes Technology"), ("SYRMA", "Syrma SGS Technology"),
        ("AMBER", "Amber Enterprises"), ("CYIENTDLM", "Cyient DLM"), ("AVALON", "Avalon Technologies"),
        ("PGEL", "PG Electroplast"), ("ELIN", "Elin Electronics"),
    ])),

    # ===================== CONSUMER DISCRETIONARY (10) =====================
    Sector("pv", "Passenger Vehicles", "Consumer Discretionary", _s([
        ("MARUTI", "Maruti Suzuki India"), ("M&M", "Mahindra & Mahindra"),
        ("TMPV", "Tata Motors Passenger Vehicles"), ("HYUNDAI", "Hyundai Motor India"),
    ])),
    Sector("two_three_wheelers", "Two & Three Wheelers", "Consumer Discretionary", _s([
        ("BAJAJ-AUTO", "Bajaj Auto"), ("HEROMOTOCO", "Hero MotoCorp"), ("TVSMOTOR", "TVS Motor"),
        ("EICHERMOT", "Eicher Motors (Royal Enfield)"), ("ATHERENERG", "Ather Energy"),
    ])),
    Sector("cv", "Commercial Vehicles", "Consumer Discretionary", _s([
        ("TMCV", "Tata Motors (Commercial Vehicles)"), ("ASHOKLEY", "Ashok Leyland"),
        ("FORCEMOT", "Force Motors"), ("VSTTILLERS", "VST Tillers Tractors"),
    ])),
    Sector("tyres", "Tyres", "Consumer Discretionary", _s([
        ("MRF", "MRF"), ("APOLLOTYRE", "Apollo Tyres"), ("BALKRISIND", "Balkrishna Industries"),
        ("CEATLTD", "CEAT"), ("JKTYRE", "JK Tyre & Industries"), ("GOODYEAR", "Goodyear India"),
    ])),
    Sector("auto_components", "Auto Components", "Consumer Discretionary", _s([
        ("MOTHERSON", "Samvardhana Motherson"), ("BOSCHLTD", "Bosch"), ("BHARATFORG", "Bharat Forge"),
        ("SONACOMS", "Sona BLW Precision"), ("UNOMINDA", "Uno Minda"), ("SCHAEFFLER", "Schaeffler India"),
        ("ENDURANCE", "Endurance Technologies"), ("TIINDIA", "Tube Investments"),
        ("SUNDRMFAST", "Sundram Fasteners"), ("ZFCVINDIA", "ZF Commercial Vehicle"),
    ])),
    Sector("batteries_ev", "Batteries & EV", "Consumer Discretionary", _s([
        ("EXIDEIND", "Exide Industries"), ("ARE&M", "Amara Raja Energy & Mobility"),
        ("HBLENGINE", "HBL Engineering"), ("OLAELEC", "Ola Electric Mobility"),
    ])),
    Sector("consumer_durables", "Consumer Durables & Appliances", "Consumer Discretionary", _s([
        ("HAVELLS", "Havells India"), ("VOLTAS", "Voltas"), ("BLUESTARCO", "Blue Star"),
        ("CROMPTON", "Crompton Greaves Consumer"), ("WHIRLPOOL", "Whirlpool of India"),
        ("VGUARD", "V-Guard Industries"), ("TTKPRESTIG", "TTK Prestige"), ("ORIENTELEC", "Orient Electric"),
        ("BAJAJELEC", "Bajaj Electricals"), ("SYMPHONY", "Symphony"), ("IFBIND", "IFB Industries"),
    ])),
    Sector("footwear", "Footwear", "Consumer Discretionary", _s([
        ("BATAINDIA", "Bata India"), ("RELAXO", "Relaxo Footwears"), ("METROBRAND", "Metro Brands"),
        ("CAMPUS", "Campus Activewear"), ("KHADIM", "Khadim India"),
    ])),
    Sector("jewellery", "Jewellery & Watches", "Consumer Discretionary", _s([
        ("TITAN", "Titan Company"), ("KALYANKJIL", "Kalyan Jewellers"), ("SENCO", "Senco Gold"),
        ("PCJEWELLER", "PC Jeweller"), ("THANGAMAYL", "Thangamayil Jewellery"), ("GOLDIAM", "Goldiam International"),
    ])),
    Sector("retail", "Retail", "Consumer Discretionary", _s([
        ("DMART", "Avenue Supermarts (DMart)"), ("TRENT", "Trent"), ("ABFRL", "Aditya Birla Fashion"),
        ("VMART", "V-Mart Retail"), ("SHOPERSTOP", "Shoppers Stop"), ("MANYAVAR", "Vedant Fashions"),
    ])),

    # ===================== CONSUMER STAPLES (7) =====================
    Sector("packaged_foods", "Packaged Foods", "Consumer Staples", _s([
        ("NESTLEIND", "Nestle India"), ("BRITANNIA", "Britannia Industries"), ("TATACONSUM", "Tata Consumer"),
        ("MARICO", "Marico"), ("PATANJALI", "Patanjali Foods"), ("BIKAJI", "Bikaji Foods"),
        ("HATSUN", "Hatsun Agro Product"), ("ZYDUSWELL", "Zydus Wellness"), ("BECTORFOOD", "Mrs. Bectors Food"),
        ("GOPAL", "Gopal Snacks"),
    ])),
    Sector("beverages", "Beverages", "Consumer Staples", _s([
        ("VBL", "Varun Beverages"), ("TATACONSUM", "Tata Consumer (Tea/Coffee)"), ("CCL", "CCL Products"),
    ])),
    Sector("personal_care", "Personal & Household Care", "Consumer Staples", _s([
        ("HINDUNILVR", "Hindustan Unilever"), ("DABUR", "Dabur India"), ("GODREJCP", "Godrej Consumer"),
        ("COLPAL", "Colgate-Palmolive"), ("EMAMILTD", "Emami"), ("GILLETTE", "Gillette India"),
        ("PGHH", "P&G Hygiene"), ("JYOTHYLAB", "Jyothy Labs"), ("HONASA", "Honasa Consumer (Mamaearth)"),
        ("BAJAJCON", "Bajaj Consumer Care"),
    ])),
    Sector("tobacco", "Tobacco", "Consumer Staples", _s([
        ("ITC", "ITC"), ("VSTIND", "VST Industries"), ("GODFRYPHLP", "Godfrey Phillips India"),
    ])),
    Sector("sugar", "Sugar", "Consumer Staples", _s([
        ("BALRAMCHIN", "Balrampur Chini Mills"), ("TRIVENI", "Triveni Engineering"),
        ("EIDPARRY", "EID Parry"), ("BAJAJHIND", "Bajaj Hindusthan Sugar"), ("DALMIASUG", "Dalmia Bharat Sugar"),
        ("DHAMPURSUG", "Dhampur Sugar Mills"), ("RENUKA", "Shree Renuka Sugars"), ("AVADHSUGAR", "Avadh Sugar & Energy"),
    ])),
    Sector("breweries_distilleries", "Breweries & Distilleries", "Consumer Staples", _s([
        ("UNITDSPR", "United Spirits"), ("UBL", "United Breweries"), ("RADICO", "Radico Khaitan"),
        ("GLOBUSSPR", "Globus Spirits"), ("SDBL", "Som Distilleries"),
    ])),
    Sector("agri_edible_oils", "Agri & Edible Oils", "Consumer Staples", _s([
        ("GODREJAGRO", "Godrej Agrovet"), ("KRBL", "KRBL (India Gate rice)"), ("AWL", "AWL Agri Business"),
        ("KSCL", "Kaveri Seed Company"), ("MANORAMA", "Manorama Industries"), ("KOHINOOR", "Kohinoor Foods"),
    ])),

    # ===================== HEALTHCARE (4) =====================
    Sector("pharma", "Pharmaceuticals", "Healthcare", _s([
        ("SUNPHARMA", "Sun Pharmaceutical"), ("DRREDDY", "Dr. Reddy's Labs"), ("CIPLA", "Cipla"),
        ("DIVISLAB", "Divi's Laboratories"), ("LUPIN", "Lupin"), ("AUROPHARMA", "Aurobindo Pharma"),
        ("ZYDUSLIFE", "Zydus Lifesciences"), ("TORNTPHARM", "Torrent Pharmaceuticals"), ("ALKEM", "Alkem Labs"),
        ("MANKIND", "Mankind Pharma"), ("GLENMARK", "Glenmark Pharma"), ("BIOCON", "Biocon"),
        ("IPCALAB", "IPCA Laboratories"), ("JBCHEPHARM", "JB Chemicals"), ("ABBOTINDIA", "Abbott India"),
        ("AJANTPHARM", "Ajanta Pharma"), ("NATCOPHARM", "Natco Pharma"), ("ERIS", "Eris Lifesciences"),
    ])),
    Sector("hospitals", "Hospitals", "Healthcare", _s([
        ("APOLLOHOSP", "Apollo Hospitals"), ("MAXHEALTH", "Max Healthcare"), ("FORTIS", "Fortis Healthcare"),
        ("NH", "Narayana Hrudayalaya"), ("MEDANTA", "Global Health (Medanta)"), ("KIMS", "Krishna Institute (KIMS)"),
        ("ASTERDM", "Aster DM Healthcare"), ("RAINBOW", "Rainbow Children's Medicare"), ("JLHL", "Jupiter Life Line"),
        ("YATHARTH", "Yatharth Hospital"),
    ])),
    Sector("diagnostics", "Diagnostics", "Healthcare", _s([
        ("LALPATHLAB", "Dr. Lal PathLabs"), ("METROPOLIS", "Metropolis Healthcare"),
        ("VIJAYA", "Vijaya Diagnostic Centre"), ("THYROCARE", "Thyrocare Technologies"), ("KRSNAA", "Krsnaa Diagnostics"),
    ])),
    Sector("crams_cro", "CRAMS & Contract Research", "Healthcare", _s([
        ("SYNGENE", "Syngene International"), ("LAURUSLABS", "Laurus Labs"), ("SUVEN", "Suven Life Sciences"),
        ("NEULANDLAB", "Neuland Laboratories"), ("JUBLPHARMA", "Jubilant Pharmova"), ("GRANULES", "Granules India"),
        ("COHANCE", "Cohance Lifesciences"),
    ])),

    # ===================== ENERGY & UTILITIES (8) =====================
    Sector("oil_ep", "Oil Exploration & Production", "Energy & Utilities", _s([
        ("ONGC", "Oil & Natural Gas Corp"), ("OIL", "Oil India"), ("HINDOILEXP", "Hindustan Oil Exploration"),
    ])),
    Sector("oil_refining", "Oil Refining & Marketing", "Energy & Utilities", _s([
        ("RELIANCE", "Reliance Industries"), ("IOC", "Indian Oil Corp"), ("BPCL", "Bharat Petroleum"),
        ("HINDPETRO", "Hindustan Petroleum"), ("MRPL", "Mangalore Refinery"), ("CHENNPETRO", "Chennai Petroleum"),
    ])),
    Sector("gas_distribution", "Gas Distribution", "Energy & Utilities", _s([
        ("GAIL", "GAIL (India)"), ("GUJENERGY", "Gujarat Energy (fmr Gujarat Gas)"), ("IGL", "Indraprastha Gas"),
        ("MGL", "Mahanagar Gas"), ("ATGL", "Adani Total Gas"), ("GSPL", "Gujarat State Petronet"),
        ("PETRONET", "Petronet LNG"), ("AEGISLOG", "Aegis Logistics"),
    ])),
    Sector("power_generation", "Power Generation", "Energy & Utilities", _s([
        ("NTPC", "NTPC"), ("NHPC", "NHPC"), ("JSWENERGY", "JSW Energy"), ("TATAPOWER", "Tata Power"),
        ("ADANIPOWER", "Adani Power"), ("TORNTPOWER", "Torrent Power"), ("CESC", "CESC"),
        ("SJVN", "SJVN"), ("NLCINDIA", "NLC India"),
    ])),
    Sector("power_tnd", "Power Transmission & Distribution", "Energy & Utilities", _s([
        ("POWERGRID", "Power Grid Corp"), ("ADANIENSOL", "Adani Energy Solutions"), ("IREDA", "IREDA"),
        ("JPPOWER", "Jaiprakash Power Ventures"),
    ])),
    Sector("renewables", "Renewable Energy", "Energy & Utilities", _s([
        ("ADANIGREEN", "Adani Green Energy"), ("NTPCGREEN", "NTPC Green Energy"), ("SUZLON", "Suzlon Energy"),
        ("INOXWIND", "Inox Wind"), ("WAAREEENER", "Waaree Energies"), ("PREMIERENE", "Premier Energies"),
        ("ACMESOLAR", "ACME Solar Holdings"), ("KPIGREEN", "KPI Green Energy"), ("GREENPOWER", "Orient Green Power"),
    ])),
    Sector("coal", "Coal & Consumable Fuels", "Energy & Utilities", _s([
        ("COALINDIA", "Coal India"), ("GMDCLTD", "Gujarat Mineral Development"), ("SANDUMA", "Sandur Manganese"),
    ])),
    Sector("lubricants", "Lubricants", "Energy & Utilities", _s([
        ("CASTROLIND", "Castrol India"), ("GULFOILLUB", "Gulf Oil Lubricants"), ("SOTL", "Savita Oil Technologies"),
    ])),

    # ===================== METALS & MINING (3) =====================
    Sector("iron_steel", "Iron & Steel", "Metals & Mining", _s([
        ("TATASTEEL", "Tata Steel"), ("JSWSTEEL", "JSW Steel"), ("SAIL", "Steel Authority of India"),
        ("JINDALSTEL", "Jindal Steel & Power"), ("JSL", "Jindal Stainless"), ("APLAPOLLO", "APL Apollo Tubes"),
        ("WELCORP", "Welspun Corp"), ("RATNAMANI", "Ratnamani Metals"), ("JTLIND", "JTL Industries"),
        ("SHYAMMETL", "Shyam Metalics"), ("GPIL", "Godawari Power & Ispat"), ("SARDAEN", "Sarda Energy & Minerals"),
    ])),
    Sector("aluminium_nonferrous", "Aluminium & Non-Ferrous", "Metals & Mining", _s([
        ("HINDALCO", "Hindalco Industries"), ("VEDL", "Vedanta"), ("NATIONALUM", "National Aluminium"),
        ("HINDZINC", "Hindustan Zinc"), ("HINDCOPPER", "Hindustan Copper"),
    ])),
    Sector("mining_minerals", "Mining & Minerals", "Metals & Mining", _s([
        ("NMDC", "NMDC"), ("MOIL", "MOIL"), ("GMDCLTD", "Gujarat Mineral Development"),
        ("VEDL", "Vedanta"), ("20MICRONS", "20 Microns"), ("ASHAPURMIN", "Ashapura Minechem"),
    ])),

    # ===================== CHEMICALS (6) =====================
    Sector("specialty_chemicals", "Specialty Chemicals", "Chemicals", _s([
        ("PIDILITIND", "Pidilite Industries"), ("SRF", "SRF"), ("PIIND", "PI Industries"),
        ("AARTIIND", "Aarti Industries"), ("NAVINFLUOR", "Navin Fluorine"), ("DEEPAKNTR", "Deepak Nitrite"),
        ("ATUL", "Atul"), ("VINATIORGA", "Vinati Organics"), ("FLUOROCHEM", "Gujarat Fluorochemicals"),
        ("CLEAN", "Clean Science & Technology"), ("ALKYLAMINE", "Alkyl Amines"), ("LXCHEM", "Laxmi Organic"),
    ])),
    Sector("commodity_chemicals", "Commodity Chemicals", "Chemicals", _s([
        ("TATACHEM", "Tata Chemicals"), ("GNFC", "Gujarat Narmada Valley Fert & Chem"), ("GHCL", "GHCL"),
        ("NOCIL", "NOCIL"), ("DCW", "DCW"), ("ANDHRSUGAR", "Andhra Sugars"),
    ])),
    Sector("fertilizers", "Fertilizers", "Chemicals", _s([
        ("COROMANDEL", "Coromandel International"), ("CHAMBLFERT", "Chambal Fertilisers"), ("GSFC", "Gujarat State Fertilizers"),
        ("RCF", "Rashtriya Chemicals & Fert"), ("NFL", "National Fertilizers"), ("FACT", "Fertilisers & Chemicals Travancore"),
        ("DEEPAKFERT", "Deepak Fertilisers"), ("PARADEEP", "Paradeep Phosphates"), ("MADRASFERT", "Madras Fertilizers"),
    ])),
    Sector("agrochemicals", "Agrochemicals", "Chemicals", _s([
        ("UPL", "UPL"), ("BAYERCROP", "Bayer CropScience"), ("RALLIS", "Rallis India"),
        ("SUMICHEM", "Sumitomo Chemical India"), ("DHANUKA", "Dhanuka Agritech"), ("INSECTICID", "Insecticides India"),
        ("SHARDACROP", "Sharda Cropchem"), ("BASF", "BASF India"),
    ])),
    Sector("paints", "Paints", "Chemicals", _s([
        ("ASIANPAINT", "Asian Paints"), ("BERGEPAINT", "Berger Paints"), ("KANSAINER", "Kansai Nerolac"),
        ("INDIGOPNTS", "Indigo Paints"),
    ])),
    Sector("plastics_packaging", "Plastic Products & Packaging", "Chemicals", _s([
        ("SUPREMEIND", "Supreme Industries"), ("EPL", "EPL"), ("POLYPLEX", "Polyplex Corp"),
        ("COSMOFIRST", "Cosmo First"), ("UFLEX", "UFLEX"), ("JINDALPOLY", "Jindal Poly Films"),
        ("TIMETECHNO", "Time Technoplast"),
    ])),

    # ===================== CONSTRUCTION & MATERIALS (5) =====================
    Sector("cement", "Cement & Cement Products", "Construction & Materials", _s([
        ("ULTRACEMCO", "UltraTech Cement"), ("AMBUJACEM", "Ambuja Cements"), ("ACC", "ACC"),
        ("SHREECEM", "Shree Cement"), ("DALBHARAT", "Dalmia Bharat"), ("JKCEMENT", "JK Cement"),
        ("RAMCOCEM", "The Ramco Cements"), ("JKLAKSHMI", "JK Lakshmi Cement"), ("NUVOCO", "Nuvoco Vistas"),
        ("INDIACEM", "The India Cements"), ("BIRLACORPN", "Birla Corporation"), ("HEIDELBERG", "HeidelbergCement India"),
    ])),
    Sector("building_materials", "Building Materials (Pipes, Tiles, Ply)", "Construction & Materials", _s([
        ("ASTRAL", "Astral"), ("FINPIPE", "Finolex Industries"), ("PRINCEPIPE", "Prince Pipes"),
        ("KAJARIACER", "Kajaria Ceramics"), ("CERA", "Cera Sanitaryware"), ("CENTURYPLY", "Century Plyboards"),
        ("GREENPANEL", "Greenpanel Industries"), ("SUPREMEIND", "Supreme Industries"), ("HINDWAREAP", "Hindware Home Innovation"),
    ])),
    Sector("cables_wires", "Cables & Wires", "Construction & Materials", _s([
        ("POLYCAB", "Polycab India"), ("KEI", "KEI Industries"), ("RRKABEL", "R R Kabel"),
        ("FINCABLES", "Finolex Cables"), ("APARINDS", "Apar Industries"), ("UNIVCABLES", "Universal Cables"),
    ])),
    Sector("realty", "Real Estate", "Construction & Materials", _s([
        ("DLF", "DLF"), ("LODHA", "Macrotech Developers (Lodha)"), ("GODREJPROP", "Godrej Properties"),
        ("OBEROIRLTY", "Oberoi Realty"), ("PRESTIGE", "Prestige Estates"), ("PHOENIXLTD", "Phoenix Mills"),
        ("BRIGADE", "Brigade Enterprises"), ("SOBHA", "Sobha"), ("ANANTRAJ", "Anant Raj"),
        ("SIGNATURE", "Signatureglobal"), ("MAHLIFE", "Mahindra Lifespace"), ("SUNTECK", "Sunteck Realty"),
    ])),
    Sector("construction_epc", "Construction & Engineering (EPC)", "Construction & Materials", _s([
        ("LT", "Larsen & Toubro"), ("KEC", "KEC International"),
        ("KPIL", "Kalpataru Projects Intl"), ("IRB", "IRB Infrastructure"), ("NCC", "NCC"),
        ("HGINFRA", "H.G. Infra Engineering"), ("PNCINFRA", "PNC Infratech"), ("GRINFRA", "G R Infraprojects"),
        ("RITES", "RITES"), ("ENGINERSIN", "Engineers India"),
    ])),

    # ===================== INDUSTRIALS (7) =====================
    Sector("capital_goods", "Capital Goods & Electrical Equipment", "Industrials", _s([
        ("ABB", "ABB India"), ("SIEMENS", "Siemens"), ("BHEL", "Bharat Heavy Electricals"),
        ("CGPOWER", "CG Power & Industrial"), ("THERMAX", "Thermax"), ("POWERINDIA", "Hitachi Energy India"),
        ("TRITURBINE", "Triveni Turbine"), ("KIRLOSENG", "Kirloskar Oil Engines"), ("GVT&D", "GE Vernova T&D India"),
        ("APARINDS", "Apar Industries"),
    ])),
    Sector("industrial_machinery", "Industrial Machinery & Bearings", "Industrials", _s([
        ("SKFINDIA", "SKF India"), ("SCHAEFFLER", "Schaeffler India"), ("TIMKEN", "Timken India"),
        ("GRINDWELL", "Grindwell Norton"), ("CARBORUNIV", "Carborundum Universal"), ("AIAENG", "AIA Engineering"),
        ("LMW", "Lakshmi Machine Works"), ("ELGIEQUIP", "Elgi Equipments"), ("KSB", "KSB"),
    ])),
    Sector("defence", "Defence", "Industrials", _s([
        ("HAL", "Hindustan Aeronautics"), ("BEL", "Bharat Electronics"), ("BDL", "Bharat Dynamics"),
        ("MAZDOCK", "Mazagon Dock Shipbuilders"), ("COCHINSHIP", "Cochin Shipyard"), ("GRSE", "Garden Reach Shipbuilders"),
        ("DATAPATTNS", "Data Patterns"), ("SOLARINDS", "Solar Industries"), ("ZENTEC", "Zen Technologies"),
        ("PARAS", "Paras Defence"), ("IDEAFORGE", "ideaForge Technology"),
    ])),
    Sector("railways", "Railways", "Industrials", _s([
        ("RVNL", "Rail Vikas Nigam"), ("IRCTC", "IRCTC"), ("IRFC", "Indian Railway Finance Corp"),
        ("IRCON", "Ircon International"), ("TITAGARH", "Titagarh Rail Systems"), ("RAILTEL", "RailTel Corp"),
        ("JWL", "Jupiter Wagons"), ("TEXRAIL", "Texmaco Rail"), ("RITES", "RITES"),
    ])),
    Sector("ports_marine", "Ports & Marine", "Industrials", _s([
        ("ADANIPORTS", "Adani Ports & SEZ"), ("JSWINFRA", "JSW Infrastructure"), ("GPPL", "Gujarat Pipavav Port"),
    ])),
    Sector("logistics", "Logistics & Distribution", "Industrials", _s([
        ("CONCOR", "Container Corp of India"), ("DELHIVERY", "Delhivery"), ("BLUEDART", "Blue Dart Express"),
        ("TCIEXP", "TCI Express"), ("VRLLOG", "VRL Logistics"), ("MAHLOG", "Mahindra Logistics"),
        ("ALLCARGO", "Allcargo Logistics"), ("TCI", "Transport Corp of India"),
    ])),
    Sector("aviation", "Aviation & Airports", "Industrials", _s([
        ("INDIGO", "InterGlobe Aviation (IndiGo)"), ("SPICEJET", "SpiceJet"), ("GMRAIRPORT", "GMR Airports"),
    ])),

    # ===================== TELECOM, MEDIA & HOSPITALITY (4) =====================
    Sector("telecom_services", "Telecom Services", "Telecom, Media & Hospitality", _s([
        ("BHARTIARTL", "Bharti Airtel"), ("IDEA", "Vodafone Idea"), ("TATACOMM", "Tata Communications"),
        ("MTNL", "MTNL"), ("BHARTIHEXA", "Bharti Hexacom"),
    ])),
    Sector("telecom_equipment", "Telecom Equipment & Infrastructure", "Telecom, Media & Hospitality", _s([
        ("INDUSTOWER", "Indus Towers"), ("HFCL", "HFCL"), ("STLTECH", "Sterlite Technologies"),
        ("TEJASNET", "Tejas Networks"), ("ITI", "ITI"),
    ])),
    Sector("media", "Media & Entertainment", "Telecom, Media & Hospitality", _s([
        ("ZEEL", "Zee Entertainment"), ("SUNTV", "Sun TV Network"), ("PVRINOX", "PVR INOX"),
        ("SAREGAMA", "Saregama India"), ("NAZARA", "Nazara Technologies"), ("NETWORK18", "Network18 Media"),
        ("DBCORP", "D.B. Corp"), ("JAGRAN", "Jagran Prakashan"), ("TIPSMUSIC", "Tips Music"),
        ("HATHWAY", "Hathway Cable"),
    ])),
    Sector("hotels_tourism", "Hotels & Tourism", "Telecom, Media & Hospitality", _s([
        ("INDHOTEL", "Indian Hotels (Taj)"), ("EIHOTEL", "EIH (Oberoi)"), ("CHALET", "Chalet Hotels"),
        ("LEMONTREE", "Lemon Tree Hotels"), ("ITCHOTELS", "ITC Hotels"), ("MHRIL", "Mahindra Holidays"),
        ("TAJGVK", "TAJGVK Hotels"), ("ORIENTHOT", "Oriental Hotels"), ("WONDERLA", "Wonderla Holidays"),
    ])),

    # ===================== DIVERSIFIED & OTHERS (5) =====================
    Sector("textiles", "Textiles & Apparel", "Diversified & Others", _s([
        ("PAGEIND", "Page Industries"), ("KPRMILL", "K.P.R. Mill"), ("TRIDENT", "Trident"),
        ("WELSPUNLIV", "Welspun Living"), ("VTL", "Vardhman Textiles"), ("ARVIND", "Arvind"),
        ("GOKEX", "Gokaldas Exports"), ("RAYMOND", "Raymond"), ("ALOKINDS", "Alok Industries"),
    ])),
    Sector("paper", "Paper & Forest Products", "Diversified & Others", _s([
        ("JKPAPER", "JK Paper"), ("WSTCSTPAPR", "West Coast Paper Mills"), ("SESHAPAPER", "Seshasayee Paper"),
        ("ANDHRAPAP", "Andhra Paper"), ("EMAMIPAP", "Emami Paper Mills"), ("STARPAPER", "Star Paper Mills"),
    ])),
    Sector("conglomerates", "Diversified / Conglomerates", "Diversified & Others", _s([
        ("RELIANCE", "Reliance Industries"), ("ADANIENT", "Adani Enterprises"), ("GRASIM", "Grasim Industries"),
        ("ITC", "ITC"), ("DCMSHRIRAM", "DCM Shriram"), ("3MINDIA", "3M India"),
        ("BALMLAWRIE", "Balmer Lawrie"), ("SIEMENS", "Siemens"),
    ])),
    Sector("shipping", "Shipping", "Diversified & Others", _s([
        ("GESHIP", "Great Eastern Shipping"), ("SCI", "Shipping Corp of India"), ("SEAMECLTD", "Seamec"),
    ])),
    Sector("restaurants_qsr", "Restaurants & QSR", "Diversified & Others", _s([
        ("JUBLFOOD", "Jubilant FoodWorks (Domino's)"), ("DEVYANI", "Devyani International (KFC/Pizza Hut)"),
        ("SAPPHIRE", "Sapphire Foods"), ("WESTLIFE", "Westlife Foodworld (McDonald's)"),
        ("RBA", "Restaurant Brands Asia (Burger King)"), ("SPECIALITY", "Speciality Restaurants"),
    ])),
]


def all_sectors() -> "list[Sector]":
    return SECTORS


def unique_symbols() -> "list[str]":
    seen = {}
    for sec in SECTORS:
        for st in sec.stocks:
            seen.setdefault(st.symbol, st)
    return sorted(seen)


def stock_index():
    idx = {}
    for sec in SECTORS:
        for st in sec.stocks:
            idx.setdefault(st.symbol, st)
    return idx
