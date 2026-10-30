#!/usr/bin/env python3
"""
Spell Checker & Copy Quality Auditor for Sovereign Nation of Waikiki Site.
Part of the 'spell-check' skill.

Audits:
  1. Typography & spacing anomalies (spaces before punctuation, spaces after <br>, double punctuation)
  2. Intra-node duplicate consecutive words ('the the', 'és és')
  3. Ampersand policy violations ('&' vs 'and' / 'és' per AGENTS.md)
  4. Empty line violations in HTML (per AGENTS.md rule: 0 empty lines)
  5. Hungarian typo, compound hyphenation, and accent audit
  6. English spelling check via native macOS NSSpellChecker (with domain whitelist & UK variant support)
  7. Optional native Hungarian NSSpellChecker (--hu-native)

Usage:
  python3 .agents/skills/spell-check/scripts/audit.py             # Audit all HTML pages
  python3 .agents/skills/spell-check/scripts/audit.py --lang en   # English pages only
  python3 .agents/skills/spell-check/scripts/audit.py --lang hu   # Hungarian pages only
  python3 .agents/skills/spell-check/scripts/audit.py --fix       # Auto-fix safe whitespace anomalies
  python3 .agents/skills/spell-check/scripts/audit.py --verbose   # Verbose output with context snippets
  python3 .agents/skills/spell-check/scripts/audit.py path/to/file.html # Audit specific file(s)
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


def find_root() -> Path:
    """Finds project root by searching upwards for .git or index.html."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / ".git").exists() or (parent / "index.html").exists():
            return parent
    return p.parents[4]


ROOT = find_root()

