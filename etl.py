"""
ETL layer — Moisturisers Interactive Dashboard
==============================================
Loads either
  (a) a JOURNEY-wide CSV (same shape as 'Sheet22': one row per customer,
      first..sixth purchased sku/date columns), or
  (b) a RAW order-level CSV (one row per order line: customer, date, sku, city)
and produces a tidy LONG table: one row per (customer, order, item).

Every SKU short-code decodes as  FC-<LINE>-<VARIANT>-<SIZE>
  LINE : CWDM / HDDM / HHDM / DM  -> Face Malai  (Cold Winter / Hot Dry /
                                       Hot Humid / Non-seasonal concern)
         AC                        -> Active Gel
         HG                        -> Aloe Vera Gel
  SIZE : 030 -> 30g, 040 -> 40g, 050 -> 50g, 080 -> 80g
"""

from __future__ import annotations

import re
from io import BytesIO

import pandas as pd

# ----------------------------------------------------------------------------- 
# Reference tables
# -----------------------------------------------------------------------------
LINE_MAP = {
    "CWDM": ("Face Malai", "Cold Winter"),
    "HDDM": ("Face Malai", "Hot Dry"),
    "HHDM": ("Face Malai", "Hot Humid"),
    "DM":   ("Face Malai", "Non-Seasonal (Concern)"),
    "AC":   ("Active Gel", "Gel"),
    "HG":   ("Aloe Vera Gel", "Gel"),
}

VARIANT_MAP = {
    # Face Malai — Cold Winter line
    "FW":  "Flax Walnut",           "TP": "Tomato Patchouli",
    # Face Malai — Hot Dry line
    "FB":  "Flax Bakuchi",          "TR": "Tomato Rosehip",     "PT":  "Pomegranate Tulsi",
    # Face Malai — Hot Humid line
    "FC":  "Flax Carrot",           "TV": "Tomato Vetiver",     "GAT": "GreenApple Tulsi",
    # Face Malai — concern / non-seasonal line
    "PG":  "Turmeric Nutmeg",       "NR": "Cocoa Mogra",
    "DP":  "Honey Multi-Nut",       "AA": "Clove Tea-Tree",
    # Active Gels
    "NT":  "Neem TeaTree",          "AC": "Aloe Cactus Hydra Lift",
    "OV":  "Olive Vit-E Night",     "OK":  "Orange Kiwi Vit-C",
    # Aloe Vera Gel
    "PA":  "Aloe Vera",
}

# 'BT' is ambiguous: Winter Blackseed in the CWDM line, Beetroot Tomato in AC
LINE_VARIANT_OVERRIDE = {("CWDM", "BT"): "Winter Blackseed",
                         ("AC", "BT"): "Beetroot Tomato Vit-A"}
VARIANT_KEY_OVERRIDES = {("CWDM", "BT"): "Winter Blackseed Tulsi (Cold)"}

# Human-readable "Variant Key" (matches the Summary Sheet naming)
VARIANT_KEY_MAP = {
    "Flax Walnut": "Flax Walnut (Cold)",
    "Tomato Patchouli": "Tomato Patchouli (Cold)",
    "Winter Blackseed": "Winter Blackseed Tulsi (Cold)",
    "Flax Bakuchi": "Flax Bakuchi (Hot Dry)",
    "Tomato Rosehip": "Tomato Rosehip (Hot Dry)",
    "Pomegranate Tulsi": "Pomegranate Tulsi (Hot Dry)",
    "Flax Carrot": "Flax Carrot (Hot Humid)",
    "Tomato Vetiver": "Tomato Vetiver (Hot Humid)",
    "GreenApple Tulsi": "GreenApple Tulsi (Hot Humid)",
    "Turmeric Nutmeg": "Turmeric Nutmeg (Pigmentation)",
    "Cocoa Mogra": "Cocoa Mogra (Overnight)",
    "Honey Multi-Nut": "Honey Multi-Nut (Dry & Peeling)",
    "Clove Tea-Tree": "Clove Tea-Tree (Anti-Acne)",
}

SIZE_MAP = {"030": 30, "040": 40, "050": 50, "080": 80}

SKU_RE = re.compile(r"^FC-([A-Z]+)-([A-Z0-9]+)-(\d{3})$")

