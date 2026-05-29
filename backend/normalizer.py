import re
from typing import Optional

# Canonical peptide names — maps lowercase/compact keys to display names
ALIASES: dict[str, str] = {
    # BPC-157
    "bpc157": "BPC-157",
    "bpc-157": "BPC-157",
    "bpc 157": "BPC-157",
    # TB-500
    "tb500": "TB-500",
    "tb-500": "TB-500",
    "tb 500": "TB-500",
    "thymosin beta 4": "TB-500",
    "thymosin beta-4": "TB-500",
    "thymosinbeta4": "TB-500",
    # CJC-1295 DAC
    "cjc1295dac": "CJC-1295 DAC",
    "cjc-1295 dac": "CJC-1295 DAC",
    "cjc1295 dac": "CJC-1295 DAC",
    # CJC-1295 No DAC
    "cjc1295nodac": "CJC-1295 No DAC",
    "cjc-1295 no dac": "CJC-1295 No DAC",
    "cjc1295 no dac": "CJC-1295 No DAC",
    # CJC-1295 (unspecified)
    "cjc1295": "CJC-1295",
    "cjc-1295": "CJC-1295",
    "cjc 1295": "CJC-1295",
    # Ipamorelin
    "ipamorelin": "Ipamorelin",
    # GHRP-2
    "ghrp2": "GHRP-2",
    "ghrp-2": "GHRP-2",
    "ghrp 2": "GHRP-2",
    # GHRP-6
    "ghrp6": "GHRP-6",
    "ghrp-6": "GHRP-6",
    "ghrp 6": "GHRP-6",
    # PT-141
    "pt141": "PT-141",
    "pt-141": "PT-141",
    "pt 141": "PT-141",
    "bremelanotide": "PT-141",
    # Melanotan II
    "melanotan2": "Melanotan II",
    "melanotan 2": "Melanotan II",
    "melanotan-2": "Melanotan II",
    "mt2": "Melanotan II",
    "mt-2": "Melanotan II",
    "mt 2": "Melanotan II",
    # Sermorelin
    "sermorelin": "Sermorelin",
    # Hexarelin
    "hexarelin": "Hexarelin",
    # Tesamorelin
    "tesamorelin": "Tesamorelin",
    # MK-677
    "mk677": "MK-677",
    "mk-677": "MK-677",
    "mk 677": "MK-677",
    "ibutamoren": "MK-677",
    # AOD-9604
    "aod9604": "AOD-9604",
    "aod-9604": "AOD-9604",
    "aod 9604": "AOD-9604",
    # Selank
    "selank": "Selank",
    # Semax
    "semax": "Semax",
    # DSIP
    "dsip": "DSIP",
    "delta sleep inducing peptide": "DSIP",
    # Epitalon
    "epitalon": "Epitalon",
    "epithalon": "Epitalon",
    # GHK-Cu
    "ghkcu": "GHK-Cu",
    "ghk-cu": "GHK-Cu",
    "ghk cu": "GHK-Cu",
    # IGF-1 LR3
    "igf1lr3": "IGF-1 LR3",
    "igf-1lr3": "IGF-1 LR3",
    "igf-1 lr3": "IGF-1 LR3",
    "igf1 lr3": "IGF-1 LR3",
    # PEG-MGF
    "pegmgf": "PEG-MGF",
    "peg-mgf": "PEG-MGF",
    "peg mgf": "PEG-MGF",
    # MGF
    "mgf": "MGF",
    # Follistatin-344
    "follistatin344": "Follistatin-344",
    "follistatin-344": "Follistatin-344",
    "follistatin 344": "Follistatin-344",
    # Thymalin
    "thymalin": "Thymalin",
    # Kisspeptin-10
    "kisspeptin10": "Kisspeptin-10",
    "kisspeptin-10": "Kisspeptin-10",
    "kisspeptin 10": "Kisspeptin-10",
    # LL-37
    "ll37": "LL-37",
    "ll-37": "LL-37",
    # Semaglutide
    "semaglutide": "Semaglutide",
    # Tirzepatide
    "tirzepatide": "Tirzepatide",
    # Retatrutide
    "retatrutide": "Retatrutide",
    # NAD+
    "nad+": "NAD+",
    "nad": "NAD+",
    # SS-31
    "ss31": "SS-31",
    "ss-31": "SS-31",
    # Humanin
    "humanin": "Humanin",
    # MOTS-c
    "motsc": "MOTS-c",
    "mots-c": "MOTS-c",
    "mots c": "MOTS-c",
    # Thymosin Alpha-1
    "thymosinalpha1": "Thymosin Alpha-1",
    "thymosin alpha-1": "Thymosin Alpha-1",
    "thymosin alpha 1": "Thymosin Alpha-1",
    "ta1": "Thymosin Alpha-1",
    "ta-1": "Thymosin Alpha-1",
}


def extract_weight_mg(name: str) -> Optional[float]:
    """Extract weight in mg from a product name string."""
    mcg = re.search(r"(\d+(?:\.\d+)?)\s*mcg\b", name, re.IGNORECASE)
    if mcg:
        return float(mcg.group(1)) / 1000.0
    mg = re.search(r"(\d+(?:\.\d+)?)\s*mg\b", name, re.IGNORECASE)
    return float(mg.group(1)) if mg else None


def _strip_quantity(name: str) -> str:
    s = re.sub(r"\s*\d+(?:\.\d+)?\s*(?:mg|mcg)\b", "", name, flags=re.IGNORECASE)
    s = re.sub(r"\s*x\s*\d+\s*(?:vials?)?\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\|\s*\d+.*$", "", s)
    return s.strip(" -–,|/")


def normalize_name(name: str) -> str:
    """Return a canonical peptide name for cross-vendor grouping."""
    base = _strip_quantity(name)
    key = base.lower().strip()
    key_compact = re.sub(r"[\s\-]+", "", key)

    if key in ALIASES:
        return ALIASES[key]
    if key_compact in ALIASES:
        return ALIASES[key_compact]

    return base.strip() or name.strip()
