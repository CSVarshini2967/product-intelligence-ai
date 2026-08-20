"""
Module 4 -- Taxonomy & Classification.
Responsibility: Assign Department, Class, Fine, and Classpath using a
controlled LOV taxonomy hierarchy. Every classification includes
predicted category, confidence, reason, and matching evidence.
"""
from typing import List, Dict, Any, Tuple
import re

# Controlled hierarchy: (Keywords, (Dept, Class, Fine, Classpath))
TAXONOMY_RULES: List[Tuple[List[str], Tuple[str, str, str, str]]] = [
    # --- APPLIANCES ---
    (
        ["dishwasher"],
        ("Appliances", "Large Appliances", "Dishwashers", "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers")
    ),
    (
        ["dryer"],
        ("Appliances", "Large Appliances", "Dryers", "Appliances & Consumer Electronics>Laundry Appliances>Dryers")
    ),
    (
        ["washer", "laundry center"],
        ("Appliances", "Large Appliances", "Washers", "Appliances & Consumer Electronics>Laundry Appliances>Washers")
    ),
    (
        ["refrigerator", "fridge", "freezer"],
        ("Appliances", "Large Appliances", "Refrigerators & Freezers", "Appliances & Consumer Electronics>Kitchen Appliances>Refrigerators")
    ),
    (
        ["microwave"],
        ("Appliances", "Kitchen Appliances", "Microwaves", "Appliances & Consumer Electronics>Kitchen Appliances>Microwaves")
    ),
    (
        ["cooktop", "range", "wall oven", "oven"],
        ("Appliances", "Large Appliances", "Ranges & Cooktops", "Appliances & Consumer Electronics>Kitchen Appliances>Ranges & Cooktops")
    ),
    (
        ["coffee maker", "espresso", "toaster", "beverage center"],
        ("Appliances", "Small Appliances", "Specialty Kitchen", "Appliances & Consumer Electronics>Kitchen Appliances>Coffee & Small Appliances")
    ),

    # --- ABRASIVES & FINISHING ---
    (
        ["stikit", "abranet", "hiolit", "sanding disc", "abrasive disc", "film p", "disc/box", "sanding sponge"],
        ("Abrasives", "Abrasive Discs", "Sanding Discs", "Abrasives & Finishing>Sanding Discs & Belts>Film & Paper Discs")
    ),
    (
        ["sanding belt", "band file"],
        ("Abrasives", "Abrasive Belts", "Sanding Belts", "Abrasives & Finishing>Sanding Discs & Belts>Sanding Belts & Sheets")
    ),
        (
        ["cut-off disc", "cut off disc", "cut and grind disc", "cut n grind", "cut & grind",
         "metal cut off", "cut/grind"],
        ("Abrasives", "Cutting & Grinding Wheels", "Cut-Off Wheels", "Abrasives & Finishing>Cut-Off & Grinding Wheels>Metal Cut-Off Wheels")
    ),
    (
        ["grinding wheel", "masonry cut off", "masonry grinding"],
        ("Abrasives", "Cutting & Grinding Wheels", "Grinding Wheels", "Abrasives & Finishing>Cut-Off & Grinding Wheels>Masonry & Grinding Wheels")
    ),

    # --- POWER TOOLS ---
    (
        ["impact driver", "drill driver", "hammer drill", "drill press", "compact drill"],
        ("Power Tools", "Cordless Power Tools", "Drills & Drivers", "Power Tools & Equipment>Cordless Drills & Drivers>Drill Drivers & Impact Drivers")
    ),
    (
        ["impact wrench", "ratchet", "angle impact", "hydraulic driver"],
        ("Power Tools", "Cordless Power Tools", "Impact Wrenches & Ratchets", "Power Tools & Equipment>Cordless Drills & Drivers>Impact Wrenches & Ratchets")
    ),
    (
        ["circular saw", "circ saw", "track saw"],
        ("Power Tools", "Saws & Woodworking", "Circular & Track Saws", "Power Tools & Equipment>Saws & Cutting>Circular Saws & Track Saws")
    ),
    (
        ["miter saw", "table saw", "bandsaw"],
        ("Power Tools", "Saws & Woodworking", "Stationary & Miter Saws", "Power Tools & Equipment>Saws & Cutting>Miter Saws & Table Saws")
    ),
    (
        ["jig saw", "jigsaw", "recip saw", "sawzall"],
        ("Power Tools", "Saws & Woodworking", "Reciprocating & Jig Saws", "Power Tools & Equipment>Saws & Cutting>Reciprocating & Jig Saws")
    ),
    (
        ["random orbit sander", "orbit sander", "sander", "planer", "planing machine", "router", "shaper", "jointer"],
        ("Power Tools", "Woodworking Equipment", "Sanders, Planers & Routers", "Power Tools & Equipment>Sanding & Woodworking>Orbit Sanders & Planers")
    ),
    (
        ["nailer", "stapler", "staple", "screw setter", "brad nailer", "finish nailer"],
        ("Power Tools", "Fastening Tools", "Nailers & Staplers", "Power Tools & Equipment>Fastening & Stapling>Brad Nailers & Framing Nailers")
    ),
    (
        ["blower", "string trimmer", "hedge trimmer"],
        ("Outdoor Power Equipment", "Lawn & Garden", "Trimmers & Blowers", "Power Tools & Equipment>Outdoor Power Equipment>Trimmers & Blowers")
    ),
    (
        ["dust extractor", "vacuum", "shop vac"],
        ("Power Tools", "Dust Collection", "Extractors & Vacuums", "Power Tools & Equipment>Dust Collection>Extractors & Vacuums")
    ),
    (
        ["starter kit", "battery pack", "powerpack", "charger", "lithium battery"],
        ("Power Tools", "Batteries & Chargers", "Cordless Power Supplies", "Power Tools & Equipment>Batteries & Chargers>Lithium-Ion Batteries & Chargers")
    ),

    # --- BUILDING MATERIALS & HARDWARE ---
    (
        ["decking", "trex", "timbertech", "azek pvc"],
        ("Building Materials", "Decking & Railing", "Composite Decking", "Building Materials & Hardware>Decking & Railing>Composite Decking")
    ),
    (
        ["rail kit", "t-rail", "post sleeve", "post trim", "post cap", "balusters", "support post", "post wrap"],
        ("Building Materials", "Decking & Railing", "Railing & Posts", "Building Materials & Hardware>Decking & Railing>Railing & Post Sleeves")
    ),
    (
        ["fascia"],
        ("Building Materials", "Decking & Railing", "Fascia & Trim", "Building Materials & Hardware>Decking & Railing>Fascia & Trim")
    ),
    (
        ["patio dr", "skylt", "skylight", "window", "attic access door"],
        ("Building Materials", "Doors & Windows", "Patio Doors & Windows", "Building Materials & Hardware>Windows & Doors>Gliding Patio Doors & Skylights")
    ),
    (
        ["drywall", "hardieplank", "hardiepanel", "smart lap", "smart pan", "soffit", "sheathing", "rainscreen", "sub floor", "ice guard"],
        ("Building Materials", "Siding & Sheathing", "Engineered Wood & Gypsum", "Building Materials & Hardware>Sheathing & Siding>Insulated Sheathing & Cement Siding")
    ),

    # --- ELECTRICAL & LIGHTING ---
    (
        ["led bulb", "incan", "halogen", "led multi cct", "flood", "candelabra", "cob bulb", "par38", "par30", "br30", "br40", "a19", "st19"],
        ("Electrical & Lighting", "Lamps & Bulbs", "LED & Incandescent Bulbs", "Electrical & Lighting>Lamps & Bulbs>LED Bulbs & Specialty Lamps")
    ),
    (
        ["downlight", "down light", "ceiling lt", "ceiling light", "flat panel", "strip light", "shop light", "wrap light", "highbay"],
        ("Electrical & Lighting", "Lighting Fixtures", "Ceiling & Downlights", "Electrical & Lighting>Fixtures & Wall Lights>Downlights & Ceiling Lights")
    ),
    (
        ["chandelier", "pendant"],
        ("Electrical & Lighting", "Lighting Fixtures", "Pendants & Chandeliers", "Electrical & Lighting>Fixtures & Wall Lights>Chandeliers & Pendants")
    ),
    (
        ["wall lt", "wall light", "bath light", "wall sconce", "ext wall lt", "post lt"],
        ("Electrical & Lighting", "Lighting Fixtures", "Wall & Vanity Fixtures", "Electrical & Lighting>Fixtures & Wall Lights>Wall Sconces & Bath Lights")
    ),
    (
        ["load center", "load cntr", "entrance cable", "triplex wire", "wire", "cord"],
        ("Electrical & Lighting", "Power Distribution", "Panels & Wire", "Electrical & Lighting>Distribution & Cords>Load Centers & Power Cords")
    ),
    (
        ["outlet", "dimmer", "timer", "gfci", "box cover", "wallplate", "switch", "plug in dimmer"],
        ("Electrical & Lighting", "Wiring Devices", "Switches & Outlets", "Electrical & Lighting>Wiring, Boxes & Devices>Outlets, GFCI & Dimmers")
    ),
    (
        ["hunter fan", "cassius fan", "anisten fan"],
        ("Electrical & Lighting", "Ceiling Fans", "Indoor & Outdoor Fans", "Electrical & Lighting>Fans & Ventilation>Ceiling Fans")
    ),
        (
        ["elect tape", "electrical tape", "vinyl tape", "insulating tape"],
        ("Electrical & Lighting", "Wiring Devices", "Tape & Insulation", "Electrical & Lighting>Wiring, Boxes & Devices>Electrical Tape & Insulation")
    ),
    (
        ["heater kit", "space heater", "heat gun", "portable heater"],
        ("HVAC & Climate Control", "Heating", "Heaters & Heat Guns", "HVAC & Climate Control>Heating Equipment>Space Heaters & Heat Guns")
    ),
    (
        ["tire pressure", "inflator gauge", "tire gauge"],
        ("Automotive & Fleet", "Automotive Tools", "Tire & Pressure Tools", "Automotive & Fleet>Tools & Diagnostics>Tire Pressure Gauges & Inflators")
    ),

    # --- SAFETY & WORKWEAR ---
    (
        ["safety glasses", "polarized", "photochromic", "hearing protector"],
        ("Safety & PPE", "Eye & Hearing Protection", "Safety Eyewear & Ear Protection", "Safety & Workwear>Eye & Hearing Protection>Safety Glasses & Ear Muffs")
    ),
    (
        ["heated glove", "glove liners", "heated hoodie", "heated work glove"],
        ("Safety & PPE", "Workwear", "Heated Apparel & Gloves", "Safety & Workwear>Heated Gear & Gloves>Heated Liners, Gloves & Hoodies")
    ),
    (
        ["fire extinguisher", "smoke & co alarm"],
        ("Safety & PPE", "Life Safety", "Fire & Smoke Alarms", "Safety & Workwear>Life Safety>Fire Extinguishers & Alarms")
    ),

    # --- HARDWARE & HAND TOOLS ---
    (
        ["saw blade", "router bit", "planer blade", "knives", "dado pro"],
        ("Hardware & Hand Tools", "Cutting Accessories", "Blades & Bits", "Hardware & Hand Tools>Blades & Bits>Saw Blades & Driver Bits")
    ),
    (
        ["drive bit", "torx drive", "phillips drive", "square drive", "bit holder", "socket adapter"],
        ("Hardware & Hand Tools", "Fastener Drive Bits", "Screwdriver Bits", "Hardware & Hand Tools>Blades & Bits>Driver & Fastening Bits")
    ),
    (
        ["laser", "laser level", "raftersquare", "mason line", "chalk & reel", "voltage detector"],
        ("Hardware & Hand Tools", "Layout & Measuring", "Lasers & Levels", "Hardware & Hand Tools>Measuring & Layout>Lasers, Levels & Tapes")
    ),
    (
        ["wrench set", "mechanics set", "ratchet & socket set", "folding knife", "mini snip"],
        ("Hardware & Hand Tools", "Hand Tools", "Wrenches & Mechanics Tools", "Hardware & Hand Tools>Mechanics Tools>Wrenches & Sockets")
    ),
]


