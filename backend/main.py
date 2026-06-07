import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import delete

from .database import Product, create_tables, get_session
from .normalizer import normalize_name
from .scrapers.amino_asylum import AminoAsylumScraper
from .scrapers.liberty_peptides import LibertyPeptidesScraper
from .scrapers.loti_labs import LotiLabsScraper
from .scrapers.nulife_peptides import NuLifePeptidesScraper
from .scrapers.prime_peptides import PrimePeptidesScraper
from .scrapers.axiom_peptides import AxiomPeptidesScraper
from .scrapers.behemoth_labz import BehemothLabzScraper
from .scrapers.biotech_peptides import BiotechPeptidesScraper
from .scrapers.blue_sky_peptide import BlueSkyPeptideScraper
from .scrapers.coastal_peptides import CoastalPeptidesScraper
from .scrapers.core_peptides import CorePeptidesScraper
from .scrapers.eternal_peptides import EternalPeptidesScraper
from .scrapers.evolved_peptides import EvolvedPeptidesScraper
from .scrapers.geo_peptides import GeoPeptidesScraper
from .scrapers.iron_daddy import IronDaddyScraper
from .scrapers.limitless_life import LimitlessLifeScraper
from .scrapers.maxim_peptide import MaximPeptideScraper
from .scrapers.nootropic_source import NootropicSourceScraper
from .scrapers.paradigm_peptides import ParadigmPeptidesScraper
from .scrapers.paramount_peptides import ParamountPeptidesScraper
from .scrapers.peptide_crafters import PeptideCraftersScraper
from .scrapers.peptide_pro import PeptideProScraper
from .scrapers.peptide_sciences import PeptideSciencesScraper
from .scrapers.peptide_warehouse import PeptideWarehouseScraper
from .scrapers.polaris_peptides import PolarispeptidesScraper
from .scrapers.pure_rawz import PureRawzScraper
from .scrapers.swiss_chems import SwissChemsScraper
from .scrapers.us_peptides import USPeptidesScraper
from .scrapers.verified_peptides import VerifiedPeptidesScraper

logger = logging.getLogger(__name__)

