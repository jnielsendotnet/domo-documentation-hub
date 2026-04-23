#!/usr/bin/env python3
"""
Batch nav update: adds ~140 articles across EN, JA, DE, ES, FR.
Run from the repo root: python3 update_nav.py
"""
import json

INPUT = "docs.json"

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

langs = data["navigation"]["languages"]


# ── helpers ──────────────────────────────────────────────────────────────────

def get_lang(code):
    for l in langs:
        if l.get("language") == code:
            return l
    raise KeyError(f"language '{code}' not found")

def get_tab(lang, name):
    for t in lang.get("tabs", []):
        if t.get("tab") == name:
            return t
    raise KeyError(f"tab '{name}' not found in {lang['language']}")

def get_group(pages, name):
    """Return the first dict in pages whose 'group' key equals name."""
    for p in pages:
        if isinstance(p, dict) and p.get("group") == name:
            return p
    raise KeyError(f"group '{name}' not found")

def idx_of_group(pages, name):
    for i, p in enumerate(pages):
        if isinstance(p, dict) and p.get("group") == name:
            return i
    raise KeyError(f"group '{name}' index not found")

def idx_of_page(pages, path):
    for i, p in enumerate(pages):
        if p == path:
            return i
    raise KeyError(f"page '{path}' not found")

def insert_before_group(pages, group_name, item):
    i = idx_of_group(pages, group_name)
    pages.insert(i, item)

def insert_after_group(pages, group_name, item):
    i = idx_of_group(pages, group_name)
    pages.insert(i + 1, item)

def insert_after_page(pages, page_path, item):
    i = idx_of_page(pages, page_path)
    pages.insert(i + 1, item)

def insert_before_last_group(pages, item):
    """Insert item before the last group-object in pages (before trailing subgroups)."""
    for i in range(len(pages) - 1, -1, -1):
        if isinstance(pages[i], dict) and "group" in pages[i]:
            pages.insert(i, item)
            return
    pages.append(item)


# ═══════════════════════════════════════════════════════════════════════════════
# ENGLISH
# ═══════════════════════════════════════════════════════════════════════════════

en = get_lang("en")
en_kb  = get_tab(en, "Knowledge Base")
en_rn  = get_tab(en, "Release Notes")

# ── Release Notes: Minor Release Notes as top-level page ─────────────────────
insert_after_page(en_rn["pages"], "s/article/Current-Release-Notes",
                  "s/article/000005908")

# ── Connect & Integrate ───────────────────────────────────────────────────────
en_ci   = get_group(en_kb["pages"], "Connect & Integrate")
en_ctd  = get_group(en_ci["pages"], "Connect Data to Domo")

# Snowflake
en_snowflake = get_group(get_group(en_ctd["pages"], "Cloud Data Warehouses")["pages"], "Snowflake")
en_snowflake["pages"].append("s/article/1500010166282")

# Workbench 5
en_wb5 = get_group(get_group(en_ctd["pages"], "On-premises Systems")["pages"], "Workbench 5")
en_wb5["pages"].extend([
    "s/article/000005219",
    "s/article/000005234",
    "s/article/000005248",
    "s/article/360048000154",
    "s/article/360056669354",
    "s/article/360062446514",
    "s/article/4406022964375",
    "s/article/4407022160791",
])

# Data Providers A-B
en_ab = get_group(en_ctd["pages"], "Data Providers A-B")
insert_before_group(en_ab["pages"], "Adobe",   "s/article/000005426")
get_group(en_ab["pages"], "Amazon")["pages"].append("s/article/4405291644311")
get_group(en_ab["pages"], "Apple")["pages"].extend([
    "s/article/000006053",
    "s/article/360057028014",
])
get_group(en_ab["pages"], "Box")["pages"].append("s/article/000005947")

# Data Providers C-F
en_cf = get_group(en_ctd["pages"], "Data Providers C-F")
insert_before_group(en_cf["pages"], "Cvent", "s/article/360042926534")
# Cvent index shifted by 1; insert 000006013 right after Campaigner
i_camp = idx_of_page(en_cf["pages"], "s/article/360042926534")
en_cf["pages"].insert(i_camp + 1, "s/article/000006013")

# Data Providers G-K
get_group(get_group(en_ctd["pages"], "Data Providers G-K")["pages"], "Google")["pages"].append(
    "s/article/000006016"
)

# Data Providers L-P
en_lp = get_group(en_ctd["pages"], "Data Providers L-P")
insert_before_group(en_lp["pages"], "LinkedIn", "s/article/4409512475927")
get_group(en_lp["pages"], "NetSuite")["pages"].append("s/article/360043437533")
en_lp["pages"].extend([
    "s/article/000005941",
    "s/article/000006000",
])