def classify_one(text: str) -> Tuple[str, str, str, str, float, str, str]:
    """
    Returns (Dept, Class, Fine, Classpath, Confidence, Reason, Matching_Evidence).
    """
    clean_text = (text or "").lower()
    for keywords, (dept, cls, fine, classpath) in TAXONOMY_RULES:
        for kw in keywords:
            if kw in clean_text:
                return (
                    dept,
                    cls,
                    fine,
                    classpath,
                    0.95,
                    f"Matched controlled category keyword '{kw}'",
                    kw
                )

    # Fallback general classification
    return (
        "Industrial & Commercial Supplies",
        "General Hardware",
        "Miscellaneous Products",
        "Industrial & Commercial Supplies>General Products>Unclassified",
        0.35,
        "No specific controlled keyword matched",
        ""
    )


def classify(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Runs controlled taxonomy classification across all rows."""
    for r in rows:
        text = f"{r.get('part_desc_normalized') or r.get('part_desc', '')} {r.get('mfg_part_num', '')}"
        dept, cls, fine, classpath, conf, reason, ev = classify_one(text)

        r["dept"] = dept
        r["class_name"] = cls
        r["fine"] = fine
        r["classpath"] = classpath
        r["classification_confidence"] = conf
        r["classification_reason"] = reason

        if conf < 0.5:
            r.setdefault("flags", []).append("unclassified_fallback")
            r.setdefault("review_reasons", []).append("Uncertain category classification")

    return rows
