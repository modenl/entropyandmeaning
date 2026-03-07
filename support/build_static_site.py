#!/usr/bin/env python3

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CONFIG = ROOT / "_config.yml"
SITE_CSS = "assets/css/site.css"
PAGE_SOURCES = [Path("foreword.md"), Path("Preface.md")] + [Path(f"Chapter{i}.md") for i in range(1, 11)]


def read_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def extract_heading_title(path: Path) -> str:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            title = re.sub(r"^#+\s*", "", line).strip()
            title = re.sub(r"[*_`]+", "", title)
            title = re.sub(r"\s+", " ", title).strip()
            return title
    return path.stem


def render_markdown(path: Path) -> str:
    result = subprocess.run(
        [
            "pandoc",
            str(path),
            "--from",
            "markdown+tex_math_dollars+tex_math_single_backslash",
            "--to",
            "html5",
            "--mathjax",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    html_body = result.stdout
    html_body = re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', html_body)
    return html_body


def build_nav(items: list[dict[str, str]], current_url: str) -> str:
    links = []
    for item in items:
        class_attr = ' class="is-active"' if item["url"] == current_url else ""
        links.append(
            f'        <a{class_attr} href="{html.escape(item["url"])}">{html.escape(item["title"])}</a>'
        )
    return "\n".join(links)


def build_page(
    *,
    page_title: str,
    site_title: str,
    brand_title: str,
    tagline: str,
    description: str,
    content_html: str,
    nav_html: str,
    first_page_url: str,
    next_item: dict[str, str] | None,
) -> str:
    next_html = ""
    if next_item:
        next_html = f"""
  <footer class="site-footer">
    <div class="footer-inner">
      <a class="next-link" href="{html.escape(next_item["url"])}" aria-label="下一章：{html.escape(next_item["title"])}">
        <span class="next-kicker">下一章</span>
        <span class="next-title">{html.escape(next_item["title"])}</span>
      </a>
    </div>
  </footer>"""

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page_title)} | {html.escape(site_title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Work+Sans:wght@500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{SITE_CSS}">
  <script>
    window.MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
        processEscapes: true
      }},
      svg: {{
        fontCache: 'global'
      }}
    }};
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
</head>
<body>
  <div class="scrollbar" aria-hidden="true"></div>
  <header class="site-shell">
    <div class="site-meta">
      <a class="brand" href="{html.escape(first_page_url)}">{html.escape(brand_title)}</a>
      <p class="tagline">{html.escape(tagline)}</p>
    </div>
    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
      <span class="hamburger"></span>
    </button>
    <nav class="site-nav" aria-label="目录" id="site-nav">
{nav_html}
    </nav>
  </header>

  <main class="page-shell">
    <article class="page-card">
{content_html}
    </article>
  </main>

  <button class="copy-btn" id="copy-btn" type="button" aria-live="polite">复制全文</button>{next_html}

  <script>
    (() => {{
      const bar = document.querySelector('.scrollbar');
      if (bar) {{
        const update = () => {{
          const doc = document.documentElement;
          const max = doc.scrollHeight - doc.clientHeight;
          const progress = max > 0 ? (doc.scrollTop / max) * 100 : 0;
          bar.style.setProperty('--scroll', `${{progress}}%`);
        }};
        document.addEventListener('scroll', update, {{ passive: true }});
        window.addEventListener('resize', update);
        update();
      }}

      const toggle = document.querySelector('.nav-toggle');
      const nav = document.querySelector('.site-nav');
      if (toggle && nav) {{
        toggle.addEventListener('click', () => {{
          const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
          toggle.setAttribute('aria-expanded', String(!isExpanded));
          nav.classList.toggle('is-visible');
          document.body.classList.toggle('menu-open');
        }});

        nav.addEventListener('click', (e) => {{
          const target = e.target;
          if (target.tagName === 'A' || target === nav) {{
            toggle.setAttribute('aria-expanded', 'false');
            nav.classList.remove('is-visible');
            document.body.classList.remove('menu-open');
          }}
        }});
      }}

      const copyBtn = document.getElementById('copy-btn');
      const article = document.querySelector('.page-card');
      const defaultCopyLabel = '复制全文';

      const updateCopyLabel = (text, reset = false) => {{
        copyBtn.textContent = text;
        if (reset) {{
          setTimeout(() => {{
            copyBtn.disabled = false;
            copyBtn.textContent = defaultCopyLabel;
          }}, 1800);
        }}
      }};

      if (copyBtn && article) {{
        copyBtn.addEventListener('click', async () => {{
          const text = article.innerText.trim();
          if (!text) return;
          copyBtn.disabled = true;
          updateCopyLabel('复制中…');
          try {{
            if (navigator.clipboard?.writeText) {{
              await navigator.clipboard.writeText(text);
            }} else {{
              const helper = document.createElement('textarea');
              helper.value = text;
              helper.style.position = 'fixed';
              helper.style.opacity = '0';
              document.body.appendChild(helper);
              helper.select();
              document.execCommand('copy');
              helper.remove();
            }}
            updateCopyLabel('已复制', true);
          }} catch (e) {{
            updateCopyLabel('复制失败', true);
          }}
        }});
      }}
    }})();
  </script>
</body>
</html>
"""


def build_index(site_title: str, first_page_url: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={html.escape(first_page_url)}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(site_title)}</title>
</head>
<body>
  <p>跳转中… 如果没有自动跳转，请打开 <a href="{html.escape(first_page_url)}">首页正文</a>。</p>
</body>
</html>
"""


def main() -> None:
    config = read_simple_yaml(CONFIG)
    site_title = config.get("title", "从熵到意义")
    brand_title = config.get("book_title", "《从熵到意义》")
    tagline = config.get("tagline", "一棵统一世界观的生成树：从物理到意识，从演化到意义")
    description = config.get("description", tagline)

    nav_items = []
    for src in PAGE_SOURCES:
        title = extract_heading_title(DOCS / src)
        nav_items.append({"source": src.name, "url": src.with_suffix(".html").name, "title": title})
    first_page_url = nav_items[0]["url"]

    for idx, item in enumerate(nav_items):
        source_path = DOCS / item["source"]
        body_html = render_markdown(source_path)
        next_item = nav_items[idx + 1] if idx + 1 < len(nav_items) else None
        nav_html = build_nav(nav_items, item["url"])
        page_html = build_page(
            page_title=item["title"],
            site_title=site_title,
            brand_title=brand_title,
            tagline=tagline,
            description=description,
            content_html=body_html,
            nav_html=nav_html,
            first_page_url=first_page_url,
            next_item=next_item,
        )
        (DOCS / item["url"]).write_text(page_html, encoding="utf-8")

    (DOCS / "index.html").write_text(build_index(site_title, first_page_url), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main()
