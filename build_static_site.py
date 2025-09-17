#!/usr/bin/env python3
"""
Simple static site generator for an Obsidian vault-like folder structure.

Features:
- Converts all .md files under input directory to .html in output directory
- Preserves directory structure; copies non-.md assets as-is
- Left-side collapsible navigation (folders/subfolders) using <details>/<summary>
- Bootstrap 5 styling via CDN
- Home page is input/index.md rendered to output/index.html

Usage (PowerShell):
  python build_static_site.py --input "C:\\Users\\Zoom\\My Drive (hello@causalmap.app)\\causal-blog-flowershow\\content" --output ./site

Notes:
- Requires the "markdown" package: pip install markdown
"""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
import hashlib
import re
import shutil
from typing import Dict, List, Optional, Tuple, Union
import json
import stat


# -- markdown conversion (simple) --
try:
    import markdown  # type: ignore
except ImportError as exc:  # minimal helpful error
    raise SystemExit(
        "Missing dependency: markdown. Install with 'pip install markdown'"
    ) from exc


# -- data structures --
class NavFile:
    """Represents a markdown file converted to HTML in the nav tree."""

    def __init__(self, title: str, src_md: Path, out_html: Path):
        self.title = title
        self.src_md = src_md
        self.out_html = out_html


class NavDir:
    """Represents a directory in the nav tree with subdirectories and files."""

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.subdirs: Dict[str, "NavDir"] = {}
        self.files: List[NavFile] = []


# -- helpers: scanning and building tree --
def is_markdown_file(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".markdown"}


_WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def _sanitize_stem_for_windows(stem: str, rel_path_for_hash: str, max_len: int = 80) -> str:
    """Return a filesystem-safe, reasonably short file stem for Windows.

    - Removes characters invalid on Windows: <>:"/|?* and control chars
    - Trims leading/trailing spaces/dots
    - Truncates to max_len
    - If truncated or changed, append a short stable hash to reduce collisions
    - Avoids reserved device names
    """
    original = stem
    # remove invalid characters
    stem = re.sub(r'[<>:"/\\|?*]', "-", stem)
    # remove control chars
    stem = re.sub(r"[\x00-\x1F]", "", stem)
    # trim
    stem = stem.strip(" .")

    changed = (stem != original)
    truncated = False
    if len(stem) > max_len:
        stem = stem[:max_len]
        truncated = True

    # avoid reserved names (reserved even with extensions)
    if stem.upper() in _WINDOWS_RESERVED_NAMES:
        stem = f"{stem}_"
        changed = True

    if changed or truncated:
        digest = hashlib.md5(rel_path_for_hash.encode("utf-8")).hexdigest()[:6]
        # ensure final length within bounds including suffix
        suffix = f"-{digest}"
        if len(stem) + len(suffix) > max_len:
            stem = stem[: max_len - len(suffix)]
        stem = f"{stem}{suffix}"

    # re-trim potential trailing dot/space after modifications
    stem = stem.strip(" .")
    return stem or "untitled"


def relative_output_html(input_root: Path, output_root: Path, md_path: Path) -> Path:
    """Map an input markdown path to its corresponding output HTML path (safe for Windows)."""
    rel = md_path.relative_to(input_root)
    # root index.md → site/index.html
    if rel.name.lower() == "index.md" and rel.parent == Path("."):
        return output_root / "index.html"

    # Subdir index.md stays as index.html within that folder
    if rel.name.lower() == "index.md":
        return (output_root / rel).with_suffix(".html")

    # Sanitize filename stem only; preserve directories
    rel_str_for_hash = rel.as_posix()
    safe_stem = _sanitize_stem_for_windows(Path(rel).stem, rel_str_for_hash)
    return (output_root / rel.parent / f"{safe_stem}.html")


def build_nav_tree(input_root: Path, output_root: Path) -> NavDir:
    """Scan input_root and build a NavDir tree with NavFile entries for .md files."""
    root = NavDir(name=input_root.name, path=input_root)

    for dirpath, dirnames, filenames in os.walk(input_root):
        # skip hidden directories; at top-level include only folders starting with a number
        current_dir = Path(dirpath)
        if current_dir == input_root:
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and (d[:1].isdigit())]
        else:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # ensure node exists along the path
        node = root
        if current_dir != input_root:
            parts = current_dir.relative_to(input_root).parts
            accumulated = Path()
            for part in parts:
                accumulated = accumulated / part
                node = node.subdirs.setdefault(part, NavDir(part, input_root / accumulated))

        # add files
        for fname in filenames:
            if fname.startswith("."):
                continue
            fpath = current_dir / fname
            # only include markdown files; at root include only index.md
            if is_markdown_file(fpath):
                if current_dir == input_root and fname.lower() != "index.md":
                    continue
                out_html = relative_output_html(input_root, output_root, fpath)
                title = fpath.stem
                node.files.append(NavFile(title=title, src_md=fpath, out_html=out_html))

        # sort by filename for stable nav ordering
        node.files.sort(key=lambda nf: nf.src_md.name.lower())

    return root