# --------------------------------------------------------------------------- #
# Domain Whitelist: Lore characters, leaders, brands, geography & abbreviations
# --------------------------------------------------------------------------- #
WHITELIST = {
    # Core Characters & Royal Family
    "waikiki", "waikikire", "waikikin", "waikikiről", "waikikivel", "waikikihez", "waikikit",
    "waikikiek", "waikikiak", "waikikié", "waikikinek", "waikikiben", "waikikis", "waikikian", "waikikians",
    "chease", "chease-nek", "cheasetől", "chease-ről", "chease-zel", "chease-é",
    "raimondo", "raimondót", "raimondónak", "raimondóval", "raimondótól", "raimondóról",
    "raimondóban", "raimondóhoz", "raimondóért", "raimondóé", "raimondóék",
    "selena", "selenát", "selenának", "selenával", "selenától", "selenáról", "selenában", "selenához", "selenáért",
    "relena", "relenának",
    "jessica", "jessicát", "jessicának", "jessicával", "jessicától", "jessicáról", "jessicában",
    "aurelia", "aureliában", "aureliába", "aureliából", "aureliát", "aureliának", "aureliával", "aureliai", "aurelia-i",
    "nova", "darius", "tanz", "posey", "lautner", "lautnert", "lautnerrel", "lautnernek", "lautner's",
    "tyler", "tylert", "tylerrel", "tylernek", "jennifer", "jennifert", "jenniferrel", "jennifernek",
    "angelina", "angelinát", "angelinával", "angelinának", "angelináról",
    "bailey", "baileyt", "baileyvel", "baileynek", "baileyhez", "baileyre", "pickett", "pickettet", "pickett's",
    "wud", "wud-ot", "wud-dal", "wud-ban",
    "walker", "walkert", "walkerrel", "walkernek",

    # Key Lore Figures & Officials
    "zack", "cody", "marcus", "london", "tipton", "tiptonnal", "moseby", "carey", "esteban", "arwin", "kirby",
    "kettlecorn", "kettlecornt", "kettlecornból", "kettlecornban", "kettlecornba",
    "mickey", "haller", "elena", "martinez", "aaron", "shore", "eckhart", "eckhart's",
    "daniel", "hardman", "emily", "whiteborough", "christian", "sewing", "rachel", "zane",
    "zoe", "lawford", "chloe", "bennet", "josh", "earnest", "eleanor", "sui", "yang",
    "alejandro", "ramirez", "julie", "stark", "harris", "cochrane", "john", "bolton",
    "winnefeld", "daniels", "dana", "scottie", "mike", "leavitt", "jason", "furman",
    "nicole", "minetti", "roger", "penrose", "carte", "goodwin", "rick", "santorum",
    "boehner", "morgan", "clark", "matt", "damon", "tom", "kirkman", "jonathan", "moss",
    "monika", "baumann", "teya", "mahana", "jacobbal",

    # World Figures & Celebrities in Lore
    "trump", "trumppal", "trumpot", "trumpnak", "melania", "melaniával", "biden", "obama", "bush",
    "putin", "putyin", "putyint", "putyinnal", "zelensky", "zelenszkij", "macron", "scholz", "kishida", "kisida", "fumio",
    "modi", "erdogan", "assad", "al-assad", "khamenei", "rouhani", "netanyahu", "netanjahu",
    "milei", "mileit", "mileivel", "milei's", "bukele", "lula", "bolsonaro", "castro", "castrónak",
    "fidel", "maduro", "chavez", "morales", "batista", "batistát", "fulgencio", "plenković", "draghi",
    "kenyatta", "uhuru", "meloni", "farage", "carlson", "musk", "muskkal", "thiel", "altman", "gates",
    "yousafzai", "adele", "dicaprio", "dicaprióval", "spears", "spearsszel", "zendaya", "zendayával",
    "crowe", "crowe-val", "styles", "thorne", "justice", "horan", "deutch", "levesque", "taubenfeld",
    "garman", "forrest", "benson", "korine", "hudgens", "cassidy", "meester", "lovato", "pitt", "aniston",
    "jolie", "pahlavi", "salman", "hamdan", "shamsa", "zayed", "nahyan", "henrik", "ivanka",

    # Classical History & Antiquity
    "caesarion", "caesarionnak", "caesarionba", "caesar", "augustus", "hadrian", "trajan",
    "vaikikia", "montezuma", "acamapichtli", "mies", "rohe", "gaudí", "gaudí's", "uffizi",

    # Geography & Landmarks
    "manaus", "manausban", "cancun", "rio", "janeiro", "riói", "bogota", "lima", "quito", "santiago",
    "caracas", "brasilia", "brasília", "brazíliaváros", "montevideo", "asuncion", "asunción",
    "copacabana", "copacabanán", "ipanema", "ipanemán", "corcovado", "maracanã", "sugarloaf",
    "guanabara", "tijuca", "petrópolis", "minas", "gerais", "szantorini", "santorini", "seychelles",
    "seychelle-szigeteken", "seychelle-szigetek", "maldives", "maldív-szigeteken", "giza", "gizai",
    "angkor", "wat", "machu", "picchu", "taktsang", "kilmainham", "moher", "skellig", "kantei",
    "harajuku", "simien", "teide", "chambord", "chenonceau", "amboise", "fushimi", "inari", "elysée",
    "velaa", "laccadive", "tenochtitlan", "chichén", "itzá", "guantánamo", "quebec", "quebecben",
    "phi", "bora", "cálido", "porto", "amazonia", "amazóniai", "brazilia", "chameleon", "kaméleon",
    "kaméleon-sziget", "kaméleon-szigetek", "kaldera", "kalderára", "kalderájára",
    "cerrado", "iguazú", "iguazu", "iguazú-scale", "estrellán", "estrella-n",

    # Tech, Acronyms & Brands
    "cbdc", "maglev", "hyperloop", "hyperloopot", "hyperloop-vonalának", "hyperloop's", "spacex",
    "spacex-szel", "spacex-et", "boeing", "concorde", "airbus", "lockheed", "rolls-royce", "genx-2b67",
    "tesla", "powerpack", "skynet", "gaianova", "titan", "xwb", "mastercard", "smartborder", "saphir",
    "miapolis", "transborder", "versace", "palazzo", "dolce", "gabbana", "casadei", "marchesa",
    "unesco", "unicef", "nato", "nato-ba", "oecd", "mercosur", "unasur", "prosur", "caricom",
    "who", "imf", "gdp", "g8", "g9", "g9-hez", "g20", "cop26", "stem", "bsc", "phd", "ceo", "vip",
    "dna", "rna", "ict", "ev", "mw", "gw", "twh", "km", "km²", "m²", "usd", "eur", "gbp", "huf",
    "w-map", "wnss", "widebody", "supercarrier", "supercarriers", "supercarrier's", "superyacht",
    "superyachts", "paddleboard", "paddleboarded", "paddleboarding", "aquapark", "aquaparkkal",
    "microgrids", "skybridges", "baseload", "overtourism", "superberries", "uncrewed", "exoplanetary",
    "microsystems", "urbanistic", "holidaymakers", "cashlessly", "gini", "mar-a-lago", "mar-a-lago-i",
    "mar-a-lagóban", "l'étoile", "l'océan", "shinkansen", "kaiseki", "churrasco", "appos", "hobbidrónok",
    "drónokhoz", "videópontok", "átváltópontok", "valutabejelentési", "beléptetőkapuknál",
    "árfolyamingadozásokat", "okostelefonos", "interoperabilitást", "kiberbiztonsági", "multispektrális",
    "multimodális", "fotó-", "videó-", "vízalatti", "okoshálózatokat", "médiainnovációra", "napelemgyár",
    "hatékonytalansági", "betegcentrikus", "mintapéldáivá", "okosmodult", "lélegeztetőgépekhez",
    "tech-vállalatot", "vakcinaelosztás", "vakcinadiplomácia", "mikrogravitációs", "zsilipelési",
    "videókonferencián", "fészkelőhelyeit", "narkoterrorizmussal", "maduro-rezsim", "legfotózottabb",
    "antigravitációs", "holdraszállást", "megastruktúrán", "tőkemegfelelési", "csupaszív", "dzsungelmélyi",
    "fellépőruhát", "dizájnon", "elvonulóhelyévé", "igényességű", "természetközeliségben", "szenátorpár",
    "karbonsemleges", "olajexportőreként", "orchideavarietást", "környezetgazdaságtan", "mahagóni",
    "történelmen", "gondolkodása", "székelnek", "kristálytiszta", "megapiramis", "megapiramist",
    "megaberuházás", "karatebajnok",

    # Landing Page (Root index.html) Hungarian Card Vocabulary & Conjunction
    "magyar", "változat", "fedezze", "fel", "nemzeti", "történelmet", "gazdasági", "mutatókat",
    "kormányzati", "modellt", "királyi", "dinasztia", "mindennapjait", "nyissa", "oldalt",
    "minden", "jog", "fenntartva", "és",

    # Real-world figures, leaders, diplomats, judges & lore entities
    "rosada", "msc", "milley", "nieto", "cavanagh", "olmeda", "lemieux", "rehman", "vitter",
    "prieto", "temer", "zambellas", "pardo", "dhalla", "menéndez", "toffoli", "aventador",
    "waverly", "bilderberg", "helu", "bridgit", "mendler", "brangelina", "monde", "sheikha",
    "emiri", "nahyan's", "weddell", "aguas", "calientes", "giorgia", "der", "legolands",
    "heli-skiing", "riverdale", "expeditioner", "expeditioner-class", "kahele", "amazonas",

    # Nature, Ecology, Botanical & Biomes
    "pantanal", "mogotes", "hypersaline", "várzea", "caatinga", "staghorn", "elkhorn",
    "amazonica", "morpho", "firme", "páramo", "puya", "raimondii", "frailejón", "viñales",
    "enriquillo", "lençóis", "heliamphora", "ipê", "mandacaru", "bromeliad", "bromeliads",
    "nicho", "escambray", "anavilhanas", "encontro", "igapó", "chapada", "poço", "encantado",
    "pai", "inácio",

    # Alpine, Ski Paradise, Engineering & Luxury
    "soberano", "pininfarina", "pérignon", "cryo-grid", "cryo-glacier", "cryo-dome",
    "cryo-recovery", "cryo-cooled", "cryo-cooling", "tiltrotor", "tiltrotors", "heli-hub",
    "heliski", "snowpark", "superpipe", "microgrid", "microgrids",

    # Space & Advanced Aeronautics
    "wsa", "its", "nrho", "retropropulsion", "aerospike", "skyport",

    # Antiquity & Regional Lore Additions
    "portus", "mesoamerican"
}