# Purchase-timing seasons (calendar month of the order)
TIMING_SEASON = {
    12: "Cold Winter (Dec-Feb)", 1: "Cold Winter (Dec-Feb)", 2: "Cold Winter (Dec-Feb)",
    3: "Hot Dry (Mar-May)", 4: "Hot Dry (Mar-May)", 5: "Hot Dry (Mar-May)",
    6: "Hot Humid (Jun-Sep)", 7: "Hot Humid (Jun-Sep)", 8: "Hot Humid (Jun-Sep)",
    9: "Hot Humid (Jun-Sep)",
    10: "Post-Monsoon (Oct-Nov)", 11: "Post-Monsoon (Oct-Nov)",
}
TIMING_SEASON_ORDER = ["Cold Winter (Dec-Feb)", "Hot Dry (Mar-May)",
                       "Hot Humid (Jun-Sep)", "Post-Monsoon (Oct-Nov)"]

# Intended-season buckets used by the dashboard tiles
INTENDED_BUCKETS = ["Cold Winter", "Hot Dry", "Hot Humid", "Non-Seasonal (Concern)"]

# Geo region mapping (extend freely)
REGION_MAP = {
    # North
    "new delhi": "North", "delhi": "North", "gurgaon": "North", "gurugram": "North",
    "noida": "North", "gautam buddha nagar": "North", "ghaziabad": "North",
    "faridabad": "North", "greater noida": "North", "jaipur": "North",
    "lucknow": "North", "kanpur": "North", "chandigarh": "North", "mohali": "North",
    "panchkula": "North", "ludhiana": "North", "amritsar": "North", "jammu": "North",
    "dehradun": "North", "varanasi": "North", "prayagraj": "North", "agra": "North",
    "meerut": "North", "sonepat": "North", "panipat": "North", "karnal": "North",
    "jind": "North", "hisar": "North", "rewari": "North", "bahadurgarh": "North",
    "rohtak": "North", "shimla": "North", "srinagar": "North", "bareilly": "North",
    "moradabad": "North", "aligarh": "North", "jodhpur": "North", "udaipur": "North",
    "kota": "North", "ajmer": "North", "bhopal": "North", "indore": "North",
    "gwalior": "North", "jabalpur": "North", "raipur": "North",
    # West
    "mumbai": "West", "thane": "West", "navi mumbai": "West", "pune": "West",
    "nahsik": "West", "nashik": "West", "nagpur": "West", "aurangabad": "West",
    "ahmedabad": "West", "surat": "West", "vadodara": "West", "rajkot": "West",
    "gandhinagar": "West", "bhavnagar": "West", "anand": "West", "valsad": "West",
    "navsari": "West", "silvassa": "West",
    # South
    "bengaluru": "South", "bangalore": "South", "mysuru": "South", "mysore": "South",
    "mangaluru": "South", "mangalore": "South", "hubballi": "South", "hubli": "South",
    "belgaum": "South", "chennai": "South", "coimbatore": "South", "madurai": "South",
    "tiruchirappalli": "South", "salem": "South", "tirunelveli": "South",
    "hyderabad": "South", "secunderabad": "South", "warangal": "South",
    "vizag": "South", "visakhapatnam": "South", "vijayawada": "South",
    "guntur": "South", "tirupati": "South",
    "kochi": "South", "ernakulam": "South", "kozhikode": "South",
    "thiruvananthapuram": "South", "thrissur": "South", "kollam": "South",
    "irinjalakuda": "South", "pollachi": "South", "palakkad": "South",
    "kannur": "South", "kottayam": "South", "pathanamthitta": "South",
    # East
    "kolkata": "East", "howrah": "East", "salt lake": "East",
    "bhubaneswar": "East", "cuttack": "East", "rourkela": "East",
    "patna": "East", "muzaffarpur": "East", "bhagalpur": "East",
    "ranchi": "East", "jamshedpur": "East", "dhanbad": "East",
    "guwahati": "East", "shillong": "East", "siliguri": "East",
    "asansol": "East", "durgapur": "East", "kharagpur": "East",
}

WIDE_SLOTS = ["first", "second", "third", "fourth", "fifth", "sixth"]
GAP_COLS = ["days_between_1st_and_2nd", "days_between_2nd_and_3rd",
            "days_between_3rd_and_4th", "days_between_4th_and_5th",
            "days_between_5th_and_6th"]