# -- helpers: asset copying --
def copy_assets(input_root: Path, output_root: Path) -> None:
    """Copy all non-markdown files, preserving structure."""
    for src in input_root.rglob("*"):
        if src.is_dir() or src.name.startswith("."):
            continue
        if is_markdown_file(src):
            continue
        rel = src.relative_to(input_root)
        dst = output_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


# -- helpers: HTML generation --

def strip_numeric_prefix(stem: str) -> str:
    """Strip leading numeric ordering like '01 ', '010.2 - ', '3_' from a filename stem."""
    cleaned = re.sub(r"^\s*\d[\d._-]*\s*[-_. ]\s*", "", stem).strip()
    return cleaned or stem


def build_wikilink_index(md_paths: List[Path], title_map: Dict[Path, str]) -> Dict[str, Path]:
    """Create a case-insensitive index for wikilink resolution.

    Keys include: original stem, stripped numeric stem, and first heading title.
    """
    index: Dict[str, Path] = {}
    for p in md_paths:
        stem = p.stem
        stripped = strip_numeric_prefix(stem)
        title = title_map.get(p, stripped)
        for key in {stem, stripped, title}:
            if key:
                index.setdefault(key.lower(), p)
    return index


def replace_wikilinks_with_embeds(md_text: str, current_md_path: Path, input_root: Path, output_root: Path, title_map: Dict[Path, str], embed_html_map: Dict[Path, str], wikilink_index: Dict[str, Path]) -> str:
    """Replace [[wikilinks]] with collapsible embeds of the target page content.

    - Uses the target page's first heading as the summary title
    - Embeds the target page HTML (without its first heading)
    - Closed by default
    """
    pattern = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
    # compute the output directory of the current page (for correct relative links)
    current_out_dir = relative_output_html(input_root, output_root, current_md_path).parent

    def _repl(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        # alias is ignored per requirement: use the target page's title
        key = target.lower()
        target_md = wikilink_index.get(key)
        if not target_md:
            # try stripped variant
            target_md = wikilink_index.get(strip_numeric_prefix(target).lower())
        if not target_md:
            return match.group(0)  # leave unchanged if unresolved

        title = html.escape(title_map.get(target_md, strip_numeric_prefix(target_md.stem)))
        inner_html = embed_html_map.get(target_md, "")
        # Provide a link to open the full page
        target_out = relative_output_html(input_root, output_root, target_md)
        href = html.escape(os.path.relpath(target_out, start=current_out_dir).replace(os.sep, "/"))
        return (
            f"<details class=\"embed-block mb-3\">"
            f"<summary class=\"text-muted d-flex align-items-center justify-content-between\">"
            f"<span>{title}</span>"
            f"<span class=\"chev\" aria-hidden=\"true\">▸</span>"
            f"</summary>"
            f"<div class=\"mt-2\">{inner_html}<div class=\"mt-2\"><a href=\"{href}\" class=\"link-secondary\">Open page →</a></div></div>"
            f"</details>"
        )

    return pattern.sub(_repl, md_text)


def render_nav_html(nav_root: NavDir, current_out_dir: Path, output_root: Path, title_map: Dict[Path, str], current_md_path: Path) -> str:
    """Render nested <details>/<summary> nav. Links are relative to current_out_dir.

    Keeps the current folder open and highlights the active page link.
    """

    def rel_href(target: Path) -> str:
        return html.escape(os.path.relpath(target, start=current_out_dir).replace(os.sep, "/"))

    def dir_contains_current(node: NavDir) -> bool:
        try:
            current_md_path.relative_to(node.path)
            return True
        except ValueError:
            return False

    def render_dir(node: NavDir) -> str:
        # top-level: list immediate children; nested: recurse
        items: List[str] = []

        # files in this dir (ordered by filename), labels from title_map
        for nf in sorted(node.files, key=lambda f: f.src_md.name.lower()):
            label_text = title_map.get(nf.src_md, strip_numeric_prefix(nf.src_md.stem))
            label = html.escape(label_text)
            is_active = (nf.src_md == current_md_path)
            active_cls = " active" if is_active else ""
            aria = " aria-current=\"page\"" if is_active else ""
            items.append(f'<li class="nav-item"><a class="nav-link{active_cls}"{aria} href="{rel_href(nf.out_html)}">{label}</a></li>')

        # subdirectories
        for name in sorted(node.subdirs.keys(), key=lambda s: s.lower()):
            sub = node.subdirs[name]
            label = html.escape(strip_numeric_prefix(sub.name))
            inner = render_dir(sub)
            open_attr = " open" if dir_contains_current(sub) else ""
            items.append(
                (
                    f"<li>"
                    f"<details class=\"mb-1\"{open_attr}>"
                    f"<summary class=\"fw-semibold d-flex align-items-center justify-content-between\"><span>{label}</span><span class=\"chev\" aria-hidden=\"true\">▸</span></summary>"
                    f"<ul class=\"list-unstyled ms-3 my-1\">{inner}</ul>"
                    f"</details>"
                    f"</li>"
                )
            )

        return "".join(items)

    # Only show children of input root; don't wrap root itself
    inner_html = render_dir(nav_root)

    # Home & Search links (at site root)
    home_href = html.escape(os.path.relpath(output_root / "index.html", start=current_out_dir).replace(os.sep, "/"))
    search_href = html.escape(os.path.relpath(output_root / "search.html", start=current_out_dir).replace(os.sep, "/"))

    return (
        f"<div class=\"p-2\">"
        f"<form class=\"mb-2\" action=\"{search_href}\" method=\"get\">"
        f"  <div class=\"input-group input-group-sm\">"
        f"    <input class=\"form-control\" type=\"text\" name=\"q\" placeholder=\"Search…\" />"
        f"    <button class=\"btn btn-outline-secondary\" type=\"submit\">Search</button>"
        f"  </div>"
        f"</form>"
        f"<a class=\"btn btn-outline-primary w-100 mb-2\" href=\"{home_href}\">Home</a>"
        f"<ul class=\"list-unstyled\">{inner_html}</ul>"
        f"</div>"
    )


def convert_markdown_to_html(md_text: str) -> str:
    """Convert markdown to HTML with minimal extensions."""
    return markdown.markdown(md_text, extensions=["extra", "fenced_code", "tables"])


def convert_markdown_with_toc(md_text: str) -> Tuple[str, str]:
    """Convert markdown and also return a generated ToC HTML.

    Returns (content_html, toc_html)
    """
    md = markdown.Markdown(extensions=["extra", "fenced_code", "tables", "toc"])
    content_html = md.convert(md_text)
    toc_html = getattr(md, "toc", "")
    return content_html, toc_html


def render_page_html(page_title: str, nav_html: str, content_html: str, site_title: str, toc_html: Optional[str] = None) -> str:
    """Render full HTML page with Bootstrap layout and left sidebar."""
    title_text = html.escape(f"{page_title} · {site_title}" if site_title else page_title)
    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{title_text}</title>
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css\" rel=\"stylesheet\" integrity=\"sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH\" crossorigin=\"anonymous\">\n
    <style>
      /* layout: sticky left sidebar */
      :root {{
        --cm-body-bg: #fcfcfc;
        --cm-text: #222;
        --cm-muted: #6c757d;
        --cm-border: #e5e5e5;
      }}
      body {{
        overflow-y: scroll;
        background: var(--cm-body-bg);
        color: var(--cm-text);
        font-size: 1.0625rem; /* ~17px, slightly larger */
      }}
      .layout-container {{
        display: grid;
        grid-template-columns: 200px 1fr 260px; /* narrow sidebar by default */
        column-gap: 2.25rem;
        min-height: 100vh;
        transition: grid-template-columns 0.3s ease;
      }}
      .layout-container.sidebar-expanded {{
        grid-template-columns: 540px 1fr 260px; /* expand when triggered by JS */
      }}
      .sidebar {{
        border-right: 1px solid var(--cm-border);
        position: sticky;
        top: 0;
        height: 100vh;
        overflow: hidden; /* hide overflow when narrow */
        background: #fafafa;
        padding: 1.25rem 1.25rem 2rem 1.25rem; /* more padding */
        transition: overflow 0.3s ease;
      }}
      .layout-container.sidebar-expanded .sidebar {{
        overflow: auto; /* show scrollbar when expanded */
      }}
      aside.sidebar .p-2 {{
        opacity: .55 !important; /* 55% opacity by default */
        transition: opacity .2s ease;
      }}
      aside.sidebar:hover .p-2 {{
        opacity: .8 !important; /* more visible on sidebar hover */
      }}
      aside.sidebar .p-2 summary {{
        opacity: inherit; /* ensure folder headers inherit the fade */
      }}
      aside.sidebar .nav-link {{
        padding: .2rem .4rem;
        color: var(--cm-text);
        font-size: 1.025rem; /* slightly larger */
      }}
      aside.sidebar .nav-link:hover {{
        background: #eef2f6;
        border-radius: .25rem;
      }}
      details > summary {{
        cursor: pointer;
        list-style: none;
        transition: opacity .15s ease;
      }}
      details > summary::marker {{
        display: none;
      }}
      aside.sidebar details:hover > summary {{
        opacity: 1 !important; /* full visibility on section hover */
      }}
      aside.sidebar .nav-link:hover {{
        opacity: 1 !important; /* full visibility on link hover */
      }}
      details > summary .chev {{
        transition: transform .15s ease, opacity .2s ease;
        opacity: 0; /* invisible by default */
        font-size: 1.2em; /* smaller */
        margin-left: .5rem;
      }}
      aside.sidebar:hover details > summary .chev {{
        opacity: .6; /* visible on sidebar hover */
      }}
      details[open] > summary .chev {{
        transform: rotate(90deg);
      }}
      .content {{
        padding: 3rem 4rem; /* more padding */
        max-width: 980px;  /* a bit wider */
        font-family: Georgia, Cambria, "Times New Roman", Times, serif;
        line-height: 1.7;
        letter-spacing: .2px;
        background: white;
        box-shadow: 0 1px 2px rgba(0,0,0,.03);
        border: 1px solid var(--cm-border);
        border-radius: 8px;
        margin: 2.5rem 2.5rem 5rem 0; /* more breathing room */
      }}
      .content img {{ max-width: 100%; height: auto; }}
      .content h1, .content h2, .content h3, .content h4 {{
        margin-top: 2rem;
        font-weight: 600;
      }}
      .content p {{
        margin-bottom: 1.1rem;
      }}
      .content pre, .content code {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
      .content pre {{
        background: #f7f7f7;
        border: 1px solid var(--cm-border);
        border-radius: 6px;
        padding: .75rem 1rem;
      }}
      .content hr {{
        border-top: 1px solid var(--cm-border);
        margin: 1.5rem 0;
      }}
      a {{
        text-decoration: none;
      }}
      a:hover {{ text-decoration: underline; }}
      /* Wikilink embed blocks */
      .embed-block {{
        border: 1px dashed var(--cm-border);
        background: #fafafa;
        border-radius: 6px;
        padding: .5rem .75rem;
      }}
      .embed-block > summary {{
        font-weight: 500;
        user-select: none;
      }}
      .embed-block > summary .chev {{
        transition: transform .15s ease;
        opacity: .6;
        font-size: 1.2em; /* smaller */
        margin-left: .5rem;
      }}
      .embed-block[open] > summary .chev {{
        transform: rotate(90deg);
      }}
      .embed-block > summary::before {{
        content: "Relevant page: ";
        font-size: 0.75rem;
        color: var(--cm-muted);
        opacity: 0.7;
        margin-right: 0.5rem;
      }}
      /* Active nav link */
      aside.sidebar .nav-link.active {{
        background: #e7effa;
        border-radius: .25rem;
        font-weight: 600;
      }}
      /* Right ToC */
      .rightbar {{
        position: sticky;
        top: 2.5rem; /* align with main content's top margin */
        align-self: start; /* start at top of grid row */
        max-height: calc(100vh - 2.5rem);
        overflow: auto;
        margin: 2.5rem 0 5rem 0; /* match main content vertical margins */
        padding: 3rem 2rem; /* similar vertical padding to content */
        background: white;
        border: 1px solid var(--cm-border);
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,.03);
      }}
      .rightbar h2 {{
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: .06em;
        color: var(--cm-muted);
      }}
      .rightbar .toc ul {{
        padding-left: 1rem;
      }}
      .rightbar .toc {{
        opacity: .55; /* paler by default */
        transition: opacity .15s ease;
      }}
      .rightbar:hover .toc {{
        opacity: 1;
      }}
    </style>
  </head>
  <body>
    <div class=\"layout-container\">
      <aside class=\"sidebar\">{nav_html}</aside>
      <main class=\"content\">
        <h1 class=\"h3\">{html.escape(page_title)}</h1>
        <hr />
        {content_html}
      </main>
      {f'<aside class="rightbar"><h2>On this page</h2><div class="toc">{toc_html}</div></aside>' if toc_html else ''}
    </div>
    <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js\" integrity=\"sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz\" crossorigin=\"anonymous\"></script>
    <script>
      // Handle sidebar expand/collapse with delay
      let sidebarTimeout;
      const layoutContainer = document.querySelector('.layout-container');
      const sidebar = document.querySelector('.sidebar');
      
      sidebar.addEventListener('mouseenter', () => {{
        clearTimeout(sidebarTimeout);
        layoutContainer.classList.add('sidebar-expanded');
      }});
      
      sidebar.addEventListener('mouseleave', () => {{
        sidebarTimeout = setTimeout(() => {{
          layoutContainer.classList.remove('sidebar-expanded');
        }}, 500); // 500ms delay before collapsing
      }});
    </script>
  </body>
 </html>
"""


# -- search assets --
def write_search_assets(input_root: Path, output_root: Path, title_map: Dict[Path, str]) -> None:
    # Build a minimal index: [{title, path, text}]
    records: List[Dict[str, str]] = []
    for md_path, title in title_map.items():
        rel_out = relative_output_html(input_root, output_root, md_path)
        href = "/" + os.path.relpath(rel_out, start=output_root).replace(os.sep, "/")
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception:
            text = ""
        # crude strip of markdown for search preview
        plain = re.sub(r"```[\s\S]*?```", " ", text)
        plain = re.sub(r"`[^`]*`", " ", plain)
        plain = re.sub(r"\[\[(.*?)\]\]", r"\1", plain)
        plain = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", plain)
        plain = re.sub(r"[#*_>\-]+", " ", plain)
        plain = re.sub(r"\s+", " ", plain).strip()
        records.append({"title": title, "path": href, "text": plain})

    (output_root / "assets").mkdir(parents=True, exist_ok=True)
    (output_root / "assets" / "search_index.json").write_text(json.dumps(records), encoding="utf-8")

    # Simple search page using the working template from search_simple.py
    search_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Search</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 2rem; }
        .result { margin-bottom: 1rem; }
        .result .title { font-weight: 600; display: block; }
        .result .snippet { color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search</h1>
        <form id="searchForm" class="mb-3">
            <div class="input-group">
                <input type="text" id="searchInput" class="form-control" placeholder="Search...">
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>
        <div id="results"></div>
    </div>
    
    <script>
        let searchIndex = [];
        
        // Load search index
        fetch('./assets/search_index.json')
            .then(response => response.json())
            .then(data => {
                searchIndex = data;
                performSearch();
            });
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function performSearch() {
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const resultsDiv = document.getElementById('results');
            
            if (!query) {
                resultsDiv.innerHTML = '';
                return;
            }
            
            const results = searchIndex.filter(item => {
                const searchText = (item.title + ' ' + item.text).toLowerCase();
                return searchText.includes(query);
            });
            
            if (results.length === 0) {
                resultsDiv.innerHTML = '<p class="text-muted">No results found.</p>';
                return;
            }
            
            let html = '';
            results.slice(0, 20).forEach(item => {
                const textLower = item.text.toLowerCase();
                const queryPos = textLower.indexOf(query);
                let snippet = item.text;
                
                if (queryPos >= 0) {
                    const start = Math.max(0, queryPos - 50);
                    const end = Math.min(item.text.length, queryPos + 150);
                    snippet = item.text.substring(start, end);
                    if (start > 0) snippet = '...' + snippet;
                    if (end < item.text.length) snippet = snippet + '...';
                }
                
                html += `<div class="result">
                    <a href="${item.path}" class="title">${escapeHtml(item.title)}</a>
                    <div class="snippet">${escapeHtml(snippet)}</div>
                </div>`;
            });
            
            resultsDiv.innerHTML = html;
        }
        
        // Get query from URL and populate search box
        const urlParams = new URLSearchParams(window.location.search);
        const initialQuery = urlParams.get('q') || '';
        document.getElementById('searchInput').value = initialQuery;
        
        // Search on form submit
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            performSearch();
        });
        
        // Search on input
        document.getElementById('searchInput').addEventListener('input', performSearch);
    </script>
</body>
</html>"""

    (output_root / "search.html").write_text(search_html, encoding="utf-8")


# -- write all pages --
def write_pages(input_root: Path, output_root: Path, site_title: str) -> None:
    """Convert all markdown files and write HTML pages with nav."""
    nav_root = build_nav_tree(input_root, output_root)

    # enumerate markdown files with inclusion rules
    def _is_included_md(p: Path) -> bool:
        if p.name.startswith("."):
            return False
        rel = p.relative_to(input_root)
        # root: only index.md
        if rel.parent == Path("."):
            return rel.name.lower() == "index.md"
        # only include content under top-level folders that start with a number
        top = rel.parts[0]
        return top[:1].isdigit()

    md_files = [p for p in input_root.rglob("*.md") if _is_included_md(p)]
    # Prefer top-level index first (ensures Home exists for nav links)
    md_files.sort(key=lambda p: (0 if p.resolve() == (input_root / "index.md").resolve() else 1, str(p).lower()))

    # Titles now derive from filenames (numbers stripped)
    title_map: Dict[Path, str] = {p: strip_numeric_prefix(p.stem) for p in md_files}

    # Precompute embed html for targets: full markdown -> HTML
    embed_html_map: Dict[Path, str] = {}
    for md_path in md_files:
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception:
            text = ""
        # Keep full content in embeds now
        embed_html_map[md_path] = convert_markdown_to_html(text)

    # Build wikilink index for resolution
    wikilink_index = build_wikilink_index(md_files, title_map)

    for md_path in md_files:
        out_html_path = relative_output_html(input_root, output_root, md_path)
        out_dir = out_html_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # nav calculated relative to this page's output directory
        nav_html = render_nav_html(nav_root, current_out_dir=out_dir, output_root=output_root, title_map=title_map, current_md_path=md_path)

        # read & convert md
        md_text = md_path.read_text(encoding="utf-8")
        # Replace [[wikilinks]] with collapsible embeds before converting to HTML
        md_text_embeds = replace_wikilinks_with_embeds(
            md_text,
            current_md_path=md_path,
            input_root=input_root,
            output_root=output_root,
            title_map=title_map,
            embed_html_map=embed_html_map,
            wikilink_index=wikilink_index,
        )
        # Convert with ToC for page content
        content_html, toc_html = convert_markdown_with_toc(md_text_embeds)
        # Only show right ToC if there are at least 2 entries
        has_toc = toc_html.count("<a ") >= 2

        # title from filename (numbers stripped)
        page_title = title_map.get(md_path, strip_numeric_prefix(md_path.stem))

        # render template
        full_html = render_page_html(page_title=page_title, nav_html=nav_html, content_html=content_html, site_title=site_title, toc_html=(toc_html if has_toc else None))

        out_html_path.write_text(full_html, encoding="utf-8")

    # After writing content pages, write search index and search page
    write_search_assets(input_root, output_root, title_map)


# -- CLI --
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a simple static site from an Obsidian content folder.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("C:/Users/Zoom/My Drive (hello@causalmap.app)/causal-blog-flowershow/content"),
        help="Path to the Obsidian content folder (default: user's content path)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./site"),
        help="Output folder for generated site",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="Optional site title appended to page titles",
    )
    return parser.parse_args()


def main() -> None:
    # parse CLI args
    args = parse_args()
    input_root: Path = args.input.expanduser().resolve()
    output_root: Path = args.output.resolve()
    site_title: str = args.title

    if not input_root.exists() or not input_root.is_dir():
        raise SystemExit(f"Input directory not found: {input_root}")

    # prepare output directory (clean create)
    if output_root.exists():
        def _handle_remove_readonly(func, path, exc_info):  # Windows: clear read-only then retry
            try:
                os.chmod(path, stat.S_IWRITE)
            except Exception:
                pass
            try:
                func(path)
            except Exception:
                raise
        shutil.rmtree(output_root, onerror=_handle_remove_readonly)
    output_root.mkdir(parents=True, exist_ok=True)

    # copy non-md assets first
    copy_assets(input_root, output_root)

    # write all pages (md -> html)
    write_pages(input_root, output_root, site_title=site_title)

    print(f"Site generated at: {output_root}")


if __name__ == "__main__":
    main()