# --------------------------------------------------------------------------- #
# HTML Text Extractor
# --------------------------------------------------------------------------- #
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines: list[tuple[int, str]] = []
        self.in_skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "code", "pre", "svg"):
            self.in_skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "code", "pre", "svg"):
            self.in_skip = False

    def handle_data(self, data):
        if self.in_skip:
            return
        t = data.strip()
        if t:
            self.lines.append((self.getpos()[0], t))


# --------------------------------------------------------------------------- #
# 1. Punctuation Spacing & Tag Boundary Check
# --------------------------------------------------------------------------- #
def check_punctuation_spacing(html_path: Path, fix: bool = False) -> tuple[list[str], bool]:
    issues = []
    content = html_path.read_text(encoding="utf-8")
    modified = False

    # Stray space after <br>
    br_matches = list(re.finditer(r"<br>\s+([A-Za-zÁ-ž])", content))
    for m in br_matches:
        start = max(0, m.start() - 20)
        end = min(len(content), m.end() + 20)
        issues.append(f"{html_path.name}: Stray space after <br>: \"{content[start:end]}\"")

    if fix and br_matches:
        content = re.sub(r"<br>\s+([A-Za-zÁ-ž])", r"<br>\1", content)
        modified = True

    # Space before closing tag and punctuation (e.g. </em> .)
    tag_punc_matches = list(re.finditer(r"</([a-z0-9]+)>\s+([,.:;?!])", content, re.IGNORECASE))
    for m in tag_punc_matches:
        start = max(0, m.start() - 20)
        end = min(len(content), m.end() + 20)
        issues.append(f"{html_path.name}: Stray space before punctuation after tag: \"{content[start:end]}\"")

    if fix and tag_punc_matches:
        content = re.sub(r"</([a-z0-9]+)>\s+([,.:;?!])", r"</\1>\2", content)
        modified = True

    # Space before punctuation in plain text (e.g. "word , next")
    extractor = TextExtractor()
    extractor.feed(content)
    for line_num, text in extractor.lines:
        for m in re.finditer(r"([A-Za-zÁ-ž0-9])\s+([,.:;?!])(?=\s|$)", text):
            if m.group(2) == "." and ".." in text:
                continue
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            issues.append(f"{html_path.name}:{line_num}: Stray space before '{m.group(2)}' in \"...{text[start:end]}...\"")

    # Double commas or unexpected double periods (not ellipsis ...)
    for line_num, text in extractor.lines:
        for m in re.finditer(r",,|(?<!\.)\.\.(?!\.)", text):
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            issues.append(f"{html_path.name}:{line_num}: Double punctuation '{m.group(0)}' in \"...{text[start:end]}...\"")

    if modified:
        html_path.write_text(content, encoding="utf-8")

    return issues, modified