def region_of(city: str) -> str:
    if not isinstance(city, str) or not city.strip():
        return "Unknown"
    return REGION_MAP.get(city.strip().lower(), "Rest of India")


# -----------------------------------------------------------------------------
# SKU decoding
# -----------------------------------------------------------------------------
def parse_sku_code(token: str) -> dict | None:
    """FC-DM-PG-050 -> dict(category, variant, size_g, sku_key, intended_season)."""
    t = token.strip().upper()
    m = SKU_RE.match(t)
    if not m:
        return None
    line, vcode, size = m.groups()
    if line not in LINE_MAP or size not in SIZE_MAP:
        return None
    variant = LINE_VARIANT_OVERRIDE.get((line, vcode)) or VARIANT_MAP.get(vcode)
    if variant is None:
        return None
    category, intended = LINE_MAP[line]
    g = SIZE_MAP[size]
    if category == "Aloe Vera Gel":
        sku_key = f"Aloe Vera Gel {g}g"
    else:
        sku_key = f"{variant} {g}g"
    vkey = VARIANT_KEY_OVERRIDES.get((line, vcode)) or VARIANT_KEY_MAP.get(variant, variant)
    return {"sku_code": t, "category": category, "variant": variant,
            "size_g": g, "sku_key": sku_key, "intended_season": intended,
            "variant_key": vkey}

# Fallback: parse human-readable names e.g.
#   "Turmeric Nutmeg (Pigmentation)  Face Malai - 50g", "Active Orange Kiwi Vit-C Gel",
#   "Aloe Vera Gel - 40 gms", "Flax Walnut (Cold) 35+ Face Malai"
_NAME_PATTERNS = [
    ("Turmeric Nutmeg", "Face Malai", "Non-Seasonal (Concern)"),
    ("Cocoa Mogra", "Face Malai", "Non-Seasonal (Concern)"),
    ("Honey Multi-Nut", "Face Malai", "Non-Seasonal (Concern)"),
    ("Clove Tea-Tree", "Face Malai", "Non-Seasonal (Concern)"),
    ("Flax Walnut", "Face Malai", "Cold Winter"),
    ("Tomato Patchouli", "Face Malai", "Cold Winter"),
    ("Winter Blackseed", "Face Malai", "Cold Winter"),
    ("Flax Bakuchi", "Face Malai", "Hot Dry"),
    ("Tomato Rosehip", "Face Malai", "Hot Dry"),
    ("Pomegranate Tulsi", "Face Malai", "Hot Dry"),
    ("Flax Carrot", "Face Malai", "Hot Humid"),
    ("Tomato Vetiver", "Face Malai", "Hot Humid"),
    ("GreenApple Tulsi", "Face Malai", "Hot Humid"),
    ("Neem TeaTree", "Active Gel", "Gel"),
    ("Aloe Cactus", "Active Gel", "Gel"),
    ("Olive Vit-E", "Active Gel", "Gel"),
    ("Beetroot Tomato", "Active Gel", "Gel"),
    ("Orange Kiwi", "Active Gel", "Gel"),
]


def parse_sku_name(token: str) -> dict | None:
    t = token.strip()
    tl = t.lower()
    variant = category = intended = None
    for pat, cat, season in _NAME_PATTERNS:
        if pat.lower() in tl:
            variant, category, intended = pat, cat, season
            break
    if variant is None:
        if "aloe vera gel" in tl:
            variant, category, intended = "Aloe Vera", "Aloe Vera Gel", "Gel"
        else:
            return None
    m = re.search(r"(\d{2})\s*g", tl)
    g = int(m.group(1)) if m else (40 if category == "Aloe Vera Gel" and "80" not in tl else 50)
    if category == "Aloe Vera Gel" and "80" in tl:
        g = 80
    sku_key = f"Aloe Vera Gel {g}g" if category == "Aloe Vera Gel" else f"{variant} {g}g"
    return {"sku_code": None, "category": category, "variant": variant,
            "size_g": g, "sku_key": sku_key, "intended_season": intended,
            "variant_key": VARIANT_KEY_MAP.get(variant, variant)}


