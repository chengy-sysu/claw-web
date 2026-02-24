#!/usr/bin/env python3
"""
Static-site build:
- Parse the bundled PDF into structured experiment data
- Generate per-experiment HTML pages under experiments/
- Update index.html experiment list between markers

This keeps pages independent (one HTML per experiment) while sharing CSS/JS in assets/.
"""

from __future__ import annotations

from dataclasses import dataclass
import html
import json
import os
import re
from pathlib import Path

from generate_experiment_data import generate_sections


PREFERRED_BLOCK_ORDER = [
    "要点",
    "试剂选择",
    "实验原理",
    "化学方程式",
    "实验仪器",
    "实验操作",
    "实验现象",
    "实验结论",
    "检验",
    "验满",
    "注意事项",
    "误差分析",
    "原因分析",
    "拓展阅读",
]


@dataclass(frozen=True)
class ExpPage:
    index: int
    title: str
    filename: str
    blocks: dict[str, list[str]]
    notes: dict[str, object]


def _safe(s: str) -> str:
    return html.escape(s, quote=True)

def _safe_chem_inline(text: str) -> str:
    """
    Escape text then render simple chemical formatting:
      - subscripts: H2O -> H<sub>2</sub>O
      - ionic charge: Mg2+ -> Mg<sup>2+</sup>, SO4^2- -> SO<sub>4</sub><sup>2-</sup>

    Best-effort, aimed at short inline notes (not full LaTeX).
    """
    esc = _safe(text)
    # caret charge (preferred): SO4^2-
    esc = re.sub(r"([A-Za-z\)\]][A-Za-z0-9\(\)\[\]]*)\^(\d+)([+-])", r"\1<sup>\2\3</sup>", esc)
    # terminal charge: Mg2+ (followed by end or a non-alphanumeric separator)
    esc = re.sub(
        r"([A-Za-z\)\]][A-Za-z0-9\(\)\[\]]*?)(\d+)([+-])(?=$|[^A-Za-z0-9])",
        r"\1<sup>\2\3</sup>",
        esc,
    )
    # subscripts in remaining formula text
    esc = re.sub(r"(?<=[A-Za-z\)\]])(\d+)", r"<sub>\1</sub>", esc)
    return esc


def _chem_species_to_html(species: str) -> str:
    """
    Convert a chemical species token to HTML with subscripts/superscripts.
    Supports:
      - coefficients: 2H2O
      - subscripts: H2SO4, Ca(OH)2
      - ionic charges: Mg2+, SO4^2-
      - simple parentheses wrappers: (MnO2)
    """
    s = species.strip()
    if not s:
        return ""

    # Wrapper parentheses like "(MnO2)".
    if s.startswith("(") and s.endswith(")") and len(s) >= 3:
        inner = s[1:-1].strip()
        return "(" + _chem_species_to_html(inner) + ")"

    # Leading coefficient (e.g. 2H2O).
    m = re.match(r"^(\d+)(.+)$", s)
    coeff = ""
    rest = s
    if m:
        coeff = m.group(1)
        rest = m.group(2)

    # Charge written as caret: SO4^2-
    m = re.match(r"^(.*)\^(\d+)([+-])$", rest)
    charge_html = ""
    if m:
        rest = m.group(1)
        charge_html = f"<sup>{m.group(2)}{m.group(3)}</sup>"
    else:
        # Terminal charge: Ca2+, Cl-
        m2 = re.match(r"^(.*?)(\d+)?([+-])$", rest)
        if m2 and re.search(r"[A-Za-z]", rest):
            base = m2.group(1)
            num = m2.group(2) or ""
            sign = m2.group(3)
            if base:
                rest = base
                charge_html = f"<sup>{num}{sign}</sup>"

    # Subscripts in the base formula.
    base = _safe(rest)
    base = re.sub(r"(?<=[A-Za-z\)\]])(\d+)", r"<sub>\1</sub>", base)

    return _safe(coeff) + base + charge_html


