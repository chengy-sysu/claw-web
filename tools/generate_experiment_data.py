#!/usr/bin/env python3
"""
Generate structured experiment data from the bundled PDF.

Output:
  JSON to stdout (UTF-8), suitable for embedding into index.html.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path


PDF_NAME = "2025年中考化学一轮复习化学实验基础知识及课本实验总结.pdf"


HEADING_RE = re.compile(r"^(实验[一二三四五六七八九十]+、|拓展[一二三]、)")
ARTIFACT_RE = re.compile(r"^\{#\{.*\}#\}$")

LABELS = [
    "试剂选择",
    "实验原理",
    "化学方程式",
    "实验仪器",
    "实验操作",
    "实验现象",
    "实验结论",
    "误差分析",
    "注意事项",
    "原因分析",
    "检验",
    "验满",
]
LABEL_SET = set(LABELS)

BULLET_PREFIXES = ("➢", "◆", "⚫", "❖", "•", "-", "﹣", "●")


def _is_artifact(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if ARTIFACT_RE.match(s):
        return True
    # page numbers / roman numerals in extracted text
    if re.fullmatch(r"\d+", s):
        return True
    if re.fullmatch(r"[IVXLC]+", s):
        return True
    return False


def _append_item(items: list[str], text: str) -> None:
    t = re.sub(r"\s+", " ", text).strip()
    if not t:
        return
    if not items:
        items.append(t)
        return
    # Merge short continuation lines into the previous item to reduce noise.
    prev = items[-1]
    if len(prev) < 90 and not prev.endswith(("。", "；", ";", ":", "：", "?", "？")):
        items[-1] = prev + " " + t
    else:
        items.append(t)


def _extract_text_from_pdf(pdf_path: Path) -> list[str]:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        txt_path = Path(f.name)
    subprocess.run(["pdftotext", str(pdf_path), str(txt_path)], check=True)
    return txt_path.read_text("utf-8", errors="ignore").splitlines()


def _find_headings(lines: list[str]) -> list[tuple[int, str]]:
    heads: list[tuple[int, str]] = []
    for i, raw in enumerate(lines):
        s = raw.replace("\f", "").strip()
        if not HEADING_RE.match(s):
            continue
        # Skip TOC lines that contain dot leaders.
        if re.search(r"\.{5,}", s):
            continue
        heads.append((i, s))
    return heads


def _parse_section(lines: list[str]) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {"要点": []}
    current = "要点"

    for raw in lines:
        s = raw.replace("\f", "").strip()
        if _is_artifact(s):
            continue

        # Some sections embed short reading passages (e.g., “拉瓦锡实验”) without a clear label.
        if "拉瓦锡实验" in s:
            current = "拓展阅读"
            blocks.setdefault(current, [])
            continue

        if s in LABEL_SET:
            current = s
            blocks.setdefault(current, [])
            continue

        # Heuristic: sometimes "化学方程式" is followed by operations text when equations are images.
        if current == "化学方程式" and ("实验" in s and ("步骤" in s or "操作" in s or "依次" in s or "连接" in s)):
            current = "实验操作"
            blocks.setdefault(current, [])

        s = re.sub(r"\s+", " ", s).strip()
        if not s:
            continue

        if s.startswith(BULLET_PREFIXES):
            s = s.lstrip("".join(BULLET_PREFIXES)).strip()
            if s:
                blocks.setdefault(current, []).append(s)
            continue

        _append_item(blocks.setdefault(current, []), s)

    return {k: v for k, v in blocks.items() if v}


def main() -> None:
    repo_dir = Path(__file__).resolve().parents[1]
    pdf_path = repo_dir / PDF_NAME
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    lines = _extract_text_from_pdf(pdf_path)
    heads = _find_headings(lines)
    sections = []
    for idx, (start, title) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        blocks = _parse_section(lines[start + 1 : end])
        sections.append({"title": title, "blocks": blocks})

    print(json.dumps(sections, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()

