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


def _safe(s: str) -> str:
    return html.escape(s, quote=True)


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


def _render_block(label: str, items: list[str]) -> str:
    lis = "\n".join(f"<li>{_safe(t)}</li>" for t in items)
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

    # Ordered blocks first; keep any remaining blocks at the end to avoid losing information.
    seen = set()
    ordered_parts: list[str] = []
    for label in PREFERRED_BLOCK_ORDER:
        items = page.blocks.get(label)
        if not items:
            continue
        ordered_parts.append(_render_block(label, items))
        seen.add(label)
    for label, items in page.blocks.items():
        if label in seen:
            continue
        if not items:
            continue
        ordered_parts.append(_render_block(label, items))

    blocks_html = "\n".join(ordered_parts)

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
  <title>{_safe(title)} - 化学+</title>
  <link rel="stylesheet" href="../assets/site.css">
</head>
<body>
  <nav>
    <div class="container nav-container">
      <div class="logo">化学+</div>
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
          <p class="muted" style="margin-bottom: 1rem;">来自 PDF《化学实验基础知识及课本实验总结》的整理。建议：先读“实验原理”，再背“操作顺序”，最后用“误差分析/注意事项”拿分。</p>

          <div class="controls">
            <button id="expandAll" class="pill" type="button">全部展开</button>
            <button id="collapseAll" class="pill" type="button">全部收起</button>
            <button id="printPage" class="pill" type="button">打印/保存 PDF</button>
          </div>

          <section class="grid" style="grid-template-columns: 1fr; gap: 12px;">
            {blocks_html}
          </section>

          <div class="nav-prev-next">
            {prev_link}
            {next_link}
          </div>
        </div>

        <aside class="keybox">
          <h3>本页速览</h3>
          <p class="muted" style="margin-bottom: 0.75rem;">一句话抓住考点：</p>
          <p style="margin-bottom: 1rem;">{_safe(short_tip)}</p>
          <h3>自测清单</h3>
          <ul>
            <li>我能用 1 句话说出实验原理吗？</li>
            <li>我能按顺序写出关键操作步骤吗？（含先后顺序）</li>
            <li>我能写出 2 个现象 + 1 个结论吗？</li>
            <li>我能说出 2 个误差来源/注意事项，并解释“为什么”吗？</li>
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
        tip = _extract_short_tip(p.blocks)
        cards.append(
            f'''<a class="exp-link card" href="experiments/{_safe(p.filename)}">
  <h3>{_safe(_normalize_title(p.title))}</h3>
  <p>{_safe(tip)}</p>
</a>'''
        )
    block = "\n".join(cards)
    replacement = f"{start}\n{block}\n{end}"
    return re.sub(re.escape(start) + r".*?" + re.escape(end), replacement, index_html, flags=re.S)


def main() -> None:
    repo_dir = Path(__file__).resolve().parents[1]
    sections = generate_sections(repo_dir)

    out_dir = repo_dir / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)

    pages: list[ExpPage] = []
    for i, sec in enumerate(sections, start=1):
        title = str(sec.get("title") or f"实验 {i}")
        blocks = sec.get("blocks") or {}
        if not isinstance(blocks, dict):
            blocks = {}
        # ensure list[str]
        blocks2: dict[str, list[str]] = {}
        for k, v in blocks.items():
            if isinstance(v, list):
                blocks2[str(k)] = [str(x) for x in v if str(x).strip()]
        pages.append(ExpPage(index=i, title=title, filename=_exp_filename(i), blocks=blocks2))

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
