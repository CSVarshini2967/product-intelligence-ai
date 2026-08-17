"""
Module 2 -- Cleaning & Text Normalization.
Responsibility: Deterministic text cleanup, abbreviation expansion, UOM formatting,
and vendor/manufacturer name canonicalization.
"""
import re
from typing import List, Dict, Any

# Known vendor name mappings: Map raw Part_Manuf strings to canonical Manufacturer & Brand
VENDOR_CANONICAL_MAP = {
    "Freud Inc (2435)": {"manufacturer": "Freud Inc", "brand": "Diablo"},
    "Jam Industrial Supply LLC (JAMIN)": {"manufacturer": "3M / Jam Industrial Supply", "brand": "3M"},
    "Mirka Abrasives Inc (MIRUS)": {"manufacturer": "Mirka Abrasives Inc", "brand": "Mirka"},
    "Milwaukee Accessory (4031)": {"manufacturer": "Milwaukee Electric Tool Corp", "brand": "Milwaukee"},
    "3 M Co (5293)": {"manufacturer": "3M Company", "brand": "3M"},
    "Emseal Joint Systems Ltd (EMSJO)": {"manufacturer": "Emseal Joint Systems Ltd", "brand": "Emseal"},
    "Appliance Dealers Cooperative (APPDE)": {"manufacturer": "Appliance Dealers Cooperative", "brand": ""},
    "V & V Appliance Parts Inc (VVAPP)": {"manufacturer": "V & V Appliance Parts Inc", "brand": ""},
    "Wera Tools NA Inc (WERTO)": {"manufacturer": "Wera Tools NA Inc", "brand": "Wera"},
    "Rees Cast Stone Company (REECA)": {"manufacturer": "Rees Cast Stone Company", "brand": ""},
    "U S Lumber (3073)": {"manufacturer": "Trex / US Lumber", "brand": "TREX"},
    "Boise Cascade Building Materials (BOICA)": {"manufacturer": "Boise Cascade Building Materials", "brand": "TREX"},
    "Parksite (6151)": {"manufacturer": "TimberTech / Parksite", "brand": "TIMBERTECH"},
    "Palmer Donavin Mfg Company (PALDO)": {"manufacturer": "Palmer Donavin Mfg Company", "brand": ""},
    "A J Manufacturing Inc (AJMAN)": {"manufacturer": "A J Manufacturing Inc", "brand": "AJM"},
    "United Window & Door Manufacturing (UNIWI)": {"manufacturer": "United Window & Door", "brand": "United Window & Door"},
    "Velux America Inc (VELAM)": {"manufacturer": "Velux America Inc", "brand": "Velux"},
    "ProVia (PRODO)": {"manufacturer": "ProVia", "brand": "PROVIA"},
    "Certainteed Gypsum (2765)": {"manufacturer": "CertainTeed Gypsum", "brand": "CertainTeed"},
    "Hager Hinge Co (4189)": {"manufacturer": "Hager Hinge Co", "brand": "Hager"},
    "Huber Eng Wood LLC (3158)": {"manufacturer": "Huber Engineered Woods", "brand": "Huber Zip"},
    "Westwood Lumber Sales (WESLU)": {"manufacturer": "Westwood Lumber Sales", "brand": ""},
    "Premier Metals (PREME)": {"manufacturer": "Premier Metals", "brand": "Premier Rib"},
    "JamesHardie": {"manufacturer": "James Hardie Building Products", "brand": "James Hardie"},
    "LP SMARTSIDE": {"manufacturer": "LP Building Solutions", "brand": "LP SmartSide"},
    "MillerTech Energy Solutions (MILTE)": {"manufacturer": "MillerTech Energy Solutions", "brand": "MillerTech"},
    "Metalmark Industrial Inc (METIN)": {"manufacturer": "Metalmark Industrial Inc", "brand": "StealthMounts"},
    "Southwire/g Turner (6603)": {"manufacturer": "Southwire Company", "brand": "Southwire"},
    "Thomas & Betts (7405)": {"manufacturer": "Thomas & Betts / ABB", "brand": "Carlon"},
    "Cooper Wiring Devices (3560)": {"manufacturer": "Cooper Wiring Devices / Eaton", "brand": "Cooper"},
    "Fenton Bros Electric Inc (FENBR)": {"manufacturer": "Fenton Bros Electric Inc", "brand": "Lutron"},
    "Leviton Mfg Co (4927)": {"manufacturer": "Leviton Mfg Co", "brand": "Leviton"},
    "Prime Wire & Cable (3562)": {"manufacturer": "Prime Wire & Cable", "brand": "Prime"},
    "Satco Prod Inc (5573)": {"manufacturer": "Satco Products Inc", "brand": "Satco"},
    "Kichler Lighting (KICLI)": {"manufacturer": "Kichler Lighting", "brand": "Kichler"},
    "Cooper Lighting (7638)": {"manufacturer": "Cooper Lighting Solutions", "brand": "Halo / Cooper"},
    "Lithonia Lighting (2776)": {"manufacturer": "Lithonia Lighting / Acuity", "brand": "Lithonia"},
    "Feit Electric (3468)": {"manufacturer": "Feit Electric", "brand": "Feit Electric"},
    "Phillips Lighting (5831)": {"manufacturer": "Philips Lighting / Signify", "brand": "Philips"},
    "Keystone (5702)": {"manufacturer": "Keystone Technologies", "brand": "GT-Lite"},
    "Black & Decker/dewlt (2585)": {"manufacturer": "Stanley Black & Decker / DEWALT", "brand": "DEWALT"},
    "Streamlight (7277)": {"manufacturer": "Streamlight Inc", "brand": "Streamlight"},
    "ACG Brands (1154)": {"manufacturer": "ACG Brands / NEBO", "brand": "NEBO"},
    "Police Security (9470)": {"manufacturer": "Police Security Flashlights", "brand": "Police Security"},
    "Square D Con Prod Dv (6825)": {"manufacturer": "Schneider Electric / Square D", "brand": "Square D"},
    "Woods Wire Southwire (7579)": {"manufacturer": "Southwire / Woods Wire", "brand": "Woods"},
    "Hunter Fan Co (4381)": {"manufacturer": "Hunter Fan Company", "brand": "Hunter"},
    "Makita Usa Inc (5142)": {"manufacturer": "Makita USA Inc", "brand": "Makita"},
    "Prebena (PREBE)": {"manufacturer": "Prebena Fastening Systems", "brand": "Prebena"},
    "Senco Products Inc (4650)": {"manufacturer": "Senco Products Inc", "brand": "Senco"},
    "National Nail Corp (7439)": {"manufacturer": "National Nail Corp", "brand": "Camo / Paslode"},
    "Festool USA (FESTO)": {"manufacturer": "Festool USA", "brand": "Festool"},
    "Kreg Tool Company (KRETO)": {"manufacturer": "Kreg Tool Company", "brand": "Kreg"},
    "CMT USA Inc (CMTUS)": {"manufacturer": "CMT USA Inc", "brand": "CMT Orange Tools"},
    "Oliver Machinery Company (OLIMA)": {"manufacturer": "Oliver Machinery Company", "brand": "Oliver"},
    "Woodpeckers Inc (WOODP)": {"manufacturer": "Woodpeckers Inc", "brand": "Woodpeckers"},
    "Edge Eyewear Inc (EDGSA)": {"manufacturer": "Edge Eyewear Inc", "brand": "Edge Safety"},
}