# Data Providers Q-S
en_qs = get_group(en_ctd["pages"], "Data Providers Q-S")
get_group(en_qs["pages"], "Salesforce")["pages"].append("s/article/000005931")
insert_after_group(en_qs["pages"], "Sage Intacct", "s/article/360043437633")
get_group(en_qs["pages"], "SAP")["pages"].append("s/article/360043437653")

# Data Providers T-Z and #
en_tz = get_group(en_ctd["pages"], "Data Providers T-Z and #")
insert_before_group(en_tz["pages"], "Vertica",  "s/article/360042928054")
insert_after_group(en_tz["pages"],  "Workfront", "s/article/360042930294")

# ── Transform & Manage ────────────────────────────────────────────────────────
en_tm = get_group(en_kb["pages"], "Transform & Manage")

# Magic ETL > Tiles
en_tiles = get_group(
    get_group(
        get_group(en_tm["pages"], "Transform Data in Domo")["pages"],
        "Magic ETL"
    )["pages"],
    "Tiles"
)
en_tiles["pages"].append("s/article/000006036")

# Manage Data in Domo — insert before Data Center Overview subgroup
en_manage = get_group(en_tm["pages"], "Manage Data in Domo")
insert_before_group(en_manage["pages"], "Data Center Overview", "s/article/000005946")

# ── Visualize & Interact ──────────────────────────────────────────────────────
en_viz = get_group(en_kb["pages"], "Visualize & Interact")

en_chart_types = get_group(
    get_group(en_viz["pages"], "Build Visualization Cards in Analyzer")["pages"],
    "Chart Types for Visualization Cards"
)
get_group(en_chart_types["pages"], "Area and Bar Charts")["pages"].append(
    "s/article/360043428993"
)
get_group(en_chart_types["pages"], "Tables, Textboxes, and Map Charts")["pages"].append(
    "s/article/360042924634"
)

get_group(en_viz["pages"], "Other Card Types (Doc, Notebook, and Sumo Cards)")["pages"].append(
    "s/article/360043430173"
)

get_group(en_viz["pages"], "Card and Dashboard Management")["pages"].extend([
    "s/article/360042932994",
    "s/article/360042933074",
    "s/article/360043440133",
    "s/article/360043440173",
])

# ── Automate ──────────────────────────────────────────────────────────────────
get_group(
    get_group(en_kb["pages"], "Automate")["pages"],
    "Workflows"
)["pages"].append("s/article/000005369")

# ── Distribute > Apps ─────────────────────────────────────────────────────────
en_apps = get_group(get_group(en_kb["pages"], "Distribute")["pages"], "Apps")
insert_before_group(en_apps["pages"], "App Studio", "s/article/1500000196462")

# ── General Information > Appstore > Available Apps (Geocoder) ───────────────
en_avail = get_group(
    get_group(
        get_group(en_kb["pages"], "General Information")["pages"],
        "Appstore"
    )["pages"],
    "Available Apps"
)
insert_before_group(en_avail["pages"], "QuickStart Apps", "s/article/000005121")


# ═══════════════════════════════════════════════════════════════════════════════
# JAPANESE
# ═══════════════════════════════════════════════════════════════════════════════

jp = get_lang("jp")
jp_kb  = get_tab(jp, "Knowledge Base")
jp_rn  = get_tab(jp, "Release Notes")
jp_wel = get_tab(jp, "Welcome")

# ── Release Notes: rename 2025 → 2025-2026, add 5 articles ───────────────────
jp_archived = get_group(jp_rn["pages"], "Archived Feature Release Notes")
jp_2025 = get_group(jp_archived["pages"], "2025")
jp_2025["group"] = "2025-2026"
jp_2025["pages"].extend([
    "ja/s/article/000005877",
    "ja/s/article/000005861",
    "ja/s/article/000005924",
    "ja/s/article/000006035",
    "ja/s/article/000005934",
])

# ── Welcome > Getting Started ─────────────────────────────────────────────────
jp_gs = get_group(jp_wel["pages"], "Getting Started")
jp_gs["pages"].extend([
    "ja/s/article/360043442453",
    "ja/s/article/000005878",
])

# ── Connect & Integrate ───────────────────────────────────────────────────────
jp_ci  = get_group(jp_kb["pages"], "Connect & Integrate")
jp_ctd = get_group(jp_ci["pages"], "Connect Data to Domo")

# Cloud Data Warehouses: add 000005871 after 4412849158167
jp_cdw = get_group(jp_ctd["pages"], "Cloud Data Warehouses")
insert_after_page(jp_cdw["pages"], "ja/s/article/4412849158167",
                  "ja/s/article/000005871")

