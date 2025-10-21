#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


PDF_FILENAME = "构建统一的世界观（重构与扩展）.pdf"
OUTPUT_DIR = Path("assets/chapters")


def find_dumppdf(exe: Path) -> str:
    cand = exe.with_name("dumppdf.py")
    if cand.exists():
        return str(cand)
    # Fallback to PATH
    return "dumppdf.py"


def extract_chapters(pdf_path: Path, dumppdf_path: str):
    # Use pdfminer.six dumppdf to extract outline as XML
    try:
        proc = subprocess.run(
            [sys.executable, dumppdf_path, "-T", "--outfile", "-", str(pdf_path)],
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

    if not chapters:
        raise SystemExit("No level-2 chapters found in outline.")

    # Sort by start page
    chapters.sort(key=lambda c: c["start"])
    return chapters


def sanitize_filename(name: str) -> str:
    # Remove characters illegal on common filesystems and tidy spacing
    name = re.sub(r"[\\/:*?\"<>|]+", "", name)
    name = name.strip().replace(" ", "-")
    # Collapse duplicate dashes
    name = re.sub(r"-+", "-", name)
    return name


def main():
    repo_root = Path(__file__).resolve().parents[1]
    pdf_path = repo_root / PDF_FILENAME
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    dumppdf_path = find_dumppdf(Path(sys.executable))
    chapters = extract_chapters(pdf_path, dumppdf_path)

    try:
        from pypdf import PdfReader, PdfWriter
    except Exception as e:
        raise SystemExit(
            "Missing dependency 'pypdf'. Install it and retry (e.g., `.venv/bin/pip install pypdf`)."
        )

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    # Compute ranges
    ranges = []
    for idx, ch in enumerate(chapters):
        start = ch["start"]
        end = (chapters[idx + 1]["start"] - 1) if idx + 1 < len(chapters) else total_pages
        if start > end or start < 1:
            continue
        ranges.append({"title": ch["title"], "start": start, "end": end})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write each chapter to its own PDF
    for i, r in enumerate(ranges, start=1):
        writer = PdfWriter()
        # Convert to 0-based indices
        s0, e0 = r["start"] - 1, r["end"] - 1
        for p in range(s0, e0 + 1):
            writer.add_page(reader.pages[p])

        safe_title = sanitize_filename(r["title"]) or f"chapter-{i:02d}"
        out_name = f"{i:02d}-{safe_title}.pdf"
        out_path = OUTPUT_DIR / out_name
        with open(out_path, "wb") as f:
            writer.write(f)

        print(f"Wrote {out_path} (pages {r['start']}-{r['end']})")

    print(f"Done. Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