# --------------------------------------------------------------------------- #
# 2. Duplicate Consecutive Words Check
# --------------------------------------------------------------------------- #
VALID_REPEATS = {"phi", "bora", "az", "ha"}  # e.g. "Phi Phi", "Bora Bora", "Az az este"

def check_duplicate_words(html_path: Path) -> list[str]:
    issues = []
    content = html_path.read_text(encoding="utf-8")
    extractor = TextExtractor()
    extractor.feed(content)

    for line_num, text in extractor.lines:
        for m in re.finditer(r"(?<![A-Za-zÁ-ž\-])\b([A-Za-zÁ-ž]{2,})\s+\1\b(?![A-Za-zÁ-ž\-])", text, re.IGNORECASE):
            w = m.group(1).lower()
            if w in VALID_REPEATS:
                continue
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            issues.append(f"{html_path.name}:{line_num}: Duplicate consecutive word '{m.group(0)}' in \"...{text[start:end]}...\"")
    return issues


# --------------------------------------------------------------------------- #
# 3. Ampersand Policy Check (AGENTS.md rule: prefer 'and' / 'és' over '&')
# --------------------------------------------------------------------------- #
ALLOWED_AMPERSANDS = {
    "Walker Finance & Insurance Holding",
    "R&D",
    "Q&A",
    "AT&T",
    "S&P",
    "&copy;",
    "&amp;",
    "&nbsp;",
    "&quot;",
    "&lt;",
    "&gt;",
}