SCRAPER_CLASSES = [
    PeptideSciencesScraper,
    LimitlessLifeScraper,
    AminoAsylumScraper,
    PureRawzScraper,
    BehemothLabzScraper,
    SwissChemsScraper,
    BlueSkyPeptideScraper,
    MaximPeptideScraper,
    PeptideWarehouseScraper,
    BiotechPeptidesScraper,
    GeoPeptidesScraper,
    CorePeptidesScraper,
    ParadigmPeptidesScraper,
    AxiomPeptidesScraper,
    EvolvedPeptidesScraper,
    PeptideProScraper,
    NootropicSourceScraper,
    USPeptidesScraper,
    IronDaddyScraper,
    PolarispeptidesScraper,
    VerifiedPeptidesScraper,
    PeptideCraftersScraper,
    EternalPeptidesScraper,
    CoastalPeptidesScraper,
    ParamountPeptidesScraper,
    # Login-gated — active only when env vars are set
    NuLifePeptidesScraper,
    LibertyPeptidesScraper,
    PrimePeptidesScraper,
    LotiLabsScraper,
]

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# ---------------------------------------------------------------------------
# Sample data — seeded on first run so the UI is immediately useful
# ---------------------------------------------------------------------------
_SAMPLE: list[dict] = [
    # BPC-157
    {"vendor": "Peptide Sciences",  "name": "BPC-157 5mg",  "price": 49.99, "url": "https://www.peptidesciences.com/bpc-157-5mg/",         "weight_mg": 5.0},
    {"vendor": "Swiss Chems",       "name": "BPC-157 5mg",  "price": 44.95, "url": "https://swisschems.is/product/bpc-157-5mg/",            "weight_mg": 5.0},
    {"vendor": "Pure Rawz",         "name": "BPC-157 5mg",  "price": 39.99, "url": "https://purerawz.co/product/bpc-157-5mg/",             "weight_mg": 5.0},
    {"vendor": "Behemoth Labz",     "name": "BPC-157 5mg",  "price": 42.50, "url": "https://behemothlabz.com/product/bpc-157/",            "weight_mg": 5.0},
    {"vendor": "Amino Asylum",      "name": "BPC-157 5mg",  "price": 37.99, "url": "https://aminoasylum.shop/products/bpc-157",            "weight_mg": 5.0},
    {"vendor": "Limitless Life",    "name": "BPC-157 5mg",  "price": 52.00, "url": "https://limitlesslifenootropics.com/bpc-157/",         "weight_mg": 5.0},
    # TB-500
    {"vendor": "Peptide Sciences",  "name": "TB-500 5mg",   "price": 59.99, "url": "https://www.peptidesciences.com/tb-500/",              "weight_mg": 5.0},
    {"vendor": "Swiss Chems",       "name": "TB-500 5mg",   "price": 54.95, "url": "https://swisschems.is/product/tb-500-5mg/",            "weight_mg": 5.0},
    {"vendor": "Pure Rawz",         "name": "TB-500 5mg",   "price": 49.99, "url": "https://purerawz.co/product/tb-500-5mg/",             "weight_mg": 5.0},
    {"vendor": "Amino Asylum",      "name": "TB-500 5mg",   "price": 46.99, "url": "https://aminoasylum.shop/products/tb-500",            "weight_mg": 5.0},
    # CJC-1295 DAC
    {"vendor": "Peptide Sciences",  "name": "CJC-1295 DAC 2mg", "price": 29.99, "url": "https://www.peptidesciences.com/cjc-1295-dac/",   "weight_mg": 2.0},
    {"vendor": "Swiss Chems",       "name": "CJC-1295 DAC 2mg", "price": 27.95, "url": "https://swisschems.is/product/cjc-1295-dac-2mg/", "weight_mg": 2.0},
    {"vendor": "Pure Rawz",         "name": "CJC-1295 DAC 2mg", "price": 24.99, "url": "https://purerawz.co/product/cjc-1295/",          "weight_mg": 2.0},
    # Ipamorelin
    {"vendor": "Peptide Sciences",  "name": "Ipamorelin 2mg",   "price": 19.99, "url": "https://www.peptidesciences.com/ipamorelin/",     "weight_mg": 2.0},
    {"vendor": "Swiss Chems",       "name": "Ipamorelin 2mg",   "price": 18.95, "url": "https://swisschems.is/product/ipamorelin-2mg/",   "weight_mg": 2.0},
    {"vendor": "Amino Asylum",      "name": "Ipamorelin 2mg",   "price": 16.99, "url": "https://aminoasylum.shop/products/ipamorelin",    "weight_mg": 2.0},
    {"vendor": "Behemoth Labz",     "name": "Ipamorelin 2mg",   "price": 21.00, "url": "https://behemothlabz.com/product/ipamorelin/",    "weight_mg": 2.0},
    # PT-141
    {"vendor": "Peptide Sciences",  "name": "PT-141 10mg",      "price": 39.99, "url": "https://www.peptidesciences.com/pt-141/",         "weight_mg": 10.0},
    {"vendor": "Swiss Chems",       "name": "PT-141 10mg",      "price": 36.95, "url": "https://swisschems.is/product/pt-141-10mg/",      "weight_mg": 10.0},
    {"vendor": "Pure Rawz",         "name": "PT-141 10mg",      "price": 34.99, "url": "https://purerawz.co/product/pt-141/",            "weight_mg": 10.0},
    {"vendor": "Amino Asylum",      "name": "PT-141 10mg",      "price": 32.99, "url": "https://aminoasylum.shop/products/pt-141",        "weight_mg": 10.0},
    # Melanotan II
    {"vendor": "Peptide Sciences",  "name": "Melanotan II 10mg","price": 29.99, "url": "https://www.peptidesciences.com/melanotan-2/",    "weight_mg": 10.0},
    {"vendor": "Swiss Chems",       "name": "Melanotan 2 10mg", "price": 27.95, "url": "https://swisschems.is/product/melanotan-2-10mg/", "weight_mg": 10.0},
    {"vendor": "Limitless Life",    "name": "Melanotan II 10mg","price": 31.00, "url": "https://limitlesslifenootropics.com/mt2/",        "weight_mg": 10.0},
    # Sermorelin
    {"vendor": "Peptide Sciences",  "name": "Sermorelin 2mg",   "price": 24.99, "url": "https://www.peptidesciences.com/sermorelin/",    "weight_mg": 2.0},
    {"vendor": "Swiss Chems",       "name": "Sermorelin 2mg",   "price": 22.95, "url": "https://swisschems.is/product/sermorelin-2mg/",  "weight_mg": 2.0},
    {"vendor": "Pure Rawz",         "name": "Sermorelin 2mg",   "price": 21.99, "url": "https://purerawz.co/product/sermorelin/",        "weight_mg": 2.0},
    # GHRP-2
    {"vendor": "Peptide Sciences",  "name": "GHRP-2 5mg",       "price": 19.99, "url": "https://www.peptidesciences.com/ghrp-2/",        "weight_mg": 5.0},
    {"vendor": "Swiss Chems",       "name": "GHRP-2 5mg",       "price": 17.95, "url": "https://swisschems.is/product/ghrp-2-5mg/",      "weight_mg": 5.0},
    {"vendor": "Amino Asylum",      "name": "GHRP-2 5mg",       "price": 15.99, "url": "https://aminoasylum.shop/products/ghrp-2",       "weight_mg": 5.0},
    # GHRP-6
    {"vendor": "Peptide Sciences",  "name": "GHRP-6 5mg",       "price": 19.99, "url": "https://www.peptidesciences.com/ghrp-6/",        "weight_mg": 5.0},
    {"vendor": "Behemoth Labz",     "name": "GHRP-6 5mg",       "price": 18.50, "url": "https://behemothlabz.com/product/ghrp-6/",       "weight_mg": 5.0},
    # AOD-9604
    {"vendor": "Pure Rawz",         "name": "AOD-9604 5mg",     "price": 34.99, "url": "https://purerawz.co/product/aod-9604/",          "weight_mg": 5.0},
    {"vendor": "Swiss Chems",       "name": "AOD-9604 5mg",     "price": 32.95, "url": "https://swisschems.is/product/aod-9604-5mg/",    "weight_mg": 5.0},
    # Selank
    {"vendor": "Peptide Sciences",  "name": "Selank 5mg",       "price": 29.99, "url": "https://www.peptidesciences.com/selank/",        "weight_mg": 5.0},
    {"vendor": "Pure Rawz",         "name": "Selank 5mg",       "price": 27.99, "url": "https://purerawz.co/product/selank/",            "weight_mg": 5.0},
    # Semax
    {"vendor": "Peptide Sciences",  "name": "Semax 30mg",       "price": 54.99, "url": "https://www.peptidesciences.com/semax/",         "weight_mg": 30.0},
    {"vendor": "Limitless Life",    "name": "Semax 30mg",       "price": 51.00, "url": "https://limitlesslifenootropics.com/semax/",     "weight_mg": 30.0},
    # Semaglutide
    {"vendor": "Pure Rawz",         "name": "Semaglutide 5mg",  "price": 99.99, "url": "https://purerawz.co/product/semaglutide/",       "weight_mg": 5.0},
    {"vendor": "Behemoth Labz",     "name": "Semaglutide 5mg",  "price": 94.99, "url": "https://behemothlabz.com/product/semaglutide/",  "weight_mg": 5.0},
    {"vendor": "Swiss Chems",       "name": "Semaglutide 5mg",  "price": 89.95, "url": "https://swisschems.is/product/semaglutide-5mg/", "weight_mg": 5.0},
    # Tirzepatide
    {"vendor": "Pure Rawz",         "name": "Tirzepatide 5mg",  "price": 109.99,"url": "https://purerawz.co/product/tirzepatide/",       "weight_mg": 5.0},
    {"vendor": "Behemoth Labz",     "name": "Tirzepatide 5mg",  "price": 104.99,"url": "https://behemothlabz.com/product/tirzepatide/",  "weight_mg": 5.0},
    # GHK-Cu
    {"vendor": "Peptide Sciences",  "name": "GHK-Cu 50mg",      "price": 39.99, "url": "https://www.peptidesciences.com/ghk-cu/",        "weight_mg": 50.0},
    {"vendor": "Pure Rawz",         "name": "GHK-Cu 50mg",      "price": 36.99, "url": "https://purerawz.co/product/ghk-cu/",            "weight_mg": 50.0},
    # IGF-1 LR3
    {"vendor": "Peptide Sciences",  "name": "IGF-1 LR3 100mcg", "price": 49.99, "url": "https://www.peptidesciences.com/igf-1-lr3/",     "weight_mg": 0.1},
    {"vendor": "Swiss Chems",       "name": "IGF-1 LR3 100mcg", "price": 44.95, "url": "https://swisschems.is/product/igf-1-lr3/",       "weight_mg": 0.1},
    # Hexarelin
    {"vendor": "Peptide Sciences",  "name": "Hexarelin 2mg",    "price": 22.99, "url": "https://www.peptidesciences.com/hexarelin/",     "weight_mg": 2.0},
    {"vendor": "Limitless Life",    "name": "Hexarelin 2mg",    "price": 21.00, "url": "https://limitlesslifenootropics.com/hexarelin/", "weight_mg": 2.0},
    # Tesamorelin
    {"vendor": "Peptide Sciences",  "name": "Tesamorelin 2mg",  "price": 34.99, "url": "https://www.peptidesciences.com/tesamorelin/",   "weight_mg": 2.0},
    {"vendor": "Swiss Chems",       "name": "Tesamorelin 2mg",  "price": 32.95, "url": "https://swisschems.is/product/tesamorelin/",     "weight_mg": 2.0},
    # MK-677
    {"vendor": "Pure Rawz",         "name": "MK-677 10mg",      "price": 44.99, "url": "https://purerawz.co/product/mk-677/",            "weight_mg": 10.0},
    {"vendor": "Behemoth Labz",     "name": "MK-677 10mg",      "price": 42.50, "url": "https://behemothlabz.com/product/mk-677/",       "weight_mg": 10.0},
    {"vendor": "Amino Asylum",      "name": "MK-677 10mg",      "price": 39.99, "url": "https://aminoasylum.shop/products/mk-677",       "weight_mg": 10.0},
    # ── New vendors ────────────────────────────────────────────────────────
    # Blue Sky Peptide
    {"vendor": "Blue Sky Peptide",  "name": "BPC-157 5mg",      "price": 43.00, "url": "https://www.blueskypeptide.com/bpc-157-5mg",     "weight_mg": 5.0},
    {"vendor": "Blue Sky Peptide",  "name": "TB-500 5mg",       "price": 51.00, "url": "https://www.blueskypeptide.com/tb-500-5mg",      "weight_mg": 5.0},
    {"vendor": "Blue Sky Peptide",  "name": "Ipamorelin 2mg",   "price": 18.00, "url": "https://www.blueskypeptide.com/ipamorelin-2mg",  "weight_mg": 2.0},
    {"vendor": "Blue Sky Peptide",  "name": "CJC-1295 DAC 2mg", "price": 26.00, "url": "https://www.blueskypeptide.com/cjc-1295-dac",   "weight_mg": 2.0},
    {"vendor": "Blue Sky Peptide",  "name": "PT-141 10mg",      "price": 33.00, "url": "https://www.blueskypeptide.com/pt-141-10mg",     "weight_mg": 10.0},
    # Maxim Peptide
    {"vendor": "Maxim Peptide",     "name": "BPC-157 5mg",      "price": 41.99, "url": "https://www.maximpeptide.com/bpc-157-5mg",       "weight_mg": 5.0},
    {"vendor": "Maxim Peptide",     "name": "TB-500 5mg",       "price": 50.99, "url": "https://www.maximpeptide.com/tb-500-5mg",        "weight_mg": 5.0},
    {"vendor": "Maxim Peptide",     "name": "Sermorelin 2mg",   "price": 20.99, "url": "https://www.maximpeptide.com/sermorelin-2mg",    "weight_mg": 2.0},
    {"vendor": "Maxim Peptide",     "name": "GHRP-2 5mg",       "price": 16.99, "url": "https://www.maximpeptide.com/ghrp-2-5mg",        "weight_mg": 5.0},
    # Peptide Warehouse
    {"vendor": "Peptide Warehouse", "name": "BPC-157 5mg",      "price": 45.00, "url": "https://www.peptidewarehouse.com/bpc-157",       "weight_mg": 5.0},
    {"vendor": "Peptide Warehouse", "name": "TB-500 5mg",       "price": 53.00, "url": "https://www.peptidewarehouse.com/tb-500",        "weight_mg": 5.0},
    {"vendor": "Peptide Warehouse", "name": "Ipamorelin 2mg",   "price": 19.50, "url": "https://www.peptidewarehouse.com/ipamorelin",    "weight_mg": 2.0},
    {"vendor": "Peptide Warehouse", "name": "Melanotan II 10mg","price": 28.00, "url": "https://www.peptidewarehouse.com/melanotan-2",   "weight_mg": 10.0},
    # Biotech Peptides
    {"vendor": "Biotech Peptides",  "name": "BPC-157 5mg",      "price": 38.95, "url": "https://www.biotechpeptides.com/bpc-157-5mg",    "weight_mg": 5.0},
    {"vendor": "Biotech Peptides",  "name": "TB-500 5mg",       "price": 47.95, "url": "https://www.biotechpeptides.com/tb-500-5mg",     "weight_mg": 5.0},
    {"vendor": "Biotech Peptides",  "name": "CJC-1295 DAC 2mg", "price": 23.95, "url": "https://www.biotechpeptides.com/cjc-1295",      "weight_mg": 2.0},
    {"vendor": "Biotech Peptides",  "name": "PT-141 10mg",      "price": 31.95, "url": "https://www.biotechpeptides.com/pt-141",         "weight_mg": 10.0},
    {"vendor": "Biotech Peptides",  "name": "Semaglutide 5mg",  "price": 87.95, "url": "https://www.biotechpeptides.com/semaglutide",    "weight_mg": 5.0},
    # Geo Peptides
    {"vendor": "Geo Peptides",      "name": "BPC-157 5mg",      "price": 36.99, "url": "https://www.geopeptides.com/bpc-157",            "weight_mg": 5.0},
    {"vendor": "Geo Peptides",      "name": "TB-500 5mg",       "price": 45.99, "url": "https://www.geopeptides.com/tb-500",             "weight_mg": 5.0},
    {"vendor": "Geo Peptides",      "name": "Ipamorelin 2mg",   "price": 15.99, "url": "https://www.geopeptides.com/ipamorelin",         "weight_mg": 2.0},
    {"vendor": "Geo Peptides",      "name": "GHRP-6 5mg",       "price": 16.99, "url": "https://www.geopeptides.com/ghrp-6",             "weight_mg": 5.0},
    # Core Peptides
    {"vendor": "Core Peptides",     "name": "BPC-157 5mg",      "price": 40.00, "url": "https://corepeptides.com/bpc-157-5mg",           "weight_mg": 5.0},
    {"vendor": "Core Peptides",     "name": "TB-500 5mg",       "price": 48.00, "url": "https://corepeptides.com/tb-500-5mg",            "weight_mg": 5.0},
    {"vendor": "Core Peptides",     "name": "Sermorelin 2mg",   "price": 22.00, "url": "https://corepeptides.com/sermorelin-2mg",        "weight_mg": 2.0},
    {"vendor": "Core Peptides",     "name": "AOD-9604 5mg",     "price": 31.00, "url": "https://corepeptides.com/aod-9604",              "weight_mg": 5.0},
    {"vendor": "Core Peptides",     "name": "Semaglutide 5mg",  "price": 92.00, "url": "https://corepeptides.com/semaglutide",           "weight_mg": 5.0},
    # Paradigm Peptides
    {"vendor": "Paradigm Peptides", "name": "BPC-157 5mg",      "price": 44.99, "url": "https://paradigmpeptides.com/bpc-157-5mg",       "weight_mg": 5.0},
    {"vendor": "Paradigm Peptides", "name": "TB-500 5mg",       "price": 54.99, "url": "https://paradigmpeptides.com/tb-500-5mg",        "weight_mg": 5.0},
    {"vendor": "Paradigm Peptides", "name": "CJC-1295 DAC 2mg", "price": 28.99, "url": "https://paradigmpeptides.com/cjc-1295",         "weight_mg": 2.0},
    {"vendor": "Paradigm Peptides", "name": "Ipamorelin 2mg",   "price": 20.99, "url": "https://paradigmpeptides.com/ipamorelin",        "weight_mg": 2.0},
    # Axiom Peptides
    {"vendor": "Axiom Peptides",    "name": "BPC-157 5mg",      "price": 38.00, "url": "https://axiompeptides.com/bpc-157",              "weight_mg": 5.0},
    {"vendor": "Axiom Peptides",    "name": "TB-500 5mg",       "price": 46.00, "url": "https://axiompeptides.com/tb-500",               "weight_mg": 5.0},
    {"vendor": "Axiom Peptides",    "name": "PT-141 10mg",      "price": 30.00, "url": "https://axiompeptides.com/pt-141",               "weight_mg": 10.0},
    {"vendor": "Axiom Peptides",    "name": "GHRP-2 5mg",       "price": 14.99, "url": "https://axiompeptides.com/ghrp-2",               "weight_mg": 5.0},
    # Evolved Peptides
    {"vendor": "Evolved Peptides",  "name": "BPC-157 5mg",      "price": 41.00, "url": "https://www.evolvedpeptides.com/bpc-157",        "weight_mg": 5.0},
    {"vendor": "Evolved Peptides",  "name": "TB-500 5mg",       "price": 49.00, "url": "https://www.evolvedpeptides.com/tb-500",         "weight_mg": 5.0},
    {"vendor": "Evolved Peptides",  "name": "Semaglutide 5mg",  "price": 91.00, "url": "https://www.evolvedpeptides.com/semaglutide",    "weight_mg": 5.0},
    {"vendor": "Evolved Peptides",  "name": "Tirzepatide 5mg",  "price": 99.00, "url": "https://www.evolvedpeptides.com/tirzepatide",    "weight_mg": 5.0},
    # Peptide Pro
    {"vendor": "Peptide Pro",       "name": "BPC-157 5mg",      "price": 42.00, "url": "https://peptidepro.com/bpc-157",                 "weight_mg": 5.0},
    {"vendor": "Peptide Pro",       "name": "TB-500 5mg",       "price": 51.00, "url": "https://peptidepro.com/tb-500",                  "weight_mg": 5.0},
    {"vendor": "Peptide Pro",       "name": "Sermorelin 2mg",   "price": 23.00, "url": "https://peptidepro.com/sermorelin",              "weight_mg": 2.0},
    # Nootropic Source
    {"vendor": "Nootropic Source",  "name": "Selank 5mg",       "price": 26.00, "url": "https://nootropicsource.com/selank",             "weight_mg": 5.0},
    {"vendor": "Nootropic Source",  "name": "Semax 30mg",       "price": 48.00, "url": "https://nootropicsource.com/semax",              "weight_mg": 30.0},
    {"vendor": "Nootropic Source",  "name": "BPC-157 5mg",      "price": 43.00, "url": "https://nootropicsource.com/bpc-157",            "weight_mg": 5.0},
    # US Peptides
    {"vendor": "US Peptides",       "name": "BPC-157 5mg",      "price": 39.99, "url": "https://uspeptides.com/bpc-157",                 "weight_mg": 5.0},
    {"vendor": "US Peptides",       "name": "TB-500 5mg",       "price": 48.99, "url": "https://uspeptides.com/tb-500",                  "weight_mg": 5.0},
    {"vendor": "US Peptides",       "name": "Ipamorelin 2mg",   "price": 17.99, "url": "https://uspeptides.com/ipamorelin",              "weight_mg": 2.0},
    {"vendor": "US Peptides",       "name": "CJC-1295 DAC 2mg", "price": 25.99, "url": "https://uspeptides.com/cjc-1295",               "weight_mg": 2.0},
    # Iron Daddy
    {"vendor": "Iron Daddy",        "name": "BPC-157 5mg",      "price": 35.99, "url": "https://www.irondaddy.to/products/bpc-157",             "weight_mg": 5.0},
    {"vendor": "Iron Daddy",        "name": "TB-500 5mg",       "price": 44.99, "url": "https://www.irondaddy.to/products/tb-500",              "weight_mg": 5.0},
    {"vendor": "Iron Daddy",        "name": "Semaglutide 5mg",  "price": 84.99, "url": "https://www.irondaddy.to/products/semaglutide",         "weight_mg": 5.0},
    {"vendor": "Iron Daddy",        "name": "Tirzepatide 5mg",  "price": 99.99, "url": "https://www.irondaddy.to/products/tirzepatide",         "weight_mg": 5.0},
    # ── Finnrick-sourced vendors ────────────────────────────────────────────
    # Polaris Peptides
    {"vendor": "Polaris Peptides",  "name": "BPC-157 5mg",      "price": 38.00, "url": "https://polarispeptides.com/product/bpc-157-5mg/",      "weight_mg": 5.0},
    {"vendor": "Polaris Peptides",  "name": "TB-500 5mg",       "price": 46.00, "url": "https://polarispeptides.com/product/tb-500-5mg/",       "weight_mg": 5.0},
    {"vendor": "Polaris Peptides",  "name": "CJC-1295 DAC 2mg", "price": 24.00, "url": "https://polarispeptides.com/product/cjc-1295-dac/",     "weight_mg": 2.0},
    {"vendor": "Polaris Peptides",  "name": "Ipamorelin 2mg",   "price": 17.00, "url": "https://polarispeptides.com/product/ipamorelin/",       "weight_mg": 2.0},
    {"vendor": "Polaris Peptides",  "name": "Semaglutide 5mg",  "price": 86.00, "url": "https://polarispeptides.com/product/semaglutide/",      "weight_mg": 5.0},
    # Verified Peptides
    {"vendor": "Verified Peptides", "name": "BPC-157 5mg",      "price": 41.00, "url": "https://verifiedpeptides.com/product/bpc157/",          "weight_mg": 5.0},
    {"vendor": "Verified Peptides", "name": "TB-500 5mg",       "price": 49.00, "url": "https://verifiedpeptides.com/product/tb-500/",          "weight_mg": 5.0},
    {"vendor": "Verified Peptides", "name": "PT-141 10mg",      "price": 34.00, "url": "https://verifiedpeptides.com/product/pt-141/",          "weight_mg": 10.0},
    {"vendor": "Verified Peptides", "name": "GHK-Cu 50mg",      "price": 38.00, "url": "https://verifiedpeptides.com/product/ghkcu/",           "weight_mg": 50.0},
    # Peptide Crafters
    {"vendor": "Peptide Crafters",  "name": "BPC-157 5mg",      "price": 43.00, "url": "https://peptidecrafters.com/shop/bpc-157/",             "weight_mg": 5.0},
    {"vendor": "Peptide Crafters",  "name": "TB-500 5mg",       "price": 52.00, "url": "https://peptidecrafters.com/shop/tb-500/",              "weight_mg": 5.0},
    {"vendor": "Peptide Crafters",  "name": "Sermorelin 2mg",   "price": 24.00, "url": "https://peptidecrafters.com/shop/sermorelin/",          "weight_mg": 2.0},
    # Eternal Peptides
    {"vendor": "Eternal Peptides",  "name": "BPC-157 5mg",      "price": 40.00, "url": "https://eternalpeptides.com/product/bpc-157/",          "weight_mg": 5.0},
    {"vendor": "Eternal Peptides",  "name": "TB-500 5mg",       "price": 48.00, "url": "https://eternalpeptides.com/product/tb-500/",           "weight_mg": 5.0},
    {"vendor": "Eternal Peptides",  "name": "Ipamorelin 2mg",   "price": 18.00, "url": "https://eternalpeptides.com/product/ipamorelin/",       "weight_mg": 2.0},
    {"vendor": "Eternal Peptides",  "name": "Semaglutide 5mg",  "price": 91.00, "url": "https://eternalpeptides.com/product/semaglutide/",      "weight_mg": 5.0},
    # Coastal Peptides
    {"vendor": "Coastal Peptides",  "name": "BPC-157 5mg",      "price": 44.00, "url": "https://coastalpeptides.com/product/bpc-157/",          "weight_mg": 5.0},
    {"vendor": "Coastal Peptides",  "name": "TB-500 5mg",       "price": 53.00, "url": "https://coastalpeptides.com/product/tb-500/",           "weight_mg": 5.0},
    {"vendor": "Coastal Peptides",  "name": "CJC-1295 DAC 2mg", "price": 27.00, "url": "https://coastalpeptides.com/product/cjc-1295/",         "weight_mg": 2.0},
    {"vendor": "Coastal Peptides",  "name": "GHRP-2 5mg",       "price": 18.00, "url": "https://coastalpeptides.com/product/ghrp-2/",           "weight_mg": 5.0},
    # Paramount Peptides
    {"vendor": "Paramount Peptides","name": "BPC-157 5mg",      "price": 42.00, "url": "https://paramountpeptides.com/product/bpc-157/",        "weight_mg": 5.0},
    {"vendor": "Paramount Peptides","name": "TB-500 5mg",       "price": 50.00, "url": "https://paramountpeptides.com/product/tb-500/",         "weight_mg": 5.0},
    {"vendor": "Paramount Peptides","name": "PT-141 10mg",      "price": 35.00, "url": "https://paramountpeptides.com/product/pt-141/",         "weight_mg": 10.0},
    {"vendor": "Paramount Peptides","name": "Sermorelin 2mg",   "price": 23.00, "url": "https://paramountpeptides.com/product/sermorelin/",     "weight_mg": 2.0},
    # ── Login-gated vendors (live data requires env vars) ──────────────────
    # NuLife Peptides
    {"vendor": "NuLife Peptides",   "name": "BPC-157 10mg",     "price": 59.99, "url": "https://nulifepeptides.com/product/bpc-157-10mg/",      "weight_mg": 10.0},
    {"vendor": "NuLife Peptides",   "name": "CJC-1295 DAC 5mg", "price": 49.99, "url": "https://nulifepeptides.com/product/cjc-1295-with-dac/", "weight_mg": 5.0},
    {"vendor": "NuLife Peptides",   "name": "Tesamorelin 2mg",  "price": 34.99, "url": "https://nulifepeptides.com/product/tesamorelin/",       "weight_mg": 2.0},
    # Liberty Peptides
    {"vendor": "Liberty Peptides",  "name": "BPC-157 5mg",      "price": 43.99, "url": "https://libertypeptides.com/product/bpc-157/",          "weight_mg": 5.0},
    {"vendor": "Liberty Peptides",  "name": "TB-500 5mg",       "price": 52.99, "url": "https://libertypeptides.com/product/tb-500/",           "weight_mg": 5.0},
    {"vendor": "Liberty Peptides",  "name": "Semaglutide 5mg",  "price": 93.99, "url": "https://libertypeptides.com/product/semaglutide/",      "weight_mg": 5.0},
    # Prime Peptides
    {"vendor": "Prime Peptides",    "name": "BPC-157 5mg",      "price": 40.99, "url": "https://primepeptides.com/product/bpc-157/",            "weight_mg": 5.0},
    {"vendor": "Prime Peptides",    "name": "TB-500 5mg",       "price": 49.99, "url": "https://primepeptides.com/product/tb-500/",             "weight_mg": 5.0},
    # Loti Labs
    {"vendor": "Loti Labs",         "name": "BPC-157 5mg",      "price": 45.00, "url": "https://lotilabs.com/product/bpc-157/",                 "weight_mg": 5.0},
    {"vendor": "Loti Labs",         "name": "TB-500 5mg",       "price": 54.00, "url": "https://lotilabs.com/product/tb-500/",                  "weight_mg": 5.0},
    {"vendor": "Loti Labs",         "name": "Ipamorelin 2mg",   "price": 22.00, "url": "https://lotilabs.com/product/ipamorelin/",              "weight_mg": 2.0},
]