def _chem_equation_to_html(eq: str) -> str:
    """
    Convert an equation string into HTML with arrows and formatted species.
    Supported formats:
      - '4P + 5O2 -> 2P2O5'           (plain arrow)
      - '4P + 5O2 =[点燃]= 2P2O5'     (arrow with condition above)
      - '2H2O2 =[MnO2]= 2H2O + O2↑'  (arrow with catalyst above)
      - 'CO2 + H2O <-> H2CO3'         (reversible)
    """
    s = eq.strip()
    if not s:
        return ""

    # Handle =[condition]= syntax: render as arrow with condition above
    m = re.search(r'=\[(.+?)\]=', s)
    if m:
        condition = _safe(m.group(1))
        # Replace the =[...]= with a special placeholder
        arrow_html = f'<span class="chem-condition"><span class="cond-text">{condition}</span><span class="cond-arrow">=====</span></span>'
        left = s[:m.start()].strip()
        right = s[m.end():].strip()
        left_html = _chem_equation_to_html_inner(left)
        right_html = _chem_equation_to_html_inner(right)
        return f"{left_html} {arrow_html} {right_html}"

    return _chem_equation_to_html_inner(s)


def _chem_equation_to_html_inner(s: str) -> str:
    """Format the species and operators in a (partial) equation string."""
    s = s.replace("<->", "⇌").replace("<=>", "⇌").replace("->", "→")
    tokens = s.split()
    out = []
    for t in tokens:
        if t in {"+", "→", "⇌", "=", "≈"}:
            out.append(_safe(t))
        else:
            out.append(_chem_species_to_html(t))
    return " ".join(out)


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def _exp_filename(i: int) -> str:
    return f"exp-{i:02d}.html"


def _extract_short_tip(blocks: dict[str, list[str]]) -> str:
    for k in ("要点", "实验原理", "实验现象", "注意事项"):
        items = blocks.get(k) or []
        if items:
            tip = re.sub(r"\s+", " ", items[0]).strip()
            # Keep cards concise on index page.
            if len(tip) > 88:
                return tip[:88].rstrip() + "…"
            return tip
    return "点击进入页面查看：原理、操作、现象、结论、误差与注意事项。"

def _render_notes(page: ExpPage) -> str:
    notes = page.notes or {}
    parts: list[str] = []

    goal = str(notes.get("goal") or "").strip()
    if goal:
        parts.append(_render_block("实验目标", [goal]))

    equations = notes.get("equations") or []
    if isinstance(equations, list) and equations:
        eq_items = [str(e).strip() for e in equations if str(e).strip()]
        if eq_items:
            eq_html = [f'<span class="chem-eq">{_chem_equation_to_html(e)}</span>' for e in eq_items]
            parts.append(_render_block_html("必背方程式", eq_html))

    title_map = {
        "principle": "核心原理",
        "steps": "关键步骤（怎么做）",
        "phenomena": "现象（看到什么）",
        "exam_points": "高频考点（怎么拿分）",
        "common_errors": "常见错误（怎么避坑）",
        "safety": "安全提醒",
        "quick_check": "自测清单",
    }
    for k, label in title_map.items():
        v = notes.get(k)
        if not isinstance(v, list) or not v:
            continue
        items = [str(x).strip() for x in v if str(x).strip()]
        if items:
            parts.append(_render_block(label, items))

    return "\n".join(parts)


def _render_pdf_extract(page: ExpPage) -> str:
    if not page.blocks:
        return ""

    ordered: list[tuple[str, list[str]]] = []
    seen = set()
    for label in PREFERRED_BLOCK_ORDER:
        items = page.blocks.get(label)
        if items:
            ordered.append((label, items))
            seen.add(label)
    for label, items in page.blocks.items():
        if label in seen:
            continue
        if items:
            ordered.append((label, items))

    inner = []
    for label, items in ordered:
        lis = "\n".join(f"<li>{_safe_chem_inline(t)}</li>" for t in items)
        inner.append(
            f"""<div class="card" style="background: rgba(15, 23, 42, 0.35);">
  <h3 style="margin-bottom: 0.5rem;">{_safe(label)}</h3>
  <ul class="block-list">{lis}</ul>
</div>"""
        )
    inner_html = "\n".join(inner)

    return f"""
    <details class="exp-block">
      <summary>PDF摘录（原文提取，供对照）</summary>
      <div class="grid" style="grid-template-columns: 1fr; gap: 12px; margin-top: 12px;">
        {inner_html}
      </div>
    </details>
    """.strip()


