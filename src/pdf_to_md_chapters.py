#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


PDF_FILENAME = "构建统一的世界观（重构与扩展）.pdf"
OUTPUT_DIR = Path("docs/chapters")


def find_tool(exe_name: str) -> str:
    # Prefer venv scripts
    venv_bin = Path(sys.executable).parent
    cand = venv_bin / exe_name
    if cand.exists():
        return str(cand)
    return exe_name


def extract_outline(pdf_path: Path) -> list[dict]:
    dumppdf = find_tool("dumppdf.py")
    try:
        proc = subprocess.run(
            [sys.executable, dumppdf, "-T", "--outfile", "-", str(pdf_path)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(
            f"Failed to extract outline via dumppdf.py: {e.stderr.decode(errors='ignore')}"
        )
    xml_text = proc.stdout.decode("utf-8", errors="ignore").strip()
    if not xml_text:
        raise SystemExit("No outline data found in PDF (missing bookmarks?).")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise SystemExit(f"Failed to parse outline XML: {e}")

    chapters = []
    for outline in root.findall("outline"):
        level = outline.get("level")
        title = outline.get("title", "").strip()
        pageno_el = outline.find("pageno")
        if level == "2" and title and pageno_el is not None:
            try:
                pageno = int(pageno_el.text)
            except (TypeError, ValueError):
                continue
            chapters.append({"title": title, "start": pageno})
    chapters.sort(key=lambda c: c["start"])
    if not chapters:
        raise SystemExit("No level-2 chapters found in outline.")
    return chapters


def pdf_page_count(pdf_path: Path) -> int:
    # Use pdfminer pdf2txt to limit pages: We can't count directly, so we use pypdf if available.
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(pdf_path)).pages)
    except Exception:
        # Fallback: try to run pdf2txt without page limits and infer? Not reliable.
        raise SystemExit("pypdf is required to count pages. Install with `.venv/bin/pip install pypdf`.")


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "", name)
    name = name.strip().replace(" ", "-")
    name = re.sub(r"-+", "-", name)
    return name


def extract_text_for_range(pdf_path: Path, start: int, end: int) -> str:
    pdf2txt = find_tool("pdf2txt.py")
    # pdf2txt supports --page-numbers with a space-separated list
    pages = [str(p) for p in range(start, end + 1)]
    try:
        proc = subprocess.run(
            [sys.executable, pdf2txt, "--page-numbers", *pages, "-t", "text", "-o", "-", str(pdf_path)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(
            f"pdf2txt.py failed for pages {start}-{end}: {e.stderr.decode(errors='ignore')}"
        )
    return proc.stdout.decode("utf-8", errors="ignore")


def normalize_text_to_markdown(text: str) -> str:
    # Collapse multiple blank lines to max two
    lines = text.splitlines()
    out = []
    blank = 0
    for ln in lines:
        if ln.strip() == "":
            blank += 1
        else:
            blank = 0
        if blank <= 2:
            out.append(ln.rstrip())
    return "\n".join(out).strip() + "\n"


def main():
    repo_root = Path(__file__).resolve().parents[1]
    pdf_path = repo_root / PDF_FILENAME
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    chapters = extract_outline(pdf_path)
    total_pages = pdf_page_count(pdf_path)

    ranges = []
    for i, ch in enumerate(chapters):
        start = ch["start"]
        end = chapters[i + 1]["start"] - 1 if i + 1 < len(chapters) else total_pages
        start = max(1, start)
        end = max(start, end)
        ranges.append({"title": ch["title"], "start": start, "end": end})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    toc_lines = ["# 章节目录", ""]

    for idx, r in enumerate(ranges, start=1):
        raw = extract_text_for_range(pdf_path, r["start"], r["end"])
        body = normalize_text_to_markdown(raw)

        safe_title = sanitize_filename(r["title"]) or f"chapter-{idx:02d}"
        md_name = f"{idx:02d}-{safe_title}.md"
        md_path = OUTPUT_DIR / md_name

        header = [
            f"# {r['title']}",
            "",
            f"> 来源：`{PDF_FILENAME}` 第 {r['start']}-{r['end']} 页",
            "",
        ]

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(header))
            f.write(body)

        toc_lines.append(f"- [{r['title']}]({md_name}) (第 {r['start']}-{r['end']} 页)")
        print(f"Wrote {md_path}")

    # Write a simple index
    with open(OUTPUT_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(toc_lines) + "\n")

    print(f"Done. Markdown chapters at {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