def parse_item_list(cell: str, fallback_cell: str | None = None) -> list[dict]:
    """Parse a comma-joined cell of SKU codes; fall back to human names."""
    items = []
    if isinstance(cell, str) and cell.strip():
        for tok in cell.split(","):
            p = parse_sku_code(tok)
            if p:
                items.append(p)
    if not items and isinstance(fallback_cell, str) and fallback_cell.strip():
        for tok in fallback_cell.split(","):
            p = parse_sku_name(tok)
            if p:
                items.append(p)
    return items


def _to_date(s):
    if pd.isna(s):
        return pd.NaT
    if isinstance(s, (pd.Timestamp,)):
        return s
    txt = str(s).strip()
    for fmt in ("%b %d, %Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return pd.Timestamp(pd.to_datetime(txt, format=fmt))
        except (ValueError, TypeError):
            continue
    try:
        return pd.Timestamp(pd.to_datetime(txt, errors="raise"))
    except (ValueError, TypeError):
        return pd.NaT


# -----------------------------------------------------------------------------
# Loaders
# -----------------------------------------------------------------------------
def load_journey_csv(source) -> pd.DataFrame:
    """Sheet22-shaped wide journey CSV -> long orders table (one row per item)."""
    df = pd.read_csv(source)
    df.columns = [c.strip() for c in df.columns]
    rows = []
    for _, r in df.iterrows():
        cust = r.get("Name")
        city = str(r.get("city", "")).strip() if pd.notna(r.get("city")) else ""
        for i, slot in enumerate(WIDE_SLOTS, start=1):
            date = _to_date(r.get(f"{slot}_order_date"))
            if pd.isna(date):
                continue
            items = parse_item_list(r.get(f"{slot}_purchased_sku"),
                                    r.get(f"{slot}_purchased_short_code"))
            if not items:
                continue
            for j, it in enumerate(items, start=1):
                rows.append({
                    "customer": cust, "order_seq": i, "order_date": date,
                    "city": city, "region": region_of(city), "item_seq": j, **it,
                })
    return _finalize(pd.DataFrame(rows))


def load_raw_csv(source) -> pd.DataFrame:
    """Raw order-level CSV -> long table. Auto-detects column names."""
    df = pd.read_csv(source)
    df.columns = [c.strip() for c in df.columns]
    low = {c.lower().strip(): c for c in df.columns}

    def find(*cands):
        for c in cands:
            for k, orig in low.items():
                if k == c or k.startswith(c):
                    return orig
        return None

    cust_c = find("name", "customer", "customer_id", "customer_name", "email",
                  "phone", "user", "buyer")
    date_c = find("order_date", "date", "created", "month-year", "month_year", "purchase")
    sku_c = find("sku", "variant", "product", "item", "short_code", "code", "title")
    city_c = find("city", "geo", "region", "shipping_city", "town")
    missing = [lbl for lbl, c in [("customer", cust_c), ("date", date_c), ("sku/item", sku_c)] if not c]
    if missing:
        raise ValueError(
            f"Could not detect column(s) {missing}. Found columns: {list(df.columns)}. "
            "Rename your columns to include a customer id, an order date and a SKU/variant column."
        )

    # order id (optional but exact): keeps same-day separate orders distinct
    order_c = find("order_id", "order no", "order_no", "order number",
                   "order name", "order_name", "invoice", "transaction")

    df = df.rename(columns={cust_c: "customer", date_c: "order_date",
                            sku_c: "sku_cell", city_c: "city",
                            order_c: "order_id"} if order_c else
                   {cust_c: "customer", date_c: "order_date",
                    sku_c: "sku_cell", city_c: "city"})
    df["order_date"] = df["order_date"].apply(_to_date)
    df = df[df["order_date"].notna() & df["customer"].notna()].copy()
    df["city"] = df.get("city", pd.Series(index=df.index, dtype="object"))
    df["city"] = df["city"].apply(lambda x: str(x).strip() if pd.notna(x) else "")

    # fallback description column = same cell (names will be parsed if codes fail)
    if "sku_cell" in df:
        df["desc_cell"] = df["sku_cell"]

    if "order_id" in df.columns and df["order_id"].notna().any():
        grp_key = ["customer", "order_id"]
    else:
        grp_key = ["customer", "order_date"]

    recs = []
    seq_counter: dict = {}
    df = df.sort_values(["customer", "order_date"], kind="stable")
    for key, grp in df.groupby(grp_key, sort=False):
        cust, date = grp["customer"].iloc[0], grp["order_date"].iloc[0]
        items = []
        for _, r in grp.iterrows():
            items.extend(parse_item_list(r.get("sku_cell"), r.get("desc_cell")))
        if not items:
            continue
        seq_counter[cust] = seq_counter.get(cust, 0) + 1
        city = grp["city"].mode().iloc[0] if len(grp) else ""
        for j, it in enumerate(items, start=1):
            recs.append({"customer": cust, "order_seq": seq_counter[cust],
                         "order_date": date, "city": city,
                         "region": region_of(city), "item_seq": j, **it})
    out = pd.DataFrame(recs)
    return _finalize(out)


def load_any(source) -> tuple[pd.DataFrame, str]:
    """Auto-detect wide-journey vs raw order-level and load."""
    head = source if isinstance(source, str) else BytesIO(source.read())
    probe = pd.read_csv(head, nrows=5)
    probe_cols = {c.strip().lower() for c in probe.columns}
    source = source if isinstance(source, str) else BytesIO(source.getvalue())
    if "first_purchased_sku" in probe_cols or "first_order_date" in probe_cols:
        return load_journey_csv(source), "journey (wide) file detected"
    return load_raw_csv(source), "raw order-level file detected"


def _finalize(long_df: pd.DataFrame) -> pd.DataFrame:
    """Add derived fields: month, timing season, journey depth, gaps."""
    if long_df.empty:
        long_df["month"] = pd.Series(dtype="period[M]")
        return long_df
    long_df = long_df.sort_values(["customer", "order_date", "item_seq"]).reset_index(drop=True)
    long_df["order_date"] = pd.to_datetime(long_df["order_date"])
    long_df["month"] = long_df["order_date"].dt.to_period("M").astype(str)
    long_df["timing_season"] = long_df["order_date"].dt.month.map(TIMING_SEASON)
    long_df["timing_bucket"] = pd.Categorical(long_df["timing_season"],
                                              categories=TIMING_SEASON_ORDER, ordered=True)
    depth = long_df.groupby("customer")["order_seq"].max().rename("journey_depth")
    long_df = long_df.merge(depth, on="customer", how="left")
    long_df["is_repeat_buyer"] = (long_df["journey_depth"] >= 2).astype(int)
    # days between consecutive orders
    dates = long_df[["customer", "order_seq", "order_date"]].drop_duplicates(
        ["customer", "order_seq"])
    dates["gap_days"] = dates.groupby("customer")["order_date"].diff().dt.days
    long_df = long_df.merge(dates[["customer", "order_seq", "gap_days"]],
                            on=["customer", "order_seq"], how="left")
    return long_df


def journey_wide(long_df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild the Sheet22-style wide table from the long table (display/export)."""
    if long_df.empty:
        return pd.DataFrame()

    meta = long_df.groupby("customer", sort=False).agg(
        City=("city", "first"), Region=("region", "first"),
        EntryMonth=("month", "first"), Depth=("journey_depth", "first"))

    items = (long_df.sort_values("item_seq")
             .groupby(["customer", "order_seq"], sort=False)["sku_key"]
             .agg(", ".join).rename("skus"))
    orders = long_df.drop_duplicates(["customer", "order_seq"])[
        ["customer", "order_seq", "order_date", "gap_days"]]
    w = orders.join(items, on=["customer", "order_seq"])

    parts = []
    for i in range(1, 7):
        wi = w[w["order_seq"] == i].set_index("customer")
        parts.append(pd.DataFrame({
            f"Order {i} SKUs": wi["skus"],
            f"Order {i} Date": wi["order_date"].dt.strftime("%d %b %Y"),
            f"Gap {i-1}→{i} (d)": wi["gap_days"],
        }, index=wi.index))
    out = meta.copy()
    for p in parts:
        out = out.join(p)
    out.insert(0, "Journey Depth", out.pop("Depth").astype(int))
    out.insert(0, "Is Repeat?", (out["Journey Depth"] >= 2).astype(int))
    out = out.reset_index().rename(columns={"customer": "Customer", "EntryMonth": "Entry Month"})
    return out.sort_values("Customer", key=lambda s: s.astype(str))