# Snowflake
jp_snow = get_group(jp_cdw["pages"], "Snowflake")
jp_snow["pages"].extend([
    "ja/s/article/000005841",
    "ja/s/article/360042931834",
    "ja/s/article/1500010166282",
])

# Workbench 5
jp_wb5 = get_group(get_group(jp_ctd["pages"], "On-premises Systems")["pages"], "Workbench 5")
jp_wb5["pages"].extend([
    "ja/s/article/000005219",
    "ja/s/article/000005234",
    "ja/s/article/360048000154",
    "ja/s/article/360056669354",
    "ja/s/article/360062446514",
    "ja/s/article/4406022964375",
])

# General Connector Information
get_group(jp_ctd["pages"], "General Connector Information")["pages"].append(
    "ja/s/article/000005825"
)

# Data Providers A-B
jp_ab = get_group(jp_ctd["pages"], "Data Providers A-B")
get_group(jp_ab["pages"], "Adobe")["pages"].append("ja/s/article/360042929154")
get_group(jp_ab["pages"], "Apple")["pages"].append("ja/s/article/360042928554")

# Data Providers C-F
jp_cf = get_group(jp_ctd["pages"], "Data Providers C-F")
insert_before_group(jp_cf["pages"], "Cvent", "ja/s/article/360042926534")

# Data Providers G-K
get_group(
    get_group(jp_ctd["pages"], "Data Providers G-K")["pages"], "Google"
)["pages"].append("ja/s/article/000005794")

# Data Providers L-P
jp_lp = get_group(jp_ctd["pages"], "Data Providers L-P")
insert_before_group(jp_lp["pages"], "LinkedIn", "ja/s/article/4409512475927")
get_group(jp_lp["pages"], "Marketo")["pages"].append("ja/s/article/360057028474")
get_group(jp_lp["pages"], "NetSuite")["pages"].append("ja/s/article/360043437533")

# Data Providers Q-S
jp_qs = get_group(jp_ctd["pages"], "Data Providers Q-S")
get_group(jp_qs["pages"], "ServiceNow")["pages"].append("ja/s/article/000005387")
insert_after_group(jp_qs["pages"], "Sage Intacct", "ja/s/article/360043437633")
get_group(jp_qs["pages"], "SAP")["pages"].append("ja/s/article/360043437653")

# Data Providers T-Z and #
jp_tz = get_group(jp_ctd["pages"], "Data Providers T-Z and #")
insert_before_group(jp_tz["pages"], "Vertica",  "ja/s/article/360042928054")
get_group(jp_tz["pages"], "Workfront")["pages"].append("ja/s/article/360043435113")

# ── Visualize & Interact ──────────────────────────────────────────────────────
jp_viz = get_group(jp_kb["pages"], "Visualize & Interact")

jp_build_viz = get_group(jp_viz["pages"], "Build Visualization Cards in Analyzer")

# "Breast Mode" group (existing typo in nav — leave name as-is)
get_group(jp_build_viz["pages"], "Breast Mode")["pages"].append(
    "ja/s/article/360043430033"
)

jp_chart_types_jp = get_group(jp_viz["pages"], "Chart Types for Visualization Cards")
get_group(jp_chart_types_jp["pages"], "Area and Bar Charts")["pages"].append(
    "ja/s/article/360043428993"
)

get_group(jp_viz["pages"], "Card and Dashboard Management")["pages"].extend([
    "ja/s/article/360042932994",
    "ja/s/article/360042933074",
])

get_group(jp_viz["pages"], "Slideshow Publications")["pages"].append(
    "ja/s/article/000005239"
)

# 360042937874 at the very bottom of Visualize & Interact (after Slideshow Publications)
jp_viz["pages"].append("ja/s/article/360042937874")

# ── General Information > Appstore > Available Apps ──────────────────────────
jp_avail = get_group(
    get_group(
        get_group(jp_kb["pages"], "General Information")["pages"],
        "Appstore"
    )["pages"],
    "Available Apps"
)
# Insert new apps before QuickStart Apps subgroup
for article in [
    "ja/s/article/360042933474",   # Digital Traffic App
    "ja/s/article/360042933874",   # Marketing Attribution App
    "ja/s/article/360042934074",   # Sales Leaderboard App
    "ja/s/article/360043438793",   # Talent Pipeline App
    "ja/s/article/360044364413",   # Marketing Attribution | 実装ガイド
    "ja/s/article/360056655734",   # Productivity Indicators App
    "ja/s/article/000005121",      # Geocoder | ユーザーガイド
]:
    insert_before_last_group(jp_avail["pages"], article)