def check_ampersands(html_path: Path) -> list[str]:
    issues = []
    content = html_path.read_text(encoding="utf-8")
    temp = content
    for allowed in ALLOWED_AMPERSANDS:
        temp = temp.replace(allowed, "")

    extractor = TextExtractor()
    extractor.feed(temp)

    for line_num, text in extractor.lines:
        if "&" in text:
            for m in re.finditer(r"(?:[A-Za-zÁ-ž]+(?:\s+&|\s*&\s*)[A-Za-zÁ-ž]+)", text):
                val = m.group(0).strip()
                issues.append(f"{html_path.name}:{line_num}: Disallowed ampersand in copy '{val}' &mdash; use 'and'/'és'")
    return issues


# --------------------------------------------------------------------------- #
# 4. Empty Lines Validator (AGENTS.md rule: 0 empty lines in HTML)
# --------------------------------------------------------------------------- #
def check_empty_lines(html_path: Path) -> list[str]:
    issues = []
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f, 1):
            if line.strip() == "":
                issues.append(f"{html_path.name}:{idx}: Empty line detected in HTML document")
    return issues


# --------------------------------------------------------------------------- #
# 5. Hungarian Typo & Accents Quality Audit
# --------------------------------------------------------------------------- #
HUNGARIAN_BAD_FORMS = {
    r'\begészég\w*\b': 'egészség',
    r'\bfelelőség\b': 'felelősség',
    r'\bbiztosit\b': 'biztosít',
    r'\bbiztositja\b': 'biztosítja',
    r'\bbiztositani\b': 'biztosítani',
    r'\bbiztositás\b': 'biztosítás',
    r'\bkülömböző\b': 'különböző',
    r'\begyenlőre\b': 'egyelőre',
    r'\bmindíg\b': 'mindig',
    r'\bdícséret\b': 'dicséret',
    r'\butan[n]+a\b': 'utána',
    r'\blessz\b': 'lesz',
    r'\bsikerűlt\b': 'sikerült',
    r'\bkissebb\b': 'kisebb',
    r'\butlevél\b': 'útlevél',
    r'\ballampolgár\w*\b': 'állampolgár',
    r'\bkormany\w*\b': 'kormány',
    r'\bvalasztás\w*\b': 'választás',
    r'\bintzmény\w*\b': 'intézmény',
    r'\bmahágóni\w*\b': 'mahagóni',
    r'\bkaldéra\w*\b': 'kaldera',
    r'\bszékhelnek\b': 'székelnek',
    r'\bgondolkása\b': 'gondolkodása',
    r'\btörténelemen\b': 'történelmen',
}

UNACCENTED_HU_WORDS = {
    "biztonsag": "biztonság",
    "orszag": "ország",
    "allam": "állam",
    "polgar": "polgár",
    "intezmeny": "intézmény",
    "mukodes": "működés",
    "tarsadalom": "társadalom",
    "gazdasag": "gazdaság",
    "fejlodes": "fejlődés",
    "torveny": "törvény",
    "felelos": "felelős",
    "kotelezettseg": "kötelezettség",
    "kerdes": "kérdés",
    "terulet": "terület"
}