def _render_block(label: str, items: list[str]) -> str:
    lis = "\n".join(f"<li>{_safe_chem_inline(t)}</li>" for t in items)
    return f"""
    <details class="exp-block" open>
      <summary>{_safe(label)}</summary>
      <ul class="block-list">
        {lis}
      </ul>
    </details>
    """.strip()


def _render_block_html(label: str, items_html: list[str]) -> str:
    lis = "\n".join(f"<li>{t}</li>" for t in items_html if t.strip())
    return f"""
    <details class="exp-block" open>
      <summary>{_safe(label)}</summary>
      <ul class="block-list">
        {lis}
      </ul>
    </details>
    """.strip()


def _render_exp_page(page: ExpPage, prev_page: ExpPage | None, next_page: ExpPage | None) -> str:
    title = _normalize_title(page.title)
    short_tip = _extract_short_tip(page.blocks)
    if page.notes and str(page.notes.get("goal") or "").strip():
        short_tip = str(page.notes.get("goal")).strip()

    cover_src = f"../assets/covers/exp-{page.index:02d}.svg"
    cover_html = f"""
      <div class="exp-cover large">
        <img src="{_safe(cover_src)}" alt="{_safe(title)} 实验装置图" loading="lazy">
      </div>
    """.strip()

    notes_html = _render_notes(page)
    pdf_html = _render_pdf_extract(page)

    prev_link = (
        f'<a class="secondary-button" href="{_safe(prev_page.filename)}">← { _safe(prev_page.title) }</a>'
        if prev_page
        else '<span class="muted">已是第一篇</span>'
    )
    next_link = (
        f'<a class="secondary-button" href="{_safe(next_page.filename)}">{ _safe(next_page.title) } →</a>'
        if next_page
        else '<span class="muted">已是最后一篇</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{_safe(short_tip)}">
  <title>{_safe(title)} - 化学+</title>
  <link rel="stylesheet" href="../assets/site.css">
</head>
<body data-exp-id="{page.index}">
  <a class="skip-link" href="#exp-content">跳到实验内容</a>

  <nav aria-label="主导航">
    <div class="container nav-container">
      <div class="logo">化学+</div>
      <div class="nav-tools">
        <button class="font-btn" data-font="font-sm" type="button" aria-label="小字体">A-</button>
        <button class="font-btn" data-font="font-md" type="button" aria-label="中字体">A</button>
        <button class="font-btn" data-font="font-lg" type="button" aria-label="大字体">A+</button>
        <button id="themeToggle" type="button" aria-label="切换亮色/暗色模式">亮色</button>
      </div>
      <button id="menuToggle" class="menu-toggle" type="button" aria-label="打开导航菜单" aria-expanded="false">☰</button>
      <div class="nav-links">
        <a href="../index.html#home">首页</a>
        <a href="../index.html#pdf">PDF</a>
        <a href="../index.html#experiments">实验目录</a>
        <a href="../index.html#contact">问答</a>
      </div>
    </div>
  </nav>

  <main class="page">
    <div class="container">
      <div class="breadcrumbs">
        <a href="../index.html#experiments">实验目录</a> / <span>{_safe(title)}</span>
      </div>

      <div class="two-col">
        <div>
          <h2 class="section-title" style="text-align:left; margin-bottom: 1rem;">{_safe(title)}</h2>
          {cover_html}
          <p class="muted" style="margin-bottom: 1rem;">来自 PDF《化学实验基础知识及课本实验总结》的整理。建议：先读"实验原理"，再背"操作顺序"，最后用"误差分析/注意事项"拿分。</p>

          <div class="controls">
            <button id="expandAll" class="pill" type="button">全部展开</button>
            <button id="collapseAll" class="pill" type="button">全部收起</button>
            <button id="quizMode" class="pill" type="button">自测模式</button>
            <button id="printPage" class="pill" type="button">打印/保存 PDF</button>
          </div>

          <section id="exp-content" class="grid" style="grid-template-columns: 1fr; gap: 12px;">
            {notes_html}
            {pdf_html}
          </section>

          <div class="controls" style="margin-top: 1.25rem;">
            <button id="markLearned" class="mark-learned-btn" type="button">标记为已学习</button>
          </div>

          <div class="nav-prev-next">
            {prev_link}
            {next_link}
          </div>
        </div>

        <aside class="keybox">
          <h3>本页速览</h3>
          <p class="muted" style="margin-bottom: 0.75rem;">一句话抓住考点：</p>
          <p style="margin-bottom: 1rem;">{_safe_chem_inline(short_tip)}</p>
          <h3>自测清单</h3>
          <ul>
            <li>我能用 1 句话说出实验原理吗？</li>
            <li>我能按顺序写出关键操作步骤吗？（含先后顺序）</li>
            <li>我能写出 2 个现象 + 1 个结论吗？</li>
            <li>我能说出 2 个误差来源/注意事项，并解释"为什么"吗？</li>
          </ul>
        </aside>
      </div>
    </div>
  </main>

  <footer>
    <div class="container">
      <p>&copy; 2026 化学+. 本页内容基于本仓库 PDF 整理，仅供学习复习使用。</p>
    </div>
  </footer>

  <script src="../assets/experiment.js" defer></script>
</body>
</html>
"""


def _update_index_experiment_list(index_html: str, pages: list[ExpPage]) -> str:
    start = "<!-- EXPERIMENT_LIST_START -->"
    end = "<!-- EXPERIMENT_LIST_END -->"
    if start not in index_html or end not in index_html:
        raise RuntimeError("index.html missing experiment list markers")

    cards = []
    for p in pages:
        if p.notes and str(p.notes.get("goal") or "").strip():
            tip = str(p.notes.get("goal")).strip()
            if len(tip) > 110:
                tip = tip[:110].rstrip() + "…"
        else:
            tip = _extract_short_tip(p.blocks)
        cover_src = f"assets/covers/exp-{p.index:02d}.svg"
        cards.append(
            f'''<a class="exp-link card" href="experiments/{_safe(p.filename)}" data-exp-id="{p.index}">
  <div class="exp-cover">
    <img src="{_safe(cover_src)}" alt="{_safe(_normalize_title(p.title))} 实验装置图" loading="lazy">
  </div>
  <h3>{_safe(_normalize_title(p.title))}</h3>
  <p>{_safe_chem_inline(tip)}</p>
</a>'''
        )
    block = "\n".join(cards)
    replacement = f"{start}\n{block}\n{end}"
    return re.sub(re.escape(start) + r".*?" + re.escape(end), replacement, index_html, flags=re.S)


def main() -> None:
    repo_dir = Path(__file__).resolve().parents[1]
    sections = generate_sections(repo_dir)

    notes_path = repo_dir / "content" / "exp_notes.json"
    notes_by_idx: dict[str, dict[str, object]] = {}
    if notes_path.exists():
        notes_by_idx = json.loads(notes_path.read_text("utf-8"))

    out_dir = repo_dir / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Fix known title errors from PDF extraction
    title_fixups = {
        "配置": "配制",  # 实验十六 "配置" should be "配制"
    }

    pages: list[ExpPage] = []
    for i, sec in enumerate(sections, start=1):
        title = str(sec.get("title") or f"实验 {i}")
        for wrong, right in title_fixups.items():
            title = title.replace(wrong, right)
        blocks = sec.get("blocks") or {}
        if not isinstance(blocks, dict):
            blocks = {}
        # ensure list[str]
        blocks2: dict[str, list[str]] = {}
        for k, v in blocks.items():
            if isinstance(v, list):
                items = [str(x) for x in v if str(x).strip()]
                for wrong, right in title_fixups.items():
                    items = [item.replace(wrong, right) for item in items]
                blocks2[str(k)] = items
        pages.append(
            ExpPage(
                index=i,
                title=title,
                filename=_exp_filename(i),
                blocks=blocks2,
                notes=notes_by_idx.get(str(i), {}),
            )
        )

    # Write experiment pages.
    for idx, p in enumerate(pages):
        prev_p = pages[idx - 1] if idx > 0 else None
        next_p = pages[idx + 1] if idx + 1 < len(pages) else None
        html_text = _render_exp_page(p, prev_p, next_p)
        (out_dir / p.filename).write_text(html_text, "utf-8")

    # Update index experiment list.
    index_path = repo_dir / "index.html"
    index_html = index_path.read_text("utf-8")
    index_html = _update_index_experiment_list(index_html, pages)
    index_path.write_text(index_html, "utf-8")

    print(f"Built {len(pages)} experiment pages into {out_dir}")


if __name__ == "__main__":
    main()
