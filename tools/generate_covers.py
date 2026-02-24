#!/usr/bin/env python3
"""
Generate simple apparatus cover SVGs for each experiment page.

These are schematic (not photos) but map to the typical setup, making the index page
more visual for students.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CoverSpec:
    idx: int
    title: str
    kind: str
    accent: str


SPECS: list[CoverSpec] = [
    CoverSpec(1, "空气中氧气含量测定", "gas_collection", "#f39c12"),
    CoverSpec(2, "加热KMnO4制氧气", "heating_gas", "#e74c3c"),
    CoverSpec(3, "H2O2分解制氧气", "gas_collection", "#22c55e"),
    CoverSpec(4, "分子的运动", "diffusion", "#60a5fa"),
    CoverSpec(5, "电解水", "electrolysis", "#38bdf8"),
    CoverSpec(6, "过滤操作", "filtration", "#a78bfa"),
    CoverSpec(7, "简易净水器", "purifier", "#34d399"),
    CoverSpec(8, "蒸馏操作", "distillation", "#fbbf24"),
    CoverSpec(9, "质量守恒定律", "balance", "#f87171"),
    CoverSpec(10, "木炭还原性", "heating_tube", "#fb7185"),
    CoverSpec(11, "CO2性质", "candle_jar", "#f59e0b"),
    CoverSpec(12, "实验室制CO2", "gas_collection", "#22c55e"),
    CoverSpec(13, "燃烧条件", "fire_triangle", "#f97316"),
    CoverSpec(14, "金属活动性", "metal_reaction", "#93c5fd"),
    CoverSpec(15, "铁生锈条件", "rusting", "#fca5a5"),
    CoverSpec(16, "配制NaCl溶液", "solution_prep", "#86efac"),
    CoverSpec(17, "粗盐除难溶杂质", "filtration", "#a3e635"),
    CoverSpec(18, "粗盐除可溶杂质", "filtration", "#c4b5fd"),
    CoverSpec(19, "酸碱中和", "titration", "#fda4af"),
    CoverSpec(20, "铁的冶炼", "heating_tube", "#fdba74"),
]


def svg_header(accent: str, label: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1e293b"/>
      <stop offset="1" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="#f39c12" stop-opacity="0.65"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
  </defs>
  <rect x="16" y="16" width="1168" height="488" rx="30" fill="url(#bg)" stroke="#334155" stroke-width="2"/>
  <rect x="40" y="40" width="250" height="54" rx="16" fill="url(#accent)" opacity="0.18" stroke="#334155"/>
  <text x="62" y="76" fill="#f8fafc" font-family="system-ui, -apple-system, Segoe UI, Arial" font-size="20" font-weight="700">{label}</text>
"""


def svg_footer() -> str:
    return "</svg>\n"


def draw_common_grid() -> str:
    return """
  <path d="M120 135 C 240 55, 360 70, 460 150" fill="none" stroke="#334155" stroke-width="3" opacity="0.55"/>
  <path d="M720 150 C 830 70, 980 80, 1090 160" fill="none" stroke="#334155" stroke-width="3" opacity="0.55"/>
"""


def kind_gas_collection(accent: str) -> str:
    # Generic gas collection over water: generator flask -> tube -> trough + inverted jar.
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="210" y="140" width="16" height="300" rx="8" fill="#94a3b8"/>
    <rect x="145" y="440" width="146" height="16" rx="8" fill="#64748b"/>
  </g>
  <g filter="url(#shadow)">
    <path d="M330 160 h110 v220 a55 55 0 0 1 -110 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M342 172 h86 v135 a43 43 0 0 1 -86 0 z" fill="#1e293b" opacity="0.7"/>
    <path d="M342 300 h86 v40 a43 43 0 0 1 -86 0 z" fill="{accent}" opacity="0.65"/>
    <rect x="365" y="138" width="38" height="22" rx="6" fill="#475569"/>
    <path d="M402 150 C 520 150, 560 210, 640 250" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
  </g>
  <g filter="url(#shadow)">
    <rect x="640" y="290" width="460" height="150" rx="22" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M660 330 h420 v90 a16 16 0 0 1 -16 16 h-388 a16 16 0 0 1 -16 -16 z" fill="#0ea5e9" opacity="0.22"/>
    <path d="M840 180 h120 v210 a60 60 0 0 1 -120 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M852 192 h96 v120 a48 48 0 0 1 -96 0 z" fill="#1e293b" opacity="0.65"/>
  </g>