def check_hungarian_copy(html_path: Path) -> list[str]:
    issues = []
    content = html_path.read_text(encoding="utf-8")
    extractor = TextExtractor()
    extractor.feed(content)

    for line_num, text in extractor.lines:
        for m in re.finditer(r'\b[A-Za-zÁ-ž]*([bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ])\1\1[A-Za-zÁ-ž]*\b', text):
            word = m.group(0)
            if word.isupper() and all(c in "IVXLCDM" for c in word):
                continue
            issues.append(f"{html_path.name}:{line_num}: Triple consonant '{word}'")

        for pat, corr in HUNGARIAN_BAD_FORMS.items():
            for m in re.finditer(pat, text, re.IGNORECASE):
                w = m.group(0)
                if w.lower() != corr.lower():
                    issues.append(f"{html_path.name}:{line_num}: Typo '{w}' -> expected '{corr}'")

        for m in re.finditer(r'\b[a-zA-Z]{3,}\b', text):
            w = m.group(0).lower()
            if w in UNACCENTED_HU_WORDS:
                corr = UNACCENTED_HU_WORDS[w]
                issues.append(f"{html_path.name}:{line_num}: Missing accent '{w}' -> expected '{corr}'")

        # Disallow double hyphenation in compound words (e.g., Covid-19-világjárvány)
        for m in re.finditer(r'\bCovid-19-[a-zA-ZáéíóöőúüűÁÉÍÓÖŐÚÜŰ]+\b', text, re.IGNORECASE):
            word = m.group(0)
            corr = word[:8] + " " + word[9:]
            issues.append(f"{html_path.name}:{line_num}: Disallowed double hyphen '{word}' -> expected '{corr}'")

        # Disallow en-dash ('–', U+2013) -> use standard hyphen ('-')
        if '\u2013' in text:
            issues.append(f"{html_path.name}:{line_num}: Disallowed en-dash ('\u2013') -> use standard hyphen ('-')")

    return issues


# --------------------------------------------------------------------------- #
# 6. Native NSSpellChecker Driver (macOS Swift Helper)
# --------------------------------------------------------------------------- #
SWIFT_SPELL_SRC = """
import Foundation
import AppKit

let checker = NSSpellChecker.shared

guard CommandLine.arguments.count > 1,
      let data = FileManager.default.contents(atPath: CommandLine.arguments[1]),
      let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
      let lang = json["lang"] as? String,
      let files = json["files"] as? [[String: Any]],
      let whitelist = json["whitelist"] as? [String] else {
    exit(1)
}

let whitelistSet = Set(whitelist.map { $0.lowercased() })
var results: [[String: Any]] = []

for fileObj in files {
    guard let file = fileObj["file"] as? String,
          let lines = fileObj["lines"] as? [[String: Any]] else { continue }
    
    for lineObj in lines {
        guard let lineNum = lineObj["line"] as? Int,
              let text = lineObj["text"] as? String else { continue }
        
        let nsText = text as NSString
        var start = 0
        while start < nsText.length {
            let range = checker.checkSpelling(of: text, startingAt: start, language: lang, wrap: false, inSpellDocumentWithTag: 0, wordCount: nil)
            if range.location == NSNotFound || range.length == 0 { break }
            
            let word = nsText.substring(with: range)
            start = range.location + range.length
            
            let wordClean = word.trimmingCharacters(in: CharacterSet.punctuationCharacters).lowercased()
            if wordClean.isEmpty || Double(wordClean) != nil || whitelistSet.contains(wordClean) || wordClean.count <= 1 {
                continue
            }
            
            let parts = wordClean.split(separator: "-").map { String($0) }
            if parts.count > 1 && parts.allSatisfy({ whitelistSet.contains($0) }) {
                continue
            }
            
            let ctxStart = max(0, range.location - 30)
            let ctxEnd = min(nsText.length, range.location + range.length + 30)
            let ctx = nsText.substring(with: NSRange(location: ctxStart, length: ctxEnd - ctxStart))
            
            let guesses = checker.guesses(forWordRange: range, in: text, language: lang, inSpellDocumentWithTag: 0) ?? []
            let topGuesses = Array(guesses.prefix(3))
            
            results.append([
                "file": file,
                "line": lineNum,
                "word": word,
                "suggestions": topGuesses,
                "context": ctx
            ])
        }
    }
}

if let outData = try? JSONSerialization.data(withJSONObject: results) {
    FileHandle.standardOutput.write(outData)
}
"""

