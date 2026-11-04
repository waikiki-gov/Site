#!/usr/bin/env python3
"""
Generate standalone SVG illustrations for banking-system.html.

Generates:
1. icons/banking/network-en.svg & network-hu.svg (1160x520) - Tripartite Financial Network
2. icons/banking/rates-en.svg & rates-hu.svg (1160x440) - Dual Benchmark Rates & Stability Corridor
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "icons" / "banking"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_network_svg(locale: str) -> str:
    is_hu = locale == "hu"
    apex_title = "WAIKIKI NEMZETI BANKJA" if is_hu else "NATIONAL BANK OF WAIKIKI"
    apex_badge = "KIZÁRÓLAGOS KIBOCSÁTÓ" if is_hu else "EXCLUSIVE ISSUER"
    apex_badge_letter_spacing = "0.8" if is_hu else "1"

    p2_line1 = "KERESKEDELMI" if is_hu else "COMMERCIAL"
    p2_line2 = "BANKOK" if is_hu else "BANKS"

    p3_line1 = "BEFEKTETÉSI" if is_hu else "INVESTMENT"
    p3_line2 = "ALAPOK" if is_hu else "FUNDS"

    base_title = "UNIVERZÁLIS CBDC SZÁMLÁK" if is_hu else "UNIVERSAL CBDC ACCOUNTS"
    base_sub = "NAPI KAMATJÓVÁÍRÁS" if is_hu else "DAILY COMPOUNDED INTEREST"

    hud_left = "0%-OS INFLÁCIÓS CÉL" if is_hu else "0% INFLATION MANDATE"
    hud_left_spacing = "0.8" if is_hu else "1"
    hud_right = "100%-OS BETÉTBIZTOSÍTÁS" if is_hu else "100% DEPOSIT GUARANTEE"
    hud_right_spacing = "0.5" if is_hu else "0.6"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1160 520">
    <defs>
        <clipPath id="bk-clip1">
            <rect width="1160" height="520" rx="20" />
        </clipPath>
        <linearGradient id="bk-teal" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#1A528F" />
            <stop offset="100%" stop-color="#002244" />
        </linearGradient>
        <linearGradient id="bk-gold" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#fcedc7" />
            <stop offset="45%" stop-color="#dfba76" />
            <stop offset="80%" stop-color="#c29a57" />
            <stop offset="100%" stop-color="#80591f" />
        </linearGradient>
        <style>
            @keyframes illPulse {{ 0% {{ transform: scale(0.6); opacity: 0.9; }} 70% {{ transform: scale(1.6); opacity: 0; }} 100% {{ opacity: 0; }} }}
            @keyframes illDash {{ to {{ stroke-dashoffset: -28; }} }}
            @keyframes illDashFast {{ to {{ stroke-dashoffset: -22; }} }}
            @keyframes illSpin {{ to {{ transform: rotate(360deg); }} }}
            .spin {{ transform-box: fill-box; transform-origin: center; animation: illSpin 6s linear infinite; }}
            .pulse {{ transform-box: fill-box; transform-origin: center; animation: illPulse 2.6s ease-out infinite; }}
            .pulse-slow {{ transform-box: fill-box; transform-origin: center; animation: illPulse 4s ease-out infinite; }}
            .dash {{ stroke-dasharray: 8 6; animation: illDash 2.4s linear infinite; }}
            .dash-fast {{ stroke-dasharray: 6 6; animation: illDashFast 1.4s linear infinite; }}
            text {{ font-family: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
            .currency-mark {{ font-family: "Fraunces", Georgia, serif; }}
        </style>
    </defs>
    <g clip-path="url(#bk-clip1)">
        <!-- Currency Vector Flow Paths -->
        <!-- Central Bank to Commercial Banks Path -->
        <path id="bk-flow-comm" d="M500 178 C 360 198, 270 228, 210 268" fill="none" stroke="#dfba76" stroke-width="2.5" stroke-dasharray="8 6" class="dash" />
        <!-- Central Bank to Investment Funds Path -->
        <path id="bk-flow-inv" d="M660 178 C 800 198, 890 228, 950 268" fill="none" stroke="#dfba76" stroke-width="2.5" stroke-dasharray="8 6" class="dash" />
        <!-- Central Bank to Citizen Accounts Direct Path -->
        <path id="bk-flow-cit" d="M580 250 L 580 388" fill="none" stroke="#6BA4D9" stroke-width="3" stroke-dasharray="6 6" class="dash-fast" />
        <!-- Commercial Banks to Citizens Circulation -->
        <path d="M210 404 C 280 472, 380 464, 460 432" fill="none" stroke="#1A528F" stroke-width="1.8" stroke-dasharray="5 6" opacity=".8" />
        <!-- Investment Funds to Corporations Circulation -->
        <path d="M950 404 C 880 472, 780 464, 700 432" fill="none" stroke="#c29a57" stroke-width="1.8" stroke-dasharray="5 6" opacity=".8" />
        <!-- Animated Currency Dots on Paths -->
        <circle r="4.5" fill="#f5c46e">
            <animateMotion dur="6s" repeatCount="indefinite">
                <mpath href="#bk-flow-comm" />
            </animateMotion>
        </circle>
        <circle r="4.5" fill="#f5c46e">
            <animateMotion dur="6s" repeatCount="indefinite">
                <mpath href="#bk-flow-inv" />
            </animateMotion>
        </circle>
        <circle r="5" fill="#6BA4D9">
            <animateMotion dur="4s" repeatCount="indefinite">
                <mpath href="#bk-flow-cit" />
            </animateMotion>
        </circle>
        <!-- 1. APEX NODE: WAIKIKI NEMZETI BANKJA / NATIONAL BANK OF WAIKIKI -->
        <g transform="translate(580, 138)">
            <!-- Outer pulsing aura -->
            <circle class="pulse-slow" cx="0" cy="0" r="85" fill="none" stroke="rgba(223, 186, 118, 0.3)" stroke-width="1.5" />
            <circle cx="0" cy="0" r="72" fill="url(#bk-teal)" stroke="#dfba76" stroke-width="2.5" />
            <!-- Rotating Vault Gear Teeth -->
            <g class="spin">
                <circle cx="0" cy="0" r="55" fill="none" stroke="#dfba76" stroke-width="6" stroke-dasharray="14 12" />
            </g>
            <!-- Bank Vault Core -->
            <circle cx="0" cy="0" r="44" fill="#001830" stroke="#fcedc7" stroke-width="1.5" />
            <!-- National Gold Insignia -->
            <circle cx="0" cy="0" r="28" fill="url(#bk-gold)" />
            <!-- WUD Currency Emblem -->
            <text x="0" y="10" fill="#001830" class="currency-mark" font-size="28" font-weight="800" text-anchor="middle">₩</text>
            <!-- Badges -->
            <rect x="-165" y="-96" width="330" height="32" rx="16" fill="#061f1d" stroke="#dfba76" stroke-width="1.4" />
            <text x="0" y="-75" fill="#fcedc7" font-size="13.5" font-weight="800" text-anchor="middle" letter-spacing="1.2">{apex_title}</text>
            <rect x="-135" y="80" width="270" height="30" rx="15" fill="#061e1c" stroke="#6BA4D9" stroke-width="1.4" />
            <text x="0" y="100" fill="#6BA4D9" font-size="12.5" font-weight="800" text-anchor="middle" letter-spacing="{apex_badge_letter_spacing}">{apex_badge}</text>
        </g>
        <!-- 2. PILLAR II: KERESKEDELMI BANKOK / COMMERCIAL BANKS (LEFT) -->
        <g transform="translate(210, 336)">
            <rect x="-150" y="-68" width="300" height="136" rx="16" fill="#082220" stroke="#1A528F" stroke-width="2" />
            <!-- Shield and lock graphics -->
            <circle cx="-95" cy="-15" r="28" fill="#003366" stroke="#6BA4D9" stroke-width="1.5" />
            <path d="M-95 -32 L-83 -28 L-83 -15 C-83 -5 -95 2 -95 2 C-95 2 -107 -5 -107 -15 L-107 -28 Z" fill="#dfba76" />
            <text x="-50" y="-23" fill="#fbf7f0" font-size="16" font-weight="800">{p2_line1}</text>
            <text x="-50" y="0" fill="#fbf7f0" font-size="16" font-weight="800">{p2_line2}</text>
            <line x1="-130" y1="18" x2="130" y2="18" stroke="rgba(107, 164, 217, 0.25)" stroke-width="1" />
            <text x="0" y="44" fill="#d5ede9" font-size="13" font-weight="600" text-anchor="middle">ICB · Bank of Waikiki · NACB</text>
        </g>
        <!-- 3. PILLAR III: BEFEKTETÉSI ALAPOK / INVESTMENT FUNDS (RIGHT) -->
        <g transform="translate(950, 336)">
            <rect x="-150" y="-68" width="300" height="136" rx="16" fill="#082220" stroke="#c29a57" stroke-width="2" />
            <!-- Growth Chart Icon -->
            <circle cx="-95" cy="-15" r="28" fill="#3d2a0d" stroke="#dfba76" stroke-width="1.5" />
            <path d="M-107 -7 L-100 -14 L-93 -9 L-83 -23" fill="none" stroke="#dfba76" stroke-width="2.5" stroke-linecap="round" />
            <polyline points="-88,-23 -83,-23 -83,-18" fill="none" stroke="#dfba76" stroke-width="2.5" />
            <text x="-50" y="-23" fill="#fbf7f0" font-size="16" font-weight="800">{p3_line1}</text>
            <text x="-50" y="0" fill="#fbf7f0" font-size="16" font-weight="800">{p3_line2}</text>
            <line x1="-130" y1="18" x2="130" y2="18" stroke="rgba(223, 186, 118, 0.25)" stroke-width="1" />
            <text x="0" y="44" fill="#d5ede9" font-size="12.5" font-weight="600" text-anchor="middle">Chease Investment Group · Walker Finance</text>
        </g>
        <!-- 4. BOTTOM BASE: CITIZEN AND ENTERPRISE DIRECT ACCOUNTS -->
        <g transform="translate(580, 430)">
            <rect x="-205" y="-42" width="410" height="84" rx="18" fill="#061e1c" stroke="#6BA4D9" stroke-width="2" />
            <circle cx="-155" cy="0" r="24" fill="#003366" stroke="#6BA4D9" stroke-width="1.5" />
            <!-- User profile silhouette -->
            <circle cx="-155" cy="-6" r="8" fill="#fbf7f0" />
            <path d="M-168 12 C-168 3 -142 3 -142 12" fill="#fbf7f0" />
            <text x="-115" y="-5" fill="#fbf7f0" font-size="16.5" font-weight="800">{base_title}</text>
            <text x="-115" y="19" fill="#6BA4D9" font-size="13.5" font-weight="700" letter-spacing="0.8">{base_sub}</text>
        </g>
        <!-- Top HUD Policy Badges -->
        <g>
            <rect x="40" y="22" width="280" height="38" rx="19" fill="#061c1b" stroke="#1A528F" stroke-width="1.4" />
            <circle cx="64" cy="41" r="6" fill="#2ecc71" class="pulse" />
            <text x="82" y="46" fill="#fbf7f0" font-size="13.5" font-weight="800" letter-spacing="{hud_left_spacing}">{hud_left}</text>
            <rect x="840" y="22" width="280" height="38" rx="19" fill="#061c1b" stroke="#c29a57" stroke-width="1.4" />
            <circle cx="864" cy="41" r="6" fill="#f5c46e" class="pulse" />
            <text x="882" y="46" fill="#fbf7f0" font-size="13.5" font-weight="800" letter-spacing="{hud_right_spacing}">{hud_right}</text>
        </g>
    </g>
</svg>"""