def _seed_sample_data() -> None:
    session = get_session()
    try:
        existing = session.query(Product).count()
        if existing > 0:
            return
        now = datetime.utcnow()
        for row in _SAMPLE:
            wt = row["weight_mg"]
            session.add(
                Product(
                    vendor=row["vendor"],
                    name=row["name"],
                    normalized_name=normalize_name(row["name"]),
                    price=row["price"],
                    url=row["url"],
                    weight_mg=wt,
                    price_per_mg=round(row["price"] / wt, 4),
                    last_updated=now,
                )
            )
        session.commit()
        logger.info("Seeded %d sample products", len(_SAMPLE))
    except Exception as exc:
        session.rollback()
        logger.warning("Sample seed failed: %s", exc)
    finally:
        session.close()


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    _seed_sample_data()
    yield


app = FastAPI(title="Peptide Hound", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------

class VendorListing(BaseModel):
    vendor: str
    name: str
    price: float
    url: str
    weight_mg: float
    price_per_mg: float
    last_updated: datetime


class PeptideGroup(BaseModel):
    normalized_name: str
    cheapest_price: float
    cheapest_vendor: str
    cheapest_price_per_mg: float
    vendor_count: int
    listings: List[VendorListing]


class ScrapeResult(BaseModel):
    scraped: int
    vendors: List[dict]
    errors: List[str]
    skipped_no_creds: List[str]


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/products", response_model=List[PeptideGroup])
def get_products():
    session = get_session()
    try:
        all_products = session.query(Product).all()
        groups: dict[str, list] = {}
        for p in all_products:
            groups.setdefault(p.normalized_name, []).append(p)

        result: List[PeptideGroup] = []
        for norm_name, listings in groups.items():
            sorted_l = sorted(listings, key=lambda x: x.price_per_mg)
            cheapest = sorted_l[0]
            result.append(
                PeptideGroup(
                    normalized_name=norm_name,
                    cheapest_price=cheapest.price,
                    cheapest_vendor=cheapest.vendor,
                    cheapest_price_per_mg=cheapest.price_per_mg,
                    vendor_count=len({l.vendor for l in listings}),
                    listings=[
                        VendorListing(
                            vendor=l.vendor,
                            name=l.name,
                            price=l.price,
                            url=l.url,
                            weight_mg=l.weight_mg,
                            price_per_mg=l.price_per_mg,
                            last_updated=l.last_updated,
                        )
                        for l in sorted_l
                    ],
                )
            )

        result.sort(key=lambda x: x.normalized_name)
        return result
    finally:
        session.close()


@app.get("/api/products/{name}", response_model=PeptideGroup)
def get_product(name: str):
    session = get_session()
    try:
        listings = (
            session.query(Product)
            .filter(Product.normalized_name == name)
            .all()
        )
        if not listings:
            raise HTTPException(status_code=404, detail="Product not found")

        sorted_l = sorted(listings, key=lambda x: x.price_per_mg)
        cheapest = sorted_l[0]
        return PeptideGroup(
            normalized_name=name,
            cheapest_price=cheapest.price,
            cheapest_vendor=cheapest.vendor,
            cheapest_price_per_mg=cheapest.price_per_mg,
            vendor_count=len({l.vendor for l in listings}),
            listings=[
                VendorListing(
                    vendor=l.vendor,
                    name=l.name,
                    price=l.price,
                    url=l.url,
                    weight_mg=l.weight_mg,
                    price_per_mg=l.price_per_mg,
                    last_updated=l.last_updated,
                )
                for l in sorted_l
            ],
        )
    finally:
        session.close()


@app.post("/api/scrape", response_model=ScrapeResult)
async def scrape_all():
    return await _run_scrapers()


# ---------------------------------------------------------------------------
# Scraping logic
# ---------------------------------------------------------------------------

async def _run_scrapers() -> dict:
    from .scrapers.base import LoginScraper

    result: dict = {"scraped": 0, "vendors": [], "errors": [], "skipped_no_creds": []}

    async with httpx.AsyncClient() as client:
        instances = [cls(client) for cls in SCRAPER_CLASSES]
        outcomes = await asyncio.gather(
            *[s.scrape() for s in instances], return_exceptions=True
        )

    session = get_session()
    try:
        for scraper, outcome in zip(instances, outcomes):
            # Detect login scrapers that were skipped due to missing credentials
            if (
                isinstance(scraper, LoginScraper)
                and isinstance(outcome, list)
                and len(outcome) == 0
                and scraper._creds() is None
            ):
                result["skipped_no_creds"].append(scraper.vendor_name)
                continue

            if isinstance(outcome, Exception):
                result["errors"].append(f"{scraper.vendor_name}: {outcome}")
                continue

            session.execute(
                delete(Product).where(Product.vendor == scraper.vendor_name)
            )

            count = 0
            for pd in outcome:
                session.add(
                    Product(
                        vendor=pd.vendor,
                        name=pd.name,
                        normalized_name=normalize_name(pd.name),
                        price=pd.price,
                        url=pd.url,
                        weight_mg=pd.weight_mg,
                        price_per_mg=pd.price_per_mg,
                        last_updated=datetime.utcnow(),
                    )
                )
                count += 1

            result["scraped"] += count
            result["vendors"].append({"vendor": scraper.vendor_name, "count": count})

        session.commit()
    except Exception as exc:
        session.rollback()
        result["errors"].append(f"DB commit error: {exc}")
    finally:
        session.close()

    return result


# ---------------------------------------------------------------------------
# Static frontend — MUST be mounted after all API routes
# ---------------------------------------------------------------------------

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