def run_native_spell_check(files_payload: list[dict], lang: str) -> list[dict]:
    """Runs NSSpellChecker via a cached or temporary Swift runner."""
    with tempfile.NamedTemporaryFile(suffix=".swift", mode="w", encoding="utf-8", delete=False) as sf:
        sf.write(SWIFT_SPELL_SRC)
        swift_path = sf.name

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", encoding="utf-8", delete=False) as pf:
        payload = {
            "lang": lang,
            "whitelist": sorted(list(WHITELIST)),
            "files": files_payload
        }
        json.dump(payload, pf)
        payload_path = pf.name

    try:
        proc = subprocess.run(["swift", swift_path, payload_path], capture_output=True, text=True)
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout)
    finally:
        try:
            os.remove(swift_path)
            os.remove(payload_path)
        except OSError:
            pass

    return []


# --------------------------------------------------------------------------- #
# File Payloads & Discovery
# --------------------------------------------------------------------------- #
def collect_html_files(root: Path, lang: str) -> list[Path]:
    files = []
    if lang in ("en", "all"):
        files.extend((root / "en").glob("*.html"))
        files.extend((root / "en" / "bio").glob("*.html"))
        if (root / "index.html").exists():
            files.append(root / "index.html")
    if lang in ("hu", "all"):
        files.extend((root / "hu").glob("*.html"))
        files.extend((root / "hu" / "bio").glob("*.html"))
    return sorted(files)


def build_file_payloads(files: list[Path]) -> list[dict]:
    payloads = []
    for f in files:
        extractor = TextExtractor()
        content = f.read_text(encoding="utf-8", errors="ignore")
        extractor.feed(content)
        lines_data = [{"line": lno, "text": txt} for lno, txt in extractor.lines]
        try:
            rel = str(f.relative_to(ROOT))
        except ValueError:
            rel = f.name
        payloads.append({"file": rel, "lines": lines_data})
    return payloads