KNOWN_BRAND_TOKENS = [
    ("DEWALT", "DEWALT"),
    ("Dewalt", "DEWALT"),
    ("MILWAUKEE", "Milwaukee"),
    ("Milw", "Milwaukee"),
    ("MAKITA", "Makita"),
    ("Makita", "Makita"),
    ("FESTOOL", "Festool"),
    ("Festool", "Festool"),
    ("DIABLO", "Diablo"),
    ("Diablo", "Diablo"),
    ("FREUD", "Freud"),
    ("3M", "3M"),
    ("MIRKA", "Mirka"),
    ("TREX", "TREX"),
    ("Trex", "TREX"),
    ("TIMBERTECH", "TIMBERTECH"),
    ("Timbertech", "TIMBERTECH"),
    ("FRIGIDAIRE", "FRIGIDAIRE"),
    ("Frigidaire", "FRIGIDAIRE"),
    ("WHIRLPOOL", "Whirlpool"),
    ("Whirlpool", "Whirlpool"),
    ("KITCHENAID", "KitchenAid"),
    ("Kitchen Aid", "KitchenAid"),
    ("KitchenAid", "KitchenAid"),
    ("SPEED QUEEN", "Speed Queen"),
    ("Speed Queen", "Speed Queen"),
    ("SQ", "Speed Queen"),
    ("LG", "LG"),
    ("GE", "GE"),
    ("BEKO", "Beko"),
    ("Beko", "Beko"),
    ("SHARP", "Sharp"),
    ("CAFE", "Café"),
    ("Café", "Café"),
    ("Cafe", "Café"),
    ("HUNTER", "Hunter"),
    ("Hunter", "Hunter"),
    ("SATCO", "Satco"),
    ("Satco", "Satco"),
    ("PHILIPS", "Philips"),
    ("Philips", "Philips"),
    ("KICHLER", "Kichler"),
    ("Kichler", "Kichler"),
    ("LEVITON", "Leviton"),
    ("Leviton", "Leviton"),
    ("SOUTHWIRE", "Southwire"),
    ("Southwire", "Southwire"),
    ("SQUARE D", "Square D"),
    ("Square D", "Square D"),
    ("WERA", "Wera"),
    ("Wera", "Wera"),
    ("KREG", "Kreg"),
    ("Kreg", "Kreg"),
    ("SENCO", "Senco"),
    ("Senco", "Senco"),
    ("DREMEL", "Dremel"),
    ("Dremel", "Dremel"),
    ("JAMES HARDIE", "James Hardie"),
    ("JamesHardie", "James Hardie"),
    ("LP SMARTSIDE", "LP SmartSide"),
    ("PROVIA", "ProVia"),
    ("AJM", "AJM"),
    ("FIRST ALERT", "First Alert"),
    ("BRK", "BRK"),
    ("STREAMLIGHT", "Streamlight"),
    ("NEBO", "NEBO"),
]

