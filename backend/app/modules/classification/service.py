"""
Module 3 -- Classification.
Responsibility: assign Department / Class / Fine (the classpath).

Per the scope decision, this pipeline is scoped to Appliances >
Kitchen/Laundry Appliances. Rather than a generative/open classification
call (risk of hallucinated classpaths), we use simple, fast keyword
routing into the small set of classpaths we've actually scoped and
verified against ground truth. This is a deliberate simplification --
say so in your pitch: classification became close to a formality once
we chose depth over breadth on one category.
"""

CLASSPATH_RULES = [
    (["dishwasher"], "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers"),
    (["dryer"], "Appliances & Consumer Electronics>Laundry Appliances>Dryers"),
    (["washer"], "Appliances & Consumer Electronics>Laundry Appliances>Washers"),
    (["refrigerator", "fridge"], "Appliances & Consumer Electronics>Kitchen Appliances>Refrigerators"),
    (["microwave"], "Appliances & Consumer Electronics>Kitchen Appliances>Microwaves"),
    (["range", "cooktop", "oven"], "Appliances & Consumer Electronics>Kitchen Appliances>Ranges & Cooktops"),
]


def classify_one(part_desc: str) -> str:
    text = (part_desc or "").lower()
    for keywords, classpath in CLASSPATH_RULES:
        if any(k in text for k in keywords):
            return classpath
    return ""  # unclassified -- downstream validation should flag this for review


def classify(rows: list[dict]) -> list[dict]:
    for r in rows:
        r["classpath"] = classify_one(r.get("part_desc_normalized") or r.get("part_desc"))
        if not r["classpath"]:
            r.setdefault("flags", []).append("classification_failed")
    return rows