# --------------------------------------------------------------------------- #
# Main Entry Point
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description="Waikiki Site Comprehensive Copy & Spell Checker")
    parser.add_argument("--lang", choices=["all", "en", "hu"], default="all", help="Language to check (default: all)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe whitespace anomalies")
    parser.add_argument("--hu-native", action="store_true", help="Run experimental native NSSpellChecker on Hungarian")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose progress output")
    parser.add_argument("paths", nargs="*", help="Optional specific HTML files to inspect")
    args = parser.parse_args()

    print("=================================================================")
    print(" Sovereign Nation of Waikiki — Site Copy & Spell Checker")
    print("=================================================================")

    if args.paths:
        html_files = [Path(p).resolve() for p in args.paths if p.endswith(".html")]
    else:
        html_files = collect_html_files(ROOT, args.lang)

    print(f"Auditing {len(html_files)} HTML file(s)...")

    total_issues = 0

    # 1. Punctuation & Spacing Anomalies
    punc_issues = []
    for f in html_files:
        issues, modified = check_punctuation_spacing(f, fix=args.fix)
        if modified and args.verbose:
            print(f"  [FIXED] {f.name}: Auto-corrected spacing anomalies")
        punc_issues.extend(issues)

    if punc_issues:
        print(f"\n[!] Spacing & Typography Anomalies ({len(punc_issues)}):")
        for iss in punc_issues:
            print(f"    - {iss}")
        total_issues += len(punc_issues)
    else:
        print("  [OK] No typography or punctuation spacing anomalies.")

    # 2. Duplicate Words
    dup_issues = []
    for f in html_files:
        dup_issues.extend(check_duplicate_words(f))

    if dup_issues:
        print(f"\n[!] Duplicate Consecutive Words ({len(dup_issues)}):")
        for iss in dup_issues:
            print(f"    - {iss}")
        total_issues += len(dup_issues)
    else:
        print("  [OK] No accidental duplicate consecutive words.")

    # 3. Ampersand Policy
    amp_issues = []
    for f in html_files:
        amp_issues.extend(check_ampersands(f))

    if amp_issues:
        print(f"\n[!] Ampersand Policy Violations ({len(amp_issues)}):")
        for iss in amp_issues:
            print(f"    - {iss}")
        total_issues += len(amp_issues)
    else:
        print("  [OK] Ampersand policy satisfied (prefer 'and' / 'és').")

    # 4. Empty Lines Rule
    empty_line_issues = []
    for f in html_files:
        empty_line_issues.extend(check_empty_lines(f))

    if empty_line_issues:
        print(f"\n[!] Empty Lines Detected ({len(empty_line_issues)}):")
        for iss in empty_line_issues[:10]:
            print(f"    - {iss}")
        if len(empty_line_issues) > 10:
            print(f"    ... and {len(empty_line_issues) - 10} more.")
        total_issues += len(empty_line_issues)
    else:
        print("  [OK] 0 empty lines across all HTML documents.")

    # 5. Hungarian Typo & Accents Audit
    hu_files = [f for f in html_files if "hu" in f.parts or (f.parent == ROOT and f.name == "index.html")]
    if hu_files and args.lang in ("hu", "all"):
        hu_typos = []
        for f in hu_files:
            hu_typos.extend(check_hungarian_copy(f))
        if hu_typos:
            print(f"\n[!] Hungarian Typo / Accent Warnings ({len(hu_typos)}):")
            for iss in hu_typos:
                print(f"    - {iss}")
            total_issues += len(hu_typos)
        else:
            print("  [OK] Hungarian text verified — no typo patterns or accent anomalies.")

    # 6. English Spelling via Native NSSpellChecker
    en_files = [f for f in html_files if "en" in f.parts or (f.parent == ROOT and f.name == "index.html")]
    if en_files and args.lang in ("en", "all"):
        print("\nChecking English spelling...")
        en_payloads = build_file_payloads(en_files)
        en_results = run_native_spell_check(en_payloads, "en_US")
        uk_suffixes = (
            "ise", "ised", "ises", "ising", "isation", "isations", "isational", "isable",
            "our", "ours", "oured", "ouring",
            "ence", "ences",
            "re", "res", "red", "ring",
            "programme", "programmes",
            "lling", "lled",
            "yse", "ysed", "yses", "ysing",
        )
        uk_words = {
            "foetus", "foetuses", "artefact", "artefacts", "manoeuvre", "manoeuvres",
            "teleferic", "innovatively", "sovereigntist", "infocommunication"
        }
        filtered_en = []
        for r in en_results:
            w = r["word"].lower().strip(".,;:\"'!?")
            if w in uk_words or any(w.endswith(sfx) for sfx in uk_suffixes):
                continue
            filtered_en.append(r)

        if filtered_en:
            print(f"[!] English Spelling Warnings ({len(filtered_en)}):")
            for r in filtered_en:
                suggs = ", ".join(r["suggestions"]) if r["suggestions"] else "none"
                print(f"    - {r['file']}:{r['line']} '{r['word']}' (suggestions: {suggs})")
                if args.verbose:
                    print(f"      Context: \"...{r['context']}...\"")
            total_issues += len(filtered_en)
        else:
            print("  [OK] English text verified — no spelling errors found.")

    # 7. Optional Native Hungarian Spell Check
    if args.hu_native and hu_files:
        print("\nChecking native Hungarian spelling (experimental)...")
        hu_payloads = build_file_payloads([f for f in hu_files if f.name != "index.html"])
        hu_results = run_native_spell_check(hu_payloads, "hu")
        if hu_results:
            print(f"[!] Native Hungarian Warnings ({len(hu_results)}):")
            for r in hu_results[:20]:
                suggs = ", ".join(r["suggestions"]) if r["suggestions"] else "none"
                print(f"    - {r['file']}:{r['line']} '{r['word']}' (suggestions: {suggs})")
            if len(hu_results) > 20:
                print(f"    ... and {len(hu_results) - 20} more.")
            total_issues += len(hu_results)
        else:
            print("  [OK] Native Hungarian text verified.")

    print("\n-----------------------------------------------------------------")
    if total_issues == 0:
        print("[SUCCESS] All checks passed! Site copy is 100% clean.")
        print("-----------------------------------------------------------------")
        sys.exit(0)
    else:
        print(f"[FAIL] Found {total_issues} issue(s) that require attention.")
        print("-----------------------------------------------------------------")
        sys.exit(1)


if __name__ == "__main__":
    main()