"""


def kind_heating_gas(accent: str) -> str:
    # Heating test tube with flame and gas collection.
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="210" y="140" width="16" height="300" rx="8" fill="#94a3b8"/>
    <rect x="145" y="440" width="146" height="16" rx="8" fill="#64748b"/>
    <rect x="226" y="185" width="140" height="10" rx="5" fill="#64748b"/>
  </g>
  <g filter="url(#shadow)">
    <path d="M360 150 h90 v260 a45 45 0 0 1 -90 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M372 162 h66 v140 a33 33 0 0 1 -66 0 z" fill="#1e293b" opacity="0.65"/>
    <rect x="392" y="128" width="30" height="22" rx="6" fill="#475569"/>
    <path d="M420 140 C 520 140, 580 220, 680 240" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
  </g>
  <g filter="url(#shadow)">
    <path d="M400 420 C 380 400, 390 370, 420 360 C 410 390, 430 395, 440 410 C 430 420, 415 426, 400 420 z" fill="url(#accent)" opacity="0.9"/>
    <path d="M410 415 C 402 400, 410 385, 424 378 C 420 392, 432 395, 436 407 C 430 413, 420 418, 410 415 z" fill="#f8fafc" opacity="0.18"/>
  </g>
  <g filter="url(#shadow)">
    <rect x="720" y="290" width="380" height="150" rx="22" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M740 330 h340 v90 a16 16 0 0 1 -16 16 h-308 a16 16 0 0 1 -16 -16 z" fill="#0ea5e9" opacity="0.22"/>
    <path d="M860 180 h120 v210 a60 60 0 0 1 -120 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M872 192 h96 v120 a48 48 0 0 1 -96 0 z" fill="#1e293b" opacity="0.65"/>
    <path d="M900 240 C 910 265, 910 285, 910 310" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
  </g>
"""