# Common unit expansion patterns
UOM_CLEAN_PATTERNS = [
    (re.compile(r'(\d+)\s*(?:inch|inches|in\.?)\b', re.IGNORECASE), r'\1 in'),
    (re.compile(r'(\d+)\s*(?:ft\.?|feet|foot)\b', re.IGNORECASE), r'\1 ft'),
    (re.compile(r'(\d+)\s*(?:lbs?\.?|pounds?)\b', re.IGNORECASE), r'\1 lb'),
    (re.compile(r'(\d+)\s*(?:volts?|v)\b', re.IGNORECASE), r'\1 V'),
    (re.compile(r'(\d+)\s*(?:amps?|amp|a)\b', re.IGNORECASE), r'\1 A'),
    (re.compile(r'(\d+)\s*(?:watts?|w)\b', re.IGNORECASE), r'\1 W'),
]


def clean_vendor_name(raw_vendor: str) -> str:
    """Strips vendor accounting codes like 'Freud Inc (2435)' -> 'Freud Inc'"""
    if not raw_vendor:
        return ""
    if raw_vendor in VENDOR_CANONICAL_MAP:
        return VENDOR_CANONICAL_MAP[raw_vendor]["manufacturer"]
    # Strip (CODE) at the end if present
    cleaned = re.sub(r'\s*\([A-Z0-9]+\)\s*$', '', raw_vendor).strip()
    return cleaned


def resolve_brand(row: Dict[str, Any]) -> str:
    """
    Reconciles explicit brand columns (E1_Brand, Unilog_Brand, DIB_Brand),
    Part_Manuf mapping, and token matches in Part_Desc.
    """
    # 1. Direct explicit brand fields if populated
    for col in ["dib_brand", "unilog_brand", "e1_brand"]:
        val = (row.get(col) or "").strip()
        if val and val not in ["--", "-", "COMMODITY - UNBRANDED"]:
            return val

    # 2. Part_Desc keyword match
    desc = row.get("part_desc", "")
    for token, canonical_brand in KNOWN_BRAND_TOKENS:
        # Match whole word
        if re.search(rf'\b{re.escape(token)}\b', desc, re.IGNORECASE):
            return canonical_brand

    # 3. Vendor mapping fallback
    manuf = row.get("part_manuf", "")
    if manuf in VENDOR_CANONICAL_MAP and VENDOR_CANONICAL_MAP[manuf]["brand"]:
        return VENDOR_CANONICAL_MAP[manuf]["brand"]

    return ""


def clean(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Runs deterministic cleaning on all ingested rows."""
    for r in rows:
        desc = r.get("part_desc", "") or ""
        norm_desc = desc
        for pat, repl in UOM_CLEAN_PATTERNS:
            norm_desc = pat.sub(repl, norm_desc)
        r["part_desc_normalized"] = norm_desc

        raw_manuf = r.get("part_manuf", "")
        r["manufacturer_name"] = clean_vendor_name(raw_manuf)
        r["brand_name"] = resolve_brand(r)

    return rows