# ═══════════════════════════════════════════════════════════════════════════════
# FRENCH — convert pages→tabs, add 2025 release notes, add KB tab
# ═══════════════════════════════════════════════════════════════════════════════

fr = get_lang("fr")
fr_rn_group = get_group(fr["pages"], "Release Notes")
fr_rn_pages = fr_rn_group["pages"]

# Add to FR 2025 group
fr_2025 = get_group(
    get_group(fr_rn_pages, "Archived Feature Release Notes")["pages"], "2025"
)
fr_2025["pages"].extend([
    "fr/s/article/000005904",
    "fr/s/article/000005924",
    "fr/s/article/000006035",
])

fr_kb_pages = [
    "fr/s/article/360043428293",   # Combiner des DataSets à l'aide d'une DataFusion
    "fr/s/article/360043434433",   # Connecteur Facebook
    "fr/s/article/360042922994",   # Création d'un DataFlow SQL
    "fr/s/article/360043430513",   # Création d'une alerte personnalisée pour une carte KPI
    "fr/s/article/360042934294",   # Création et gestion des groupes d'utilisateurs
    "fr/s/article/360042934614",   # Création et suppression des politiques PDP
    "fr/s/article/360042926154",   # Meilleures pratiques de gestion des DataSets
    "fr/s/article/360043437793",   # Partage de contenu à l'aide de diaporamas
]

fr["tabs"] = [
    {"tab": "Release Notes",  "pages": fr_rn_pages},
    {"tab": "Knowledge Base", "pages": fr_kb_pages},
]
del fr["pages"]


# ═══════════════════════════════════════════════════════════════════════════════
# GERMAN — same pattern
# ═══════════════════════════════════════════════════════════════════════════════

de = get_lang("de")
de_rn_group = get_group(de["pages"], "Release Notes")
de_rn_pages = de_rn_group["pages"]

de_2025 = get_group(
    get_group(de_rn_pages, "Archived Feature Release Notes")["pages"], "2025"
)
de_2025["pages"].extend([
    "de/s/article/000005904",
    "de/s/article/000005924",
    "de/s/article/000006035",
])

de_kb_pages = [
    "de/s/article/360043430513",   # Erstellen einer benutzerdefinierten Mitteilung für eine KPI-Karte
    "de/s/article/360042922994",   # Erstellen eines SQL-DataFlows
    "de/s/article/360042934294",   # Erstellen und Verwalten von Benutzergruppen
    "de/s/article/360043434433",   # Facebook-Konnektor
    "de/s/article/360043437793",   # Inhalte mithilfe von Diashows freigeben
    "de/s/article/360043428293",   # Kombinieren von DataSets mit DataFusion
    "de/s/article/360042926154",   # Optimales Vorgehen zum Verwalten von DataSets
    "de/s/article/360042934614",   # PDP-Richtlinien erstellen und löschen
]

de["tabs"] = [
    {"tab": "Release Notes",  "pages": de_rn_pages},
    {"tab": "Knowledge Base", "pages": de_kb_pages},
]
del de["pages"]


# ═══════════════════════════════════════════════════════════════════════════════
# SPANISH — same pattern
# ═══════════════════════════════════════════════════════════════════════════════

es = get_lang("es")
es_rn_group = get_group(es["pages"], "Release Notes")
es_rn_pages = es_rn_group["pages"]

es_2025 = get_group(
    get_group(es_rn_pages, "Archived Feature Release Notes")["pages"], "2025"
)
es_2025["pages"].extend([
    "es/s/article/000005904",
    "es/s/article/000005924",
    "es/s/article/000006035",
])

es_kb_pages = [
    "es/s/article/360043428293",   # Combinación de DataSets mediante DataFusion
    "es/s/article/360043437793",   # Compartir contenido mediante presentaciones
    "es/s/article/360043434433",   # Conector de Facebook
    "es/s/article/360042922994",   # Creación de un DataFlow de SQL
    "es/s/article/360043430513",   # Creación de una alerta personalizada…
    "es/s/article/360042934294",   # Creación y administración de grupos de usuarios
    "es/s/article/360042934614",   # Crear y eliminar políticas de permisos…
]

es["tabs"] = [
    {"tab": "Release Notes",  "pages": es_rn_pages},
    {"tab": "Knowledge Base", "pages": es_kb_pages},
]
del es["pages"]


# ═══════════════════════════════════════════════════════════════════════════════
# Write output
# ═══════════════════════════════════════════════════════════════════════════════

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("docs.json updated successfully.")