def build_rates_svg(locale: str) -> str:
    is_hu = locale == "hu"
    gold_title = "NEMZETI ARANYFEDEZET" if is_hu else "NATIONAL GOLD ANCHOR"
    gold_tonnes = "4 000 TONNA ARANYTÖMB" if is_hu else "4,000 TONNES BULLION"
    gold_val = "ÉRTÉK: > 100 MILLIÁRD WUD" if is_hu else "VALUATION: > 100 BILLION WUD"
    gold_base = "100%-BAN FÜGGETLEN PÉNZALAP" if is_hu else "100% INDEPENDENT MONETARY BASE"

    target_title = "0%-OS RETROAKTÍV INFLÁCIÓS CÉL" if is_hu else "0% RETROACTIVE INFLATION TARGET"
    zero_val = "0,0%" if is_hu else "0.0%"
    target_box_title = "TÖBBMÉRÉSI RETROAKTÍV KORREKCIÓ" if is_hu else "MULTI-PERIOD RETROACTIVE CORRECTION"
    target_box_sub = (
        "Automatikusan kompenzáció a következő periódusokban"
        if is_hu
        else "Yearly variances fully offset over successive periods"
    )

    dep_title = "BETÉTI ALAPKAMAT" if is_hu else "DEPOSIT BASE RATE"
    dep_sub = "NAPI AUTOMATIKUS HOZAM" if is_hu else "DAILY AUTOMATIC YIELD"
    dep_line1 = (
        "Minden állampolgári CBDC számlára jóváírva"
        if is_hu
        else "Credited to 100% of Citizen CBDC Accounts"
    )
    dep_line2 = (
        "Zéró partnerkockázat · Teljes állami kezesség"
        if is_hu
        else "Zero Counterparty Risk · State Guarantee"
    )

    lend_title = "HITEL ALAPKAMAT" if is_hu else "LENDING BASE RATE"
    lend_sub = "5 ÉVES KÖZVETLEN VÁLLALATI HITEL" if is_hu else "5-YEAR DIRECT CORPORATE LOANS"
    lend_line1 = (
        "Min. 1 milliárd WUD stratégiai nagyvállalatoknak"
        if is_hu
        else "Min. 1 Billion WUD to National Champions"
    )
    lend_line2 = (
        "5 kategóriás ESG, szolvencia és innovációs mátrix"
        if is_hu
        else "5-Tier ESG, Solvency, and Innovation Matrix"
    )

    council_title = "MONETÁRIS TANÁCS RENDSZERE" if is_hu else "MONETARY COUNCIL REGIME"
    council_sub = (
        "HAVI LIKVIDITÁSI SZELEP · KÉSZPÉNZMENTES WUD"
        if is_hu
        else "MONTHLY LIQUIDITY VALVE · CASHLESS WUD"
    )

    dual_title = "KETTŐS TRANSZMISSZIÓS REFERENCIA" if is_hu else "DUAL TRANSMISSION BENCHMARKS"
    dual_sub = (
        "NAPI BETÉTI HOZAM + 5 ÉVES FEJLESZTÉSI HITEL"
        if is_hu
        else "DAILY YIELD + 5-YR DEVELOPMENT LOANS"
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1160 440">
    <defs>
        <linearGradient id="bk2-gold-bar" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#fff5db" />
            <stop offset="35%" stop-color="#dfba76" />
            <stop offset="75%" stop-color="#b88937" />
            <stop offset="100%" stop-color="#694b15" />
        </linearGradient>
        <linearGradient id="bk2-corridor-glow" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="rgba(46, 204, 113, 0.15)" />
            <stop offset="50%" stop-color="rgba(107, 164, 217, 0.25)" />
            <stop offset="100%" stop-color="rgba(46, 204, 113, 0.15)" />
        </linearGradient>
        <style>
            @keyframes illPulse {{ 0% {{ transform: scale(0.6); opacity: 0.9; }} 70% {{ transform: scale(1.6); opacity: 0; }} 100% {{ opacity: 0; }} }}
            @keyframes illDash {{ to {{ stroke-dashoffset: -28; }} }}
            @keyframes illGlow {{ from {{ opacity: 0.5; filter: drop-shadow(0 0 2px #dfba76); }} to {{ opacity: 1; filter: drop-shadow(0 0 8px #dfba76); }} }}
            @keyframes illCorridorPulse {{ 0% {{ opacity: 0.25; stroke-width: 1.5; }} 100% {{ opacity: 0.55; stroke-width: 2.5; }} }}
            .pulse {{ transform-box: fill-box; transform-origin: center; animation: illPulse 2.6s ease-out infinite; }}
            .dash {{ stroke-dasharray: 6 8; animation: illDash 2.4s linear infinite; }}
            .dash-gold {{ stroke-dasharray: 6 8; animation: illDash 2s linear infinite; }}
            .glow {{ animation: illGlow 3s ease-in-out infinite alternate; }}
            .corridor-pulse {{ animation: illCorridorPulse 4s ease-in-out infinite alternate; }}
            text {{ font-family: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        </style>
    </defs>
    <g transform="translate(185, 168)">
        <rect x="-145" y="-128" width="290" height="256" rx="16" fill="#061e1d" stroke="#dfba76" stroke-width="2" />
        <rect x="-143" y="-128" width="286" height="36" rx="16" fill="#092826" />
        <text x="0" y="-105" fill="#fcedc7" font-size="14.5" font-weight="800" text-anchor="middle" letter-spacing="1.2">{gold_title}</text>
        <g transform="translate(0, -25)">
            <rect x="-80" y="15" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="-40" y="15" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="4" y="15" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="44" y="15" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="-60" y="-5" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="-18" y="-5" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="24" y="-5" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="-40" y="-25" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="4" y="-25" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" />
            <rect x="-18" y="-45" width="36" height="18" rx="2" fill="url(#bk2-gold-bar)" stroke="#694b15" stroke-width="0.8" class="glow" />
        </g>
        <rect x="-135" y="24" width="270" height="30" rx="8" fill="#041615" stroke="rgba(223, 186, 118, 0.35)" stroke-width="1.2" />
        <text x="0" y="44" fill="#fcedc7" font-size="12" font-weight="800" text-anchor="middle" letter-spacing="0.5">{gold_tonnes}</text>
        <text x="0" y="78" fill="#6BA4D9" font-size="14.5" font-weight="800" text-anchor="middle">{gold_val}</text>
        <text x="0" y="102" fill="#dfba76" font-size="13.5" font-weight="700" text-anchor="middle">{gold_base}</text>
    </g>
    <g>
        <path d="M330 108 L 364 108 L 364 142 L 398 142" fill="none" stroke="#dfba76" stroke-width="2.5" class="dash-gold" />
        <path d="M330 228 L 364 228 L 364 194 L 398 194" fill="none" stroke="#6BA4D9" stroke-width="2" class="dash" />
    </g>
    <g>
        <path d="M782 122 L 801 122 L 801 105 L 820 105" fill="none" stroke="#2ecc71" stroke-width="2.5" class="dash" />
        <path d="M782 214 L 801 214 L 801 231 L 820 231" fill="none" stroke="#dfba76" stroke-width="2.5" class="dash-gold" />
    </g>
    <g transform="translate(590, 168)">
        <rect x="-192" y="-128" width="384" height="256" rx="16" fill="#061e1d" stroke="#1A528F" stroke-width="2" />
        <rect x="-190" y="-128" width="380" height="36" rx="16" fill="#082826" />
        <text x="0" y="-105" fill="#fcedc7" font-size="14.5" font-weight="800" text-anchor="middle" letter-spacing="1.2">{target_title}</text>
        <rect x="-145" y="-36" width="290" height="56" fill="url(#bk2-corridor-glow)" class="corridor-pulse" />
        <line x1="-145" y1="-8" x2="145" y2="-8" stroke="#dfba76" stroke-width="2" stroke-dasharray="6 4" />
        <text x="152" y="-4" fill="#dfba76" font-size="12.5" font-weight="800">{zero_val}</text>
        <line x1="-145" y1="-36" x2="145" y2="-36" stroke="rgba(107, 164, 217, 0.5)" stroke-width="1.2" />
        <text x="152" y="-32" fill="#6BA4D9" font-size="12" font-weight="700">+1.0%</text>
        <line x1="-145" y1="20" x2="145" y2="20" stroke="rgba(107, 164, 217, 0.5)" stroke-width="1.2" />
        <text x="152" y="24" fill="#6BA4D9" font-size="12" font-weight="700">-1.0%</text>
        <path d="M-140 5 C -110 -24, -85 14, -50 -18 C -20 -30, 10 8, 40 -4 C 70 -16, 110 0, 140 -8" fill="none" stroke="#2ecc71" stroke-width="2.5" />
        <g>
            <circle cx="-50" cy="-18" r="4.5" fill="#dfba76" class="pulse" />
            <circle cx="10" cy="8" r="4.5" fill="#6BA4D9" class="pulse" style="animation-delay: 0.8s;" />
            <circle cx="70" cy="-16" r="4.5" fill="#dfba76" class="pulse" style="animation-delay: 1.6s;" />
            <circle cx="140" cy="-8" r="5" fill="#2ecc71" class="pulse" />
        </g>
        <text x="-140" y="44" fill="#bedbd6" font-size="12.5" font-weight="700" text-anchor="middle">2008</text>
        <text x="-70" y="44" fill="#bedbd6" font-size="12.5" font-weight="700" text-anchor="middle">2012</text>
        <text x="0" y="44" fill="#bedbd6" font-size="12.5" font-weight="700" text-anchor="middle">2016</text>
        <text x="70" y="44" fill="#bedbd6" font-size="12.5" font-weight="700" text-anchor="middle">2020</text>
        <text x="140" y="44" fill="#bedbd6" font-size="12.5" font-weight="700" text-anchor="middle">2024</text>
        <rect x="-182" y="60" width="364" height="54" rx="8" fill="#041615" stroke="rgba(107, 164, 217, 0.25)" stroke-width="1.2" />
        <text x="0" y="80" fill="#fcedc7" font-size="13" font-weight="800" text-anchor="middle" letter-spacing="0.5">{target_box_title}</text>
        <text x="0" y="100" fill="#6BA4D9" font-size="12" font-weight="600" text-anchor="middle">{target_box_sub}</text>
    </g>
    <g transform="translate(975, 168)">
        <g transform="translate(0, -63)">
            <rect x="-155" y="-55" width="310" height="110" rx="14" fill="#061e1d" stroke="#2ecc71" stroke-width="2" />
            <circle cx="-115" cy="-20" r="21" fill="#093836" stroke="#2ecc71" stroke-width="1.5" />
            <text x="-115" y="-13" fill="#2ecc71" font-size="19" font-weight="800" text-anchor="middle">%</text>
            <text x="-80" y="-24" fill="#fbf7f0" font-size="15" font-weight="800">{dep_title}</text>
            <text x="-80" y="-6" fill="#2ecc71" font-size="12.5" font-weight="700">{dep_sub}</text>
            <line x1="-135" y1="10" x2="135" y2="10" stroke="rgba(107, 164, 217, 0.25)" stroke-width="1" />
            <text x="0" y="27" fill="#d5ede9" font-size="12.5" font-weight="600" text-anchor="middle">{dep_line1}</text>
            <text x="0" y="44" fill="#fcedc7" font-size="12" font-weight="700" text-anchor="middle">{dep_line2}</text>
        </g>
        <g transform="translate(0, 63)">
            <rect x="-155" y="-55" width="310" height="110" rx="14" fill="#061e1d" stroke="#dfba76" stroke-width="2" />
            <circle cx="-115" cy="-20" r="21" fill="#35260e" stroke="#dfba76" stroke-width="1.5" />
            <rect x="-124" y="-30" width="18" height="20" fill="none" stroke="#dfba76" stroke-width="1.5" />
            <line x1="-120" y1="-24" x2="-120" y2="-17" stroke="#dfba76" stroke-width="1.2" />
            <line x1="-115" y1="-24" x2="-115" y2="-17" stroke="#dfba76" stroke-width="1.2" />
            <text x="-80" y="-24" fill="#fbf7f0" font-size="15" font-weight="800">{lend_title}</text>
            <text x="-80" y="-6" fill="#dfba76" font-size="12.5" font-weight="700">{lend_sub}</text>
            <line x1="-135" y1="10" x2="135" y2="10" stroke="rgba(223, 186, 118, 0.25)" stroke-width="1" />
            <text x="0" y="27" fill="#d5ede9" font-size="12.5" font-weight="600" text-anchor="middle">{lend_line1}</text>
            <text x="0" y="44" fill="#fcedc7" font-size="12" font-weight="700" text-anchor="middle">{lend_line2}</text>
        </g>
    </g>
    <g>
        <rect x="40" y="348" width="380" height="52" rx="12" fill="#061c1b" stroke="rgba(107, 164, 217, 0.4)" stroke-width="1.4" opacity=".95" />
        <text x="58" y="371" fill="#f5c46e" font-size="14" font-weight="800" letter-spacing="1">{council_title}</text>
        <text x="58" y="389" fill="#bedbd6" font-size="12.5" font-weight="600">{council_sub}</text>
    </g>
    <g>
        <rect x="740" y="348" width="380" height="52" rx="12" fill="#061c1b" stroke="rgba(107, 164, 217, 0.4)" stroke-width="1.4" opacity=".95" />
        <text x="1102" y="371" fill="#6BA4D9" font-size="14" font-weight="800" letter-spacing="1" text-anchor="end">{dual_title}</text>
        <text x="1102" y="389" fill="#bedbd6" font-size="12.5" font-weight="600" text-anchor="end">{dual_sub}</text>
    </g>
</svg>"""


def main():
    files = {
        "network-hu.svg": build_network_svg("hu"),
        "network-en.svg": build_network_svg("en"),
        "rates-hu.svg": build_rates_svg("hu"),
        "rates-en.svg": build_rates_svg("en"),
    }
    for filename, content in files.items():
        target = OUT_DIR / filename
        target.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"Generated {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