def kind_diffusion(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="240" y="180" width="260" height="240" rx="24" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M260 320 h220 v84 a18 18 0 0 1 -18 18 h-184 a18 18 0 0 1 -18 -18 z" fill="{accent}" opacity="0.16"/>
    <rect x="700" y="180" width="260" height="240" rx="24" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M720 320 h220 v84 a18 18 0 0 1 -18 18 h-184 a18 18 0 0 1 -18 -18 z" fill="{accent}" opacity="0.30"/>
  </g>
  <g filter="url(#shadow)">
    <path d="M520 250 C 580 250, 630 250, 680 250" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <path d="M650 232 L 680 250 L 650 268" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="560" cy="230" r="6" fill="{accent}" opacity="0.6"/>
    <circle cx="600" cy="270" r="5" fill="{accent}" opacity="0.5"/>
    <circle cx="620" cy="235" r="4" fill="{accent}" opacity="0.4"/>
  </g>
"""


def kind_electrolysis(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="300" y="170" width="600" height="280" rx="26" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M330 290 h540 v140 a20 20 0 0 1 -20 20 h-500 a20 20 0 0 1 -20 -20 z" fill="#0ea5e9" opacity="0.20"/>
    <rect x="420" y="210" width="20" height="210" rx="10" fill="#94a3b8"/>
    <rect x="760" y="210" width="20" height="210" rx="10" fill="#94a3b8"/>
    <path d="M430 190 C 430 160, 470 150, 500 160" fill="none" stroke="{accent}" stroke-width="5" opacity="0.7"/>
    <path d="M770 190 C 770 160, 730 150, 700 160" fill="none" stroke="{accent}" stroke-width="5" opacity="0.7"/>
    <circle cx="430" cy="305" r="7" fill="#f8fafc" opacity="0.45"/>
    <circle cx="430" cy="340" r="5" fill="#f8fafc" opacity="0.35"/>
    <circle cx="770" cy="295" r="8" fill="#f8fafc" opacity="0.50"/>
    <circle cx="770" cy="335" r="5" fill="#f8fafc" opacity="0.35"/>
  </g>
"""


def kind_filtration(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="230" y="320" width="320" height="140" rx="22" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M250 380 h280 v70 a18 18 0 0 1 -18 18 h-244 a18 18 0 0 1 -18 -18 z" fill="#0ea5e9" opacity="0.18"/>
    <path d="M520 130 L 700 130 L 640 240 L 580 240 Z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M610 240 L 610 320" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <path d="M595 130 L 640 130 L 622 210 Z" fill="{accent}" opacity="0.25"/>
    <path d="M610 320 C 610 330, 600 340, 590 350" fill="none" stroke="{accent}" stroke-width="5" opacity="0.5"/>
  </g>
"""


def kind_purifier(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <path d="M470 120 h260 v320 a60 60 0 0 1 -260 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <rect x="495" y="155" width="210" height="52" rx="12" fill="{accent}" opacity="0.18"/>
    <rect x="495" y="210" width="210" height="62" rx="12" fill="#94a3b8" opacity="0.18"/>
    <rect x="495" y="275" width="210" height="70" rx="12" fill="#0ea5e9" opacity="0.12"/>
    <rect x="495" y="348" width="210" height="72" rx="12" fill="#a3e635" opacity="0.10"/>
    <path d="M600 440 C 600 460, 580 470, 560 470" fill="none" stroke="{accent}" stroke-width="6" stroke-linecap="round" opacity="0.55"/>
  </g>
"""


def kind_distillation(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <path d="M260 300 C 280 220, 350 180, 420 180 C 490 180, 560 220, 580 300"
          fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M325 180 L 325 130 L 515 130 L 515 180" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <path d="M515 140 C 610 140, 660 175, 720 215" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <rect x="720" y="190" width="280" height="70" rx="18" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M740 225 C 780 200, 820 250, 860 225 C 900 200, 940 250, 980 225"
          fill="none" stroke="{accent}" stroke-width="5" opacity="0.55"/>
    <path d="M1000 225 C 1040 260, 1060 290, 1080 330" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <rect x="1020" y="330" width="120" height="120" rx="22" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M1040 380 h80 v70 a14 14 0 0 1 -14 14 h-52 a14 14 0 0 1 -14 -14 z" fill="#0ea5e9" opacity="0.16"/>
  </g>
"""


def kind_balance(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="260" y="350" width="680" height="90" rx="22" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <rect x="300" y="385" width="180" height="18" rx="9" fill="#334155"/>
    <rect x="700" y="385" width="200" height="18" rx="9" fill="#334155"/>
    <text x="520" y="410" fill="#94a3b8" font-family="system-ui, -apple-system, Segoe UI, Arial" font-size="16">电子天平（示意）</text>
  </g>
  <g filter="url(#shadow)">
    <path d="M520 160 C 540 120, 600 110, 640 130 C 680 150, 700 200, 690 240 C 680 290, 620 320, 580 310 C 540 300, 500 250, 520 160 z"
          fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M570 220 C 590 210, 610 210, 630 220" fill="none" stroke="{accent}" stroke-width="5" opacity="0.55"/>
    <rect x="590" y="120" width="40" height="26" rx="8" fill="#475569"/>
  </g>
"""


def kind_heating_tube(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <path d="M250 260 C 350 210, 500 210, 650 250" fill="none" stroke="#94a3b8" stroke-width="18" stroke-linecap="round"/>
    <path d="M260 260 C 360 215, 500 215, 635 250" fill="none" stroke="#0b1220" stroke-width="12" stroke-linecap="round" opacity="0.9"/>
    <path d="M650 250 C 740 270, 820 300, 920 340" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <path d="M900 320 L 930 342 L 895 350" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M420 380 C 400 360, 410 330, 440 320 C 430 350, 450 355, 460 370 C 450 380, 435 386, 420 380 z"
          fill="url(#accent)" opacity="0.9"/>
  </g>
"""


def kind_candle_jar(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <path d="M420 140 h360 v280 a90 90 0 0 1 -360 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <rect x="560" y="320" width="80" height="70" rx="16" fill="#334155"/>
    <rect x="595" y="295" width="10" height="35" rx="5" fill="#94a3b8"/>
    <path d="M600 290 C 585 275, 590 250, 615 245 C 610 265, 625 270, 630 285 C 622 292, 612 296, 600 290 z"
          fill="url(#accent)" opacity="0.9"/>
    <path d="M450 330 h300 v70 a18 18 0 0 1 -18 18 h-264 a18 18 0 0 1 -18 -18 z"
          fill="{accent}" opacity="0.10"/>
  </g>
"""


def kind_fire_triangle(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <path d="M600 140 L 880 400 L 320 400 Z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M600 170 L 840 390 L 360 390 Z" fill="{accent}" opacity="0.10"/>
    <text x="560" y="220" fill="#f8fafc" font-family="system-ui, -apple-system, Segoe UI, Arial" font-size="18" font-weight="700">可燃物</text>
    <text x="350" y="410" fill="#f8fafc" font-family="system-ui, -apple-system, Segoe UI, Arial" font-size="18" font-weight="700">氧气</text>
    <text x="780" y="410" fill="#f8fafc" font-family="system-ui, -apple-system, Segoe UI, Arial" font-size="18" font-weight="700">温度</text>
    <path d="M600 300 C 580 280, 590 250, 620 240 C 610 270, 635 278, 642 292 C 632 302, 617 308, 600 300 z"
          fill="url(#accent)" opacity="0.9"/>
  </g>
"""


def kind_metal_reaction(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="320" y="160" width="560" height="290" rx="26" fill="#0b1220" stroke="#334155" stroke-width="3"/>
    <path d="M350 300 h500 v140 a20 20 0 0 1 -20 20 h-460 a20 20 0 0 1 -20 -20 z" fill="#0ea5e9" opacity="0.18"/>
    <rect x="520" y="190" width="26" height="230" rx="13" fill="#94a3b8"/>
    <rect x="654" y="190" width="26" height="230" rx="13" fill="#94a3b8"/>
    <path d="M533 250 C 570 260, 590 310, 610 330" fill="none" stroke="{accent}" stroke-width="5" opacity="0.55"/>
    <circle cx="680" cy="320" r="6" fill="#f8fafc" opacity="0.35"/>
    <circle cx="680" cy="350" r="4.5" fill="#f8fafc" opacity="0.25"/>
  </g>
"""


def kind_rusting(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <path d="M320 150 h180 v300 a90 90 0 0 1 -180 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M700 150 h180 v300 a90 90 0 0 1 -180 0 z" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M332 320 h156 v110 a78 78 0 0 1 -156 0 z" fill="#0ea5e9" opacity="0.12"/>
    <path d="M712 320 h156 v110 a78 78 0 0 1 -156 0 z" fill="#0ea5e9" opacity="0.22"/>
    <rect x="400" y="210" width="20" height="230" rx="10" fill="{accent}" opacity="0.55"/>
    <rect x="780" y="210" width="20" height="230" rx="10" fill="{accent}" opacity="0.75"/>
  </g>
"""


def kind_solution_prep(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="300" y="140" width="240" height="330" rx="28" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M320 300 h200 v160 a18 18 0 0 1 -18 18 h-164 a18 18 0 0 1 -18 -18 z" fill="{accent}" opacity="0.14"/>
    <rect x="700" y="140" width="180" height="330" rx="28" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M715 240 h150 v230 a18 18 0 0 1 -18 18 h-114 a18 18 0 0 1 -18 -18 z" fill="#0ea5e9" opacity="0.14"/>
    <path d="M735 185 h110" stroke="#334155" stroke-width="3"/>
    <path d="M735 215 h110" stroke="#334155" stroke-width="3"/>
    <path d="M735 245 h110" stroke="#334155" stroke-width="3"/>
  </g>
"""


def kind_titration(accent: str) -> str:
    return f"""
  {draw_common_grid()}
  <g filter="url(#shadow)">
    <rect x="520" y="110" width="40" height="330" rx="20" fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <rect x="528" y="160" width="24" height="200" rx="12" fill="{accent}" opacity="0.16"/>
    <path d="M540 440 C 540 470, 520 480, 495 480" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <path d="M495 480 C 470 480, 450 470, 450 440" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <path d="M450 440 C 450 415, 470 395, 495 395" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round"/>
    <path d="M520 440 C 520 410, 550 390, 580 390 C 610 390, 640 410, 640 440"
          fill="#0b1220" stroke="#94a3b8" stroke-width="3"/>
    <path d="M560 420 h60 v40 a14 14 0 0 1 -14 14 h-32 a14 14 0 0 1 -14 -14 z" fill="{accent}" opacity="0.18"/>
  </g>
"""


KIND_FN = {
    "gas_collection": kind_gas_collection,
    "heating_gas": kind_heating_gas,
    "diffusion": kind_diffusion,
    "electrolysis": kind_electrolysis,
    "filtration": kind_filtration,
    "purifier": kind_purifier,
    "distillation": kind_distillation,
    "balance": kind_balance,
    "heating_tube": kind_heating_tube,
    "candle_jar": kind_candle_jar,
    "fire_triangle": kind_fire_triangle,
    "metal_reaction": kind_metal_reaction,
    "rusting": kind_rusting,
    "solution_prep": kind_solution_prep,
    "titration": kind_titration,
}


def main() -> None:
    repo_dir = Path(__file__).resolve().parents[1]
    out_dir = repo_dir / "assets" / "covers"
    out_dir.mkdir(parents=True, exist_ok=True)

    for spec in SPECS:
        fn = KIND_FN.get(spec.kind)
        if not fn:
            raise SystemExit(f"Unknown kind: {spec.kind}")

        label = f"实验{spec.idx}：{spec.title}"
        svg = svg_header(spec.accent, label) + fn(spec.accent) + svg_footer()
        (out_dir / f"exp-{spec.idx:02d}.svg").write_text(svg, "utf-8")

    print(f"Generated {len(SPECS)} cover SVGs into {out_dir}")


if __name__ == "__main__":
    main()

