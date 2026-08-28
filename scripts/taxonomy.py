"""Pain-signal taxonomy: Etsy buyer complaints -> what 3DAPI's routing fixes.

Every signal here is a symptom of one root cause: the item was printed far from
the person who bought it. That is the failure mode a distributed print network
removes, which is why these signals qualify a shop as a lead.
"""
import re

SIGNALS = [
    {
        "id": "transit_time",
        "label": "Slow delivery",
        "means": "Long transit from a single origin",
        "fix": "Route the order to the print farm nearest the buyer",
        "patterns": [
            r"\b(took|waited|waiting)\b.{0,20}\b(weeks?|months?)\b",
            r"\b\d+\s*(weeks?|months?)\b.{0,25}\b(arrive|deliver|ship|receiv)",
            r"\b(slow|late|delayed|still (?:hasn'?t|has not|not) arrived)\b",
            r"\barrived (?:after|too late)\b",
            r"\bmissed (?:christmas|the birthday|the deadline)\b",
        ],
    },
    {
        "id": "customs",
        "label": "Customs / import fees",
        "means": "Order crossed a border to reach the buyer",
        "fix": "Produce inside the buyer's market — no customs event",
        "patterns": [
            r"\bcustoms?\b", r"\bimport (?:fee|duty|duties|tax|charge)",
            r"\bduties\b", r"\bhandling fee\b", r"\bVAT\b.{0,20}\bcharge",
        ],
    },
    {
        "id": "damage",
        "label": "Damaged in transit",
        "means": "Long shipping leg increases handling and damage exposure",
        "fix": "Shorter domestic leg, fewer handoffs",
        "patterns": [
            r"\b(arrived|came)\b.{0,25}\b(broken|damaged|cracked|snapped|crushed|warped|bent)\b",
            r"\bbroken in (?:transit|the post|shipping)\b",
            r"\bpackag(?:e|ing) (?:was )?(?:crushed|destroyed|damaged)\b",
        ],
    },
    {
        "id": "processing",
        "label": "Long make time",
        "means": "Made-to-order backlog on one printer",
        "fix": "On-demand capacity across the network absorbs spikes",
        "patterns": [
            r"\bmade to order\b.{0,30}\b(wait|delay|long)",
            r"\bstill (?:being )?(?:printed|processing|in production)\b",
            r"\b(?:processing|production) time\b.{0,25}\b(long|slow|weeks)",
        ],
    },
    {
        "id": "capacity",
        "label": "Capacity ceiling",
        "means": "Demand exceeds what the seller can physically print",
        "fix": "Network capacity instead of one workshop",
        "patterns": [
            r"\bsold out\b", r"\bout of stock\b",
            r"\b(?:vacation|holiday) mode\b",
            r"\bnot (?:currently )?accepting orders\b",
            r"\bcancell?ed my order\b.{0,30}\b(?:couldn'?t|could not|unable)\b",
        ],
    },
    {
        "id": "shipping_cost",
        "label": "Shipping cost",
        "means": "Distance priced into every order",
        "fix": "Local fulfilment collapses the shipping leg",
        "patterns": [
            r"\bshipping (?:was |is |cost )?(?:so |too |very )?expensive\b",
            r"\bpostage\b.{0,20}\b(?:expensive|more than|cost)\b",
            r"\bshipping cost more than\b",
        ],
    },
]

SIGNALS += [
    {
        "id": "geo_blocked",
        "label": "Cannot buy from that country",
        "means": "The seller's shipping footprint excludes demand that already exists",
        "fix": "Sell anywhere — production happens inside the buyer's market, so "
               "the shop is not limited by what one workshop can post",
        "weight": 1.5,
        "patterns": [
            r"\b(?:do(?:es)?n'?t|does not|do not|no longer|won'?t)\s+ship\s+to\b",
            r"\bnot (?:available|shipping|sold)\b.{0,20}\b(?:in|to)\s+(?:my|the)\s+countr",
            r"\bwish (?:you|they)\b.{0,15}\bship(?:ped)?\s+to\b",
            r"\bno shipping (?:option|available)\b.{0,20}\bto\b",
            r"\bcan(?:'?t| ?not)\s+order\b.{0,25}\b(?:from|in)\s+(?:my )?countr",
            r"\b(?:please|any chance)\b.{0,20}\bship to\b",
            r"\bunavailable in my (?:country|region)\b",
        ],
    },
    {
        "id": "quality_defect",
        "label": "Inconsistent print quality",
        "means": "Output varies between runs on a single workshop's machines",
        "fix": "Every order passes 3DAPI's QC pipeline, so the buyer receives the "
               "product exactly as the seller specified it",
        "patterns": [
            r"\blayer lines?\b", r"\bstringing\b", r"\bunder ?extru",
            r"\b(?:poor|bad|sloppy|rough|messy)\b.{0,15}\b(?:print|finish|quality)\b",
            r"\bprint quality\b.{0,20}\b(?:poor|bad|disappointing|not great)\b",
            r"\bmisprint(?:ed)?\b", r"\b(?:misaligned|uneven) layers?\b",
            r"\bnot as (?:pictured|shown)\b.{0,25}\b(?:finish|quality|rough)\b",
        ],
    },
]

COMPILED = {
    s["id"]: [re.compile(p, re.I) for p in s["patterns"]] for s in SIGNALS
}
BY_ID = {s["id"]: s for s in SIGNALS}


def weight(sid):
    return BY_ID[sid].get("weight", 1.0)


def match_signals(text):
    """Return the set of signal ids present in a single review body."""
    if not text:
        return set()
    return {sid for sid, pats in COMPILED.items() if any(p.search(text) for p in pats)}
