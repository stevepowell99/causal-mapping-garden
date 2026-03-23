#!/usr/bin/env python3
"""
Simple static site generator for an Obsidian vault-like folder structure.

Now configurable via config.yml; run with --config path/to/config.yml.
"""

from __future__ import annotations

import argparse
import base64
import html
import os
from pathlib import Path
import hashlib
import re
import shutil
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union, Set
import json
import stat
import subprocess
import sys
import time
from datetime import date, datetime
from urllib.parse import quote, urljoin
PIPELINE_VERSION = "2025-10-15-wikilinks-anchors-v1"

# Media extensions: images + local video (mp4, webm, etc.)
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
_VIDEO_EXTS = {".mp4", ".webm", ".ogg", ".mov", ".m4v"}
_MEDIA_EXTS = _IMAGE_EXTS | _VIDEO_EXTS

# --- PDF post-processing ---
def _merge_prefixed_pdfs_in_each_folder(output_root: Path, *, prefix: str, merged_name: str) -> None:
    """Merge PDFs whose filename starts with `prefix` into `merged_name` (per folder).

    Skips if the merged output is already up-to-date w.r.t. the source PDFs.
    """
    def _merge_with_backend(pdfs_sorted: List[Path], out_pdf: Path) -> bool:
        """Return True if merge succeeded."""
        # Prefer pypdf (newer).
        try:
            from pypdf import PdfReader, PdfWriter  # type: ignore
            writer = PdfWriter()
            for p in pdfs_sorted:
                reader = PdfReader(str(p))
                for page in reader.pages:
                    writer.add_page(page)
            out_pdf.parent.mkdir(parents=True, exist_ok=True)
            with open(out_pdf, "wb") as f:
                writer.write(f)
            return True
        except Exception:
            pass

        # Fallback: PyPDF2 (older installs).
        try:
            from PyPDF2 import PdfReader, PdfWriter  # type: ignore
            writer = PdfWriter()
            for p in pdfs_sorted:
                reader = PdfReader(str(p))
                for page in reader.pages:
                    writer.add_page(page)
            out_pdf.parent.mkdir(parents=True, exist_ok=True)
            with open(out_pdf, "wb") as f:
                writer.write(f)
            return True
        except Exception:
            return False

    # Group candidates by folder.
    by_dir: Dict[Path, List[Path]] = defaultdict(list)
    try:
        for p in output_root.rglob(f"{prefix}*.pdf"):
            try:
                if not p.is_file():
                    continue
                by_dir[p.parent].append(p)
            except Exception:
                continue
    except Exception:
        return

    for d, pdfs in sorted(by_dir.items(), key=lambda kv: str(kv[0]).lower()):
        if not pdfs:
            continue
        pdfs_sorted = sorted(pdfs, key=lambda p: p.name.lower())
        out_pdf = d / merged_name

        # Stale check: skip if output exists and is newer than all inputs.
        try:
            newest_in = max(p.stat().st_mtime for p in pdfs_sorted)
        except Exception:
            newest_in = None
        try:
            out_mtime = out_pdf.stat().st_mtime if out_pdf.exists() else None
        except Exception:
            out_mtime = None

        if newest_in is not None and out_mtime is not None and out_mtime >= newest_in:
            continue

        try:
            ok = _merge_with_backend(pdfs_sorted, out_pdf)
            if not ok:
                msg = "PDF merge requested but could not import a PDF backend (pypdf or PyPDF2). Install with: pip install pypdf"
                _warn("pdf_merge", msg)
                try:
                    print(f"[WARN] pdf_merge: {msg}")
                except Exception:
                    pass
                continue
            try:
                rel = out_pdf.relative_to(output_root).as_posix()
            except Exception:
                rel = str(out_pdf)
            print(f"[PDF merge] {prefix}*.pdf -> {rel}")
        except PermissionError:
            _warn("pdf_merge", f"Could not write merged PDF (file locked?): {out_pdf}")
        except Exception as e:
            _warn("pdf_merge", f"Failed merging PDFs in {d}: {e}")

# --- social previews (Open Graph / Twitter cards) ---
# LinkedIn uses Open Graph tags; without them it often falls back to a bare <title>.
DEFAULT_SITE_URL = "https://garden.causalmap.app"
# Default social image (can be overridden in config.yml via og_image_path).
DEFAULT_OG_IMAGE_PATH = "https://firebasestorage.googleapis.com/v0/b/digital-axon-366208.appspot.com/o/sites%2FirD5tHiGP3mTEFbsiwNH%2Flogo%2Fcm%20logo%20blue.png?alt=media&token=a03afb3c-0ee2-4cc1-9e3a-3762983da685"

# --- warnings → text files (repo root) ---
# Keep terminal output clean: collect warnings and write them to warnings_<type>.txt / missing_<type>.txt.
_WARN_COLLECTOR: Optional["WarningCollector"] = None

class WarningCollector:
    """Collect warnings by type and flush them to text files in the repo root."""
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.by_type: Dict[str, List[str]] = defaultdict(list)
        self.debug_embed_lines: List[str] = []
        # Clear old reports each run to avoid stale warnings.
        try:
            for p in repo_root.glob("warnings_*.txt"):
                try:
                    p.unlink()
                except Exception:
                    pass
            for p in repo_root.glob("missing_*.txt"):
                try:
                    p.unlink()
                except Exception:
                    pass
            # Clear embed debug log too
            try:
                (repo_root / "debug_embed.txt").unlink()
            except Exception:
                pass
        except Exception:
            pass

    def warn(self, kind: str, msg: str) -> None:
        kind_clean = re.sub(r"[^a-z0-9_-]+", "_", (kind or "general").strip().lower()).strip("_") or "general"
        self.by_type[kind_clean].append(msg.rstrip())

    def write_lines(self, filename: str, lines: List[str]) -> None:
        """Write a report file (overwrites)."""
        try:
            out = self.repo_root / filename
            out.write_text("\n".join(lines).rstrip() + ("\n" if lines else ""), encoding="utf-8")
        except Exception:
            pass

    def flush(self) -> None:
        for kind, msgs in sorted(self.by_type.items()):
            if not msgs:
                continue
            lines = [f"[{kind}] {m}" for m in msgs]
            self.write_lines(f"warnings_{kind}.txt", lines)
        if self.debug_embed_lines:
            self.write_lines("debug_embed.txt", self.debug_embed_lines)

def _warn(kind: str, msg: str) -> None:
    """Central warning hook: write to collector if configured, else fall back to printing."""
    global _WARN_COLLECTOR
    if _WARN_COLLECTOR is not None:
        _WARN_COLLECTOR.warn(kind, msg)
        # Important: incremental build issues are easy to miss if they're only written to warnings_incremental.txt.
        # Print them to the console as well so the user immediately sees why a page wasn't rebuilt.
        if (kind or "").strip().lower() == "incremental":
            try:
                print(f"[WARN] incremental: {msg}")
            except Exception:
                pass
    else:
        try:
            print(f"[WARN] {kind}: {msg}")
        except Exception:
            pass

def _debug_embed(msg: str) -> None:
    """Collect embed debug logs into debug_embed.txt (repo root)."""
    global _WARN_COLLECTOR
    if _WARN_COLLECTOR is not None:
        _WARN_COLLECTOR.debug_embed_lines.append(msg.rstrip())

# Windows-safe text read for long paths / sync providers.
# Some Windows setups still hit MAX_PATH-ish issues without the \\?\ prefix.
def _read_text_windows_safe(p: Path, *, encoding: str = "utf-8", errors: str = "ignore") -> str:
    try:
        return p.read_text(encoding=encoding, errors=errors)
    except Exception:
        # Try extended-length path on Windows only
        if os.name != "nt":
            return ""
        try:
            ap = p.resolve()
            s = str(ap)
            if s.startswith("\\\\"):
                # UNC path: \\server\share\path -> \\?\UNC\server\share\path
                longp = "\\\\?\\UNC\\" + s.lstrip("\\")
            else:
                longp = "\\\\?\\" + s
            with open(longp, "r", encoding=encoding, errors=errors) as f:
                return f.read()
        except Exception:
            return ""

# Optional PDF engine (Playwright present? We'll call external exporter only if available)
try:
    from playwright.sync_api import sync_playwright  # type: ignore
    _PLAYWRIGHT_AVAILABLE = True
except Exception:
    _PLAYWRIGHT_AVAILABLE = False

# Minimal citation tools for HTML conversion (avoid external deps at import time)
def _build_bib_index_simple(bib_path: Path) -> Dict[str, Tuple[List[str], str]]:
    """Parse a BibTeX file minimally into key -> (author family names, year)."""
    index: Dict[str, Tuple[List[str], str]] = {}
    try:
        text = _read_text_windows_safe(bib_path, encoding="utf-8", errors="ignore")
    except Exception:
        return index
    for m in re.finditer(r"@[^@{]+\{\s*([^,\s]+)\s*,([\s\S]*?)\n\}\s*", text):
        key = m.group(1)
        body = m.group(2)
        ym = re.search(r"year\s*=\s*\{([^}]*)\}|year\s*=\s*\"([^\"]*)\"", body, flags=re.IGNORECASE)
        year = (ym.group(1) if ym and ym.group(1) is not None else (ym.group(2) if ym else "")).strip()
        if not year:
            dm = re.search(r"date\s*=\s*\{([^}]*)\}|date\s*=\s*\"([^\"]*)\"", body, flags=re.IGNORECASE)
            year = (dm.group(1) if dm and dm.group(1) is not None else (dm.group(2) if dm else "")).strip().split("-")[0]
        if not year:
            year = "n.d."
        am = re.search(r"author\s*=\s*\{([^}]*)\}|author\s*=\s*\"([^\"]*)\"", body, flags=re.IGNORECASE)
        author_raw = (am.group(1) if am and am.group(1) is not None else (am.group(2) if am else "")).strip()
        fams: List[str] = []
        for author in [a.strip() for a in author_raw.split(" and ") if a.strip()]:
            if "," in author:
                fam = author.split(",", 1)[0].strip()
            else:
                parts = author.split()
                fam = parts[-1] if parts else author
            if fam:
                fams.append(fam)
        index[key] = (fams, year or "n.d.")
    return index


def _build_bib_link_index(bib_path: Path) -> Dict[str, str]:
    """Build key -> preferred link (DOI URL if available, else URL)."""
    links: Dict[str, str] = {}
    try:
        text = bib_path.read_text(encoding="utf-8", errors="ignore")
        entries = re.split(r'\n@', text)
        for raw_entry in entries:
            if not raw_entry:
                continue
            if not raw_entry.startswith('@'):
                raw_entry = '@' + raw_entry
            header = re.match(r'@\w+\{([^,]+),', raw_entry)
            if not header:
                continue
            key = header.group(1).strip()
            body = raw_entry[header.end():]

            def extract_field_value(field_name: str, t: str) -> Optional[str]:
                # brace-delimited
                m = re.search(rf"{field_name}\\s*=\\s*\\{{", t, flags=re.IGNORECASE)
                if m:
                    start = m.end()
                    depth = 1
                    i = start
                    while i < len(t) and depth > 0:
                        if t[i] == '{':
                            depth += 1
                        elif t[i] == '}':
                            depth -= 1
                        i += 1
                    if depth == 0:
                        v = t[start:i-1].strip()
                        v = v.replace('{', '').replace('}', '')
                        return v.strip()
                qm = re.search(rf"{field_name}\\s*=\\s*\"([^\"]*)\"", t, flags=re.IGNORECASE)
                if qm:
                    return qm.group(1).strip()
                return None

            doi = extract_field_value('doi', body)
            url = extract_field_value('url', body)
            href: Optional[str] = None
            if doi:
                dd = doi.strip()
                # normalize to full DOI URL
                if dd.lower().startswith('http://doi.org/') or dd.lower().startswith('https://doi.org/'):
                    href = dd
                else:
                    dd = dd.lstrip('doi:').strip()
                    href = f"https://doi.org/{dd}"
            elif url:
                href = url.strip()
            if href:
                links[key] = href
    except Exception:
        return links
    return links


def _format_author_text(authors: List[str]) -> str:
    """Return author text used in rendered citations (kept intentionally simple)."""
    n = len(authors)
    if n == 0:
        return ""
    if n == 1:
        return authors[0]
    if n == 2:
        return f"{authors[0]} & {authors[1]}"
    return f"{authors[0]} et al."


def _extract_simple_page_locator(s: str) -> str:
    """Extract only the simple 'p. <digits>' locator form (ignore everything else)."""
    m = re.search(r"\bp\.\s*\d+\b", s)
    return m.group(0) if m else ""


def _format_parenthetical_author_year(authors: List[str], year: str, locator: str = "") -> str:
    """Format like: 'Smith et al. 2005, p. 5' (outer parentheses added elsewhere)."""
    a = _format_author_text(authors)
    base = f"{a} {year}".strip() if a else str(year).strip()
    return f"{base}, {locator}" if locator else base


def _format_narrative_author_year(authors: List[str], year: str, locator: str = "") -> str:
    """Format like: 'Smith et al. (2005, p. 5)'."""
    a = _format_author_text(authors)
    if not a:
        return f"({year}, {locator})" if locator else f"({year})"
    return f"{a} ({year}, {locator})" if locator else f"{a} ({year})"


def _convert_citations_bracket_to_apa(md_text: str, bib_index: Dict[str, Tuple[List[str], str]], bib_links: Optional[Dict[str, str]] = None) -> Tuple[str, Set[str]]:
    """Convert bracket citations [@key; @key2, p.12] to APA text. Returns (converted_text, set_of_used_keys)."""
    pattern = re.compile(r"\[([^\]]*@[^\]]+)\]")
    used_keys: Set[str] = set()

    def _repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        out: List[str] = []
        # Find each @key in the bracket. Anything after the key (until next @ or ;)
        # is treated as a locator/suffix (e.g., ", p. 12").
        for km in re.finditer(r"@([A-Za-z0-9:_-]+)([^@;]*)", inner):
            key = km.group(1)
            suffix_raw = (km.group(2) or "").strip(" ,")
            locator = _extract_simple_page_locator(suffix_raw)

            if key in bib_index:
                used_keys.add(key)

            authors, year = bib_index.get(key, ([], "n.d."))
            base_inner = _format_parenthetical_author_year(authors, year, locator=locator)

            href = bib_links.get(key) if bib_links else None
            if href:
                out.append(f"[{base_inner}]({href})")
            else:
                out.append(base_inner)

        # One pair of parentheses for the whole group: (A; B), not (A); (B)
        return f"({'; '.join(out)})" if out else m.group(0)

    converted = pattern.sub(_repl, md_text)
    
    # Also convert standalone citations like "@key" to narrative style.
    # Example: "@friese2025, p. 5" -> "Friese (2025, p. 5)"
    bare_pattern = re.compile(r"(?<![\w\[])\@([A-Za-z0-9:_-]+)\b(?:\s*,\s*(p\.\s*\d+))?")

    def _repl_bare(m2: re.Match[str]) -> str:
        key = m2.group(1)
        locator = (m2.group(2) or "").strip()
        if key in bib_index:
            used_keys.add(key)
        authors, year = bib_index.get(key, ([], "n.d."))
        base_inner = _format_narrative_author_year(authors, year, locator=locator)
        href = bib_links.get(key) if bib_links else None
        if href:
            return f"[{base_inner}]({href})"
        return base_inner

    converted = bare_pattern.sub(_repl_bare, converted)
    return converted, used_keys


def _format_reference_list(used_keys: Set[str], bib_index: Dict[str, Tuple[List[str], str]], full_bib_path: Path) -> str:
    """Generate APA 7th reference list HTML for used citations."""
    if not used_keys:
        return ""
    
    # Parse bib file to get full entries
    bib_entries: Dict[str, Dict[str, str]] = {}
    try:
        text = full_bib_path.read_text(encoding="utf-8", errors="ignore")
        # Split into entries
        entries = re.split(r'\n@', text)
        for raw_entry in entries:
            if not raw_entry.startswith('@'):
                raw_entry = '@' + raw_entry
            # Extract key
            header = re.match(r'@\w+\{([^,]+),', raw_entry)
            if not header:
                continue
            key = header.group(1).strip()
            if key not in used_keys:
                continue
            
            body = raw_entry[header.end():]
            entry_data = {}
            
            def extract_field_value(field_name: str, text: str) -> Optional[str]:
                """Extract a BibTeX field value, handling nested braces."""
                # Try brace-delimited first
                pattern = rf'{field_name}\s*=\s*\{{'
                m = re.search(pattern, text, flags=re.IGNORECASE)
                if m:
                    start = m.end()
                    depth = 1
                    i = start
                    while i < len(text) and depth > 0:
                        if text[i] == '{':
                            depth += 1
                        elif text[i] == '}':
                            depth -= 1
                        i += 1
                    if depth == 0:
                        value = text[start:i-1]
                        # Strip LaTeX braces: {{Phrase}} -> Phrase, {Word} -> Word
                        # Handle double braces first
                        value = re.sub(r'\{\{([^}]+)\}\}', r'\1', value)
                        # Then single braces around single words
                        value = re.sub(r'\{(\w+)\}', r'\1', value)
                        # Finally, drop any remaining braces defensively
                        value = value.replace('{', '').replace('}', '')
                        return value.strip()
                
                # Try quote-delimited
                qm = re.search(rf'{field_name}\s*=\s*"([^"]*)"', text, flags=re.IGNORECASE)
                if qm:
                    return qm.group(1).strip()
                
                return None
            
            # Extract fields
            if title := extract_field_value('title', body):
                entry_data['title'] = title
            if journal := extract_field_value('journal', body):
                entry_data['journal'] = journal
            if volume := extract_field_value('volume', body):
                entry_data['volume'] = volume
            if pages := extract_field_value('pages', body):
                entry_data['pages'] = pages
            if booktitle := extract_field_value('booktitle', body):
                entry_data['booktitle'] = booktitle
            if publisher := extract_field_value('publisher', body):
                entry_data['publisher'] = publisher
            if doi := extract_field_value('doi', body):
                entry_data['doi'] = doi
            if url := extract_field_value('url', body):
                entry_data['url'] = url
            
            bib_entries[key] = entry_data
    except Exception:
        pass
    
    # Format references
    refs = []
    for key in sorted(used_keys, key=lambda k: (bib_index.get(k, ([""], ""))[0][0].lower() if bib_index.get(k, ([""], ""))[0] else "", bib_index.get(k, ([""], ""))[1])):
        authors, year = bib_index.get(key, ([], "n.d."))
        entry_data = bib_entries.get(key, {})
        
        # Format author list
        if len(authors) == 0:
            author_str = ""
        elif len(authors) == 1:
            author_str = authors[0]
        elif len(authors) <= 20:
            author_str = ", ".join(authors[:-1]) + ", & " + authors[-1]
        else:
            author_str = ", ".join(authors[:19]) + ", ... " + authors[-1]
        
        # Get title
        title = entry_data.get('title', f"[{key}]")
        
        # Build preferred href
        href: Optional[str] = None
        doi = entry_data.get('doi')
        url = entry_data.get('url')
        if doi:
            dd = doi.strip()
            if dd.lower().startswith('http://doi.org/') or dd.lower().startswith('https://doi.org/'):
                href = dd
            else:
                dd = dd.lstrip('doi:').strip()
                href = f"https://doi.org/{dd}"
        elif url:
            href = url.strip()
        
        # Format reference
        ref_html = f"<p class=\"reference\">"
        if author_str:
            ref_html += f"{html.escape(author_str)} ({year}). "
        else:
            ref_html += f"({year}). "
        
        ref_html += f"<em>{html.escape(title)}</em>"
        
        # Add journal/book info if available
        if 'journal' in entry_data:
            ref_html += f". {html.escape(entry_data['journal'])}"
            if 'volume' in entry_data:
                ref_html += f", <em>{html.escape(entry_data['volume'])}</em>"
            if 'pages' in entry_data:
                ref_html += f", {html.escape(entry_data['pages'])}"
        elif 'booktitle' in entry_data:
            ref_html += f". In <em>{html.escape(entry_data['booktitle'])}</em>"
        elif 'publisher' in entry_data:
            ref_html += f". {html.escape(entry_data['publisher'])}"
        
        if href:
            safe_href = html.escape(href)
            ref_html += f". <a href=\"{safe_href}\" target=\"_blank\" rel=\"noopener\">{safe_href}</a>"
        
        ref_html += ".</p>"
        refs.append(ref_html)
    
    if refs:
        return '<div class="references"><h2>References</h2>' + "".join(refs) + '</div>'
    return ""


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

def _numeric_prefix_tuple(name: str) -> Optional[Tuple[int, ...]]:
    """Return leading numeric prefix as tuple, else None.

    Examples:
    - "010 Foo" -> (10,)
    - "0.01 Intro" -> (0, 1)
    - "AI-assisted ..." -> None
    """
    m = re.match(r"^\s*(\d+(?:\.\d+)*)", name)
    if not m:
        return None
    return tuple(int(p) for p in m.group(1).split(".") if p != "")


def _path_file_key(p: Path) -> Tuple[int, Tuple[int, ...], str]:
    """Obsidian-like ordering for files: numbered first (numeric), then name."""
    nums = _numeric_prefix_tuple(p.name)
    return (0 if nums is not None else 1, nums or (), p.name.lower())


def _nav_file_key(nf: "NavFile") -> Tuple[int, Tuple[int, ...], str]:
    """Obsidian-like ordering for nav files: numbered first (numeric), then name."""
    return _path_file_key(nf.src_md)


def _nav_dirname_key(name: str) -> Tuple[int, Tuple[int, ...], str]:
    """Obsidian-like ordering for directories: numbered first (numeric), then name."""
    nums = _numeric_prefix_tuple(name)
    return (0 if nums is not None else 1, nums or (), name.lower())


def _sanitize_stem_for_windows(stem: str, rel_path_for_hash: str, max_len: int = 45) -> str:
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


def _preflight_check_windows_path_lengths(
    *,
    input_root: Path,
    output_root: Path,
    md_files_to_process: List[Path],
    # Use a MAX_PATH-ish threshold (legacy Windows APIs often fail around 260 chars).
    # We keep a small buffer vs 260 to account for occasional internal additions.
    max_full_path_chars: int = 259,
    max_filename_chars: int = 180,
) -> None:
    """Fail early (with a clear error) if Windows path/filename lengths are likely to break writes.

    We check:
    - Full output paths (as strings) against a conservative MAX_PATH-ish threshold.
    - Output filename length against a conservative per-component threshold.
    """
    if os.name != "nt":
        return

    problems: List[str] = []
    for md_path in md_files_to_process:
        try:
            rel_md = md_path.relative_to(input_root).as_posix()
        except Exception:
            rel_md = str(md_path)

        out_html_path = relative_output_html(input_root, output_root, md_path)

        out_s = str(out_html_path)
        if len(out_s) > max_full_path_chars:
            problems.append(
                f"- OUTPUT ({len(out_s)} chars) {rel_md}\n  {out_s}"
            )
        if len(out_html_path.name) > max_filename_chars:
            problems.append(
                f"- OUTPUT NAME ({len(out_html_path.name)} chars) {rel_md}\n  {out_html_path.name}"
            )

    if problems:
        raise SystemExit(
            "Build aborted: one or more pages would generate OUTPUT paths/filenames that are too long for Windows.\n"
            "Shorten the folder/file names (page titles) and try again.\n\n"
            + "\n".join(problems)
        )


def build_nav_tree(input_root: Path, output_root: Path, require_numbered_folders: bool = True) -> NavDir:
    """Scan input_root and build a NavDir tree with NavFile entries for .md files."""
    root = NavDir(name=input_root.name, path=input_root)

    for dirpath, dirnames, filenames in os.walk(input_root):
        # skip hidden directories; at top-level include only folders starting with a number (if required)
        current_dir = Path(dirpath)
        if current_dir == input_root:
            if require_numbered_folders:
                dirnames[:] = [d for d in dirnames if not d.startswith((".","_")) and ('!' not in d) and d.lower() != "img" and (d[:1].isdigit())]
            else:
                dirnames[:] = [d for d in dirnames if not d.startswith((".","_")) and ('!' not in d) and d.lower() != "img"]
        else:
            dirnames[:] = [d for d in dirnames if not d.startswith((".","_")) and ('!' not in d) and d.lower() != "img"]

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
            # Files with ! in filename are EXCLUDED from nav (but still built for preview)
            if '!' in fname:
                continue
            fpath = current_dir / fname
            # only include markdown files; at root include only index.md (unless require_numbered_folders is False)
            if is_markdown_file(fpath):
                if require_numbered_folders and current_dir == input_root and fname.lower() != "index.md":
                    continue
                out_html = relative_output_html(input_root, output_root, fpath)
                title = fpath.stem
                node.files.append(NavFile(title=title, src_md=fpath, out_html=out_html))

        # sort by numeric prefixes (2 < 10), then name; keep index.md first within a folder
        node.files.sort(key=_nav_file_key)

    return root


def _flatten_nav_files_in_order(node: NavDir) -> List[Path]:
    """Return markdown Paths in the same order as the sidebar nav renders them.

    Order is hierarchical (Obsidian-like): subdirs first (sorted), then files
    (sorted). This matches what users see in Obsidian's file explorer.
    """
    out: List[Path] = []
    for name in sorted(node.subdirs.keys(), key=_nav_dirname_key):
        out.extend(_flatten_nav_files_in_order(node.subdirs[name]))
    for nf in sorted(node.files, key=_nav_file_key):
        out.append(nf.src_md)
    return out


# -- helpers: asset copying --
def copy_assets(input_root: Path, output_root: Path) -> None:
    """Copy all non-markdown files, preserving structure."""
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
    for src in input_root.rglob("*"):
        if src.is_dir() or src.name.startswith("."):
            continue
        # Ignore Obsidian/automation cache folders we never want to publish
        if ".smart-env" in src.parts:
            continue
        # Files with ! in filename are included (folders with ! are excluded below)
        if is_markdown_file(src):
            continue
        # Skip .qmd (source only; we copy the generated .html)
        if src.suffix.lower() == ".qmd":
            continue
        # Copy pre-built .html (e.g. Quarto output); we only generate .html from .md
        if src.suffix.lower() == ".html":
            # Copy: Quarto etc. generate .html from .qmd; we don't process .qmd
            pass
        # Skip .obsidian and any folder path segment containing '!'
        elif ".obsidian" in src.parts or any('!' in part for part in src.parts[:-1]):
            continue
        # Allow all files under 'assets' or Quarto *_files folders
        in_assets = any(part.lower() == "assets" for part in src.parts)
        in_quarto_files = any(p.endswith("_files") for p in src.parts)
        if in_assets or in_quarto_files:
            pass  # copy everything
        else:
            # Skip images unless in assets or quarto _files
            if src.suffix.lower() in image_exts:
                continue
            # Skip bulk 'img' folders unless under 'assets'
            if any(part.lower() == "img" for part in src.parts):
                continue
        rel = src.relative_to(input_root)
        dst = output_root / rel
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        except Exception as e:
            _warn("copy_assets", f"Failed to copy {src} to {dst}: {e}")


def copy_project_favicons(output_root: Path) -> None:
    """Copy standard favicon files from project ./assets to output /assets if present.

    Looks for: favicon.ico, favicon.svg, apple-touch-icon.png, site.webmanifest
    """
    try:
        project_assets = Path(__file__).parent / "assets"
        dest_dir = output_root / "assets"
        names = [
            "favicon.ico",
            "favicon.svg",
            "apple-touch-icon.png",
            "site.webmanifest",
        ]
        any_found = False
        for name in names:
            src = project_assets / name
            if src.exists() and src.is_file():
                if not any_found:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    any_found = True
                shutil.copy2(src, dest_dir / name)
    except Exception:
        # Best-effort; ignore failures
        pass

def build_image_name_index(input_root: Path, vault_root: Path, image_exts: Set[str]) -> Dict[str, Path]:
    """Build a lowercase filename -> absolute Path index for image files."""
    lower_name_to_path: Dict[str, Path] = {}
    for root in (input_root, vault_root):
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in image_exts:
                lower_name_to_path.setdefault(p.name.lower(), p)
    return lower_name_to_path


_EXTERNAL_README_PATH_CACHE: Optional[Path] = None
_EXTERNAL_README_PATH_CACHE_READY = False


def resolve_external_readme_path(readme_path: Optional[str] = None) -> Optional[Path]:
    """Resolve external README path from arg/config/default, with lightweight caching."""
    global _EXTERNAL_README_PATH_CACHE, _EXTERNAL_README_PATH_CACHE_READY

    if readme_path:
        try:
            return Path(readme_path).expanduser().resolve()
        except Exception:
            return Path(readme_path).expanduser()

    if _EXTERNAL_README_PATH_CACHE_READY:
        return _EXTERNAL_README_PATH_CACHE

    resolved: Optional[Path] = None
    try:
        config_path = Path("config.yml")
        if config_path.exists():
            import yaml
            cfg_text = config_path.read_text(encoding="utf-8")
            loaded = yaml.safe_load(cfg_text) or {}
            if isinstance(loaded, dict) and loaded.get("readme"):
                resolved = Path(str(loaded["readme"])).expanduser().resolve()
    except Exception:
        resolved = None

    if resolved is None:
        resolved = Path(r"C:\dev\causal-map-extension\webapp\README.md")

    _EXTERNAL_README_PATH_CACHE = resolved
    _EXTERNAL_README_PATH_CACHE_READY = True
    return resolved


def resolve_image_src_path(ref: str, md_path: Path, input_root: Path, vault_root: Path, name_index: Dict[str, Path], image_exts: Set[str]) -> Optional[Path]:
    """Resolve an image reference to a source file Path.

    Resolution order for bare filenames: ./img/<file> → relative path → root-absolute under vault → name index.
    """
    # Skip URLs and data URIs
    if re.match(r"^(?:[a-z]+:)?//", ref) or ref.startswith("data:"):
        return None

    # Strip angle brackets, anchors, queries
    if ref.startswith("<") and ref.endswith(">"):
        ref = ref[1:-1]
    ref_clean = ref.split("#", 1)[0].split("?", 1)[0]

    # Obsidian sometimes stores image embeds as vault-relative paths without a leading slash,
    # e.g. ![[001 Working Papers/img/foo.png]]. If that path exists under input_root, prefer it.
    if not ref_clean.startswith("/"):
        cand_under_input = input_root / Path(ref_clean)
        if cand_under_input.exists() and cand_under_input.is_file():
            return cand_under_input

    # Bare filename with image extension: prefer ./img/<file>
    is_bare = (os.sep not in ref_clean and "/" not in ref_clean)
    if is_bare and Path(ref_clean).suffix.lower() in image_exts:
        local_img = md_path.parent / "img" / ref_clean
        if local_img.exists() and local_img.is_file():
            return local_img

    # Relative or root-absolute path
    if ref_clean.startswith("/"):
        candidate = (vault_root / ref_clean.lstrip("/"))
    else:
        candidate = (md_path.parent / ref_clean)
    if candidate.exists() and candidate.is_file():
        return candidate

    # External README fallback: refs like "help-images/foo.png" are relative to README folder.
    if not ref_clean.startswith("/"):
        try:
            external_readme = resolve_external_readme_path()
            if external_readme is not None:
                readme_rel_candidate = (external_readme.parent / ref_clean)
                if readme_rel_candidate.exists() and readme_rel_candidate.is_file():
                    return readme_rel_candidate
        except Exception:
            pass

    # Special-case fallback: references like 'img/...' located at site root '/img/...'
    ref_no_dot = ref_clean[2:] if ref_clean.startswith("./") else ref_clean
    if ref_no_dot.lower().startswith("img/") or ref_no_dot.lower().startswith("img\\"):
        cand_input = input_root / Path(ref_no_dot)
        if cand_input.exists() and cand_input.is_file():
            return cand_input
        cand_vault = vault_root / Path(ref_no_dot)
        if cand_vault.exists() and cand_vault.is_file():
            return cand_vault

    # Fallback to name index for bare filenames
    if is_bare and Path(ref_clean).suffix.lower() in image_exts:
        return name_index.get(ref_clean.lower())

    return None


def _extract_image_like_refs(md_text: str) -> Set[str]:
    """Extract candidate image/video references from markdown/html.

    Catches:
    - Markdown images: ![alt](path)
    - HTML <img src="path"> and <video src="path">
    - Obsidian embeds: ![[name.ext]]
    Returns raw references as they appear (may be relative, root-absolute, etc.).
    """
    refs: Set[str] = set()
    # markdown image: ![alt](path)
    md_img_pat = re.compile(r"!\[[^\]]*\]\(\s*(<[^>]+>|\"[^\"]+\"|'[^']+'|[^)\s]+)")
    for m in md_img_pat.finditer(md_text):
        dest = m.group(1).strip()
        if (dest.startswith("<") and dest.endswith(">")) or (dest.startswith('"') and dest.endswith('"')) or (dest.startswith("'") and dest.endswith("'")):
            dest = dest[1:-1]
        refs.add(dest)
    for m in re.finditer(r"<img[^>]+src=[\"']([^\"']+)[\"']", md_text, flags=re.IGNORECASE):
        refs.add(m.group(1))
    for m in re.finditer(r"<video[^>]+src=[\"']([^\"']+)[\"']", md_text, flags=re.IGNORECASE):
        refs.add(m.group(1))
    for m in re.finditer(r"!\[\[([^\]|#]+)(?:#[^\]]+)?\]\]", md_text):
        refs.add(m.group(1).strip())
    return refs


def _maybe_copy_single_asset(src_path: Path, base_root: Path, output_root: Path) -> None:
    """Copy a single asset from src_path into output_root, preserving relative path under base_root.

    - If src_path not under base_root, do nothing.
    - Creates parent directories as needed.
    """
    try:
        rel = src_path.relative_to(base_root)
    except ValueError:
        return
    dst_path = output_root / rel
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    # Only copy or update if source is newer or destination missing
    if dst_path.exists():
        try:
            if src_path.stat().st_mtime <= dst_path.stat().st_mtime:
                return
        except Exception:
            pass
    shutil.copy2(src_path, dst_path)


def _map_asset_to_output_path(
    src_path: Path,
    input_root: Path,
    vault_root: Path,
    output_root: Path,
    external_readme_root: Optional[Path] = None,
) -> Tuple[Path, Path]:
    """Map a source asset path to output path and return (dst, base_root)."""
    try:
        rel_under_input = src_path.relative_to(input_root)
        return output_root / rel_under_input, input_root
    except ValueError:
        pass

    if external_readme_root is not None:
        try:
            rel_under_readme = src_path.relative_to(external_readme_root)
            return output_root / rel_under_readme, external_readme_root
        except ValueError:
            pass

    rel_under_vault = src_path.relative_to(vault_root)
    return output_root / rel_under_vault, vault_root


def _resolve_md_href_to_md_path(href: str, md_path: Path, input_root: Path) -> Optional[Path]:
    """Try to resolve a markdown link href to a markdown file within input_root.

    Handles relative paths, root-absolute paths, optional missing .md extension, and index.md in directories.
    Returns absolute Path if found, else None.
    """
    # ignore external and hash-only links
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or href.startswith("#") or href.startswith("data:"):
        return None
    # strip angle brackets, anchors, queries
    if href.startswith("<") and href.endswith(">"):
        href = href[1:-1]
    href_clean = href.split("#", 1)[0].split("?", 1)[0]

    def _check(p: Path) -> Optional[Path]:
        if p.is_file() and p.suffix.lower() in {".md", ".markdown"}:
            try:
                p.relative_to(input_root)
                return p
            except ValueError:
                return None
        if p.is_dir():
            idx = p / "index.md"
            if idx.exists():
                try:
                    idx.relative_to(input_root)
                    return idx
                except ValueError:
                    return None
        # try adding .md if no extension
        if p.suffix == "":
            with_md = p.with_suffix(".md")
            if with_md.exists():
                try:
                    with_md.relative_to(input_root)
                    return with_md
                except ValueError:
                    return None
        return None

    # root-absolute under input_root
    if href_clean.startswith("/"):
        cand = input_root / href_clean.lstrip("/")
        hit = _check(cand)
        if hit:
            return hit
    else:
        # relative to current note
        cand = (md_path.parent / href_clean)
        hit = _check(cand)
        if hit:
            return hit
    return None


def extract_outgoing_internal_links(
    md_text: str,
    md_path: Path,
    input_root: Path,
    wikilink_index: Dict[str, Path],
    missing_wikilinks: Optional[Dict[str, Set[str]]] = None,
    missing_md_links: Optional[Dict[str, Set[str]]] = None,
) -> Set[Path]:
    """Extract outgoing links to other markdown notes (Paths) from the text.

    Includes: wikilinks [[...]] (excludes image embeds ![[...]]) and markdown links [text](href) resolving to markdown files.
    """
    targets: Set[Path] = set()
    rel_page: Optional[str] = None
    if missing_wikilinks is not None or missing_md_links is not None:
        try:
            rel_page = str(md_path.relative_to(input_root))
        except Exception:
            rel_page = str(md_path)

    # wikilinks including transclusions: [[Target]] and ![[Target]]
    for m in re.finditer(r"!?\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]", md_text):
        raw = m.group(1).strip()
        if raw.startswith("#"):
            continue  # intra-page anchors
        key = raw.lower()
        hit = wikilink_index.get(key) or wikilink_index.get(strip_numeric_prefix(raw).lower())
        if hit:
            targets.add(hit)
        else:
            if missing_wikilinks is not None and rel_page is not None:
                missing_wikilinks[rel_page].add(raw)

    # markdown links [text](href)
    for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", md_text):
        href = m.group(1)
        hit = _resolve_md_href_to_md_path(href, md_path, input_root)
        if hit:
            targets.add(hit)
        else:
            if (
                missing_md_links is not None
                and rel_page is not None
                and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href)
                and not href.startswith("#")
            ):
                missing_md_links[rel_page].add(href)

    return targets


def copy_referenced_images(md_files: List[Path], input_root: Path, output_root: Path, missing_images: Optional[Dict[str, Set[str]]] = None) -> Set[Path]:
    """Ensure images and videos referenced by markdown are copied to output and return set of expected destination Paths.

    Handles relative paths, root-absolute paths (relative to vault root = input_root.parent),
    HTML <img>/<video> tags, and Obsidian ![[file.ext]] embeds by name.
    """
    vault_root = input_root.parent
    external_readme = resolve_external_readme_path()
    external_readme_root = external_readme.parent if external_readme is not None else None
    name_index = build_image_name_index(input_root, vault_root, _MEDIA_EXTS)
    expected_dests: Set[Path] = set()

    for md_path in md_files:
        rel_page = None
        if missing_images is not None:
            try:
                rel_page = str(md_path.relative_to(input_root))
            except Exception:
                rel_page = str(md_path)
        # Keep image copying in sync with page rendering: use the same Windows-safe reader.
        # (Some sync providers / non-UTF8 chars can make a strict read fail; pages still render with _read_text_windows_safe.)
        text = _read_text_windows_safe(md_path, encoding="utf-8", errors="ignore")
        if not text.strip():
            continue
        text = strip_yaml_front_matter(text)
        refs = _extract_image_like_refs(text)
        if not refs:
            continue

        for ref in refs:
            src_file = resolve_image_src_path(ref, md_path, input_root, vault_root, name_index, _MEDIA_EXTS)

            if not src_file or not src_file.exists() or not src_file.is_file():
                if missing_images is not None and rel_page is not None:
                    missing_images[rel_page].add(ref)
                continue
            
            # Normalize (eliminate '..' etc.) so relative_to() and copy destinations are stable.
            # This matters for refs like '../img/foo.png' which otherwise carry '..' into output paths.
            try:
                src_file = src_file.resolve()
            except Exception:
                pass

            # Determine destination and copy if needed
            try:
                dst, base_root = _map_asset_to_output_path(
                    src_file,
                    input_root,
                    vault_root,
                    output_root,
                    external_readme_root=external_readme_root,
                )
            except ValueError:
                if missing_images is not None and rel_page is not None:
                    missing_images[rel_page].add(ref)
                continue
            _maybe_copy_single_asset(src_file, base_root, output_root)
            expected_dests.add(dst)
    return expected_dests

def build_links_maps(
    md_files: List[Path],
    input_root: Path,
    title_map: Dict[Path, str],
    wikilink_index: Dict[str, Path],
    missing_wikilinks: Optional[Dict[str, Set[str]]] = None,
    missing_md_links: Optional[Dict[str, Set[str]]] = None,
) -> Tuple[Dict[Path, Set[Path]], Dict[Path, Set[Path]]]:
    """Build outgoing links and backlinks maps between notes.

    Returns (outgoing_map, backlinks_map) mapping each note to sets of target/source notes.
    """
    outgoing: Dict[Path, Set[Path]] = {p: set() for p in md_files}
    backlinks: Dict[Path, Set[Path]] = {p: set() for p in md_files}

    for p in md_files:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            text = ""
        text = strip_yaml_front_matter(text)
        targets = extract_outgoing_internal_links(
            text,
            p,
            input_root,
            wikilink_index,
            missing_wikilinks=missing_wikilinks,
            missing_md_links=missing_md_links,
        )
        # limit to known md_files to avoid listing excluded pages
        filtered = {t for t in targets if t in title_map}
        outgoing[p] = filtered

    for src, tgts in outgoing.items():
        for t in tgts:
            if t in backlinks:
                backlinks[t].add(src)

    return outgoing, backlinks


def render_links_list_html(md_targets: List[Path], current_out_dir: Path, input_root: Path, output_root: Path, title_map: Dict[Path, str]) -> Optional[str]:
    """Render a simple unordered list of links to target notes. Returns None if empty."""
    if not md_targets:
        return None
    items: List[str] = []
    for t in sorted(md_targets, key=lambda p: title_map.get(p, strip_numeric_prefix(p.stem)).lower()):
        href = os.path.relpath(relative_output_html(input_root, output_root, t), start=current_out_dir).replace(os.sep, "/")
        label = html.escape(title_map.get(t, strip_numeric_prefix(t.stem)))
        items.append(f'<li><a href="{html.escape(href)}" class="link-secondary">{label}</a></li>')
    return f'<ul>{"".join(items)}</ul>'


def replace_image_wikilinks(md_text: str, current_md_path: Path, input_root: Path, output_root: Path) -> str:
    """Replace Obsidian media embeds ![[...]] with <img> or <video> tags pointing to copied assets."""
    vault_root = input_root.parent
    external_readme = resolve_external_readme_path()
    external_readme_root = external_readme.parent if external_readme is not None else None
    name_index = build_image_name_index(input_root, vault_root, _MEDIA_EXTS)
    out_dir = relative_output_html(input_root, output_root, current_md_path).parent

    pattern = re.compile(r"!\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")

    def _repl(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        alt = match.group(2).strip() if match.group(2) else ""
        src_file = resolve_image_src_path(target, current_md_path, input_root, vault_root, name_index, _MEDIA_EXTS)
        if not src_file:
            return match.group(0)

        # Determine destination path, ensure asset is copied, then compute relative href.
        try:
            dst, base_root = _map_asset_to_output_path(
                src_file,
                input_root,
                vault_root,
                output_root,
                external_readme_root=external_readme_root,
            )
        except ValueError:
            return match.group(0)
        _maybe_copy_single_asset(src_file, base_root, output_root)

        href = html.escape(os.path.relpath(dst, start=out_dir).replace(os.sep, "/"))
        alt_attr = html.escape(alt or Path(target).stem)
        ext = src_file.suffix.lower()
        if ext in _VIDEO_EXTS:
            return f'<div class="video-embed mb-3"><video src="{href}" controls class="w-100">Your browser does not support the video tag.</video></div>'
        # NOTE: Avoid lazy-loading; it breaks Playwright PDF generation (images often won't load before print).
        return f'<img src="{href}" alt="{alt_attr}" class="img-fluid" />'

    return pattern.sub(_repl, md_text)


# Rewrite standard markdown and HTML image/video references to correct output-relative paths
def rewrite_standard_image_refs(md_text: str, current_md_path: Path, input_root: Path, output_root: Path) -> str:
    """Fix image/video src/hrefs so that references resolve to correct output structure.

    - Handles: markdown ![alt](path), HTML <img src="path">, <video src="path">
    - For video files: emits <video> tag instead of <img>
    - Leaves external URLs and data URIs unchanged
    """
    vault_root = input_root.parent
    external_readme = resolve_external_readme_path()
    external_readme_root = external_readme.parent if external_readme is not None else None
    name_index = build_image_name_index(input_root, vault_root, _MEDIA_EXTS)
    out_dir = relative_output_html(input_root, output_root, current_md_path).parent

    def _rewrite_path(ref: str) -> Optional[Tuple[str, str]]:
        """Return (href, kind) with kind in ('image','video') or None."""
        if re.match(r"^(?:[a-z]+:)?//", ref) or ref.startswith("data:"):
            return None
        src_file = resolve_image_src_path(ref, current_md_path, input_root, vault_root, name_index, _MEDIA_EXTS)
        if not src_file:
            return None
        try:
            dst, _ = _map_asset_to_output_path(
                src_file, input_root, vault_root, output_root, external_readme_root=external_readme_root,
            )
        except ValueError:
            return None
        href_rel = os.path.relpath(dst, start=out_dir).replace(os.sep, "/")
        kind = "video" if src_file.suffix.lower() in _VIDEO_EXTS else "image"
        return (href_rel, kind)

    # markdown images: ![alt](path) -> rewrite path or replace with <video> for video files
    def _md_repl(m: re.Match[str]) -> str:
        before, ws, dest_raw, tail, close = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        dest = dest_raw.strip()
        wrapped = False
        if (dest.startswith("<") and dest.endswith(">")) or (dest.startswith('"') and dest.endswith('"')) or (dest.startswith("'") and dest.endswith("'")):
            dest = dest[1:-1]
            wrapped = True
        result = _rewrite_path(dest)
        if not result:
            return m.group(0)
        new, kind = result
        if kind == "video":
            return f'<div class="video-embed mb-3"><video src="{html.escape(new)}" controls class="w-100">Your browser does not support the video tag.</video></div>'
        new_dest = f"<{new}>" if wrapped or any(ch.isspace() for ch in new) else new
        return f"{before}{ws}{new_dest}{tail}{close}"

    md_pattern = re.compile(r"(!\[[^\]]*\]\()(\s*)(<[^>]+>|\"[^\"]+\"|'[^']+'|[^)\s]+)([^)]*)(\))")
    md_text = md_pattern.sub(_md_repl, md_text)

    # html <img src="...">: rewrite path, or replace whole tag with <video> for video files
    def _img_repl(m: re.Match[str]) -> str:
        before_attr, ref, after_attr = m.group(1), m.group(2), m.group(3)
        result = _rewrite_path(ref)
        if not result:
            return m.group(0)
        new, kind = result
        if kind == "video":
            return f'<div class="video-embed mb-3"><video src="{html.escape(new)}" controls class="w-100">Your browser does not support the video tag.</video></div>'
        return f"<img{before_attr}src=\"{html.escape(new)}\"{after_attr}>"
    html_img_pattern = re.compile(r"<img([^>]*\s)src=[\"']([^\"']+)[\"']([^>]*)>", flags=re.IGNORECASE)
    md_text = html_img_pattern.sub(_img_repl, md_text)

    # html <video src="...">: just rewrite the path
    def _video_repl(m: re.Match[str]) -> str:
        before, ref, quote = m.group(1), m.group(2), m.group(3)
        result = _rewrite_path(ref)
        return f"{before}{html.escape(result[0])}{quote}" if result else m.group(0)
    html_video_pattern = re.compile(r"(<video[^>]+src=[\"'])([^\"']+)([\"'])", flags=re.IGNORECASE)
    md_text = html_video_pattern.sub(_video_repl, md_text)

    return md_text


# -- helpers: HTML generation --

def absolutize_img_srcs(html_fragment: str, base_dir: Path) -> str:
    """Turn relative <img src> and <video src> URLs into file:// URIs using base_dir.

    Leaves absolute (http/https/file/data) unchanged.
    """
    def _repl(m: re.Match[str]) -> str:
        before, ref, quote = m.group(1), m.group(2), m.group(3)
        if re.match(r"^(?:[a-z]+:)?//", ref) or ref.startswith("data:") or ref.startswith("file:"):
            return m.group(0)
        abs_path = (base_dir / ref).resolve()
        try:
            uri = abs_path.as_uri()
        except Exception:
            return m.group(0)
        return f"{before}{html.escape(uri)}{quote}"

    html_fragment = re.compile(r"(<img[^>]+src=[\"'])([^\"']+)([\"'])", flags=re.IGNORECASE).sub(_repl, html_fragment)
    html_fragment = re.compile(r"(<video[^>]+src=[\"'])([^\"']+)([\"'])", flags=re.IGNORECASE).sub(_repl, html_fragment)
    return html_fragment


def embed_video_links(md_text: str) -> str:
    """Replace YouTube and Vimeo URLs with embedded iframe players."""
    
    def _youtube_embed(match: re.Match[str]) -> str:
        """Extract video ID from YouTube URL and return embed iframe."""
        url = match.group(0)
        video_id = None
        
        # Extract video ID from various YouTube URL formats
        if "v=" in url:
            video_id = re.search(r"v=([^&\s]+)", url)
            if video_id:
                video_id = video_id.group(1)
        elif "youtu.be/" in url:
            video_id = re.search(r"youtu\.be/([^?\s]+)", url)
            if video_id:
                video_id = video_id.group(1)
        
        if video_id:
            return f'<div class="video-embed mb-3"><iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
        return url
    
    def _vimeo_embed(match: re.Match[str]) -> str:
        """Extract video ID from Vimeo URL and return embed iframe."""
        url = match.group(0)
        video_id = re.search(r"vimeo\.com/(\d+)", url)
        
        if video_id:
            video_id = video_id.group(1)
            return f'<div class="video-embed mb-3"><iframe src="https://player.vimeo.com/video/{video_id}" width="560" height="315" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>'
        return url
    
    # Replace YouTube links (various formats)
    youtube_pattern = re.compile(r"https?://(?:www\.)?(?:youtube\.com/watch\?[^\s]+|youtu\.be/[^\s]+)")
    md_text = youtube_pattern.sub(_youtube_embed, md_text)
    
    # Replace Vimeo links
    vimeo_pattern = re.compile(r"https?://(?:www\.)?vimeo\.com/\d+")
    md_text = vimeo_pattern.sub(_vimeo_embed, md_text)
    
    return md_text


def render_compilation_pdf_html(title: str, sections: List[Tuple[str, str]], show_chapter_label: bool = True, highlight_first_section: bool = True) -> str:
    """Render a combined HTML for chapter/global PDF with ToC and page breaks between sections.

    show_chapter_label controls whether the title page prints the word "Chapter" above the title.
    """
    safe_title = html.escape(title)
    # Build ToC and sections with anchors
    toc_items: List[str] = []
    body_items: List[str] = []
    for idx, (sec_title, sec_html) in enumerate(sections, start=1):
        anchor = f"s{idx}"
        toc_items.append(f'<li><a href="#{anchor}">{html.escape(sec_title)}</a></li>')
        section_classes = "section"
        if highlight_first_section and idx == 1:
            section_classes += " section-first"
        body_items.append(
            f'<section id="{anchor}" class="{section_classes}">'
            f'<div class="page-title">{html.escape(sec_title)}</div>'
            f'{sec_html}'
            f'</section>'
        )
        if idx < len(sections):
            body_items.append('<div class="page-break"></div>')

    toc_html = '<ul class="list-unstyled">' + "".join(toc_items) + '</ul>' if len(sections) >= 2 else ''

    chapter_label_html = '<div class="chapter-number">Chapter</div>' if show_chapter_label else ''
    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\"> 
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> 
    <title>{safe_title}</title>
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css\" rel=\"stylesheet\"> 
    <style>
      @page {{ size: A4; margin: 22mm 18mm; }}
      body {{ font-family: Georgia, Cambria, \"Times New Roman\", Times, serif; font-size: 11pt; line-height: 1.65; color:#222; }}
      /* Page titles (match per-page PDF sizing) */
      /* Move title down ~1cm without moving body: +10mm above, -10mm below (clamped at 0). */
      .page-title {{ font-family: system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,'Noto Sans',sans-serif; font-size: 2.05rem; font-weight: 700; line-height: 1.3; margin: 10mm 0 max(0mm, calc(2.25rem - 10mm)) 0; }}
      h1, h2, h3, h4, h5, h6 {{
        page-break-after: avoid;
        page-break-inside: avoid;
        line-height: 1.2;
        font-weight: 600;
      }}
      /* Match per-page PDF heading sizes */
      h1 {{ font-size: 1.65rem; font-weight: 600; margin-top: 1.9rem; margin-bottom: 1rem; }}
      h2 {{ font-size: 1.4rem; font-weight: 600; margin-top: 1.6rem; margin-bottom: .95rem; }}
      h3 {{ font-size: 1.2rem; font-weight: 600; margin-top: 1.4rem; margin-bottom: .85rem; }}
      h4 {{ font-size: 1.05rem; font-weight: 600; margin-top: 1.2rem; margin-bottom: .75rem; }}
      h5 {{ font-size: .95rem; font-weight: 600; margin-top: 1.05rem; margin-bottom: .65rem; }}
      h6 {{ font-size: .9rem; font-weight: 600; margin-top: .95rem; margin-bottom: .55rem; }}
      /* Hide anchor links in headings */
      h1 a[href^="#"], h2 a[href^="#"], h3 a[href^="#"], h4 a[href^="#"], h5 a[href^="#"], h6 a[href^="#"] {{
        display: none;
      }}
      /* Keep headings with following content together */
      h1 + *, h2 + *, h3 + *, h4 + *, h5 + *, h6 + * {{ page-break-before: avoid; }}
      p {{ widows: 2; orphans: 2; margin: 0 0 0.8em 0; }}
      img {{ max-width: 100%; height: auto; page-break-inside: avoid; }}
      pre {{
        background:#f7f7f7;
        border:1px solid #e5e5e5;
        border-radius:6px;
        padding:.6rem .8rem;
        page-break-inside: avoid;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        word-break: break-word;
      }}
      blockquote {{ border-left:3px solid #e5e5e5; background:#fafafa; padding:.5rem .8rem; margin:1rem 0; color:#495057; page-break-inside: avoid; }}
      /* Compact tables for PDF (avoid overflow off the page) */
      table {{ width:100%; border-collapse: collapse; table-layout: fixed; page-break-inside: avoid; font-size: 8.8pt; }}
      th, td {{ border:1px solid #e5e5e5; padding:.2rem .35rem; font-size: 8.4pt; vertical-align: top; word-break: break-word; }}
      .title {{ font-size:1.3rem; font-weight:600; margin-bottom:.2rem; }}
      .toc h2 {{ font-size:.95rem; text-transform: uppercase; letter-spacing:.06em; color:#6c757d; margin:0 0 .4rem 0; }}
      .toc ul {{ padding-left:1rem; margin:0; }}
      .page-break {{ page-break-before: always; }}
      .tr-float {{ position: fixed; right: 10mm; top: 10mm; }}
      .container {{ max-width: 720px; }}
      .section-first {{ background: linear-gradient(to bottom, #f8feff 0%, #ffffff 300px); border-left: 4px solid #79bb93; padding: 1.5rem 1.75rem; border-radius: 6px; }}
      .section-first h2 {{ border-bottom: 3px solid #79bb93; padding-bottom: .75rem; margin-bottom: 1rem; }}
      .section-first p:first-of-type {{ font-size: 1.1rem; line-height: 1.7; color: #445; margin-bottom: 1.6rem; background: rgba(121,187,147,0.08); padding: 0.85rem 1.1rem; border-left: 3px solid #79bb93; border-radius: 4px; }}
      /* Alternative heading styles */
      h1.rounded, h1.rounded-left, h1.banner {{ font-size: inherit; }}
      h2.rounded, h2.rounded-left, h2.banner {{ font-size: inherit; }}
      h3.rounded, h3.rounded-left, h3.banner {{ font-size: inherit; }}
      h1.rounded, h2.rounded, h3.rounded {{ background: rgba(121,187,147,0.08); border-left: 4px solid #79bb93; padding: 0.75rem 1rem 0.75rem 1.5rem; border-radius: 6px; }}
      h1.rounded-left, h2.rounded-left, h3.rounded-left {{ border-left: 4px solid #79bb93; padding-left: 1.5rem; background: rgba(121,187,147,0.12); }}
      h1.banner, h2.banner, h3.banner {{ background: #79bb93; color: white; padding: 0.75rem 1rem 0.75rem 1.5rem; border-radius: 6px; }}
      /* Heading colour variants (Bootstrap-ish palette). Usage: add class ".rounded-info" etc to the heading */
      h1.rounded-info, h2.rounded-info, h3.rounded-info {{ background: rgba(13,202,240,0.10); border-left: 4px solid #0dcaf0; }}
      h1.rounded-warning, h2.rounded-warning, h3.rounded-warning {{ background: rgba(255,193,7,0.14); border-left: 4px solid #ffc107; }}
      h1.rounded-danger, h2.rounded-danger, h3.rounded-danger {{ background: rgba(220,53,69,0.10); border-left: 4px solid #dc3545; }}
      h1.rounded-tip, h2.rounded-tip, h3.rounded-tip {{ background: rgba(25,135,84,0.10); border-left: 4px solid #198754; }}
      h1.rounded-left-info, h2.rounded-left-info, h3.rounded-left-info {{ border-left: 4px solid #0dcaf0; background: rgba(13,202,240,0.12); }}
      h1.rounded-left-warning, h2.rounded-left-warning, h3.rounded-left-warning {{ border-left: 4px solid #ffc107; background: rgba(255,193,7,0.16); }}
      h1.rounded-left-danger, h2.rounded-left-danger, h3.rounded-left-danger {{ border-left: 4px solid #dc3545; background: rgba(220,53,69,0.12); }}
      h1.rounded-left-tip, h2.rounded-left-tip, h3.rounded-left-tip {{ border-left: 4px solid #198754; background: rgba(25,135,84,0.12); }}
      h1.banner-info, h2.banner-info, h3.banner-info {{ background: #0dcaf0; color: #083944; }}
      h1.banner-warning, h2.banner-warning, h3.banner-warning {{ background: #ffc107; color: #3b2c00; }}
      h1.banner-danger, h2.banner-danger, h3.banner-danger {{ background: #dc3545; color: #fff; }}
      h1.banner-tip, h2.banner-tip, h3.banner-tip {{ background: #198754; color: #fff; }}
      /* Paper styling (YAML tag: paper) — slightly more academic, not fusty */
      .paper {{ font-size: 11.5pt; line-height: 1.7; }}
      .paper h1 {{ font-size: 1.55rem; }}
      .paper a {{ text-decoration: underline; text-underline-offset: 2px; }}
      .paper .callout, .paper .callout-note {{
        border-left: none;
        border: 1px solid #90c3c6;
        background: rgba(144,195,198,0.08);
      }}
      /* Make "banner-info" look like an academic section header (not a loud full banner) */
      .paper h1.banner-info, .paper h2.banner-info, .paper h3.banner-info {{
        background: transparent;
        color: #2c3e50;
        border-left: 4px solid #90c3c6;
        padding: 0.55rem 0.9rem 0.55rem 1.7rem;
        border-radius: 4px;
      }}
      .paper h1.rounded-info, .paper h2.rounded-info, .paper h3.rounded-info {{
        background: rgba(144,195,198,0.10);
        border-left-color: #90c3c6;
        padding: 0.35rem 0.9rem 0.35rem 1.7rem;
        border-radius: 4px;
      }}
      /* Callout styles */
      .callout {{ border-left: 4px solid #6c757d; background: #f8f9fa; padding: 1rem 1.25rem; margin: 1.5rem 0; border-radius: 4px; page-break-inside: avoid; }}
      .callout p:last-child, .callout ul:last-child, .callout ol:last-child {{ margin-bottom: 0; }}
      .callout ul, .callout ol {{ margin-top: 0.5rem; margin-bottom: 0.5rem; }}
      .callout-info {{ border-left-color: #0dcaf0; background: #e7f5f8; }}
      .callout-warning {{ border-left-color: #ffc107; background: #fff8e1; }}
      .callout-tip {{ border-left-color: #198754; background: #e8f5e9; }}
      .callout-note {{ border-left-color: #6c757d; background: #f8f9fa; }}
      /* Callout layout/style modifiers (can be combined) */
      .callout-narrow {{ max-width: 66%; }}
      .callout-right {{ margin-left: auto; }}
      .callout-center {{ margin-left: auto; margin-right: auto; }}
      .callout-heavy {{ border-left-width: 6px !important; border-radius: 0; }}
      .callout-left-border {{ border-top: none; border-right: none; border-bottom: none; }}
      .callout-rounded {{ border-left: none; border: 2px solid #e5e5e5; border-radius: 6px; }}
      .callout-inverted {{ background: #79bb93 !important; color: #ffffff; }}
      .callout-info.callout-inverted {{ border-left-color: #0dcaf0 !important; }}
      .callout-warning.callout-inverted {{ border-left-color: #ffc107 !important; }}
      .callout-tip.callout-inverted {{ border-left-color: #198754 !important; }}
      .callout-note.callout-inverted {{ border-left-color: #6c757d !important; }}
      /* Highlight style */
      mark {{ background: #d4edda; padding: 0.1em 0.2em; border-radius: 2px; }}
      /* References section (generated by citations) */
      .references {{ margin-top: 2.6rem; padding-top: 1.6rem; border-top: 1px solid #e5e5e5; }}
      .references h2 {{ font-size: 1.15rem; font-weight: 600; margin-bottom: .85rem; }}
      /* Column styles for PDF (wider gutter than before: +50%) */
      .row {{
        display: flex;
        flex-wrap: wrap;
        page-break-inside: avoid;
        margin-left: -1.125rem;
        margin-right: -1.125rem;
      }}
      .row [class*="col-"] {{
        page-break-inside: avoid;
        padding-left: 1.125rem;
        padding-right: 1.125rem;
        flex: 0 0 auto;
      }}
      .row .col-md-1 {{ width: 8.33333333%; }}
      .row .col-md-2 {{ width: 16.66666667%; }}
      .row .col-md-3 {{ width: 25%; }}
      .row .col-md-4 {{ width: 33.33333333%; }}
      .row .col-md-5 {{ width: 41.66666667%; }}
      .row .col-md-6 {{ width: 50%; }}
      .row .col-md-7 {{ width: 58.33333333%; }}
      .row .col-md-8 {{ width: 66.66666667%; }}
      .row .col-md-9 {{ width: 75%; }}
      .row .col-md-10 {{ width: 83.33333333%; }}
      .row .col-md-11 {{ width: 91.66666667%; }}
      .row .col-md-12 {{ width: 100%; }}
      /* Chapter title page */
      .chapter-title-page {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        text-align: center;
        page-break-after: always;
        padding: 2rem;
      }}
      .chapter-title-page .chapter-number {{
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #6c757d;
        margin-bottom: 1.5rem;
        font-weight: 500;
      }}
      .chapter-title-page .chapter-title-text {{
        font-size: 3rem;
        font-weight: 300;
        line-height: 1.2;
        color: #2c3e50;
        margin-bottom: 1rem;
        max-width: 80%;
      }}
    </style>
  </head>
  <body>
    <div class="chapter-title-page">
      {chapter_label_html}
      <div class="chapter-title-text">{safe_title}</div>
    </div>
    <div class=\"container\">
      {('<section class="toc"><h2>Contents</h2>' + toc_html + '</section><div class="page-break"></div>') if toc_html else ''}
      {"".join(body_items)}
    </div>
  </body>
</html>
"""

def strip_numeric_prefix(stem: str) -> str:
    """Strip page-anchor suffix ((id)) and leading numeric ordering from a filename stem.
    Also converts standalone 'qq' tokens to '?' (for convenient title punctuation).

    Examples:
    '010 Title ((my-id))' -> 'Title'
    '3_ Something' -> 'Something'
    '01a Why causal mapping' -> 'Why causal mapping'
    'foo bar qq' -> 'foo bar?'
    """
    # Remove trailing page anchor like ((my-id))
    no_anchor = re.sub(r"\s*\(\([^)]+\)\)\s*$", "", stem).strip()
    # Remove leading numeric prefixes (digits, optional letters e.g. 01a, then separator)
    cleaned = re.sub(r"^\s*\d[\d._-]*[a-zA-Z]*\s*[-_. ]?\s*", "", no_anchor).strip()
    cleaned = convert_qq_to_question_mark(cleaned)
    return cleaned or no_anchor or stem


def convert_qq_to_question_mark(text: str) -> str:
    """Convert standalone 'qq' tokens into '?' (supports optional trailing markdown attr block).
    
    Examples:
    - 'foo qq bar' -> 'foo ? bar'
    - 'foo qq {#id}' -> 'foo ? {#id}'
    - 'Whyqq' -> 'Why?'
    """
    s = (text or "").strip()
    if not s:
        return text
    # If there's a trailing { ... } attribute block, keep it but apply qq conversion before it.
    m_attr = re.search(r"\s*(\{[^}]*\})\s*$", s)
    if m_attr:
        suffix = m_attr.group(1)
        base = s[:m_attr.start(1)].rstrip()
        # Replace qq at the end of a word: supports both "qq" and "...Whyqq"
        base = re.sub(r"(?i)qq\b", "?", base)
        return (base + " " + suffix).strip()
    return re.sub(r"(?i)qq\b", "?", s)


def extract_page_anchor_from_stem(stem: str) -> Optional[str]:
    """Return trailing page anchor id from a stem in the form '... ((id))', lowercased."""
    m = re.search(r"\(\(([^)]+)\)\)\s*$", stem)
    if not m:
        return None
    return m.group(1).strip().lower()


def _short_route_stub_html(
    *,
    target_html: Path,
    output_root: Path,
    site_url: str,
    ident: str,
    stub_url_abs: str,
) -> str:
    """Full copy of the target page at /{ident}/ so the URL bar tracks real navigation (no iframe).

    Injected <base href> is the real output folder so relative href/src resolve like the original.
    Fragment-only links href=\"#...\" are rewritten to /{ident}/#... so <base> does not jump to the long URL.
    """
    import bs4  # type: ignore

    raw = target_html.read_text(encoding="utf-8")
    soup = bs4.BeautifulSoup(raw, "html.parser")
    try:
        parent_rel = target_html.parent.relative_to(output_root)
    except ValueError:
        parent_rel = Path(".")
    parts = parent_rel.parts
    if not parts:
        base_dir_url = f"{site_url.rstrip('/')}/"
    else:
        enc = "/".join(quote(str(seg), safe="") for seg in parts)
        base_dir_url = f"{site_url.rstrip('/')}/{enc}/"
    for b in soup.find_all("base"):
        b.decompose()
    head = soup.head
    if head is not None:
        head.insert(0, soup.new_tag("base", href=base_dir_url))
    stub_prefix = f"/{ident}/"
    for el in soup.find_all(["a", "area"], href=True):
        h = el.get("href", "")
        if not isinstance(h, str) or not h.startswith("#"):
            continue
        el["href"] = stub_prefix + h
    for link in soup.find_all("link"):
        rel = link.get("rel")
        if rel is None:
            continue
        rel_list = rel if isinstance(rel, (list, tuple)) else [rel]
        if any(str(r).lower() == "canonical" for r in rel_list):
            link["href"] = stub_url_abs
    for meta in soup.find_all("meta", attrs={"property": "og:url"}):
        meta["content"] = stub_url_abs

    html_el = soup.find("html")
    if html_el is None:
        raise ValueError(f"stub target has no <html>: {target_html}")
    m_dt = re.match(r"[\s\uFEFF]*<!DOCTYPE[^>]*>", raw, flags=re.IGNORECASE)
    prefix = (m_dt.group(0).rstrip() + "\n") if m_dt else "<!DOCTYPE html>\n"
    return prefix + str(html_el)


def strip_yaml_front_matter(text: str) -> str:
    """Remove leading YAML front matter delimited by lines of '---'. Handles BOM and CRLF.

    Examples:
    ---\nkey: val\n---\ncontent -> content
    """
    # Strip BOM if present
    if text.startswith("\ufeff"):
        text = text[1:]
    # Regex: start of string, line with ---, any content, line with ---, optional trailing newline
    pattern = r'^\s*---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n?'
    return re.sub(pattern, '', text, count=1, flags=re.MULTILINE)


def strip_percent_comments(text: str) -> str:
    """Remove custom %% ... %% comment blocks from text (can span multiple lines)."""
    return re.sub(r"%%[\s\S]*?%%", "", text)


def extract_yaml_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    """Extract and parse YAML front matter, return (metadata_dict, content_without_frontmatter).
    
    Returns ({}, original_text) if no valid front matter found.
    """
    # Strip BOM if present
    if text.startswith("\ufeff"):
        text = text[1:]
    
    pattern = r'^\s*---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?'
    m = re.match(pattern, text, flags=re.MULTILINE)
    if not m:
        return {}, text
    
    yaml_text = m.group(1)
    content = text[m.end():]
    
    try:
        import yaml  # type: ignore
        metadata = yaml.safe_load(yaml_text) or {}
        if not isinstance(metadata, dict):
            return {}, text
        return metadata, content
    except Exception:
        return {}, text


def _upsert_frontmatter_date_text(md_text: str, date_iso: str) -> str:
    """Insert or update YAML front matter 'date:' while preserving other front matter lines."""
    # Preserve BOM if present
    bom = "\ufeff" if md_text.startswith("\ufeff") else ""
    text = md_text[1:] if bom else md_text

    newline = "\r\n" if "\r\n" in text else "\n"
    pattern = r'^\s*---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?'
    m = re.match(pattern, text, flags=re.MULTILINE)

    # No front matter: add minimal one
    if not m:
        fm = f"---{newline}date: {date_iso}{newline}---{newline}{newline}"
        return bom + fm + text

    fm_body = m.group(1)
    rest = text[m.end():]

    lines = fm_body.splitlines()
    date_re = re.compile(r"^(\s*)date\s*:\s*.*$", flags=re.IGNORECASE)
    replaced = False
    for i, line in enumerate(lines):
        m_date = date_re.match(line)
        if m_date:
            indent = m_date.group(1) or ""
            lines[i] = f"{indent}date: {date_iso}"
            replaced = True
            break

    if not replaced:
        # Append at end of front matter for minimal diff
        if lines and lines[-1].strip() != "":
            lines.append(f"date: {date_iso}")
        else:
            # If front matter is empty or ends with blanks, insert before trailing blanks
            insert_at = len(lines)
            while insert_at > 0 and lines[insert_at - 1].strip() == "":
                insert_at -= 1
            lines.insert(insert_at, f"date: {date_iso}")

    new_fm_body = newline.join(lines)
    new_text = f"---{newline}{new_fm_body}{newline}---{newline}"
    return bom + new_text + rest


def sync_created_dates_in_content(input_root: Path) -> None:
    """Walk input_root and set YAML front matter 'date' to filesystem created date (Windows st_ctime)."""
    updated = 0
    skipped = 0

    for md_path in sorted(input_root.rglob("*.md")):
        # Skip Zotero template files (they contain Jinja-like placeholders in front matter)
        if "zotero_templates" in {p.lower() for p in md_path.parts}:
            skipped += 1
            continue

        try:
            created_iso = datetime.fromtimestamp(md_path.stat().st_ctime).date().isoformat()
            original = md_path.read_text(encoding="utf-8")
            new_text = _upsert_frontmatter_date_text(original, created_iso)
            if new_text != original:
                md_path.write_text(new_text, encoding="utf-8")
                updated += 1
        except Exception:
            skipped += 1

    print(f"[SYNC DATES] Updated: {updated} | Skipped: {skipped} | Root: {input_root}")


def extract_first_heading(md_text: str) -> Optional[str]:
    """Extract first H1 or H2 from markdown text, return None if not found."""
    lines = md_text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## "):
            return line[3:].strip()
    return None


def strip_html_comments(text: str) -> str:
    """Remove all HTML comments from text (including multiline comments)."""
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)


def normalize_heading_anchors(md_text: str) -> Tuple[str, Set[str]]:
    """Normalize trailing heading anchors to canonical {#id} and collect ids.

    Accepts both {id} and {#id} forms at end of ATX heading lines and rewrites
    to a single space + {#id}. Returns (normalized_text, set_of_ids).
    """
    lines = md_text.splitlines()
    ids: Set[str] = set()
    out_lines: List[str] = []
    heading_re = re.compile(r"^\s{0,3}#{1,6}\s+.*")
    anchor_end_re = re.compile(r"\{#?([A-Za-z][A-Za-z0-9_-]*)\}\s*$")

    for line in lines:
        if heading_re.match(line):
            m = anchor_end_re.search(line)
            if m:
                ident = m.group(1).lower()
                # replace with canonical form
                line = anchor_end_re.sub(f" {{#{ident}}}", line.rstrip())
                ids.add(ident)
        out_lines.append(line)

    return "\n".join(out_lines), ids

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


def parse_external_readme_sections(readme_path: Optional[str] = None) -> Dict[str, str]:
    """Parse external README.md file and extract sections with {#anchor} IDs.
    
    If readme_path is not provided, tries to read from config.yml, otherwise uses default.
    
    Returns a dict mapping anchor IDs (without #) to section content (markdown text).
    Sections are delimited by headings. A section includes content from one heading to the next.
    """
    sections: Dict[str, str] = {}
    try:
        resolved_readme = resolve_external_readme_path(readme_path)
        if resolved_readme is None or not resolved_readme.exists():
            return sections

        content = resolved_readme.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        current_anchor: Optional[str] = None
        current_lines: List[str] = []
        
        for line in lines:
            # Check if this is a heading with {#anchor}
            heading_match = re.match(r'^(#{1,6})\s+(.+?)\s*\{#([^}]+)\}\s*$', line)
            if heading_match:
                # Save previous section if any
                if current_anchor and current_lines:
                    sections[current_anchor] = "\n".join(current_lines).strip()
                
                # Start new section
                level, title, anchor = heading_match.groups()
                current_anchor = anchor.strip()
                current_lines = [f"{level} {title.strip()}"]  # Keep heading without {#anchor}
            elif current_anchor is not None:
                # We're in a section, accumulate lines
                # Stop if we hit another heading (without {#anchor})
                if re.match(r'^#{1,6}\s+', line) and '{#' not in line:
                    # Save current section and reset
                    if current_lines:
                        sections[current_anchor] = "\n".join(current_lines).strip()
                    current_anchor = None
                    current_lines = []
                else:
                    current_lines.append(line)
        
        # Save last section
        if current_anchor and current_lines:
            sections[current_anchor] = "\n".join(current_lines).strip()
        
    except Exception as e:
        _warn("external_readme", f"Could not parse external README: {e}")
    
    return sections


def generate_chapter_toc_html(
    target_md: Path,
    input_root: Path,
    output_root: Path,
    md_files: List[Path],
    title_map: Dict[Path, str],
    current_out_dir: Path,
    page_anchor_map: Optional[Dict[Path, Optional[str]]] = None,
) -> str:
    """Generate the 'Pages in this Chapter' TOC HTML for a given file if it's the first in its folder.
    
    Used by the !toc[[filename]] transclusion syntax to embed a chapter TOC listing.
    Returns HTML listing all pages in the folder with their first-paragraph summaries.
    Returns empty string if target_md is not the first file in a folder or has no other pages.
    """
    try:
        rel_parts = target_md.relative_to(input_root).parts
        if len(rel_parts) < 2:
            return ""  # Not in a subfolder
        
        top = rel_parts[0]
        pages_in_folder = [p for p in md_files if p.relative_to(input_root).parts[0] == top]
        # Exclude draft files (with ! in filename) when determining first page
        pages_in_folder_no_drafts = [p for p in pages_in_folder if '!' not in p.name]
        pages_in_folder_no_drafts.sort(key=lambda p: (0 if p.name.lower() == "index.md" else 1, str(p).lower()))
        
        # Check if target_md is the first non-draft file in the folder
        if not pages_in_folder_no_drafts or target_md.resolve() != pages_in_folder_no_drafts[0].resolve():
            return ""  # Not the first file
        
        if len(pages_in_folder_no_drafts) <= 1:
            return ""  # No other pages to list
        
        blocks: List[str] = []
        # Exclude draft files (with ! in filename) from chapter ToC
        for p in pages_in_folder_no_drafts:
            if p.resolve() == target_md.resolve():
                continue  # omit the intro page itself
            page_slug = page_anchor_map.get(p) if page_anchor_map else None
            if page_slug:
                href = f"/{page_slug}/"
            else:
                href = os.path.relpath(relative_output_html(input_root, output_root, p), start=current_out_dir).replace(os.sep, "/")
            title_p = title_map.get(p, strip_numeric_prefix(p.stem)) or strip_numeric_prefix(p.stem)
            title_p = title_p.replace("--", "–")
            try:
                srcp = p.read_text(encoding="utf-8")
            except Exception:
                srcp = ""
            snippet = _first_non_heading_paragraph_html(srcp) or ""
            blocks.append(
                f"<div class=\"mb-3 pb-2 border-bottom\">"
                f"<a class=\"fw-semibold link-dark text-decoration-none\" href=\"{html.escape(href)}\">{html.escape(title_p)}</a>"
                + (f"<div class=\"small text-muted mt-1 ps-2 border-start\" style=\"border-color:#e5e5e5!important\">{snippet}</div>" if snippet else "")
                + "</div>"
            )
        
        if blocks:
            return (
                '<div class="mt-4 pt-3">'
                + "".join(blocks) +
                '</div>'
            )
        return ""
    except Exception:
        return ""


def replace_wikilinks_with_embeds(
    md_text: str,
    current_md_path: Path,
    input_root: Path,
    output_root: Path,
    title_map: Dict[Path, str],
    embed_html_map: Union[Dict[Path, str], Any],  # Can be Dict or LazyEmbedCache
    wikilink_index: Dict[str, Path],
    md_files: Optional[List[Path]] = None,
    page_anchor_map: Optional[Dict[Path, Optional[str]]] = None,
    missing_wikilinks: Optional[Dict[str, Set[str]]] = None,
) -> str:
    """Replace wikilinks with either inline links or collapsible embeds.

    Wikilink syntax:
    - [[link]]: creates a simple inline link to the target page
    - ![[link]]: embeds the full target page content in a collapsible block
    - !toc[[link]]: embeds the chapter TOC from the target page (if it's the first file in a folder)
                    Shows "Pages in this Chapter" listing with summaries, in a collapsible block
    
    External README fallback:
    If a target (including anchors like [[foo#bar]] or ![[foo#bar]]) is not found in the wikilink_index, 
    this function searches C:\\dev\\causal-map-extension\\webapp\\README.md for sections with matching 
    {#anchor} IDs. If found, the section content is embedded as a collapsible block.
    
    For [[link#anchor]] or ![[link#anchor]], the anchor (if present) is checked first, then the link target.
    """
    current_out_dir = relative_output_html(input_root, output_root, current_md_path).parent
    rel_page: Optional[str] = None
    if missing_wikilinks is not None:
        try:
            rel_page = str(current_md_path.relative_to(input_root))
        except Exception:
            rel_page = str(current_md_path)
    
    # Parse external README sections for fallback lookup
    external_sections = parse_external_readme_sections()

    def _slug_anchor(s: str) -> str:
        a = s.lower()
        a = re.sub(r"\s+", "-", a)
        a = re.sub(r"[^a-z0-9-]", "", a)
        return a

    # Pass 0: handle TOC embeds first (!toc[[...]])
    pat_toc = re.compile(r"!toc\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

    def _repl_toc(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        anchor = (match.group(2).strip() if match.group(2) else None)
        alias = (match.group(3).strip() if match.group(3) else None)

        if target.startswith("#"):
            return match.group(0)

        key = target.lower()
        target_md = wikilink_index.get(key) or wikilink_index.get(strip_numeric_prefix(target).lower())
        
        if not target_md:
            if missing_wikilinks is not None and rel_page is not None and not target.startswith("#"):
                missing_wikilinks[rel_page].add(f"!toc[[{target}]]")
            return match.group(0)

        title = html.escape(title_map.get(target_md, strip_numeric_prefix(target_md.stem)))
        
        # Check if target has a page-level anchor ((shortcut)) and use short route if so
        page_anchor_id = None
        if page_anchor_map:
            page_anchor_id = page_anchor_map.get(target_md)
        
        if page_anchor_id and not anchor:
            # Use short route like /shortcut for pages with page-level anchors
            href_base = f"/{page_anchor_id}"
        else:
            # Use relative path
            target_out = relative_output_html(input_root, output_root, target_md)
            href_base = os.path.relpath(target_out, start=current_out_dir).replace(os.sep, "/")
            if anchor:
                a = _slug_anchor(anchor)
                if a:
                    href_base = f"{href_base}#{a}"
        
        href = html.escape(href_base)

        # Generate chapter TOC
        if md_files is not None:
            inner_html = generate_chapter_toc_html(
                target_md, input_root, output_root, md_files, title_map, current_out_dir, page_anchor_map
            )
            if not inner_html:
                # If no TOC generated (not first file or no other pages), fall back to regular embed
                inner_html = embed_html_map.get(target_md, "")
        else:
            inner_html = embed_html_map.get(target_md, "")

        # Rewrite nested [[links]] inside embedded HTML to ordinary links
        nested_link_pat = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

        def _rewrite_nested(m: re.Match[str]) -> str:
            tgt = m.group(1).strip()
            anch = (m.group(2).strip() if m.group(2) else None)
            md = wikilink_index.get(tgt.lower()) or wikilink_index.get(strip_numeric_prefix(tgt).lower())
            if not md:
                return m.group(0)
            
            # Check if target has a page-level anchor ((shortcut)) and use short route if so
            nested_page_anchor_id = None
            if page_anchor_map:
                nested_page_anchor_id = page_anchor_map.get(md)
            
            if nested_page_anchor_id and not anch:
                # Use short route like /shortcut for pages with page-level anchors
                nested_base = f"/{nested_page_anchor_id}"
            else:
                # Use relative path from current output directory
                out = relative_output_html(input_root, output_root, md)
                nested_base = os.path.relpath(out, start=current_out_dir).replace(os.sep, "/")
                if anch:
                    a2 = _slug_anchor(anch)
                    if a2:
                        nested_base = f"{nested_base}#{a2}"
            
            nested_href = html.escape(nested_base)
            label = html.escape(title_map.get(md, strip_numeric_prefix(md.stem)))
            return f'<a href="{nested_href}" class="link-secondary">{label}</a>'

        inner_html_rewritten = nested_link_pat.sub(_rewrite_nested, inner_html)

        return (
            f"<details class=\"embed-block mb-3\">"
            f"<summary class=\"text-muted d-flex align-items-center justify-content-between\">"
            f"<span>{title}</span>"
            f"<span class=\"chev\" aria-hidden=\"true\">▸</span>"
            f"</summary>"
            f"<div class=\"mt-2\">{inner_html_rewritten}<div class=\"mt-2\"><a href=\"{href}\" class=\"link-secondary\">Open page →</a></div></div>"
            f"</details>"
        )

    md_text = pat_toc.sub(_repl_toc, md_text)

    # Pass 1: handle regular embeds (![[...]])
    pat_embed = re.compile(r"!\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

    def _repl_embed(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        anchor = (match.group(2).strip() if match.group(2) else None)
        alias = (match.group(3).strip() if match.group(3) else None)

        if target.startswith("#"):
            return match.group(0)

        key = target.lower()
        stripped_key = strip_numeric_prefix(target).lower()
        target_md = wikilink_index.get(key) or wikilink_index.get(stripped_key)
        
        if not target_md:
            _debug_embed(f"Target not found: '{target}' (key: '{key}', stripped: '{stripped_key}')")
            # Show possible matches
            matches = [k for k in wikilink_index.keys() if target.lower() in k or k in target.lower()]
            if matches:
                _debug_embed(f"  Possible matches in index: {matches[:5]}")
        
        # Check external README sections if not found in index
        if not target_md:
            ext_key = anchor if anchor else target
            if ext_key.lower() in external_sections:
                section_md = external_sections[ext_key.lower()]
                # Convert markdown to HTML
                section_md_processed = preprocess_inline_footnotes(ensure_blank_lines_before_lists(section_md))
                section_md_processed = preprocess_mathjax_delimiters(section_md_processed)
                md_converter = markdown.Markdown(extensions=markdown_extensions())
                inner_html = md_converter.convert(section_md_processed)
                inner_html = strip_html_comments(inner_html)
                
                # Extract title from first heading in section (keep HTML for icons)
                first_line = section_md.split('\n')[0] if section_md else ext_key
                if first_line.startswith('#'):
                    # Remove markdown heading markers but keep the rest for HTML conversion
                    title_md = re.sub(r'^#+\s*', '', first_line).strip()
                    title_converter = markdown.Markdown(extensions=markdown_extensions())
                    section_title = title_converter.convert(title_md)
                    section_title = strip_html_comments(section_title)
                    # Remove wrapping <p> tags if present
                    section_title = re.sub(r'^<p>(.*)</p>$', r'\1', section_title.strip())
                else:
                    section_title = html.escape(ext_key)
                
                external_link = f"https://app.causalmap.app/help-docs.html#{ext_key}"
                
                return (
                    f"<details class=\"embed-block mb-3\">"
                    f"<summary class=\"d-flex align-items-center justify-content-between\">"
                    f"<span><span class=\"small text-muted\">Relevant page from Causal Map help:</span><br>{section_title}</span>"
                    f"<span class=\"chev\" aria-hidden=\"true\">▸</span>"
                    f"</summary>"
                    f"<div class=\"mt-2\">{inner_html}<div class=\"mt-2\"><a href=\"{html.escape(external_link)}\" class=\"link-secondary\" target=\"_blank\">Open help page →</a></div></div>"
                    f"</details>"
                )
            if missing_wikilinks is not None and rel_page is not None:
                if not target.startswith("#"):
                    missing_wikilinks[rel_page].add(f"![[{target}]]")
            return match.group(0)

        title = html.escape(title_map.get(target_md, strip_numeric_prefix(target_md.stem)))
        
        # Check if target has a page-level anchor ((shortcut)) and use short route if so
        page_anchor_id = None
        if page_anchor_map:
            page_anchor_id = page_anchor_map.get(target_md)
        
        if page_anchor_id and not anchor:
            # Use short route like /shortcut for pages with page-level anchors
            href_base = f"/{page_anchor_id}"
        else:
            # Use relative path
            target_out = relative_output_html(input_root, output_root, target_md)
            href_base = os.path.relpath(target_out, start=current_out_dir).replace(os.sep, "/")
            if anchor:
                a = _slug_anchor(anchor)
                if a:
                    href_base = f"{href_base}#{a}"
        
        href = html.escape(href_base)

        inner_html = embed_html_map.get(target_md, "")
        _debug_embed(f"Found '{target}' -> {target_md.name}, inner_html length: {len(inner_html)}")

        # Rewrite nested [[links]] inside embedded HTML to ordinary links
        nested_link_pat = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

        def _rewrite_nested(m: re.Match[str]) -> str:
            tgt = m.group(1).strip()
            anch = (m.group(2).strip() if m.group(2) else None)
            md = wikilink_index.get(tgt.lower()) or wikilink_index.get(strip_numeric_prefix(tgt).lower())
            if not md:
                return m.group(0)
            
            # Check if target has a page-level anchor ((shortcut)) and use short route if so
            nested_page_anchor_id = None
            if page_anchor_map:
                nested_page_anchor_id = page_anchor_map.get(md)
            
            if nested_page_anchor_id and not anch:
                # Use short route like /shortcut for pages with page-level anchors
                nested_base = f"/{nested_page_anchor_id}"
            else:
                # Use relative path from current output directory
                out = relative_output_html(input_root, output_root, md)
                nested_base = os.path.relpath(out, start=current_out_dir).replace(os.sep, "/")
                if anch:
                    a2 = _slug_anchor(anch)
                    if a2:
                        nested_base = f"{nested_base}#{a2}"
            
            nested_href = html.escape(nested_base)
            label = html.escape(title_map.get(md, strip_numeric_prefix(md.stem)))
            return f'<a href="{nested_href}" class="link-secondary">{label}</a>'

        inner_html_rewritten = nested_link_pat.sub(_rewrite_nested, inner_html)

        return (
            f"<details class=\"embed-block mb-3\">"
            f"<summary class=\"text-muted d-flex align-items-center justify-content-between\">"
            f"<span>{title}</span>"
            f"<span class=\"chev\" aria-hidden=\"true\">▸</span>"
            f"</summary>"
            f"<div class=\"mt-2\">{inner_html_rewritten}<div class=\"mt-2\"><a href=\"{href}\" class=\"link-secondary\">Open page →</a></div></div>"
            f"</details>"
        )

    md_text = pat_embed.sub(_repl_embed, md_text)

    # Pass 2: handle normal wikilinks
    pat_link = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

    def _repl_link(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        anchor = (match.group(2).strip() if match.group(2) else None)
        alias = (match.group(3).strip() if match.group(3) else None)

        key = target.lower()
        target_md = wikilink_index.get(key) or wikilink_index.get(strip_numeric_prefix(target).lower())
        
        if target.startswith("#"):
            slug = _slug_anchor(target[1:])
            if not slug:
                return match.group(0)
            href_base = f"#{slug}"
            href = html.escape(href_base)
            display_text = html.escape(alias) if alias else html.escape(target.lstrip("#"))
            return f'<a href="{href}" class="wikilink">{display_text}</a>'

        # Check external README sections if not found in index
        if not target_md:
            if missing_wikilinks is not None and rel_page is not None and not target.startswith("#"):
                missing_wikilinks[rel_page].add(f"[[{target}]]")
            return ""

        title = html.escape(title_map.get(target_md, strip_numeric_prefix(target_md.stem)))
        
        # Check if target has a page-level anchor ((shortcut)) and use short route if so
        page_anchor_id = None
        if page_anchor_map:
            page_anchor_id = page_anchor_map.get(target_md)
        
        if page_anchor_id and not anchor:
            # Use short route like /shortcut for pages with page-level anchors
            href_base = f"/{page_anchor_id}"
        else:
            # Use relative path
            target_out = relative_output_html(input_root, output_root, target_md)
            href_base = os.path.relpath(target_out, start=current_out_dir).replace(os.sep, "/")
            if anchor:
                a = _slug_anchor(anchor)
                if a:
                    href_base = f"{href_base}#{a}"
        
        href = html.escape(href_base)
        display_text = html.escape(alias) if alias else title
        return f'<a href="{href}" class="wikilink">{display_text}</a>'

    md_text = pat_link.sub(_repl_link, md_text)

    return md_text


def build_sidebar_footer_html(config: Dict[str, object]) -> str:
    """Build footer inner HTML from config (sidebar_footer_links + CC badge). Used by sidebar and fullscreen footer."""
    footer_links: List[Tuple[str, str]] = []
    company_href = ""
    app_href = ""
    try:
        for item in (config.get("sidebar_footer_links") or []):
            if isinstance(item, dict):
                href = str(item.get("href", "")).strip()
                text = str(item.get("text", "")).strip()
                if href and text:
                    tnorm = text.strip().lower()
                    if tnorm in {"causal map ltd", "causalmap ltd"}:
                        company_href = href
                        continue
                    if tnorm in {"causal map app", "causalmap app"}:
                        app_href = href
                        continue
                    footer_links.append((href, text))
    except Exception:
        pass
    current_year = date.today().year
    company_href = company_href or "https://causalmap.app"
    app_href = app_href or "https://app.causalmap.app"
    cc_badge = (
        f'<span>© <a href="{html.escape(company_href)}" class="link-secondary">Causal Map Ltd</a> {current_year}</span> · '
        f'<a rel="license" href="https://creativecommons.org/licenses/by-nc/4.0/" target="_blank" title="CC BY-NC 4.0">'
        f'<img alt="CC BY-NC 4.0" style="height:18px;opacity:0.7;vertical-align:middle;" src="https://licensebuttons.net/l/by-nc/4.0/88x31.png" />'
        f'</a>'
        f'<a href="{html.escape(app_href)}" class="link-secondary ms-2" target="_blank" title="Causal Map app">App <span aria-hidden="true">↗</span></a>'
    )
    links_part = " · ".join([f'<a href="{html.escape(h)}" class="link-secondary">{html.escape(t)}</a>' for h, t in footer_links])
    inner = (links_part + " · " + cc_badge) if footer_links else cc_badge
    return f'<div class="sidebar-footer small text-muted">{inner}</div>'


def render_nav_html_shared(
    nav_root: NavDir,
    output_root: Path,
    title_map: Dict[Path, str],
    config: Dict[str, object],
    page_anchor_map: Optional[Dict[Path, Optional[str]]] = None,
) -> str:
    """Render a shared left sidebar nav.

    Links are stored as site-root-relative paths in data attributes, then turned into real hrefs
    at runtime by generated_site/assets/sidebar.js. This avoids regenerating all pages when nav changes.
    """

    def root_rel_path(target: Path) -> str:
        return os.path.relpath(target, start=output_root).replace(os.sep, "/")

    def nav_path_for_file(nf: NavFile) -> str:
        """Short route folder URL ({slug}/) when the note has ((slug)) in the filename.

        Trailing slash keeps hrefs as /anchor/ (not /anchor/index.html); sidebar.js normalizes
        paths the same way for active-link highlighting.
        """
        if page_anchor_map:
            slug = page_anchor_map.get(nf.src_md)
            if slug:
                return f"{slug}/"
        return root_rel_path(nf.out_html)

    def render_dir(node: NavDir) -> str:
        items: List[str] = []

        # subdirectories
        for name in sorted(node.subdirs.keys(), key=_nav_dirname_key):
            sub = node.subdirs[name]
            sub_label_text = strip_numeric_prefix(sub.name).replace("--", "–")
            label = html.escape(sub_label_text)
            # Stable folder id for JS to persist open/closed state across page loads.
            folder_key = html.escape(os.path.relpath(sub.path, start=nav_root.path).replace(os.sep, "/"))

            inner = render_dir(sub)
            items.append(
                (
                    f"<li>"
                    f"<details class=\"mb-1\" data-folder=\"{folder_key}\">"
                    f"<summary class=\"fw-semibold d-flex align-items-center justify-content-between\"><span>{label}</span><span class=\"chev\" aria-hidden=\"true\">▸</span></summary>"
                    f"<ul class=\"list-unstyled ms-3 my-1\">{inner}</ul>"
                    f"</details>"
                    f"</li>"
                )
            )

        # files in this dir (ordered like Obsidian), labels from title_map
        for nf in sorted(node.files, key=_nav_file_key):
            # hide root index.md from the sidebar (Home button exists)
            if nf.src_md == (nav_root.path / "index.md"):
                continue
            label_text = title_map.get(nf.src_md, strip_numeric_prefix(nf.src_md.stem)) or ""
            label_text = label_text.replace("--", "–")
            label = html.escape(label_text)
            path_from_root = html.escape(nav_path_for_file(nf))
            # href is set at runtime; keep inert here
            items.append(f'<li class="nav-item"><a class="nav-link" href="#" data-path="{path_from_root}">{label}</a></li>')

        return "".join(items)

    inner_html = render_dir(nav_root)

    home_path = html.escape(root_rel_path(output_root / "index.html"))
    search_path = html.escape(root_rel_path(output_root / "search.html"))

    # Split a leading icon (e.g. "💐") from the main title so the subtitle can align with the text, not the icon.
    raw_site_label = str(config.get("site_label", "Site"))
    site_icon = ""
    site_text = raw_site_label
    if " " in raw_site_label:
        head, tail = raw_site_label.split(" ", 1)
        # Heuristic: treat non-ascii "head" as an icon token.
        if any(ord(ch) > 127 for ch in head):
            site_icon = head
            site_text = tail

    site_icon = html.escape(site_icon)
    site_text = html.escape(site_text)
    site_sub = html.escape(str(config.get("site_subtitle", "")))

    footer_html = build_sidebar_footer_html(config)

    return (
        f"<div class=\"p-2\">"
        f"<div class=\"sidebar-header\">"
        f"<a class=\"btn site-title\" href=\"#\" data-path=\"{home_path}\">"
        f"<span class=\"site-title-icon\">{site_icon}</span>"
        f"<span class=\"site-title-text\">{site_text}</span>"
        f"<div class=\"site-title-sub\">{site_sub}</div>"
        f"</a>"
        f"<form class=\"mb-2\" data-action-path=\"{search_path}\" method=\"get\">"
        f"  <div class=\"input-group input-group-sm\">"
        f"    <input class=\"form-control\" type=\"text\" name=\"q\" placeholder=\"Search…\" />"
        f"    <button class=\"btn btn-outline-secondary\" type=\"submit\">Search</button>"
        f"  </div>"
        f"</form>"
        f"</div>"
        f"<button id=\"tocToggle\" class=\"btn btn-outline-secondary btn-sm mb-2 toc-toggle\" type=\"button\" aria-expanded=\"false\" aria-controls=\"tocList\">Show Contents</button>"
        f"<div class=\"nav-fade toc-collapsed\" id=\"tocList\"><ul class=\"list-unstyled\">{inner_html}</ul></div>"
        f"{footer_html}"
        f"</div>"
    )


def write_sidebar_js(output_root: Path, nav_html: str) -> None:
    """Write generated_site/assets/sidebar.js (shared sidebar injected into each page)."""
    assets_dir = output_root / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    out_path = assets_dir / "sidebar.js"

    nav_html_js = json.dumps(nav_html, ensure_ascii=False)
    js = (
        "/* Shared left sidebar injected into every page (generated). */\n"
        "(function(){\n"
        "  'use strict';\n"
        "  var NAV_HTML = " + nav_html_js + ";\n"
        "  var OPEN_KEY = 'sidebarOpenFolders';\n"
        "\n"
        "  function getSiteRootUrl(){\n"
        "    try {\n"
        "      var cs = document.currentScript;\n"
        "      if (!cs || !cs.src) return null;\n"
        "      var assetsDir = new URL('./', cs.src);\n"
        "      return new URL('../', assetsDir);\n"
        "    } catch(e) { return null; }\n"
        "  }\n"
        "\n"
        "  function normalizePathname(pathname){\n"
        "    if (!pathname) return pathname;\n"
        "    // Support both /foo/index.html and clean URLs like /foo (served via rewrite).\n"
        "    if (pathname === '/') return '/index.html';\n"
        "    // Trailing slash implies folder index on many static hosts.\n"
        "    if (pathname.endsWith('/')) return pathname + 'index.html';\n"
        "    var last = pathname.split('/').pop() || '';\n"
        "    if (last && last.indexOf('.') === -1) return pathname + '.html';\n"
        "    return pathname;\n"
        "  }\n"
        "\n"
        "  function loadOpenSet(){\n"
        "    try {\n"
        "      var raw = localStorage.getItem(OPEN_KEY);\n"
        "      if (!raw) return new Set();\n"
        "      var arr = JSON.parse(raw);\n"
        "      if (!Array.isArray(arr)) return new Set();\n"
        "      return new Set(arr.filter(function(x){ return typeof x === 'string' && x; }));\n"
        "    } catch(e) { return new Set(); }\n"
        "  }\n"
        "\n"
        "  function saveOpenSet(set){\n"
        "    try { localStorage.setItem(OPEN_KEY, JSON.stringify(Array.from(set))); } catch(e) {}\n"
        "  }\n"
        "\n"
        "  function mount(){\n"
        "    var sidebar = document.querySelector('aside.sidebar');\n"
        "    if (!sidebar) return;\n"
        "    sidebar.innerHTML = NAV_HTML;\n"
        "\n"
        "    var siteRoot = getSiteRootUrl();\n"
        "    if (!siteRoot) return;\n"
        "\n"
        "    // Turn data-path / data-action-path into real URLs.\n"
        "    sidebar.querySelectorAll('a[data-path]').forEach(function(a){\n"
        "      var p = a.getAttribute('data-path');\n"
        "      if (!p) return;\n"
        "      try { a.href = new URL(p, siteRoot).href; } catch(e) {}\n"
        "    });\n"
        "    sidebar.querySelectorAll('form[data-action-path]').forEach(function(f){\n"
        "      var p = f.getAttribute('data-action-path');\n"
        "      if (!p) return;\n"
        "      try { f.action = new URL(p, siteRoot).href; } catch(e) {}\n"
        "    });\n"
        "    sidebar.querySelectorAll('a.site-title[data-path]').forEach(function(a){\n"
        "      var p = a.getAttribute('data-path');\n"
        "      if (!p) return;\n"
        "      try { a.href = new URL(p, siteRoot).href; } catch(e) {}\n"
        "    });\n"
        "\n"
        "    // Restore and persist folder open/closed state.\n"
        "    var openSet = loadOpenSet();\n"
        "    sidebar.querySelectorAll('details[data-folder]').forEach(function(d){\n"
        "      var key = d.getAttribute('data-folder');\n"
        "      if (key && openSet.has(key)) d.open = true;\n"
        "      d.addEventListener('toggle', function(){\n"
        "        if (!key) return;\n"
        "        if (d.open) openSet.add(key); else openSet.delete(key);\n"
        "        saveOpenSet(openSet);\n"
        "      });\n"
        "    });\n"
        "\n"
        "    // Mark the current page as active and open its ancestor folders.\n"
        "    var curPath = normalizePathname(decodeURIComponent(window.location.pathname));\n"
        "    var active = null;\n"
        "    sidebar.querySelectorAll('a[data-path]').forEach(function(a){\n"
        "      try {\n"
        "        var u = new URL(a.href);\n"
        "        if (normalizePathname(decodeURIComponent(u.pathname)) === curPath) active = a;\n"
        "      } catch(e) {}\n"
        "    });\n"
        "    if (active) {\n"
        "      active.classList.add('active');\n"
        "      active.setAttribute('aria-current', 'page');\n"
        "      // Open only this page's ancestor folders; close all others.\n"
        "      var keep = new Set();\n"
        "      var el = active;\n"
        "      while (el) {\n"
        "        if (el.tagName === 'DETAILS') {\n"
        "          var k = el.getAttribute('data-folder');\n"
        "          if (k) keep.add(k);\n"
        "        }\n"
        "        el = el.parentElement;\n"
        "      }\n"
        "      sidebar.querySelectorAll('details[data-folder]').forEach(function(d){\n"
        "        var k = d.getAttribute('data-folder');\n"
        "        d.open = !!(k && keep.has(k));\n"
        "      });\n"
        "      openSet = keep;\n"
        "      saveOpenSet(openSet);\n"
        "      // If we deep-linked to a page, don't keep the TOC hidden on desktop.\n"
        "      // Do not override an explicit user preference (tocCollapsed=1) or the Home animation.\n"
        "      setTimeout(function(){\n"
        "        try {\n"
        "          if (document.querySelector('main.content.home')) return;\n"
        "          var tocList = document.getElementById('tocList');\n"
        "          if (!tocList || !tocList.classList.contains('toc-collapsed')) return;\n"
        "          var persisted = null;\n"
        "          try { persisted = localStorage.getItem('tocCollapsed'); } catch(e) {}\n"
        "          if (persisted === '1') return;\n"
        "          tocList.classList.remove('toc-collapsed');\n"
        "          var btn = document.getElementById('tocToggle');\n"
        "          if (btn) {\n"
        "            btn.setAttribute('aria-expanded', 'true');\n"
        "            btn.textContent = 'Hide Contents';\n"
        "          }\n"
        "        } catch(e) {}\n"
        "      }, 0);\n"
        "    }\n"
        "  }\n"
        "\n"
        "  mount();\n"
        "})();\n"
    )

    old = out_path.read_text(encoding="utf-8") if out_path.exists() else None
    if old != js:
        out_path.write_text(js, encoding="utf-8")


def preprocess_callout_blocks(md_text: str) -> str:
    """Convert --{.class} blocks to final HTML callout/box divs.

    Syntax:
    --{.callout-info}
    content here
    can include lists
    - item 1
    - item 2
    --

    We render the inner markdown *before* the main page conversion, then
    insert the finished HTML so it is not re-parsed.
    """
    lines = md_text.splitlines()
    result: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # Match opening --{.class} - simplified syntax: .info-narrow-right-heavy or .warning-rounded
        match = re.match(r'^--\{\.([^}]+)\}\s*$', line)
        if match:
            # Parse class string: split by hyphens, first part is type (info/warning/tip/note)
            class_str = match.group(1)
            parts = class_str.split('-')
            
            # First part is the type
            type_name = parts[0] if parts else 'note'
            modifiers = parts[1:] if len(parts) > 1 else []
            
            # Build class list: base class is 'callout' + type
            classes = ['callout', f'callout-{type_name}']
            
            # Add modifiers
            for mod in modifiers:
                if mod == 'narrow':
                    classes.append('callout-narrow')
                elif mod == 'right':
                    classes.append('callout-right')
                elif mod == 'center':
                    classes.append('callout-center')
                elif mod == 'heavy':
                    classes.append('callout-heavy')
                elif mod == 'left-border':
                    classes.append('callout-left-border')
                elif mod == 'inverted':
                    classes.append('callout-inverted')
                elif mod == 'rounded':
                    classes.append('callout-rounded')
            
            class_attr = ' '.join(classes)
            
            # Collect content until closing --
            inner_lines: List[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != "--":
                inner_lines.append(lines[i])
                i += 1
            # Skip closing "--" if present
            if i < len(lines) and lines[i].strip() == "--":
                i += 1

            body_md = "\n".join(inner_lines).strip("\n")
            if body_md:
                # Step blocks: wrap content in step-content span so flex layout doesn't split inline elements
                step_replacements: List[Tuple[str, str]] = []
                if type_name == 'step':
                    # 1) List-style: 1), 1., 2), a., b., etc. -> ### <span data-step="N"></span><span class="step-content">Title</span>
                    # If starts with 1 or a: force incremental (1,2,3 or a,b,c). If starts with 2, b, etc: leave as-is.
                    list_state: List[object] = [None, 0, ord('a')]  # [mode, counter, alpha_base]
                    def _list_repl(m):
                        k = m.group(1)
                        if list_state[0] is None:
                            if k == '1' or (len(k) == 1 and k.lower() == 'a'):
                                list_state[0] = 'num' if k == '1' else 'alpha'
                                list_state[1] = 1
                                if list_state[0] == 'alpha':
                                    list_state[2] = ord('a') if k.islower() else ord('A')
                                display_k = '1' if list_state[0] == 'num' else k
                            else:
                                list_state[0] = False
                                display_k = k
                        else:
                            if list_state[0] is False:
                                display_k = k
                            else:
                                list_state[1] += 1
                                if list_state[0] == 'num':
                                    display_k = str(list_state[1])
                                else:
                                    display_k = chr(list_state[2] + list_state[1] - 1)
                        step_replacements.append((f'<span data-step="{k}"></span>', f'<span class="step-num">{display_k}</span>'))
                        return f'### <span data-step="{k}"></span><span class="step-content"> {m.group(2)}</span>'
                    body_md = re.sub(r'^(\d+|[a-zA-Z])[.)]\s+(.+)$', _list_repl, body_md, flags=re.MULTILINE)
                    # 2) Headings: ### Title or ### 2. Title -> ### <span data-step="N"></span><span class="step-content"> Title</span>
                    # If heading has number and it's not 1: use as-is. Else: force incremental.
                    step_counter = [0]
                    hdg_state: List[object] = [None]  # None, True (force), False (as-is)
                    def _hdg_repl(m):
                        if 'data-step=' in m.group(3) or 'step-content' in m.group(3):
                            return m.group(0)
                        num = m.group(2)  # captured optional number
                        if hdg_state[0] is None:
                            if num and num != '1':
                                hdg_state[0] = False
                                k = num
                                step_counter[0] = int(num)
                            else:
                                hdg_state[0] = True
                                step_counter[0] += 1
                                k = str(step_counter[0])
                        else:
                            if hdg_state[0] is False:
                                if num:
                                    k = num
                                    step_counter[0] = int(num)
                                else:
                                    step_counter[0] += 1
                                    k = str(step_counter[0])
                            else:
                                step_counter[0] += 1
                                k = str(step_counter[0])
                        step_replacements.append((f'<span data-step="{k}"></span>', f'<span class="step-num">{k}</span>'))
                        return f'{m.group(1)} <span data-step="{k}"></span><span class="step-content"> {m.group(3)}</span>'
                    body_md = re.sub(r'^(#{1,3})\s+(?:(\d+)\.\s+)?(.+)$', _hdg_repl, body_md, flags=re.MULTILINE)
                # ==highlight== and *italic* **bold** parsed by markdown
                body_md = preprocess_highlight_syntax(body_md)
                body_md = preprocess_inline_footnotes(ensure_blank_lines_before_lists(body_md))
                body_md = preprocess_mathjax_delimiters(body_md)
                inner_html = markdown.markdown(
                    body_md,
                    extensions=markdown_extensions(),
                )
                for old_s, new_s in step_replacements:
                    inner_html = inner_html.replace(old_s, new_s)
            else:
                inner_html = ""

            result.append(f'<div class="{class_attr}">')
            if inner_html:
                result.append(inner_html)
            result.append("</div>")
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def preprocess_column_blocks(md_text: str) -> str:
    """Convert Obsidian multi-column syntax to Bootstrap grid columns.
    
    Syntax:
    --- start-multi-column: RegionName
    number of columns: 2
    largest column: left
    Content for column 1.
    --- end-column ---
    Content for column 2.
    --- end-multi-column
    
    Metadata is hidden with CSS. Columns are wrapped in a Bootstrap row.
    """
    lines = md_text.splitlines()
    result: List[str] = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        # Match opening --- start-multi-column: RegionName
        match_start = re.match(r'^---\s+start-multi-column:\s*(.+)$', line, re.IGNORECASE)
        if match_start:
            region_name = match_start.group(1).strip()
            column_group: List[str] = []
            num_columns = 2  # default
            largest_column = None  # None = equal width
            metadata_lines: List[str] = [line]  # Keep metadata for hiding with CSS
            
            # Parse configuration lines (keep them but hide with CSS)
            i += 1
            config_section_ended = False
            while i < len(lines) and not config_section_ended:
                config_line = lines[i]
                # Support Obsidian-style fenced config block:
                # ```column-settings
                # number of columns: 2
                # largest column: left
                # ```
                # We parse and CONSUME this block so it doesn't render as a code block in HTML.
                if re.match(r'^\s*```\s*column-settings\s*$', config_line, re.IGNORECASE):
                    i += 1
                    while i < len(lines) and not re.match(r'^\s*```\s*$', lines[i]):
                        inner = lines[i]
                        num_match = re.match(r'^\s*number\s+of\s+columns:\s*(\d+)', inner, re.IGNORECASE)
                        if num_match:
                            num_columns = int(num_match.group(1))
                        largest_match = re.match(r'^\s*largest\s+column:\s*(left|right|center)', inner, re.IGNORECASE)
                        if largest_match:
                            largest_column = largest_match.group(1).lower()
                        i += 1
                    # Skip closing fence if present
                    if i < len(lines) and re.match(r'^\s*```\s*$', lines[i]):
                        i += 1
                    continue
                # Skip blank lines in config section
                if not config_line.strip():
                    metadata_lines.append(config_line)
                    i += 1
                    continue
                # Check for number of columns
                num_match = re.match(r'^\s*number\s+of\s+columns:\s*(\d+)', config_line, re.IGNORECASE)
                if num_match:
                    num_columns = int(num_match.group(1))
                    metadata_lines.append(config_line)
                    i += 1
                    continue
                # Check for largest column
                largest_match = re.match(r'^\s*largest\s+column:\s*(left|right|center)', config_line, re.IGNORECASE)
                if largest_match:
                    largest_column = largest_match.group(1).lower()
                    metadata_lines.append(config_line)
                    i += 1
                    continue
                # If line doesn't match config pattern, we've reached content
                config_pattern = r'^\s*(number\s+of\s+columns|largest\s+column):'
                if not re.match(config_pattern, config_line, re.IGNORECASE):
                    # Not a config line, start collecting content from this line
                    config_section_ended = True
                    break
                # Unknown config line, keep it in metadata
                metadata_lines.append(config_line)
                i += 1
            
            # Skip any remaining config-like lines before collecting content
            while i < len(lines):
                content_line = lines[i]
                # Skip blank lines
                if not content_line.strip():
                    i += 1
                    continue
                # If someone placed the fenced column-settings block after blank lines, still consume it.
                if re.match(r'^\s*```\s*column-settings\s*$', content_line, re.IGNORECASE):
                    i += 1
                    while i < len(lines) and not re.match(r'^\s*```\s*$', lines[i]):
                        inner = lines[i]
                        num_match = re.match(r'^\s*number\s+of\s+columns:\s*(\d+)', inner, re.IGNORECASE)
                        if num_match:
                            num_columns = int(num_match.group(1))
                        largest_match = re.match(r'^\s*largest\s+column:\s*(left|right|center)', inner, re.IGNORECASE)
                        if largest_match:
                            largest_column = largest_match.group(1).lower()
                        i += 1
                    if i < len(lines) and re.match(r'^\s*```\s*$', lines[i]):
                        i += 1
                    continue
                # Skip any remaining config lines (shouldn't happen, but safety check)
                config_pattern = r'^\s*(number\s+of\s+columns|largest\s+column):'
                if re.match(config_pattern, content_line, re.IGNORECASE):
                    # Add to metadata but don't include in output
                    metadata_lines.append(content_line)
                    i += 1
                    continue
                # Not a config line, start collecting content (even if it's a marker, we'll handle it in the collection loop)
                break
            
            # Collect column content
            current_column: List[str] = []
            end_marker_line = ""
            while i < len(lines):
                content_line = lines[i]
                # Match --- end-column ---
                if re.match(r'^---\s+end-column\s+---\s*$', content_line, re.IGNORECASE):
                    if current_column:
                        column_group.append("\n".join(current_column).strip())
                    current_column = []
                    i += 1
                    continue
                # Match --- end-multi-column
                elif re.match(r'^---\s+end-multi-column\s*$', content_line, re.IGNORECASE):
                    if current_column:
                        column_group.append("\n".join(current_column).strip())
                    end_marker_line = content_line
                    i += 1
                    break
                else:
                    # Skip any config lines that might have slipped through
                    config_pattern = r'^\s*(number\s+of\s+columns|largest\s+column):'
                    if not re.match(config_pattern, content_line, re.IGNORECASE):
                        current_column.append(content_line)
                    i += 1
            
            # Render columns with hidden metadata
            if column_group:
                num_cols = len(column_group)
                if num_cols > 0:
                    # Determine column classes based on largest column setting
                    if largest_column == "left" and num_cols == 2:
                        col_classes = ["col-md-8", "col-md-4"]
                    elif largest_column == "right" and num_cols == 2:
                        col_classes = ["col-md-4", "col-md-8"]
                    elif largest_column == "center" and num_cols == 3:
                        col_classes = ["col-md-3", "col-md-6", "col-md-3"]
                    else:
                        # Equal width columns
                        col_width = 12 // num_cols
                        col_classes = [f"col-md-{col_width}"] * num_cols
                    
                    # Metadata is parsed and used, no need to include it in output
                    # Slightly wider default gutter than Bootstrap's g-3 (50% more): g-4
                    result.append('<div class="row g-4 mb-3">')
                    for idx, col_content in enumerate(column_group):
                        if col_content:
                            col_md = preprocess_inline_footnotes(ensure_blank_lines_before_lists(col_content))
                            col_md = preprocess_mathjax_delimiters(col_md)
                            # Ensure custom callout blocks work inside multi-column regions.
                            col_md = preprocess_callout_blocks(col_md)
                            col_html = markdown.markdown(
                                col_md,
                                extensions=markdown_extensions(),
                            )
                            col_class = col_classes[idx] if idx < len(col_classes) else f"col-md-{12 // num_cols}"
                            result.append(f'<div class="{col_class}">')
                            result.append(col_html)
                            result.append('</div>')
                    result.append('</div>')
            continue
        
        result.append(line)
        i += 1

    return "\n".join(result)


def preprocess_heading_attributes(md_text: str) -> str:
    """Preprocess heading attributes to ensure attr_list extension works.
    
    Converts: ## heading{.class} -> ## heading {.class}
    """
    # Match headings with attributes that might be missing space
    pattern = r'^(#{1,6}\s+[^{]+)\{\.([^}]+)\}'
    def fix_spacing(match):
        heading_text = match.group(1).rstrip()
        class_name = match.group(2)
        return f'{heading_text} {{.{class_name}}}'
    return re.sub(pattern, fix_spacing, md_text, flags=re.MULTILINE)


def _metadata_has_tag(metadata: Dict[str, Any], tag: str) -> bool:
    """Return True if YAML metadata contains the given tag in 'tags'/'Tags'."""
    tags_val = metadata.get("tags") if isinstance(metadata, dict) else None
    if tags_val is None and isinstance(metadata, dict):
        tags_val = metadata.get("Tags")
    if tags_val is None:
        return False
    if isinstance(tags_val, list):
        return any(str(t).strip().lower() == tag for t in tags_val)
    return str(tags_val).strip().lower() == tag


def _format_date_badge_text(date_value: Any) -> Optional[str]:
    """Parse a YAML 'date' value and return a nice display string like '30 Dec 2025'."""
    try:
        from datetime import datetime, date as _date
    except Exception:
        return None

    if date_value is None:
        return None

    # YAML may already decode ISO-like dates into a date/datetime
    if isinstance(date_value, datetime):
        d = date_value.date()
        return f"{d.day} {d.strftime('%b %Y')}"
    if isinstance(date_value, _date):
        return f"{date_value.day} {date_value.strftime('%b %Y')}"

    s = str(date_value).strip()
    if not s:
        return None

    # Try a few common human-entered formats (day-first first)
    fmts = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%m/%d/%Y",  # US-style (fallback)
        "%m-%d-%Y",
    ]
    for fmt in fmts:
        try:
            d = datetime.strptime(s, fmt).date()
            return f"{d.day} {d.strftime('%b %Y')}"
        except Exception:
            continue

    return None


def render_date_badge_html(metadata: Dict[str, Any]) -> Optional[str]:
    """Render a date badge if YAML front matter contains 'date'."""
    if not isinstance(metadata, dict):
        return None
    if "date" not in metadata and "Date" not in metadata:
        return None
    raw = metadata.get("date") if "date" in metadata else metadata.get("Date")
    nice = _format_date_badge_text(raw)
    label = nice if nice else str(raw).strip()
    if not label:
        return None
    return (
        '<div class="mb-3">'
        f'<span class="badge text-bg-light border"><i class="far fa-calendar"></i> {html.escape(label)}</span>'
        "</div>"
    )


def preprocess_case_study_styles(md_text: str) -> str:
    """Apply consistent case study styling rules to markdown.
    
    Rules:
    - H2 (##) -> add {.banner} unless a class is already specified
    - H3 (###) -> add {.rounded} unless a class is already specified
    - Callouts: --{.note...} -> --{.tip...} (treat default note callouts as tips)
    - Blockquotes (lines starting with '>') are treated as "normal callouts" and rendered as tip callouts
    """
    lines = md_text.splitlines()
    out: List[str] = []
    in_fence = False

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue

        # "Normal callouts": markdown blockquotes -> tip callout blocks (case study pages only)
        if re.match(r"^\s*>\s?", line):
            inner_lines: List[str] = []
            while i < len(lines) and re.match(r"^\s*>\s?", lines[i]):
                inner_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("--{.tip}")
            out.extend(inner_lines)
            out.append("--")
            continue
        
        # Callouts: promote note -> tip (keep modifiers)
        m_callout = re.match(r'^--\{\.([^}]+)\}\s*$', line)
        if m_callout:
            class_str = m_callout.group(1).strip()
            parts = class_str.split("-") if class_str else []
            type_name = parts[0] if parts else ""
            mods = parts[1:] if len(parts) > 1 else []
            if type_name == "note":
                new_class = "tip" + ("-" + "-".join(mods) if mods else "")
                out.append(f'--{{.{new_class}}}')
                i += 1
                continue
        
        # Headings: auto-add classes unless overridden by an explicit class
        cls_to_add = None
        if line.startswith("## "):
            cls_to_add = "banner"
        elif line.startswith("### "):
            cls_to_add = "rounded"
        
        if cls_to_add:
            m_attr = re.search(r'\s*\{([^}]*)\}\s*$', line)
            if m_attr:
                attrs = m_attr.group(1)
                # If any class is explicitly set, treat as override
                if "." in attrs:
                    out.append(line)
                    i += 1
                    continue
                # Otherwise it's likely just an id {#...}; add the class into the same attr block
                new_attrs = (attrs.strip() + f" .{cls_to_add}").strip()
                out.append(line[:m_attr.start(1)] + new_attrs + line[m_attr.end(1):])
                i += 1
                continue
            else:
                out.append(line.rstrip() + f" {{.{cls_to_add}}}")
                i += 1
                continue
        
        out.append(line)
        i += 1

    return "\n".join(out)


def preprocess_paper_styles(md_text: str) -> str:
    """Apply consistent paper styling rules to markdown.

    Enabled by YAML tag: paper

    Rules:
    - H2 (##) -> add {.banner-info} unless a class is already specified
    - H3 (###) -> add {.rounded-info} unless a class is already specified
    - Blockquotes (lines starting with '>') are treated as "normal callouts" and rendered as note callouts
    """
    lines = md_text.splitlines()
    out: List[str] = []
    in_fence = False

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue

        # "Normal callouts": markdown blockquotes -> note callout blocks (paper pages only)
        if re.match(r"^\s*>\s?", line):
            inner_lines: List[str] = []
            while i < len(lines) and re.match(r"^\s*>\s?", lines[i]):
                inner_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("--{.note}")
            out.extend(inner_lines)
            out.append("--")
            continue

        # Headings: auto-add classes unless overridden by an explicit class
        cls_to_add = None
        if line.startswith("## "):
            cls_to_add = "banner-info"
        elif line.startswith("### "):
            cls_to_add = "rounded-info"

        if cls_to_add:
            m_attr = re.search(r'\s*\{([^}]*)\}\s*$', line)
            if m_attr:
                attrs = m_attr.group(1)
                # If any class is explicitly set, treat as override
                if "." in attrs:
                    out.append(line)
                    i += 1
                    continue
                # Otherwise it's likely just an id {#...}; add the class into the same attr block
                new_attrs = (attrs.strip() + f" .{cls_to_add}").strip()
                out.append(line[:m_attr.start(1)] + new_attrs + line[m_attr.end(1):])
                i += 1
                continue
            else:
                out.append(line.rstrip() + f" {{.{cls_to_add}}}")
                i += 1
                continue

        out.append(line)
        i += 1

    return "\n".join(out)


def ensure_blank_lines_before_lists(md_text: str) -> str:
    """Insert blank lines before list items if not already present (Obsidian compatibility).
    
    Obsidian allows lists immediately after text without blank lines, but standard markdown requires them.
    """
    # Obsidian also allows ordered lists like "1) item" which python-markdown won't treat as a list.
    # Normalize "n)" -> "n." everywhere before further list handling.
    lines_raw = md_text.split('\n')
    lines = [re.sub(r'^(\s*)(\d+)\)\s+', r'\1\2. ', ln) for ln in lines_raw]
    result: List[str] = []
    
    for i, line in enumerate(lines):
        # Check if this is a list item (unordered or ordered)
        is_list_item = re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line)
        
        if is_list_item and i > 0:
            prev_line = lines[i - 1]
            # Check if previous line is not blank and not a list item
            if prev_line.strip() and not (re.match(r'^\s*[-*+]\s+', prev_line) or re.match(r'^\s*\d+\.\s+', prev_line)):
                # Insert blank line before this list item
                result.append('')
        
        result.append(line)
    
    return '\n'.join(result)


def preprocess_highlight_syntax(md_text: str) -> str:
    """Convert Obsidian-style ==highlight== to <mark>highlight</mark>, skipping fenced code."""
    lines = md_text.splitlines()
    out_lines: List[str] = []
    in_fence = False
    fence_pat = re.compile(r"^\s*(```|~~~)")
    mark_pat = re.compile(r"==([^=\n]+)==")

    for line in lines:
        s = line.strip()
        if fence_pat.match(s):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        out_lines.append(mark_pat.sub(r"<mark>\1</mark>", line))

    return "\n".join(out_lines)


def preprocess_inline_footnotes(md_text: str) -> str:
    """Convert inline footnotes of the form ^[text] into standard footnotes.
    
    Obsidian supports inline footnotes like: This is a claim.^[Source details]
    Python-Markdown's 'footnotes' extension supports only reference-style footnotes, so we
    rewrite inline footnotes into [^inlN] refs + append definitions at the end.
    
    Note: we intentionally skip fenced code blocks (``` ... ```).
    """
    lines = md_text.splitlines()
    in_fence = False
    defs: List[str] = []
    counter = 0
    out_lines: List[str] = []

    pat = re.compile(r"\^\[([^\]]+)\]")

    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue

        def _repl(m: re.Match[str]) -> str:
            nonlocal counter, defs
            counter += 1
            fid = f"inl{counter}"
            defs.append(f"[^{fid}]: {m.group(1).strip()}")
            return f"[^{fid}]"

        out_lines.append(pat.sub(_repl, line))

    if defs:
        # Ensure a blank line before footnote definitions (markdown requirement)
        if out_lines and out_lines[-1].strip():
            out_lines.append("")
        out_lines.extend(defs)

    return "\n".join(out_lines)


def preprocess_mathjax_delimiters(md_text: str) -> str:
    r"""Preserve MathJax TeX delimiters in Python-Markdown input.

    Python-Markdown treats backslash escapes like `\(` as an escape for `(`, so the backslash
    is removed before MathJax runs. We fix this by doubling ONLY single backslashes in the
    standard TeX delimiters so the rendered HTML contains the intended `\(` / `\)` / `\[`
    / `\]` sequences.

    Notes:
    - We intentionally skip fenced code blocks (```), to avoid changing code samples.
    - If authors already wrote `\\(` in markdown (the correct way), we leave it unchanged.
    """
    lines = md_text.splitlines()
    out_lines: List[str] = []
    in_fence = False

    # Only transform single-backslash delimiters (not already doubled)
    pat_lparen = re.compile(r"(?<!\\)\\\(")
    pat_rparen = re.compile(r"(?<!\\)\\\)")
    pat_lbrack = re.compile(r"(?<!\\)\\\[")
    pat_rbrack = re.compile(r"(?<!\\)\\\]")

    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue

        line = pat_lparen.sub(r"\\\\(", line)
        line = pat_rparen.sub(r"\\\\)", line)
        line = pat_lbrack.sub(r"\\\\[", line)
        line = pat_rbrack.sub(r"\\\\]", line)
        out_lines.append(line)

    return "\n".join(out_lines)


def preprocess_mermaid_fences(md_text: str) -> str:
    """Convert fenced Mermaid blocks to Mermaid divs so they render in HTML/PDF."""
    lines = md_text.splitlines()
    out_lines: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*```\s*mermaid\s*$", line, re.IGNORECASE):
            i += 1
            block_lines: List[str] = []
            while i < len(lines) and not re.match(r"^\s*```\s*$", lines[i]):
                # Keep entities like &#10; intact; only escape angle brackets for safe HTML.
                block_lines.append(lines[i].replace("<", "&lt;").replace(">", "&gt;"))
                i += 1
            if i < len(lines) and re.match(r"^\s*```\s*$", lines[i]):
                i += 1

            out_lines.append('<div class="mermaid">')
            out_lines.extend(block_lines)
            out_lines.append("</div>")
            continue

        out_lines.append(line)
        i += 1

    return "\n".join(out_lines)


# Centralised Markdown extension list (used everywhere we convert Markdown to HTML)
MARKDOWN_EXTENSIONS_BASE = ["extra", "fenced_code", "tables", "attr_list", "footnotes"]


def markdown_extensions(with_toc: bool = False) -> List[str]:
    """Return the markdown extensions list (optionally including ToC generation)."""
    return MARKDOWN_EXTENSIONS_BASE + (["toc"] if with_toc else [])


def convert_markdown_to_html(md_text: str) -> str:
    """Convert markdown to HTML with minimal extensions."""
    md_text = strip_percent_comments(md_text)
    md_text = preprocess_column_blocks(md_text)
    md_text = preprocess_callout_blocks(md_text)
    md_text = preprocess_heading_attributes(md_text)
    md_text = ensure_blank_lines_before_lists(md_text)
    md_text = preprocess_highlight_syntax(md_text)
    md_text = preprocess_inline_footnotes(md_text)
    md_text = preprocess_mathjax_delimiters(md_text)
    md_text = preprocess_mermaid_fences(md_text)
    # Use 'extra' extension which processes markdown inside HTML blocks
    return markdown.markdown(md_text, extensions=markdown_extensions())


def convert_markdown_with_toc(md_text: str) -> Tuple[str, str]:
    """Convert markdown and also return a generated ToC HTML.

    Returns (content_html, toc_html)
    """
    md_text = strip_percent_comments(md_text)
    md_text = preprocess_column_blocks(md_text)
    md_text = preprocess_callout_blocks(md_text)
    md_text = preprocess_heading_attributes(md_text)
    md_text = ensure_blank_lines_before_lists(md_text)
    md_text = preprocess_highlight_syntax(md_text)
    md_text = preprocess_inline_footnotes(md_text)
    md_text = preprocess_mathjax_delimiters(md_text)
    md_text = preprocess_mermaid_fences(md_text)
    # Use 'extra' extension which processes markdown inside HTML blocks
    md = markdown.Markdown(extensions=markdown_extensions(with_toc=True))
    content_html = md.convert(md_text)
    toc_html = getattr(md, "toc", "")
    return content_html, toc_html


def _first_non_heading_paragraph_html(md_text: str) -> Optional[str]:
    """Return the first non-heading paragraph as HTML (or None).

    Skips YAML front matter, headings (#), code fences, lists, and blank lines.
    """
    md_text = strip_yaml_front_matter(md_text)
    lines = md_text.splitlines()
    in_fence = False
    para_lines: List[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not s:
            if para_lines:
                break
            continue
        # skip headings and non-paragraph starters
        if s.startswith("#"):
            continue
        if s.startswith(("- ", "* ", "+ ")):
            continue
        if re.match(r"^\d+\.\s", s):
            continue
        if s.startswith(("!", ">", "|")):
            continue
        # take this line as the start of a paragraph
        para_lines.append(line)
        # include following lines until blank
        continue
    # If we started a paragraph, extend with subsequent lines until blank
    if para_lines:
        started = False
        out: List[str] = []
        for line in lines:
            if not started:
                if line == para_lines[0]:
                    started = True
                    out.append(line)
                continue
            if not line.strip():
                break
            out.append(line)
        snippet = "\n".join(out) if out else para_lines[0]
        html_snip = convert_markdown_to_html(snippet)
        return html_snip
    return None


def normalize_alpha_ordered_lists(md_text: str) -> str:
    """Convert lettered list markers (a., a) etc.) into numeric ordered lists.

    This makes inputs like 'z. foo' or 'b) bar' render as an ordered list.
    """
    lines = md_text.splitlines()
    out: List[str] = []
    in_block = False
    current_indent = ""
    n = 0
    pat = re.compile(r"^([ \t]{0,3})([A-Za-z])[\.)][ \t]+(.*)$")
    for line in lines:
        m = pat.match(line)
        if m:
            indent, _letter, rest = m.group(1), m.group(2), m.group(3)
            if not in_block:
                in_block = True
                current_indent = indent
                n = 1
                # Insert an HTML comment marker to tag this list as alpha for post-processing
                out.append("<!--ALPHA-OL-->")
            else:
                if indent != current_indent:
                    # indentation changed: end block and restart
                    in_block = True
                    current_indent = indent
                    n = 1
                    out.append("<!--ALPHA-OL-->")
            out.append(f"{current_indent}{n}. {rest}")
            n += 1
        else:
            in_block = False
            out.append(line)
    return "\n".join(out)


def postprocess_alpha_ol_html(html_text: str) -> str:
    """Turn ALPHA list markers into <ol type="a"> and strip the markers.

    Looks for <!--ALPHA-OL--> immediately before an <ol> and sets type="a".
    """
    # Replace marker + opening ol
    html_text = re.sub(r"<!--ALPHA-OL-->\s*<ol>", "<ol type=\"a\">", html_text, flags=re.IGNORECASE)
    # Remove any stray markers that weren't followed by <ol>
    html_text = html_text.replace("<!--ALPHA-OL-->", "")
    return html_text


def build_breadcrumb_data(md_path: Path, input_root: Path, output_root: Path, md_files: List[Path], title_map: Dict[Path, str], current_out_dir: Path) -> List[Dict[str, Any]]:
    """Build breadcrumb data structure with siblings at each level.
    
    Returns list of breadcrumb items, each containing:
    - title: display name
    - href: link to this item
    - siblings: list of {title, href, is_current} for items at this level
    """
    # Root is always first
    breadcrumb_items: List[Dict[str, Any]] = []
    
    # Add Home link
    home_href = os.path.relpath(output_root / "index.html", start=current_out_dir).replace(os.sep, "/")
    home_siblings = []
    
    # Get all top-level folders as siblings of Home
    top_folders = sorted({p.relative_to(input_root).parts[0] for p in md_files if len(p.relative_to(input_root).parts) >= 2})
    for folder in top_folders:
        folder_pages = [p for p in md_files if p.relative_to(input_root).parts[0] == folder]
        # Exclude draft files (with ! in filename) when determining first page
        folder_pages_no_drafts = [p for p in folder_pages if '!' not in p.name]
        folder_pages_no_drafts.sort(key=_path_file_key)
        if folder_pages_no_drafts:
            first_page = folder_pages_no_drafts[0]
            folder_href = os.path.relpath(relative_output_html(input_root, output_root, first_page), start=current_out_dir).replace(os.sep, "/")
            folder_title = strip_numeric_prefix(folder).replace("--", "–")
            home_siblings.append({"title": folder_title, "href": folder_href, "is_current": False})
    
    breadcrumb_items.append({"title": "Home", "href": home_href, "siblings": home_siblings})
    
    # If not root index, add path segments
    if md_path.resolve() != (input_root / "index.md").resolve():
        rel_parts = md_path.relative_to(input_root).parts
        
        # Add folder if present
        if len(rel_parts) >= 2:
            folder = rel_parts[0]
            folder_pages = [p for p in md_files if p.relative_to(input_root).parts[0] == folder]
            # Exclude draft files (with ! in filename) when determining first page
            folder_pages_no_drafts = [p for p in folder_pages if '!' not in p.name]
            folder_pages_no_drafts.sort(key=_path_file_key)
            if folder_pages_no_drafts:
                first_page = folder_pages_no_drafts[0]
                folder_href = os.path.relpath(relative_output_html(input_root, output_root, first_page), start=current_out_dir).replace(os.sep, "/")
                folder_title = strip_numeric_prefix(folder).replace("--", "–")
                
                # Siblings = all non-draft files in this folder
                folder_siblings = []
                for p in folder_pages_no_drafts:
                    p_href = os.path.relpath(relative_output_html(input_root, output_root, p), start=current_out_dir).replace(os.sep, "/")
                    p_title = title_map.get(p, strip_numeric_prefix(p.stem)).replace("--", "–")
                    folder_siblings.append({"title": p_title, "href": p_href, "is_current": (p.resolve() == md_path.resolve())})
                
                breadcrumb_items.append({"title": folder_title, "href": folder_href, "siblings": folder_siblings})
    
    return breadcrumb_items


def _extract_tags_from_metadata(metadata: Dict[str, Any]) -> List[str]:
    """Extract tags from YAML metadata (supports tags: 'x' or tags: ['x','y'])."""
    if not isinstance(metadata, dict):
        return []
    tags_val = metadata.get("tags") if "tags" in metadata else metadata.get("Tags")
    if tags_val is None:
        return []
    if isinstance(tags_val, list):
        return [str(t).strip() for t in tags_val if str(t).strip()]
    s = str(tags_val).strip()
    return [s] if s else []


def _extract_icon_override_from_metadata(metadata: Dict[str, Any]) -> Optional[str]:
    """Parse YAML front matter 'icon:' (preferred) or legacy tag 'icon; star' for the page title icon.

    Returns:
    - None: no override found (use the default icon)
    - "": explicit 'none' (render no icon)
    - "<emoji>": an emoji character to render
    """
    emoji_map = {
        "sunflower": "🌻",
        "star": "⭐",
        "sparkles": "✨",
        "fire": "🔥",
        "rocket": "🚀",
        "lightbulb": "💡",
        "book": "📘",
        "pencil": "✏️",
        "gear": "⚙️",
        "search": "🔎",
        "warning": "⚠️",
        "info": "ℹ️",
        "check": "✅",
        "cross": "❌",
    }

    def _parse_icon_value(raw_value: Any, *, src_label: str) -> Optional[str]:
        raw = str(raw_value).strip() if raw_value is not None else ""
        if not raw:
            return ""

        raw_l = raw.lower()
        if raw_l in {"none", "no", "false", "0"}:
            return ""

        # Support ":star:" style too (purely as a convenience).
        if raw.startswith(":") and raw.endswith(":") and len(raw) >= 3:
            raw = raw[1:-1].strip()
            raw_l = raw.lower()

        if raw_l in emoji_map:
            return emoji_map[raw_l]

        # If the user already supplied an emoji literal (non-ascii), accept it as-is.
        if any(ord(ch) > 127 for ch in raw):
            return raw

        _warn(
            "icon",
            f"Unknown icon name '{raw}' from {src_label} (expected e.g. 'star', 'sparkles', or a literal emoji). Using default.",
        )
        return None

    # Preferred: explicit YAML field (top-level) icon:
    if isinstance(metadata, dict):
        if "icon" in metadata or "Icon" in metadata:
            raw_icon = metadata.get("icon") if "icon" in metadata else metadata.get("Icon")
            return _parse_icon_value(raw_icon, src_label="YAML field 'icon:'")

    # Legacy (back-compat): tags include "icon; star"
    tags = _extract_tags_from_metadata(metadata or {})
    for t in tags:
        m = re.match(r"^\s*icon\s*;\s*(.*?)\s*$", str(t), flags=re.IGNORECASE)
        if m:
            return _parse_icon_value(m.group(1), src_label="YAML tag 'icon; ...'")

    return None


def _extract_logo_overlay_from_metadata(metadata: Dict[str, Any]) -> Optional[str]:
    """Parse YAML front matter 'logo:' for a small overlay logo in the top-left of the content.

    Returns:
    - None: no override found (no logo)
    - "": explicit none/empty (no logo)
    - "<filename>": a filename under output /assets/ (e.g. "cm-logo.png")
    """
    if not isinstance(metadata, dict):
        return None
    if "logo" not in metadata and "Logo" not in metadata:
        return None

    raw = metadata.get("logo") if "logo" in metadata else metadata.get("Logo")
    s = str(raw).strip().lower() if raw is not None else ""
    if not s or s in {"none", "no", "false", "0"}:
        return ""

    # Map short names to the expected asset filenames under input_root/assets/.
    # These get copied to output_root/assets/ by copy_assets().
    logo_map = {
        "cm": "cm-logo.png",
        "qualia": "qualia.png",
    }
    if s in logo_map:
        return logo_map[s]

    _warn("logo", f"Unknown logo '{raw}' in YAML field 'logo:' (expected 'cm' or 'qualia'). Ignoring.")
    return None


def _extract_page_layout_from_metadata(metadata: Dict[str, Any]) -> str:
    """Parse YAML front matter 'layout:' for page-level layout mode.

    Supported values:
    - "fullscreen": full-width display, no sidebars/chrome (starts in fullscreen).
    - "showcase": alias for fullscreen.

    Returns normalized layout string or empty string.
    """
    if not isinstance(metadata, dict):
        return ""
    if "layout" not in metadata and "Layout" not in metadata:
        return ""

    raw = metadata.get("layout") if "layout" in metadata else metadata.get("Layout")
    val = str(raw).strip().lower() if raw is not None else ""
    if not val or val in {"default", "normal"}:
        return ""
    if val in ("fullscreen", "showcase"):
        return "fullscreen"
    _warn("layout", f"Unknown layout '{raw}' in YAML field 'layout:'. Ignoring.")
    return ""


def build_tags_index(md_files: List[Path], metadata_map: Dict[Path, Dict[str, Any]]) -> Dict[str, List[Path]]:
    """Build tag -> pages index (tag keys are lowercased for grouping)."""
    idx: Dict[str, List[Path]] = defaultdict(list)
    for p in md_files:
        tags = _extract_tags_from_metadata(metadata_map.get(p, {}) or {})
        for t in tags:
            key = t.strip().lower()
            if not key:
                continue
            # Control tags should not appear in the user-facing tag index dropdown.
            if re.match(r"^\s*icon\s*;", key, flags=re.IGNORECASE):
                continue
            idx[key].append(p)
    return idx


def render_tags_dropdown_html(tag_index: Dict[str, List[Path]], current_out_dir: Path, input_root: Path, output_root: Path, title_map: Dict[Path, str]) -> str:
    """Render a breadcrumb dropdown listing tags and their pages (nested lists)."""
    if not tag_index:
        return ""
    parts: List[str] = []
    parts.append('<div class="bc-dropdown">')
    parts.append('<span class="bc-label">Tags</span><span class="bc-chevron">▼</span>')
    parts.append('<div class="bc-menu bc-menu-tags"><div class="bc-heading">Tags</div>')

    def _tag_display_label(tag_key: str) -> str:
        # Custom display labels
        if tag_key == "paper":
            return "Papers and Drafts"
        if tag_key == "case_study":
            return "Case Studies"
        # Default: prettify snake_case / kebab-case
        pretty = tag_key.replace("_", " ").replace("-", " ").strip()
        return pretty.title() if pretty else tag_key

    # sort tags A→Z
    for tag_key in sorted(tag_index.keys()):
        pages = tag_index.get(tag_key) or []
        if not pages:
            continue
        # sort pages by displayed title
        pages_sorted = sorted(pages, key=lambda p: (title_map.get(p, strip_numeric_prefix(p.stem)) or "").lower())
        parts.append(f'<div class="bc-tag">{html.escape(_tag_display_label(tag_key))}</div>')
        parts.append('<ul class="bc-tag-pages">')
        for p in pages_sorted:
            href = os.path.relpath(relative_output_html(input_root, output_root, p), start=current_out_dir).replace(os.sep, "/")
            label = (title_map.get(p, strip_numeric_prefix(p.stem)) or strip_numeric_prefix(p.stem)).replace("--", "–")
            parts.append(f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>')
        parts.append("</ul>")
    parts.append("</div></div>")
    return "".join(parts)


def render_breadcrumb_html(breadcrumb_data: List[Dict[str, Any]], tags_dropdown_html: str = "") -> str:
    """Render breadcrumb navigation with dropdown menus for siblings."""
    if not breadcrumb_data:
        return ""
    # Build a fixed breadcrumb: Home > Chapters > Pages > (optional) Tags
    parts: List[str] = []
    home_item = breadcrumb_data[0]
    last_item = breadcrumb_data[-1] if len(breadcrumb_data) >= 1 else None

    # 1) Home (clickable)
    parts.append(f'<span class="breadcrumb-item"><a href="{html.escape(home_item["href"])}">Home</a></span>')

    # separator
    parts.append('<span class="breadcrumb-separator">/</span>')

    # 2) Chapters (dropdown with Home + top-level chapters)
    chapters_dropdown = '<div class="bc-dropdown">'
    chapters_dropdown += '<span class="bc-label">Chapters</span><span class="bc-chevron">▼</span>'
    chapters_dropdown += '<div class="bc-menu"><div class="bc-heading">Chapters</div>'
    chapters_dropdown += f'<a href="{html.escape(home_item["href"])}">Home</a>'
    for sibling in (home_item.get("siblings") or []):
        chapters_dropdown += f'<a href="{html.escape(sibling["href"])}">{html.escape(sibling["title"])}</a>'
    chapters_dropdown += '</div></div>'
    parts.append(f'<span class="breadcrumb-item">{chapters_dropdown}</span>')

    # separator
    parts.append('<span class="breadcrumb-separator">/</span>')

    # 3) Pages (dropdown with pages in current chapter) — only if not on site index and pages exist
    pages_siblings = (last_item.get("siblings") if (last_item and len(breadcrumb_data) >= 2) else [])  # type: ignore[union-attr]
    if pages_siblings:
        pages_dropdown = '<div class="bc-dropdown">'
        pages_dropdown += '<span class="bc-label">Pages</span><span class="bc-chevron">▼</span>'
        pages_dropdown += '<div class="bc-menu"><div class="bc-heading">Pages in this chapter</div>'
        for sibling in pages_siblings:
            css_class = "current" if sibling.get("is_current") else ""
            pages_dropdown += f'<a href="{html.escape(sibling["href"])}" class="{css_class}">{html.escape(sibling["title"])}</a>'
        pages_dropdown += '</div></div>'
        parts.append(f'<span class="breadcrumb-item">{pages_dropdown}</span>')

    # Optional tags dropdown
    if tags_dropdown_html:
        parts.append('<span class="breadcrumb-separator">/</span>')
        parts.append(f'<span class="breadcrumb-item">{tags_dropdown_html}</span>')

    return f'<nav class="breadcrumb-nav">{"".join(parts)}</nav>'


def _html_text_snippet_for_meta(content_html: str, max_len: int = 220) -> str:
    """Create a short plain-text description from rendered HTML (for meta description/OG)."""
    try:
        t = content_html or ""
        # Drop script/style blocks then strip tags.
        t = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", t, flags=re.IGNORECASE)
        t = re.sub(r"<[^>]+>", " ", t)
        t = html.unescape(t)
        t = re.sub(r"\s+", " ", t).strip()
        return t[:max_len].rstrip()
    except Exception:
        return ""


def _extract_first_img_src(content_html: str) -> str:
    """Return the first usable <img src="..."> from the page HTML (empty string if none)."""
    try:
        for m in re.finditer(r"<img\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"]", content_html or "", flags=re.IGNORECASE):
            src = (m.group(1) or "").strip()
            if not src:
                continue
            if src.startswith("data:"):
                continue
            # LinkedIn previews are unreliable for SVG; prefer bitmap images.
            if src.lower().endswith(".svg"):
                continue
            return src
        return ""
    except Exception:
        return ""


def render_page_html(page_title: Optional[str], content_html: str, site_title: str, page_anchor: Optional[str] = None, toc_html: Optional[str] = None, links_html: Optional[str] = None, backlinks_html: Optional[str] = None, prev_href: Optional[str] = None, next_href: Optional[str] = None, prev_title: Optional[str] = None, next_title: Optional[str] = None, pdf_link_html: Optional[str] = None, assets_href: str = "assets/", breadcrumb_html: Optional[str] = None, is_chapter_start: bool = False, chapter_subtitle: Optional[str] = None, page_anchor_routing_map: Optional[Dict[str, str]] = None, head_meta_html: str = "", page_icon: Optional[str] = None, page_layout: Optional[str] = None, sidebar_footer_html: str = "") -> str:
    """Render full HTML page with Bootstrap layout and left sidebar."""
    title_text = html.escape((f"{page_title} · {site_title}" if site_title else page_title) if page_title else (site_title or ""))
    subtitle_html = f'<div class="page-subtitle">{html.escape(chapter_subtitle)}</div>' if chapter_subtitle else ""
    # Page title icon: default is 🌻 unless overridden by YAML
    icon_prefix_html = ""
    if page_title:
        icon_to_use = page_icon if page_icon is not None else "🌻"
        icon_to_use = (icon_to_use or "").strip()
        if icon_to_use:
            icon_prefix_html = html.escape(icon_to_use) + " "
    layout_mode = (page_layout or "").strip().lower()
    is_fullscreen_layout = layout_mode == "fullscreen"
    body_class = "layout-fullscreen" if is_fullscreen_layout else ""
    body_attr = f' class="{body_class}"' if body_class else ""
    # Format page anchor routing map as JSON for JavaScript
    page_anchor_routing_json = json.dumps(page_anchor_routing_map or {}).replace('<', '\\u003c').replace('>', '\\u003e') if page_anchor_routing_map else '{}'
    # Top-right PDF + fullscreen block (position: absolute). No fullscreen icon when already in fullscreen layout.
    if is_fullscreen_layout:
        pdf_block = pdf_link_html if pdf_link_html else ''
    elif page_title and pdf_link_html:
        pdf_block = pdf_link_html[:-6] + ' <a href="?fullscreen=1" class="fullscreen-enter" aria-label="Fullscreen" title="Fullscreen">⛶</a></div>'
    elif pdf_link_html:
        pdf_block = pdf_link_html
    elif page_title:
        pdf_block = '<div class="pdf-links"><a href="?fullscreen=1" class="fullscreen-enter" aria-label="Fullscreen" title="Fullscreen">⛶</a></div>'
    else:
        pdf_block = ''
    top_right_html = pdf_block if (page_title or pdf_link_html) else ''
    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title_text}</title>
{head_meta_html}
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><circle cx='8' cy='8' r='8' fill='%2390c3c6'/></svg>">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <!-- Analytics loader (optional, generated at build time from config.yml) -->
    <script defer src="{assets_href}analytics.js"></script>
    <!-- MathJax v3: inline ($...$, \\(...\\)) and display (\\[...\\]); ignored in <code>/<pre> -->
    <script>
      window.MathJax = {{
        tex: {{
          inlineMath: [['$','$'], ['\\\\(','\\\\)']],
          displayMath: [['\\\\[','\\\\]']],
          processEscapes: true
        }},
        options: {{
          skipHtmlTags: ['script','noscript','style','textarea','pre','code']
        }}
      }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
    <style>
      /* layout: sticky left sidebar */
      :root {{
        --cm-body-bg: #fcfcfc;
        --cm-text: #222;
        --cm-muted: #6c757d;
        --cm-border: #e5e5e5;
        --bs-link-color: #79bb93; /* default link colour */
        --bs-link-hover-color: #647779; /* link hover colour */
        /* Showcase accents (aligned to existing site palette + requested highlights) */
        --cm-accent-primary: #79bb93;
        --cm-accent-secondary: #90c3c6;
        --cm-accent-ink: #1f1f36;
        --cm-accent-teal: #6dc4c8;
        --cm-accent-cyan: #76f7ff;
        --cm-accent-pink: #ff8fb8;
        --cm-accent-highlight: #f7ed73;
        --cm-accent-neon: #00ffaf;
      }}
      a {{
        color: #79bb93; /* default link colour */
      }}
      a:hover, a:focus {{
        color: #647779; /* hover/link focus colour */
      }}
      ul li::marker {{
        color: #79bb93; /* default bullet colour */
      }}
      body {{
        overflow-y: scroll;
        background: var(--cm-body-bg);
        color: var(--cm-text);
        font-size: 1.2rem; /* ~18px, slightly larger */
      }}
      .layout-container {{
        display: grid;
        grid-template-columns: 462px minmax(0, 980px) 390px; /* sidebar, fixed content width, wider rightbar */
        column-gap: 2.25rem;
        min-height: 100vh;
        background-color: #eee;
        transition: grid-template-columns 0.3s ease;
      }}
      /* Page-level layout override (YAML: layout: fullscreen / showcase) */
      body.layout-fullscreen .layout-container {{
        grid-template-columns: minmax(0, 1fr);
        column-gap: 0;
        background: var(--cm-body-bg);
      }}
      body.layout-fullscreen aside.sidebar,
      body.layout-fullscreen aside.rightbar,
      body.layout-fullscreen .breadcrumb-nav,
      body.layout-fullscreen #hamburgerBtn {{
        display: none !important;
      }}
      body.layout-fullscreen .content .edge-nav-box {{
        left: max(0px, calc(50% - min(700px, 50vw))) !important;
        right: max(0px, calc(50% - min(700px, 50vw))) !important;
        max-width: none !important;
      }}
      body.layout-fullscreen .content {{
        max-width: min(1400px, 100vw);
        margin: 0 auto 4rem auto;
        border: 0;
        border-radius: 0;
        box-shadow: none;
        --cm-content-pad-y: clamp(1rem, 3vw, 3rem);
        --cm-content-pad-x: clamp(1rem, 5vw, 4rem);
      }}
      .fullscreen-footer {{ display: none; }}
      body.layout-fullscreen .fullscreen-footer {{
        display: block;
        margin-top: 4rem;
        padding: 1.25rem 1.5rem;
        font-size: 0.8rem;
        color: #6b7280;
        border-top: 1px solid #e5e7eb;
        background: #fafafa;
      }}
      body.layout-fullscreen .fullscreen-footer a {{ color: #6b7280; text-decoration: none; }}
      body.layout-fullscreen .fullscreen-footer a:hover {{ color: #374151; }}
      body.layout-fullscreen .fullscreen-footer .sidebar-footer {{
        background: none; border: none; padding: 0; margin: 0;
      }}
      .fullscreen-nav {{ display: none; }}
      body.layout-fullscreen .fullscreen-nav {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .75rem;
        margin: 0 0 1rem 0;
        padding: .35rem .25rem;
        border-bottom: 1px solid #e7eaf1;
      }}
      body.layout-fullscreen .fullscreen-nav a {{
        color: #344054;
        font-size: .95rem;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      }}
      body.layout-fullscreen .fullscreen-nav a:hover {{
        color: #1d4ed8;
      }}
      /* Page title (filename) as full-bleed hero in fullscreen */
      body.layout-fullscreen .page-title-row {{
        width: 100vw;
        max-width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-right: calc(-50vw + 50%);
        background: linear-gradient(135deg, #f0f9f9 0%, #e8f6f7 50%, #f4faf9 100%);
        padding: clamp(1.5rem, 4vw, 3rem) clamp(1rem, 5vw, 4rem);
        text-align: center;
        justify-content: center !important;
      }}
      body.layout-fullscreen .page-title-row .page-title {{
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        font-size: clamp(2rem, 5vw, 4rem);
        font-weight: 800;
      }}
      /* Generic showcase components (can be used in any page, with/without layout: showcase) */
      .content .cm-hero {{
        background: linear-gradient(135deg, #f0f9f9 0%, #e8f6f7 50%, #f4faf9 100%);
        color: var(--cm-accent-ink);
        border: 1px solid rgba(144, 195, 198, 0.4);
        border-left: 8px solid var(--cm-accent-secondary);
        border-radius: 16px;
        padding: clamp(1.25rem, 3vw, 3rem);
        margin: .25rem 0 1.6rem 0;
        box-shadow: 0 8px 20px rgba(144, 195, 198, 0.12);
      }}
      .content .cm-hero h1 {{
        margin: 0 0 .45rem 0;
        color: var(--cm-accent-ink);
        font-size: clamp(2rem, 5.2vw, 4.4rem);
        line-height: 1.08;
        font-weight: 800;
      }}
      .content .cm-hero .cm-hero-accent {{
        color: var(--cm-accent-teal);
      }}
      .content .cm-hero p {{
        margin: 0;
        color: #475467;
        font-size: clamp(1rem, 1.5vw, 1.2rem);
      }}
      .content .cm-intro-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.25rem;
        margin: 1rem 0 2rem 0;
      }}
      .content .cm-panel {{
        background: linear-gradient(180deg, #ffffff 0%, #f7f9fd 100%);
        border: 1px solid #dfe6f3;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 8px 20px rgba(35, 64, 129, 0.06);
      }}
      .content .cm-steps {{
        display: grid;
        gap: 1rem;
        margin: 0.5rem 0 2rem 0;
      }}
      .content .cm-step {{
        display: grid;
        grid-template-columns: 56px 1fr;
        gap: 1rem;
        align-items: center;
        background: linear-gradient(180deg, #f8f9fc 0%, #f1f4fb 100%);
        border: 1px solid #e0e6f5;
        border-radius: 12px;
        padding: 1rem 1.1rem;
      }}
      .content .cm-step-num {{
        width: 48px;
        height: 48px;
        border-radius: 999px;
        background: #dfe4ff;
        color: #4338ca;
        font-weight: 700;
        font-size: 1.45rem;
        line-height: 48px;
        text-align: center;
      }}
      .content .cm-step h3 {{
        margin: 0 0 .25rem 0;
        font-size: 1.85rem;
        color: #101828;
      }}
      .content .cm-step p {{
        margin: 0 0 .6rem 0;
        color: #344054;
      }}
      .content .cm-win {{
        display: inline-block;
        background: #dcfce7;
        border: 1px solid #86efac;
        color: #166534;
        border-radius: 6px;
        padding: .28rem .55rem;
        font-weight: 600;
        font-size: .95rem;
      }}
      @media (max-width: 980px) {{
        .content .cm-intro-grid {{
          grid-template-columns: 1fr;
        }}
        .content .cm-step {{
          grid-template-columns: 1fr;
        }}
      }}
      .sidebar {{
        border-right: 1px solid var(--cm-border);
        position: sticky;
        top: 0;
        max-height: 100vh; /* constrain sidebar to viewport height */
        overflow: hidden; /* no scroll on sidebar itself */
        background: #fefefe;
        padding: 0 5px; /* remove vertical padding so footer remains in view */
        transition: overflow 0.3s ease;
      }}
      aside.sidebar > div {{
        display: flex;
        flex-direction: column;
        height: 100vh;
        padding: 2.5rem 1rem 0 1rem !important;
      }}
      aside.sidebar .sidebar-header {{
        padding .5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
      }}
      aside.sidebar .nav-fade {{
        flex: 1;
        overflow-y: auto; /* scrollable TOC */
        overflow-x: hidden;
        padding: 20px;
        opacity: .10; /* dimmer by default */
        transition: opacity .2s ease;
      }}
      aside.sidebar:hover .nav-fade {{
        opacity: .8; /* more visible on sidebar hover */
      }}
      aside.sidebar .nav-fade summary {{
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
        transition: opacity .35s ease;
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
        transition: transform .35s ease, opacity .35s ease;
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
        position: relative; /* needed for positioned inner elements */
        /* Use vars so overlays (logo) can align with text margins */
        --cm-content-pad-y: 3rem;
        --cm-content-pad-x: 4rem;
        padding: var(--cm-content-pad-y) var(--cm-content-pad-x); /* more padding */
        max-width: 980px;  /* a bit wider */
        font-family: Georgia, Cambria, \"Times New Roman\", Times, serif;
        line-height: 1.7;
        letter-spacing: .2px;
        background: white;
        box-shadow: 0 1px 2px rgba(0,0,0,.03);
        border: 1px solid var(--cm-border);
        border-radius: 8px;
        margin: 2.5rem 0 5rem 0; /* remove right margin so rightbar hugs content */
      }}
      /* Containing box for edge nav buttons to constrain positioning */
      .content .edge-nav-box {{
        position: fixed;
        top: 0;
        bottom: 0;
        left: 462px; /* left sidebar width */
        right: 280px; /* right sidebar width when present */
        max-width: calc(980px + 8rem); /* content max-width + padding */
        pointer-events: none; /* allow clicks through to content */
      }}
      .content .edge-nav-box a {{
        pointer-events: auto; /* restore clicks on nav buttons */
      }}
      @media (max-width: 1799.98px) {{
        .content .edge-nav-box {{
          right: 0; /* no right sidebar */
          max-width: none; /* content expands, no max-width */
        }}
      }}
      @media (max-width: 1199.98px) {{
        .content .edge-nav-box {{
          left: 0; /* no left sidebar */
        }}
        .content .edge-nav.prev {{ left: 8px !important; }}
        .content .edge-nav.next {{ right: 8px !important; }}
      }}
      .content img {{ max-width: 100%; height: auto; margin: 20px 0; }}
      .content h1, .content h2, .content h3, .content h4 {{
        margin-top: 2rem;
        font-weight: 600;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
      }}
      /* Larger H1 on Home (index.md) */
      .content.home h1:first-of-type {{
        font-size: 5rem;
      }}
      /* Floating PDF links inside content container */
      .content .pdf-links {{
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 5;
      }}
      .content .pdf-links a {{ margin-left: .5rem; white-space: nowrap; }}
      .content .fullscreen-enter {{ font-size: 1.1rem; color: #6c757d; text-decoration: none; margin-left: .35rem; }}
      .content .fullscreen-enter:hover {{ color: #1d4ed8; }}
      body.layout-fullscreen .fullscreen-enter {{ display: none !important; }}
      /* Tighter hierarchy for lower headings */
      .content h2 {{ font-size: 1.6rem; font-weight: 600; }}
      .content h3 {{ font-size: 1.25rem; font-weight: 600; }}
      .content h4 {{ font-size: 1.1rem; font-weight: 600; }}
      .content h5 {{ font-size: 1rem; font-weight: 600; }}
      .content h6 {{ font-size: .95rem; font-weight: 600; }}
      /* Heading self-link icon (revealed on hover) */
      .content .anchor-link {{
        visibility: hidden;
        text-decoration: none;
        color: #adb5bd;
        margin-left: .5rem;
        font-weight: normal;
      }}
      .content h1:hover .anchor-link, .content h2:hover .anchor-link,
      .content h3:hover .anchor-link, .content h4:hover .anchor-link,
      .content h5:hover .anchor-link, .content h6:hover .anchor-link {{
        visibility: visible;
      }}
      .content .anchor-link:hover {{ color: #6c757d; }}
      /* Hide anchor links in print/PDF */
      @media print {{
        .anchor-link {{
          display: none !important;
        }}
        /* Ensure multi-column blocks render as columns in PDF even if Bootstrap CSS isn't loaded (wider gutter: +50%) */
        .row {{
          display: flex;
          flex-wrap: wrap;
          page-break-inside: avoid;
          margin-left: -1.125rem;
          margin-right: -1.125rem;
        }}
        .row [class*="col-"] {{
          page-break-inside: avoid;
          padding-left: 1.125rem;
          padding-right: 1.125rem;
          flex: 0 0 auto;
        }}
        .row .col-md-1 {{ width: 8.33333333%; }}
        .row .col-md-2 {{ width: 16.66666667%; }}
        .row .col-md-3 {{ width: 25%; }}
        .row .col-md-4 {{ width: 33.33333333%; }}
        .row .col-md-5 {{ width: 41.66666667%; }}
        .row .col-md-6 {{ width: 50%; }}
        .row .col-md-7 {{ width: 58.33333333%; }}
        .row .col-md-8 {{ width: 66.66666667%; }}
        .row .col-md-9 {{ width: 75%; }}
        .row .col-md-10 {{ width: 83.33333333%; }}
        .row .col-md-11 {{ width: 91.66666667%; }}
        .row .col-md-12 {{ width: 100%; }}
      }}
      /* Prominent page title (sans, larger than in-page headings) */
      .content h1{{
        margin-bottom: 2rem;
      }}
      /* Prominent page title (sans, larger than in-page headings) */
      .page-title {{
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif;
        font-size: 2rem; /* ~32px: not smaller than default h1 */
        font-weight: 700;
        line-height: 1.25;
        letter-spacing: .04em; /* slightly wider tracking */
        font-variant-caps: small-caps; /* subtle distinction from h1/h2 */
        margin: 0 0 2.25rem 0;
        position: relative; /* For anchor link positioning */
      }}
      .page-title .anchor-link {{
        visibility: hidden;
        text-decoration: none;
        color: #adb5bd;
        margin-left: .5rem;
        font-weight: normal;
      }}
      .page-title:hover .anchor-link {{
        visibility: visible;
      }}
      .page-title .anchor-link:hover {{
        color: #6c757d;
      }}
      .page-title .page-subtitle {{
        display: block;
        font-size: 1.05rem;
        font-weight: 500;
        color: var(--cm-muted);
        margin-top: .35rem;
      }}
      .content p {{
        margin-bottom: 1.1rem;
      }}
      .content pre, .content code {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace;
      }}
      .content pre {{
        background: #f7f7f7;
        border: 1px solid var(--cm-border);
        border-radius: 6px;
        padding: .75rem 1rem;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        word-break: break-word;
      }}
      .content pre code {{
        white-space: inherit;
        overflow-wrap: inherit;
        word-break: inherit;
      }}
      .content hr {{
        border-top: 1px solid var(--cm-border);
        margin: 1.5rem 0;
      }}
      /* Blockquotes */
      .content blockquote {{
        border-left: 4px solid var(--cm-border);
        background: #f8f9fa;
        padding: .75rem 1rem;
        margin: 1.25rem 0;
        color: #495057;
      }}
      .content blockquote p:last-child {{
        margin-bottom: 0;
      }}
      .content blockquote cite {{
        display: block;
        margin-top: .5rem;
        color: var(--cm-muted);
        font-style: normal;
      }}
      /* Tables */
      .content table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: white;
      }}
      .content thead th {{
        background: #f1f3f5;
        color: #343a40;
        font-weight: 600;
        border-bottom: 2px solid var(--cm-border);
      }}
      .content th, .content td {{
        padding: .5rem .75rem;
        border: 1px solid var(--cm-border);
        vertical-align: top;
      }}
      .content tbody tr:nth-child(odd) {{
        background: #fcfcfc;
      }}
      .content caption {{
        caption-side: bottom;
        color: var(--cm-muted);
        font-size: .875rem;
        padding-top: .25rem;
      }}
      /* Alternative heading styles */
      .content h1.rounded, .content h1.rounded-left, .content h1.banner {{
        font-size: inherit; /* Use h1 base size */
      }}
      .content h2.rounded, .content h2.rounded-left, .content h2.banner {{
        font-size: inherit; /* Use h2 base size */
      }}
      .content h3.rounded, .content h3.rounded-left, .content h3.banner {{
        font-size: inherit; /* Use h3 base size */
      }}
      .content h1.rounded, .content h2.rounded, .content h3.rounded {{
        background: rgba(121,187,147,0.08);
        border-left: 4px solid #79bb93;
        padding: 0.75rem 1rem 0.75rem 1.5rem;
        border-radius: 6px;
        margin-left: -1rem;
        margin-right: -1rem;
      }}
      .content h1.rounded-left, .content h2.rounded-left, .content h3.rounded-left {{
        border-left: 4px solid #79bb93;
        padding-left: 1.5rem;
        background: rgba(121,187,147,0.12);
      }}
      .content h1.banner, .content h2.banner, .content h3.banner {{
        background: #79bb93;
        color: white;
        padding: 0.75rem 1rem 0.75rem 1.5rem;
        border-radius: 6px;
        margin-left: -1rem;
        margin-right: -1rem;
      }}
      /* Heading colour variants (Bootstrap-ish palette). Usage: add class ".rounded-info" etc to the heading */
      .content h1.rounded-info, .content h2.rounded-info, .content h3.rounded-info {{ background: rgba(13,202,240,0.10); border-left-color: #0dcaf0; }}
      .content h1.rounded-warning, .content h2.rounded-warning, .content h3.rounded-warning {{ background: rgba(255,193,7,0.14); border-left-color: #ffc107; }}
      .content h1.rounded-danger, .content h2.rounded-danger, .content h3.rounded-danger {{ background: rgba(220,53,69,0.10); border-left-color: #dc3545; }}
      .content h1.rounded-tip, .content h2.rounded-tip, .content h3.rounded-tip {{ background: rgba(25,135,84,0.10); border-left-color: #198754; }}
      .content h1.rounded-left-info, .content h2.rounded-left-info, .content h3.rounded-left-info {{ border-left-color: #0dcaf0; background: rgba(13,202,240,0.12); }}
      .content h1.rounded-left-warning, .content h2.rounded-left-warning, .content h3.rounded-left-warning {{ border-left-color: #ffc107; background: rgba(255,193,7,0.16); }}
      .content h1.rounded-left-danger, .content h2.rounded-left-danger, .content h3.rounded-left-danger {{ border-left-color: #dc3545; background: rgba(220,53,69,0.12); }}
      .content h1.rounded-left-tip, .content h2.rounded-left-tip, .content h3.rounded-left-tip {{ border-left-color: #198754; background: rgba(25,135,84,0.12); }}
      .content h1.banner-info, .content h2.banner-info, .content h3.banner-info {{ background: #0dcaf0; color: #083944; }}
      .content h1.banner-warning, .content h2.banner-warning, .content h3.banner-warning {{ background: #ffc107; color: #3b2c00; }}
      .content h1.banner-danger, .content h2.banner-danger, .content h3.banner-danger {{ background: #dc3545; color: #fff; }}
      .content h1.banner-tip, .content h2.banner-tip, .content h3.banner-tip {{ background: #198754; color: #fff; }}
      /* Showcase hero heading: use on H1 with class "hero" */
      .content h1.hero {{
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
        background: #f0f9f9;
        color: var(--cm-accent-ink);
        border: 1px solid rgba(144, 195, 198, 0.4);
        border-left: 8px solid var(--cm-accent-secondary);
        border-radius: 16px;
        padding: clamp(1.25rem, 3vw, 3rem);
        margin: .25rem 0 1rem 0;
        box-shadow: 0 6px 16px rgba(144, 195, 198, 0.12);
        font-size: clamp(2rem, 5.2vw, 4.4rem);
        line-height: 1.08;
        font-weight: 800;
      }}
      .content h1.hero + p {{
        margin: 0 0 1.5rem 0;
        color: #475467;
        font-size: 1.08rem;
      }}
      /* Paper styling (YAML tag: paper) — slightly more academic, not fusty */
      .content .paper {{ font-size: 1.12rem; line-height: 1.75; }}
      .content .paper h1 {{ font-size: 1.55rem; }}
      .content .paper h3 {{ margin-top: 1.25rem; margin-bottom: 0.75rem; }} /* tighter headings in paper mode */
      .content .paper a {{ text-decoration: underline; text-underline-offset: 2px; }}
      .content .paper .callout, .content .paper .callout-note {{
        border-left: none;
        border: 1px solid #90c3c6;
        background: rgba(144,195,198,0.08);
      }}
      .content .paper h1.banner-info, .content .paper h2.banner-info, .content .paper h3.banner-info {{
        background: transparent;
        color: #2c3e50;
        border-left: 4px solid #90c3c6;
        padding: 0.55rem 0.9rem 0.55rem 1.2rem;
        border-radius: 4px;
        margin-left: -1rem;
        margin-right: -1rem;
      }}
      .content .paper h1.rounded-info, .content .paper h2.rounded-info, .content .paper h3.rounded-info {{
        background: rgba(144,195,198,0.10);
        border-left-color: #90c3c6;
      }}
      /* Callout styles */
      .content .callout {{
        border-left: 4px solid #6c757d;
        background: #f8f9fa;
        padding: 1rem 1.25rem;
        margin: 1.5rem 0;
        border-radius: 4px;
      }}
      .content .callout p:last-child,
      .content .callout ul:last-child,
      .content .callout ol:last-child {{
        margin-bottom: 0;
      }}
      .content .callout ul,
      .content .callout ol {{
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
      }}
      .content .callout-info {{
        border-left-color: #0dcaf0;
        background: #e7f5f8;
      }}
      .content .callout-warning {{
        border-left-color: #ffc107;
        background: #fff8e1;
      }}
      .content .callout-tip {{
        border-left-color: #198754;
        background: #e8f5e9;
      }}
      .content .callout-note {{
        border-left-color: #6c757d;
        background: #f8f9fa;
      }}
      /* Hero callout: full-bleed in showcase mode */
      .content .callout-hero {{
        background: linear-gradient(135deg, #f0f9f9 0%, #e8f6f7 50%, #f4faf9 100%);
        border: none;
        border-radius: 0;
        padding: clamp(2rem, 5vw, 4rem) clamp(1.5rem, 5vw, 4rem);
        margin: 0;
        box-shadow: none;
      }}
      .content .callout-hero h1 {{
        margin: 0 0 .5rem 0;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        font-size: clamp(2rem, 5vw, 4rem);
        font-weight: 800;
        color: var(--cm-accent-ink);
      }}
      /* Showcase-style generic callouts for panel/step blocks */
      .content .callout-panel {{
        border-left-color: var(--cm-accent-secondary);
        background: linear-gradient(180deg, #ffffff 0%, rgba(144, 195, 198, 0.10) 100%);
        border: 1px solid rgba(144, 195, 198, 0.45);
        border-left-width: 4px;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.08);
      }}
      .content .callout-step {{
        border-left-color: var(--cm-accent-primary);
        background: linear-gradient(180deg, #f8f9fc 0%, rgba(121, 187, 147, 0.12) 100%);
        border: 1px solid rgba(121, 187, 147, 0.35);
        border-left-width: 4px;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.08);
      }}
      .content .callout-step h1,
      .content .callout-step h2,
      .content .callout-step h3 {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
      }}
      .content .callout-step .step-content {{
        flex: 1;
        min-width: 0;
      }}
      .content .callout-step h1 strong,
      .content .callout-step h2 strong,
      .content .callout-step h3 strong {{
        font-weight: 700;
      }}
      .content .callout-step .step-num {{
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 3.5rem;
        height: 3.5rem;
        font-size: 1.5rem;
        border-radius: 50%;
        background: #E8E6F8;
        color: #5D3FD3;
        font-weight: 700;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      }}
      /* Popular web elements: card, stat, testimonial, cta, alert */
      .content .callout-card {{
        border-left-color: var(--cm-accent-secondary);
        background: #fff;
        border: 1px solid rgba(144, 195, 198, 0.4);
        border-left-width: 4px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
      }}
      .content .callout-stat {{
        border-left: none;
        border: 1px solid rgba(144, 195, 198, 0.35);
        background: rgba(144, 195, 198, 0.08);
        border-radius: 10px;
        text-align: center;
        padding: 1.25rem;
      }}
      .content .callout-stat p:first-child {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--cm-accent-ink);
        margin: 0 0 0.25rem 0;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      }}
      .content .callout-testimonial {{
        border-left: 4px solid var(--cm-accent-primary);
        background: #fafcf9;
        font-style: italic;
        font-size: 1.2rem;
        line-height: 1.6;
        padding: 1.25rem 1.5rem;
      }}
      .content .callout-testimonial p:last-child {{
        font-style: normal;
        font-size: 0.95rem;
        color: var(--cm-muted);
        margin-top: 0.5rem;
      }}
      .content .callout-cta {{
        border: 2px solid var(--cm-accent-primary);
        background: rgba(121, 187, 147, 0.12);
        border-radius: 10px;
        text-align: center;
        padding: 1.5rem;
      }}
      .content .callout-cta a {{
        font-weight: 600;
      }}
      .content .callout-alert {{
        border-left: 4px solid #ffc107;
        background: #fffbf0;
        border-radius: 6px;
      }}
      /* Callout layout/style modifiers (can be combined) */
      .content .callout-narrow {{
        max-width: 66%;
      }}
      .content .callout-right {{
        margin-left: auto;
        display: block;
      }}
      .content .callout-center {{
        margin-left: auto;
        margin-right: auto;
      }}
      .content .callout-heavy {{
        border-left-width: 6px !important;
        border-radius: 0;
      }}
      .content .callout-left-border {{
        border-top: none;
        border-right: none;
        border-bottom: none;
      }}
      /* Rounded style - like a box, no left border, rounded border */
      .content .callout-rounded {{
        border-left: none;
        border: 2px solid var(--cm-border);
        border-radius: 6px;
      }}
      /* Inverted style - override background but preserve border colors */
      .content .callout-inverted {{
        background: #79bb93 !important;
        color: #ffffff;
      }}
      /* Ensure type-specific border colors work with inverted */
      .content .callout-info.callout-inverted {{
        border-left-color: #0dcaf0 !important;
      }}
      .content .callout-warning.callout-inverted {{
        border-left-color: #ffc107 !important;
      }}
      .content .callout-tip.callout-inverted {{
        border-left-color: #198754 !important;
      }}
      .content .callout-note.callout-inverted {{
        border-left-color: #6c757d !important;
      }}
      /* Highlight style */
      mark {{
        background: var(--cm-accent-highlight);
        color: var(--cm-accent-ink);
        padding: 0.1em 0.2em;
        border-radius: 2px;
      }}
      a {{
        text-decoration: none;
      }}
      a:hover {{ text-decoration: underline; }}
      aside.sidebar .site-title {{
          flex-shrink: 0;
          background-color: #f3f8f9;
          border-radius: 6px;
          width: 100%;
          margin-bottom: 1rem;
          text-align: left;
          padding: 1rem;
      }}
      aside.sidebar form {{
          flex-shrink: 0;
      }}
      aside.sidebar .site-title {{
        display: block;
        color: var(--cm-text);
        font-size: larger;
        cursor: pointer; /* make whole box feel clickable */
        text-decoration: none;
        /* Align subtitle under the title text (not under the emoji/icon). */
        display: grid;
        grid-template-columns: max-content 1fr;
        column-gap: .35rem;
      }}
      aside.sidebar .site-title:hover {{
        font-size: larger;
        color: var(--cm-text);
        text-decoration: none;
      }}
      /* Smaller subtitle (e.g., Work in progress) under site title */
      aside.sidebar .site-title .site-title-sub {{
        grid-column: 2;
        font-size: .9rem;
        font-style: italic;
        color: var(--cm-muted);
        margin-top: .25rem;
      }}
      aside.sidebar .site-title .site-title-icon {{
        grid-column: 1;
      }}
      aside.sidebar .site-title .site-title-text {{
        grid-column: 2;
      }}
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
        content: \"Relevant page: \";
        font-size: 0.75rem;
        color: var(--cm-muted);
        opacity: 0.7;
        margin-right: 0.5rem;
      }}
      /* Video embeds - responsive container */
      .video-embed {{
        position: relative;
        padding-bottom: 56.25%; /* 16:9 aspect ratio */
        height: 0;
        overflow: hidden;
        max-width: 100%;
      }}
      .video-embed iframe {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
      }}
      .video-embed video {{
        width: 100%;
        max-width: 100%;
        height: auto;
        display: block;
      }}
      /* Active nav link */
      aside.sidebar .nav-link.active {{
        background: #e7effa;
        border-radius: .25rem;
        font-weight: 600;
      }}
      /* Sidebar footer at bottom of flex container */
      aside.sidebar .sidebar-footer {{
        flex-shrink: 0;
        background: #fafafa;
        padding: 1rem;
        border-top: 1px solid var(--cm-border);
        margin-top: 1rem;
        background-color: #f3f8f9;
      }}
      /* Hamburger button (hidden by default) */
      .hamburger {{
        display: none;
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 1100;
      }}
      /* Desktop ToC toggle: only on wide screens */
      .toc-toggle {{
        display: none;
      }}
      @media (min-width: 1200px) {{
        .toc-toggle {{
          display: inline-flex;
          align-items: center;
          gap: .4rem;
          width: 100%;
        }}
        aside.sidebar .nav-fade.toc-collapsed {{
          display: none;
        }}
      }}
      /* Desktop sidebar toggle button (hidden by default; shown on wide screens) */
      .desktop-toggle {{
        display: none;
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 1100;
      }}
      @media (min-width: 1200px) {{
        .desktop-toggle {{
          display: inline-flex;
          align-items: center;
          gap: .4rem;
        }}
        .hamburger {{
          display: none; /* hamburger only for <1200px */
        }}
      }}
      /* Reference list */
      .content .references {{
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--cm-border);
      }}
      .content .references h2 {{
        font-size: 1.3rem;
        margin-bottom: 1rem;
      }}
      .content .references .reference {{
        margin-left: 2em;
        text-indent: -2em;
        margin-bottom: 0.8rem;
        line-height: 1.5;
      }}
      /* Chapter start styling */
      .content.chapter-start {{
        background: linear-gradient(to bottom, #f8feff 0%, var(--cm-body-bg) 300px);
      }}
      .content.chapter-start .page-title {{
        font-size: 2.5rem;
        margin-bottom: 2.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 3px solid #90c3c6;
        font-weight: 600;
      }}
      .content.chapter-start > p:first-of-type {{
        font-size: 1.35rem;
        line-height: 1.8;
        color: #555;
        margin-bottom: 2.5rem;
        margin-top: 2rem;
        padding: 1.5rem;
        background: #f0f8f9;
        border-left: 4px solid #90c3c6;
        border-radius: 4px;
      }}
      .content.chapter-start a:not(.edge-nav) {{
        position: relative;
        z-index: 1;
      }}
      /* Ensure edge nav is always on top and positioned correctly */
      .content .edge-nav-box {{
        z-index: 10 !important;
      }}
      .content .edge-nav {{
        z-index: 11 !important;
      }}
      .content .edge-nav.prev {{
        left: -52px !important;
      }}
      .content .edge-nav.next {{
        right: -52px !important;
      }}
      /* Chapter page links styling */
      .chapter-page-link {{
        display: inline-block;
        transition: all 0.2s ease;
      }}
      .chapter-page-link:hover {{
        transform: translateX(4px);
        color: #0d6efd !important;
      }}
      .chapter-page-link:hover i {{
        color: #0d6efd !important;
      }}
      /* Right ToC */
      .rightbar {{
        position: sticky;
        top: 2.5rem; /* align with main content's top margin */
        align-self: start; /* start at top of grid row */
        max-height: calc(100vh - 2.5rem);
        overflow: auto;
        margin: 2.5rem 0 5rem 0; /* match main content vertical margins */
        padding: 1.5rem; /* consistent padding for TOC */
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
      @media (max-width: 1199.98px) {{
        .rightbar .toc {{
          opacity: 1 !important;
        }}
      }}
      .rightbar .toc a.active {{
        font-weight: 600;
        color: #0d6efd;
        opacity: 1;
      }}
      /* Edge previous/next chevrons (inside content) */
      .edge-nav {{
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 44px;
        height: 44px;
        border-radius: 999px;
        background: #fff;
        border: 1px solid #d5d5d5;
        color: #495057;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        opacity: .8;
        box-shadow: 0 2px 6px rgba(0,0,0,.08);
        transition: opacity .15s ease, background .15s ease, box-shadow .15s ease;
        z-index: 5;
      }}
      .edge-nav:hover {{
        opacity: 1;
        box-shadow: 0 3px 10px rgba(0,0,0,.12);
      }}
      .edge-nav.prev {{ left: -52px; }}  /* outside content, in left gutter */
      .edge-nav.next {{ right: -52px; }}  /* outside content, in right gutter */

      /* Breadcrumb navigation */
      .breadcrumb-nav {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: var(--cm-muted);
        margin-bottom: 1rem;
        padding: 0.5rem 0;
        flex-wrap: wrap;
      }}
      .breadcrumb-nav a {{
        color: #555;
        text-decoration: none;
      }}
      .breadcrumb-nav a:hover {{
        color: var(--cm-text);
        text-decoration: underline;
      }}
      .breadcrumb-item {{
        position: relative;
        display: inline-flex;
        align-items: center;
      }}
      .breadcrumb-item .bc-dropdown {{
        position: relative;
        display: inline-block;
      }}
      .breadcrumb-item .bc-current-link {{
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        transition: background 0.15s ease;
        text-decoration: none;
      }}
      .breadcrumb-item .bc-current-link:hover {{
        background: #f0f0f0;
        text-decoration: none;
      }}
      .breadcrumb-item .bc-label {{
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        user-select: none;
      }}
      .breadcrumb-item .bc-label:hover {{
        background: #f0f0f0;
      }}
      .breadcrumb-item .bc-chevron {{
        font-size: 0.7em;
        opacity: 0.6;
        transition: transform 0.15s ease;
      }}
      .breadcrumb-item .bc-dropdown.open .bc-chevron {{
        transform: rotate(180deg);
      }}
      .breadcrumb-item .bc-menu {{
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        background: white;
        border: 1px solid var(--cm-border);
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,.1);
        min-width: 675px;
        max-width: 900px;
        max-height: 800px;
        overflow-y: auto;
        z-index: 1000;
        margin-top: 0.25rem;
      }}
      .breadcrumb-item .bc-dropdown.open .bc-menu {{
        display: block;
      }}
      .breadcrumb-item .bc-menu a {{
        display: block;
        padding: 0.5rem 0.75rem;
        color: var(--cm-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }}
      .breadcrumb-item .bc-menu a:hover {{
        background: #f5f5f5;
        text-decoration: none;
      }}
      .breadcrumb-item .bc-menu a.current {{
        background: #e7effa;
        font-weight: 600;
      }}
      .breadcrumb-item .bc-menu .bc-heading {{
        padding: 0.35rem 0.75rem 0.25rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--cm-muted);
        text-transform: uppercase;
        letter-spacing: .06em;
      }}
      /* Tags dropdown (nested lists) */
      .breadcrumb-item .bc-menu-tags .bc-tag {{
        padding: 0.4rem 0.75rem 0.2rem;
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--cm-muted);
        border-top: 1px solid #eee;
        /* keep tag labels in normal case (e.g. "Papers and Drafts") */
      }}
      .breadcrumb-item .bc-menu-tags .bc-tag-pages {{
        list-style: none;
        margin: 0;
        padding: 0 0 0.15rem 0;
      }}
      .breadcrumb-item .bc-menu-tags .bc-tag-pages a {{
        padding-left: 1.25rem;
      }}
      .breadcrumb-separator {{
        opacity: 0.4;
        margin: 0 0.25rem;
      }}

      /* < 1800px: hide right sidebar, let content expand */
      @media (max-width: 1799.98px) {{
        .layout-container {{
          grid-template-columns: 462px minmax(0, 1fr);
        }}
        .rightbar {{
          display: none !important;
        }}
        .content {{
          max-width: none;
        }}
      }}

      /* < 1200px: hide left sidebar behind hamburger; single-column layout */
      @media (max-width: 1199.98px) {{
        .hamburger {{
          display: inline-flex;
          align-items: center;
          gap: .4rem;
        }}
        .layout-container {{
          grid-template-columns: 1fr;
          column-gap: 0;
        }}
        aside.sidebar {{
          position: fixed;
          top: 0;
          left: 0;
          height: 100vh;
          width: 86vw;
          max-width: 360px;
          transform: translateX(-100%);
          transition: transform .2s ease;
          z-index: 1040;
          box-shadow: 0 0 16px rgba(0,0,0,.12);
        }}
        body.sidebar-open aside.sidebar {{
          transform: translateX(0);
        }}
        .content {{
          margin: 1rem 0 4rem 0;
          --cm-content-pad-y: 1.25rem;
          --cm-content-pad-x: 1rem;
          padding: var(--cm-content-pad-y) var(--cm-content-pad-x);
        }}
      }}
    </style>
  </head>
  <body{body_attr} data-fullscreen-default="{str(is_fullscreen_layout).lower()}">
    <button id=\"hamburgerBtn\" class=\"btn btn-outline-secondary btn-sm hamburger\" type=\"button\" aria-label=\"Toggle navigation\">☰ Menu</button>
    <div class=\"layout-container\">
      <aside class="sidebar"></aside>
      <main class=\"content{" chapter-start" if is_chapter_start else ""}{" home" if not page_title else ""}\">
        <div class=\"edge-nav-box\">{(
          f'<a href="{html.escape(prev_href)}" class="edge-nav prev" aria-label="Previous{": " + html.escape(prev_title) if prev_title else ""}">‹</a>'
        ) if prev_href else ''}{(
          f'<a href="{html.escape(next_href)}" class="edge-nav next" aria-label="Next{": " + html.escape(next_title) if next_title else ""}">›</a>'
        ) if next_href else ''}</div>
        {(f'<nav class="fullscreen-nav"><a href="?fullscreen=0" id="exitFullscreenBtn" class="fullscreen-exit">⊟ Exit fullscreen</a></nav>' if page_title else '')}
        {(breadcrumb_html or '')}
        {top_right_html}
        {(
          f'<div class="page-title-row d-flex justify-content-between align-items-center">'
          f'<div class="page-title" id="{html.escape(page_anchor) if page_anchor else ""}">'
          f'{icon_prefix_html}{html.escape(page_title)}'
          # If the filename includes a ((shortcut)) anchor, link to the root short route (/{shortcut})
          f'{(f"<a aria-label='Permalink' class='anchor-link' href='/{html.escape(page_anchor)}'>#</a>" if page_anchor else "")}'
          f'{subtitle_html}'
          f'</div>'
          f'</div><hr />'
        ) if page_title else ('<hr />' if pdf_link_html else '')}
        {content_html}
        {(f'<footer class="fullscreen-footer">{sidebar_footer_html}</footer>' if sidebar_footer_html else '')}
      </main>
      {(
        '<aside class="rightbar">'
        + (f'<h2>On this page</h2><div class="toc">{toc_html}</div>' if toc_html else '')
        + (f'<hr /><h2>Links</h2><div class="toc">{links_html}</div>' if links_html else '')
        + (f'<hr /><h2>Backlinks</h2><div class="toc">{backlinks_html}</div>' if backlinks_html else '')
        + '</aside>'
      ) if (toc_html or links_html or backlinks_html) else ''}
    </div>
    <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js\" integrity=\"sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz\" crossorigin=\"anonymous\"></script>
    <script src=\"{assets_href}sidebar.js\"></script>
    <script>
      // Hamburger toggle for small screens
      (function(){{
        var btn = document.getElementById('hamburgerBtn');
        if (btn) {{
          btn.addEventListener('click', function(){{
            document.body.classList.toggle('sidebar-open');
          }});
        }}
      }})();

      // Fullscreen mode: ?fullscreen=1 adds layout-fullscreen, ?fullscreen=0 removes it
      (function(){{
        var params = new URLSearchParams(window.location.search);
        var fs = params.get('fullscreen');
        if (fs === '0') document.body.classList.remove('layout-fullscreen');
        else if (fs === '1') document.body.classList.add('layout-fullscreen');
      }})();

      // Clamp anchor scrolling so near-top anchors don't shift page up awkwardly
      (function(){{
        function scrollToClamped(targetId, smooth) {{
          if (!targetId) return;
          var el = document.getElementById(targetId);
          if (!el) return;
          var targetTop = (el.getBoundingClientRect().top || 0) + window.scrollY;
          var desiredTop = Math.max(0, targetTop - 100); // keep ~100px padding, clamp at 0
          if (Math.abs(window.scrollY - desiredTop) > 1) {{
            try {{
              window.scrollTo({{ top: desiredTop, behavior: smooth ? 'smooth' : 'auto' }});
            }} catch(e) {{
              window.scrollTo(0, desiredTop);
            }}
          }}
        }}
        // On load with a hash, adjust after browser's default jump
        window.addEventListener('load', function(){{
          if (window.location.hash && window.location.hash.length > 1) {{
            setTimeout(function() {{
              scrollToClamped(window.location.hash.slice(1), false);
            }}, 0);
          }}
        }});
        // Intercept same-document anchor clicks to apply clamped scrolling
        document.addEventListener('click', function(e){{
          var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
          if (!a) return;
          var href = a.getAttribute('href');
          if (!href || href === '#') return;
          var id = href.slice(1);
          var target = document.getElementById(id);
          if (!target) return; // let browser handle if element not found
          e.preventDefault();
          // Update URL hash without reloading
          try {{ history.replaceState(null, '', '#' + id); }} catch(e) {{}}
          scrollToClamped(id, true);
        }}, true);
      }})();

      // Root-level hash routing for page anchors (e.g., domain.com/#new-features)
      (function(){{
        var pageAnchorMap = {page_anchor_routing_json};
        if (pageAnchorMap && Object.keys(pageAnchorMap).length > 0) {{
          window.addEventListener('load', function(){{
            var hash = window.location.hash;
            if (hash && hash.length > 1) {{
              var anchorId = hash.slice(1).toLowerCase();
              var targetUrl = pageAnchorMap[anchorId];
              if (targetUrl) {{
                window.location.replace(targetUrl);
              }}
            }}
          }});
        }}
      }})();

      // Keyboard navigation: ArrowLeft/ArrowRight go to prev/next page
      (function(){{
        document.addEventListener('keydown', function(e){{
          // Ignore when typing or with modifiers
          if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) return;
          var ae = document.activeElement;
          if (ae && (ae.tagName === 'INPUT' || ae.tagName === 'TEXTAREA' || ae.tagName === 'SELECT' || ae.isContentEditable)) return;
          var key = e.key || e.code;
          if (key === 'ArrowLeft' || key === 'Left') {{
            var prev = document.querySelector('.edge-nav.prev');
            if (prev && prev.getAttribute('href')) {{
              e.preventDefault();
              window.location.href = prev.getAttribute('href');
            }}
          }} else if (key === 'ArrowRight' || key === 'Right') {{
            var next = document.querySelector('.edge-nav.next');
            if (next && next.getAttribute('href')) {{
              e.preventDefault();
              window.location.href = next.getAttribute('href');
            }}
          }}
        }});
      }})();

      // Restore sidebar scroll position after navigation (for smoother feel)
      (function(){{
        try {{
          var saved = sessionStorage.getItem('sidebarScroll');
          if (saved !== null) {{
            var box = document.querySelector('aside.sidebar .nav-fade');
            if (box) {{
              box.scrollTop = parseInt(saved, 10) || 0;
            }}
            sessionStorage.removeItem('sidebarScroll');
          }}
        }} catch(e) {{}}
      }})();

      // Desktop ToC toggle (wide screens): hide/show only the ToC list; default hidden on desktop
      (function(){{
        var btn = document.getElementById('tocToggle');
        var list = document.getElementById('tocList');
        if (!list) return;
        function setButtonState(collapsed) {{
          if (!btn) return;
          btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
          btn.textContent = collapsed ? 'Show Contents' : 'Hide Contents';
        }}
        function applyInitial() {{
          try {{
            var isDesktop = window.matchMedia('(min-width: 1200px)').matches;
            if (!isDesktop) {{
              list.classList.remove('toc-collapsed');
              setButtonState(false);
              return;
            }}
            var persisted = null;
            try {{ persisted = localStorage.getItem('tocCollapsed'); }} catch(e) {{}}
            var collapsed = true; // default hidden on desktop
            if (persisted === '0') collapsed = false;
            if (persisted === '1') collapsed = true;
            if (collapsed) list.classList.add('toc-collapsed'); else list.classList.remove('toc-collapsed');
            setButtonState(collapsed);
            // Flash ToC after navigation when desired
            var flash = null;
            try {{ flash = sessionStorage.getItem('flashToc'); }} catch(e) {{}}
            if (flash === '1') {{
              try {{ sessionStorage.removeItem('flashToc'); }} catch(e) {{}}
              if (list.classList.contains('toc-collapsed')) {{
                // Briefly show ToC, then restore collapsed state
                list.classList.remove('toc-collapsed');
                setButtonState(false);
                setTimeout(function() {{
                  list.classList.add('toc-collapsed');
                  setButtonState(true);
                }}, 1200);
              }}
            }}
            // First visit to Home: open ToC then smoothly roll it up (desktop only)
            try {{
              var isHome = !!document.querySelector('main.content.home');
              var alreadyAnimated = (localStorage.getItem('initialHomeTocAnimated') === '1');
              var hasPref = (persisted === '0' || persisted === '1');
              if (isHome && !alreadyAnimated && !hasPref) {{
                // Show it
                list.classList.remove('toc-collapsed');
                setButtonState(false);
                // After short delay, animate collapse
                setTimeout(function() {{
                  var full = list.scrollHeight;
                  list.style.overflow = 'hidden';
                  list.style.maxHeight = full + 'px';
                  list.style.opacity = '1';
                  void list.offsetHeight; // reflow
                  list.style.transition = 'max-height 450ms ease, opacity 450ms ease';
                  list.style.maxHeight = '0px';
                  list.style.opacity = '0';
                  setTimeout(function() {{
                    list.style.transition = '';
                    list.style.maxHeight = '';
                    list.style.opacity = '';
                    list.style.overflow = '';
                    list.classList.add('toc-collapsed');
                    setButtonState(true);
                    try {{ localStorage.setItem('tocCollapsed', '1'); }} catch(e) {{}}
                    try {{ localStorage.setItem('initialHomeTocAnimated', '1'); }} catch(e) {{}}
                  }}, 480);
                }}, 900);
              }}
            }} catch(e) {{}}
          }} catch(e) {{}}
        }}
        if (btn) {{
          btn.addEventListener('click', function(){{
            var collapsed = list.classList.toggle('toc-collapsed');
            setButtonState(collapsed);
            try {{ localStorage.setItem('tocCollapsed', collapsed ? '1' : '0'); }} catch(e) {{}}
          }});
        }}
        applyInitial();
        window.addEventListener('resize', applyInitial);
      }})();

      // Breadcrumb dropdown toggle (click chevron or label to open)
      document.querySelectorAll('.bc-chevron, .bc-label').forEach(function(trigger) {{
        trigger.addEventListener('click', function(e) {{
          e.preventDefault();
          e.stopPropagation();
          var dropdown = trigger.closest('.bc-dropdown');
          if (!dropdown) return;
          var isOpen = dropdown.classList.contains('open');
          // Close all other dropdowns
          document.querySelectorAll('.bc-dropdown.open').forEach(function(d) {{
            d.classList.remove('open');
          }});
          // Toggle current
          if (!isOpen) {{
            dropdown.classList.add('open');
          }}
        }});
      }});
      // Close dropdowns when clicking outside
      document.addEventListener('click', function(e) {{
        if (!e.target.closest('.bc-dropdown')) {{
          document.querySelectorAll('.bc-dropdown.open').forEach(function(d) {{
            d.classList.remove('open');
          }});
        }}
      }});

      // Scroll active sidebar link into view if it sits outside the visible nav area
      (function() {{
        var activeLink = document.querySelector('aside.sidebar .nav-link.active');
        if (!activeLink) return;
        var scrollBox = document.querySelector('aside.sidebar .nav-fade');
        if (!scrollBox) return;
        var linkRect = activeLink.getBoundingClientRect();
        var boxRect = scrollBox.getBoundingClientRect();
        if (linkRect.bottom > boxRect.bottom || linkRect.top < boxRect.top) {{
          scrollBox.scrollTop += linkRect.top - boxRect.top - 40;
        }}
      }})();

      // Highlight current section in rightbar TOC
      (function() {{
        var rightbar = document.querySelector('.rightbar .toc');
        if (!rightbar) return;
        
        var tocLinks = rightbar.querySelectorAll('a');
        if (tocLinks.length === 0) return;
        
        function updateActiveSection() {{
          var fromTop = window.scrollY + 100;
          var current = null;
          
          tocLinks.forEach(function(link) {{
            var href = link.getAttribute('href');
            if (!href || !href.startsWith('#')) return;
            var section = document.querySelector(href);
            if (section) {{
              if (section.offsetTop <= fromTop) {{
                current = link;
              }}
            }}
          }});
          
          tocLinks.forEach(function(link) {{
            link.classList.remove('active');
          }});
          
          if (current) {{
            current.classList.add('active');
          }}
        }}
        
        window.addEventListener('scroll', updateActiveSection);
        window.addEventListener('resize', updateActiveSection);
        updateActiveSection();
      }})();
    </script>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true }});
    </script>
  </body>
 </html>
"""


# -- search assets --
def write_search_assets(input_root: Path, output_root: Path, title_map: Dict[Path, str]) -> None:
    # Build a minimal index: [{title, path, text}]
    # Deduplicate records so "single hit" auto-open is reliable.
    records: List[Dict[str, str]] = []
    seen: Set[Tuple[str, str]] = set()

    def add_record(rec: Dict[str, str]) -> None:
        key = (rec.get("title", ""), rec.get("path", ""))
        if not key[0] or not key[1]:
            return
        if key in seen:
            return
        seen.add(key)
        records.append(rec)

    for md_path, title in title_map.items():
        rel_out = relative_output_html(input_root, output_root, md_path)
        # Use path relative to search.html (which is in output_root)
        href = os.path.relpath(rel_out, start=output_root).replace(os.sep, "/")
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception:
            text = ""
        text = strip_yaml_front_matter(text)

        # Index page-level shortcuts from filename "((shortcut))" so searching "#map-panel" works
        # even when it's not a heading id.
        try:
            page_id = extract_page_anchor_from_stem(md_path.stem)
        except Exception:
            page_id = None
        if page_id:
            add_record(
                {
                    "title": f"{title} #{page_id}",
                    # Short-route stub lives at /{id}/index.html
                    "path": f"{page_id}/index.html",
                    "text": f"Shortcut: #{page_id}",
                }
            )

        # Index anchor IDs so searching "#file-menu" finds the exact section.
        #
        # Sources:
        # - explicit anchors in markdown (## Title {#id} / {id}) via normalize_heading_anchors()
        # - explicit HTML ids written in markdown (e.g. <div id="id">)
        # - implicit heading ids generated by the markdown->HTML converter (read from output HTML)
        ids_in_page: Set[str] = set()
        scan_text = text
        try:
            # Avoid indexing ids that appear only in examples.
            scan_text = re.sub(r"```[\s\S]*?```", " ", scan_text)
            scan_text = re.sub(r"`[^`]*`", " ", scan_text)
        except Exception:
            pass
        try:
            _, ids_in_page = normalize_heading_anchors(scan_text)
        except Exception:
            ids_in_page = set()
        try:
            html_id_re = re.compile(r"\bid\s*=\s*['\"]([A-Za-z][A-Za-z0-9_-]*)['\"]", flags=re.IGNORECASE)
            ids_in_page |= {m.group(1).lower() for m in html_id_re.finditer(scan_text)}
        except Exception:
            pass
        # Also index ids actually present on rendered headings (<h1..h6 id="...">),
        # which includes implicit ids generated from headings like "## File menu".
        try:
            rendered_html = rel_out.read_text(encoding="utf-8", errors="ignore") if rel_out.exists() else ""
            if rendered_html:
                heading_id_re = re.compile(
                    r"<h[1-6]\b[^>]*\bid\s*=\s*['\"]([A-Za-z][A-Za-z0-9_-]*)['\"]",
                    flags=re.IGNORECASE,
                )
                ids_in_page |= {m.group(1).lower() for m in heading_id_re.finditer(rendered_html)}
        except Exception:
            pass
        for ident in sorted(ids_in_page):
            add_record(
                {
                    "title": f"{title} #{ident}",
                    "path": f"{href}#{ident}",
                    "text": f"Anchor: #{ident}",
                }
            )

        # crude strip of markdown for search preview
        plain = re.sub(r"```[\s\S]*?```", " ", text)
        plain = re.sub(r"`[^`]*`", " ", plain)
        plain = re.sub(r"\[\[(.*?)\]\]", r"\1", plain)
        plain = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", plain)
        plain = re.sub(r"[#*_>\-]+", " ", plain)
        plain = re.sub(r"\s+", " ", plain).strip()
        add_record({"title": title, "path": href, "text": plain})

    (output_root / "assets").mkdir(parents=True, exist_ok=True)
    # Write search index; if the assets path is problematic on Windows (long path, provider),
    # fall back to a shorter root-level path. The search page uses the inline index anyway.
    try:
        (output_root / "assets" / "search_index.json").write_text(json.dumps(records), encoding="utf-8")
    except Exception:
        try:
            (output_root / "search_index.json").write_text(json.dumps(records), encoding="utf-8")
        except Exception:
            # Ignore if we can't persist the extra copy
            pass

    # Simple search page embedding the index inline (works over file:// without fetch)
    search_html = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Search</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><circle cx='8' cy='8' r='8' fill='%2390c3c6'/></svg>">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Analytics loader (optional, generated at build time from config.yml) -->
    <script defer src="./assets/analytics.js"></script>
    <style>
        /* palette + base layout */
        body { font-family: "Segoe UI", Arial, sans-serif; background: #f3f8f9; color: #222; padding: 2rem; }
        a { color: #79bb93; text-decoration: none; }
        a:hover, a:focus { color: #647779; text-decoration: underline; }
        /* form controls */
        .input-group .form-control { border-color: #79bb93; }
        .btn-primary { background-color: #79bb93; border-color: #79bb93; }
        .btn-primary:hover, .btn-primary:focus { background-color: #647779; border-color: #647779; }
        .btn-outline-secondary { color: #647779; border-color: #647779; }
        .btn-outline-secondary:hover, .btn-outline-secondary:focus { background-color: #647779; border-color: #647779; color: #fff; }
        /* results list */
        .result { margin-bottom: 1rem; background: #fff; border: 1px solid #e5e5e5; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .result .title { font-weight: 600; display: block; margin-bottom: 0.35rem; }
        .result .snippet { color: #647779; }
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Search</h1>
        <form id=\"searchForm\" class=\"mb-3\">
            <div class=\"input-group\">
                <input type=\"text\" id=\"searchInput\" class=\"form-control\" placeholder=\"Search...\">
                <button type=\"submit\" class=\"btn btn-primary\">Search</button>
            </div>
        </form>
        <div class=\"mb-3\"><button id=\"backBtn\" class=\"btn btn-outline-secondary btn-sm\">← Back</button></div>
        <div id=\"results\"></div>
    </div>
    
    <script>\n        // Inline index to support file:// access without fetch\n        const SEARCH_INDEX = __INDEX__;\n        let searchIndex = SEARCH_INDEX || [];\n        \n        // Normalize for fuzzy matching (lowercase, alphanumerics + spaces only)\n        function norm(s) {\n            return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\\s+/g, ' ').trim();\n        }\n        \n        function escapeHtml(text) {\n            const div = document.createElement('div');\n            div.textContent = text;\n            return div.innerHTML;\n        }\n        \n        // Small Levenshtein distance for short strings (typo-tolerance)\n        function levenshtein(a, b) {\n            if (a === b) return 0;\n            const al = a.length, bl = b.length;\n            if (al === 0) return bl;\n            if (bl === 0) return al;\n            let v0 = new Array(bl + 1);\n            let v1 = new Array(bl + 1);\n            for (let i = 0; i <= bl; i++) v0[i] = i;\n            for (let i = 0; i < al; i++) {\n                v1[0] = i + 1;\n                const ai = a.charCodeAt(i);\n                for (let j = 0; j < bl; j++) {\n                    const cost = (ai === b.charCodeAt(j)) ? 0 : 1;\n                    v1[j + 1] = Math.min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost);\n                }\n                const tmp = v0; v0 = v1; v1 = tmp;\n            }\n            return v0[bl];\n        }\n        \n        // Precompute normalized fields/words once for speed\n        function prepareIndex() {\n            for (const item of searchIndex) {\n                item._titleN = norm(item.title);\n                item._textN = norm(item.text);\n                // Limit word list scanned for fuzzy matching (keeps large sites fast)\n                item._words = (item._titleN + ' ' + item._textN).split(' ').filter(Boolean).slice(0, 250);\n            }\n        }\n        \n        // Score: exact phrase > token substring > small edit-distance word match\n        function scoreItem(item, qTokens, qNorm) {\n            const hay = (item._titleN || '') + ' ' + (item._textN || '');\n            if (hay.includes(qNorm)) return 1000;\n            \n            let total = 0;\n            for (const tok of qTokens) {\n                if (tok.length < 2) continue;\n                if (hay.includes(tok)) { total += 50; continue; }\n                \n                let best = 0;\n                const maxDist = (tok.length <= 4) ? 1 : 2;\n                for (const w of (item._words || [])) {\n                    if (!w) continue;\n                    if (Math.abs(w.length - tok.length) > maxDist) continue;\n                    const d = levenshtein(tok, w);\n                    if (d <= maxDist) {\n                        const sim = 1 - (d / Math.max(tok.length, w.length));\n                        if (sim > best) best = sim;\n                        if (best >= 1) break;\n                    }\n                }\n                \n                if (best <= 0) return 0; // require every token to match at least a bit\n                total += best * 25;\n            }\n            return total;\n        }\n        \n        // autoNavigate=true: if there is exactly one hit, immediately open it.\n        function performSearch(autoNavigate) {\n            const queryRaw = document.getElementById('searchInput').value;\n            const resultsDiv = document.getElementById('results');\n            const qNorm = norm(queryRaw);\n            const qTokens = qNorm ? qNorm.split(' ').filter(Boolean) : [];\n            \n            if (!qNorm) {\n                resultsDiv.innerHTML = '';\n                return;\n            }\n            \n            const results = searchIndex\n                .map(item => ({ item, score: scoreItem(item, qTokens, qNorm) }))\n                .filter(x => x.score > 0)\n                .sort((a, b) => b.score - a.score)\n                .slice(0, 20);\n            \n            if (results.length === 0) {\n                resultsDiv.innerHTML = '<p class=\"text-muted\">No results found.</p>';\n                return;\n            }\n            \n            if (autoNavigate && results.length === 1) {\n                window.location.href = results[0].item.path;\n                return;\n            }\n            \n            let html = '';\n            results.forEach(r => {\n                const item = r.item;\n                const textLower = (item.text || '').toLowerCase();\n                const firstTok = qTokens[0] || '';\n                const queryPos = firstTok ? textLower.indexOf(firstTok) : -1;\n                let snippet = (item.text || '');\n                \n                if (queryPos >= 0) {\n                    const start = Math.max(0, queryPos - 50);\n                    const end = Math.min((item.text || '').length, queryPos + 150);\n                    snippet = (item.text || '').substring(start, end);\n                    if (start > 0) snippet = '...' + snippet;\n                    if (end < (item.text || '').length) snippet = snippet + '...';\n                } else {\n                    snippet = snippet.substring(0, 200);\n                    if ((item.text || '').length > 200) snippet = snippet + '...';\n                }\n                \n                html += `<div class=\"result\">\n                    <a href=\"${item.path}\" class=\"title\">${escapeHtml(item.title)}</a>\n                    <div class=\"snippet\">${escapeHtml(snippet)}</div>\n                </div>`;\n            });\n            \n            resultsDiv.innerHTML = html;\n        }\n        \n        // Back button behavior\n        (function(){\n          const backBtn = document.getElementById('backBtn');\n          if (backBtn) {\n            backBtn.addEventListener('click', function(){\n              if (history.length > 1) { history.back(); } else { window.location.href = './index.html'; }\n            });\n          }\n        })();\n        \n        // Prepare the index for fuzzy matching before any searches\n        prepareIndex();\n        \n        // Get query from URL and populate search box\n        const urlParams = new URLSearchParams(window.location.search);\n        const initialQuery = urlParams.get('q') || '';\n        document.getElementById('searchInput').value = initialQuery;\n        // Immediately run search if there's an initial query\n        if (initialQuery) { performSearch(true); }\n        \n        // Search on form submit\n        document.getElementById('searchForm').addEventListener('submit', function(e) {\n            e.preventDefault();\n            performSearch(true);\n        });\n        \n        // Search on input\n        document.getElementById('searchInput').addEventListener('input', function(){ performSearch(false); });\n    </script>
</body>
</html>"""
    search_html = search_html.replace("__INDEX__", json.dumps(records))
    # Auto-open immediately when search narrows to a single result (including while typing).
    search_html = search_html.replace("performSearch(false)", "performSearch(true)")

    (output_root / "search.html").write_text(search_html, encoding="utf-8")

    # 404 page: redirect unknown URLs to search with the missing slug prefilled as ?q=...
    # Note: this assumes the site is hosted at the domain root (so /search.html exists).
    not_found_html = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Not Found</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-5">
    <h1 class="h3 mb-3">Page not found</h1>
    <p class="text-muted mb-3">Redirecting to search…</p>
    <p class="mb-0">
      <a id="searchLink" class="btn btn-primary" href="/search.html">Go to search</a>
    </p>
  </div>

  <script>
    // Turn /some/missing/page into a reasonable search term.
    (function () {
      var pathname = window.location.pathname || '';
      try { pathname = decodeURIComponent(pathname); } catch (e) {}

      // Remove leading slashes and pick last segment; fall back to whole path if needed.
      var clean = pathname.replace(/^\/+/, '');
      var parts = clean.split('/').filter(function (x) { return !!x; });
      var slug = (parts.length ? parts[parts.length - 1] : clean) || '';
      slug = slug.replace(/\.html$/i, '').replace(/[-_]+/g, ' ').trim();

      var dest = new URL('/search.html', window.location.origin);
      dest.searchParams.set('q', slug);

      var a = document.getElementById('searchLink');
      if (a) a.href = dest.toString();

      window.location.replace(dest.toString());
    })();
  </script>
</body>
</html>"""
    (output_root / "404.html").write_text(not_found_html, encoding="utf-8")


# -- write all pages --
def write_pages(input_root: Path, output_root: Path, site_title: str, config: Dict[str, object], args: Any = None) -> None:
    """Convert all markdown files and write HTML pages with nav."""
    # Optional timing breakdown (opt-in via --timing) to find slow steps.
    timing_enabled = bool(args and getattr(args, "timing", False))
    _timings: List[Tuple[str, float]] = []
    _t_start = time.perf_counter()
    _t_last = _t_start
    def _tmark(label: str) -> None:
        nonlocal _t_last
        if not timing_enabled:
            return
        now = time.perf_counter()
        _timings.append((label, now - _t_last))
        _t_last = now

    # Check config for folder numbering requirement (default True for backwards compatibility)
    require_numbered_folders = config.get("require_numbered_folders", True)
    blog_mode = config.get("blog_mode", False)
    
    nav_root = build_nav_tree(input_root, output_root, require_numbered_folders)
    _tmark("write_pages: build_nav_tree")
    
    # Analytics JS (optional). We write one shared file: output_root/assets/analytics.js
    # Configure in config.yml: goatcounter: "https://YOUR.goatcounter.com/count"
    assets_dir = output_root / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Social preview base (used for Open Graph tags and absolute canonicals).
    # Set in config.yml as: site_url: "https://garden.causalmap.app"
    try:
        cfg_site_url = config.get("site_url")
        site_url = (str(cfg_site_url).strip() if cfg_site_url else DEFAULT_SITE_URL).rstrip("/")
    except Exception:
        site_url = DEFAULT_SITE_URL.rstrip("/")
    try:
        cfg_og = config.get("og_image_path")
        og_val = (str(cfg_og).strip() if cfg_og else DEFAULT_OG_IMAGE_PATH).strip()
        if og_val.lower().startswith("http://") or og_val.lower().startswith("https://"):
            og_image_url = og_val
        else:
            og_path = og_val
            if og_path and not og_path.startswith("/"):
                og_path = "/" + og_path
            og_image_url = f"{site_url}{og_path}" if og_path else DEFAULT_OG_IMAGE_PATH
    except Exception:
        og_image_url = DEFAULT_OG_IMAGE_PATH

    # Keep page meta for anchor redirect stubs (/foo/ → target) so shared short links get good previews.
    out_html_meta: Dict[Path, Dict[str, str]] = {}
    gc_url: Optional[str] = None
    try:
        gc = config.get("goatcounter")
        if isinstance(gc, str) and gc.strip():
            gc_url = gc.strip()
    except Exception:
        gc_url = None

    gc_url_js = json.dumps(gc_url)  # safe JS string or "null"
    analytics_js = (
        "(function(){\n"
        "  'use strict';\n"
        "  // GoatCounter analytics. Disabled on file:// to avoid counting local previews/PDF builds.\n"
        f"  var goatcounter = {gc_url_js};\n"
        "  if (!goatcounter) return;\n"
        "  if (location.protocol === 'file:') return;\n"
        "  var s = document.createElement('script');\n"
        "  s.async = true;\n"
        "  s.src = 'https://gc.zgo.at/count.js';\n"
        "  s.setAttribute('data-goatcounter', goatcounter);\n"
        "  document.head.appendChild(s);\n"
        "})();\n"
    )
    (assets_dir / "analytics.js").write_text(analytics_js, encoding="utf-8")
    _tmark("write_pages: write assets/analytics.js")

    def _wait_for_pdf_assets(pagep: Any, timeout_ms: int = 20000) -> None:
        """Wait for images to be ready before printing PDFs (fixes missing images in Playwright)."""
        try:
            # Ensure lazy images start loading (PDF print doesn't scroll, so lazy often never triggers)
            pagep.evaluate("() => document.querySelectorAll('img[loading=\"lazy\"]').forEach(i => i.loading = 'eager')")
        except Exception:
            pass
        try:
            # Give CDN assets (Bootstrap, etc.) time to settle
            pagep.wait_for_load_state("networkidle", timeout=timeout_ms)
        except Exception:
            pass
        try:
            # Wait until all images are fully decoded/available
            pagep.wait_for_function(
                "() => Array.from(document.images || []).every(img => img.complete && img.naturalWidth > 0)",
                timeout=timeout_ms,
            )
        except Exception:
            pass
        try:
            # Wait for Mermaid diagrams to finish rendering before PDF print.
            pagep.wait_for_function(
                """() => {
                    const nodes = Array.from(document.querySelectorAll('.mermaid'));
                    if (nodes.length === 0) return true;
                    return nodes.every(el => el.querySelector('svg') || el.getAttribute('data-processed') === 'true');
                }""",
                timeout=timeout_ms,
            )
        except Exception:
            pass
        try:
            # Ensure MathJax async typesetting has completed before print.
            pagep.evaluate(
                """async () => {
                    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
                        await window.MathJax.startup.promise;
                    }
                    return true;
                }"""
            )
        except Exception:
            pass

    def _generate_page_pdf_from_html(out_html_path: Path, pdf_out_path: Path, md_path: Path, page_title: Optional[str]) -> None:
        """Generate a per-page PDF by printing the already-written HTML file (single path for PDFs)."""
        from playwright.sync_api import sync_playwright  # type: ignore
        from datetime import date
        print(f"[PDF page] {md_path.relative_to(input_root)} -> {pdf_out_path.relative_to(output_root)}")
        with sync_playwright() as pweb:
            browser = pweb.chromium.launch()
            pagep = browser.new_page()
            pagep.set_viewport_size({"width": 1600, "height": 1200})
            pagep.goto(out_html_path.as_uri(), wait_until="load")
            try:
                pagep.emulate_media(media="print")
            except Exception:
                pass

            # Inject layout tweaks for clean PDFs
            top_folder_name = None
            try:
                rel_parts = md_path.relative_to(input_root).parts
                if len(rel_parts) >= 2:
                    top_folder_name = strip_numeric_prefix(rel_parts[0])
            except Exception:
                top_folder_name = None

            # Optional PDF header logo (Playwright header_template). This is the correct way to
            # add fixed-position elements without interfering with the page layout.
            header_html = "<div></div>"
            try:
                meta_text = md_path.read_text(encoding="utf-8")
                meta, _ = extract_yaml_front_matter(meta_text)
            except Exception:
                meta = {}
            try:
                logo_file = _extract_logo_overlay_from_metadata(meta) or ""
                if logo_file:
                    logo_src = (input_root / "assets" / logo_file)
                    if logo_src.exists() and logo_src.is_file():
                        b64 = base64.b64encode(logo_src.read_bytes()).decode("ascii")
                        data_uri = f"data:image/png;base64,{b64}"
                        # Center a 720px container (matches .content max-width) and align logo to its left edge.
                        header_html = (
                            "<div style=\"width:100%; padding-top:7.5mm; font-size:0;\">"
                            "<div style=\"width:720px; margin:0 auto;\">"
                            f"<img src=\"{data_uri}\" style=\"height:0.84cm; width:auto; object-fit:contain; display:block; margin-left:8mm;\" />"
                            "</div></div>"
                        )
                    else:
                        _warn("logo", f"logo: '{logo_file}' requested but not found at {logo_src}")
            except Exception:
                header_html = "<div></div>"

            pdf_print_css = (
                "@media print{"
                "html,body{background:#fff!important;}"
                "aside.sidebar, aside.rightbar, .edge-nav, #hamburgerBtn{display:none!important;}"
                ".layout-container{grid-template-columns:1fr!important;column-gap:0!important;background:#fff!important;}"
                ".content{max-width:720px;margin:0 auto;box-shadow:none;border:none;--cm-content-pad-x:0;--cm-content-pad-y:0;padding:0;font-size:11pt;line-height:1.65;}"
                ".content .page-title{font-family:system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,'Noto Sans',sans-serif;font-size:2.05rem;font-weight:700;line-height:1.3;margin:10mm 0 max(0mm,calc(2.25rem - 10mm)) 0;}"
                ".content h1,.content h2,.content h3,.content h4,.content h5,.content h6{font-family:system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;}"
                ".content h1{font-size:1.65rem;font-weight:600;margin-top:1.9rem;margin-bottom:1rem;}"
                ".content h2{font-size:1.4rem;font-weight:600;margin-top:1.6rem;margin-bottom:.95rem;}"
                ".content h3{font-size:1.2rem;font-weight:600;margin-top:1.4rem;margin-bottom:.85rem;}"
                ".content h4{font-size:1.05rem;font-weight:600;margin-top:1.2rem;margin-bottom:.75rem;}"
                ".content h5{font-size:.95rem;font-weight:600;margin-top:1.05rem;margin-bottom:.65rem;}"
                ".content h6{font-size:.9rem;font-weight:600;margin-top:.95rem;margin-bottom:.55rem;}"
                ".content h1,.content h2,.content h3,.content h4,.content h5,.content h6{page-break-after:avoid;page-break-inside:avoid;}"
                ".content h1+*,.content h2+*,.content h3+*,.content h4+*,.content h5+*,.content h6+*{page-break-before:avoid;}"
                ".content p{widows:2;orphans:2;}"
                ".content .anchor-link{display:none!important;}"
                ".content .pdf-links{display:none!important;}"
                ".breadcrumb-nav{display:none!important;}"
                ".content .references{margin-top:2.6rem;padding-top:1.6rem;border-top:1px solid #e5e5e5;}"
                ".content .references h2{font-size:1.15rem;font-weight:600;margin-bottom:.85rem;}"
                ".content.chapter-start>p:first-of-type{border-left:none!important;}"
                ".content > *:last-child{margin-bottom:0!important;}"
                ".content h1.rounded,.content h1.rounded-left,.content h1.banner{font-size:inherit;}"
                ".content h2.rounded,.content h2.rounded-left,.content h2.banner{font-size:inherit;}"
                ".content h3.rounded,.content h3.rounded-left,.content h3.banner{font-size:inherit;}"
                ".content h1.rounded,.content h2.rounded,.content h3.rounded{background:rgba(121,187,147,0.08);border-left:4px solid #79bb93;padding:0.75rem 1rem 0.75rem 1.5rem;border-radius:6px;margin-left:-1rem;margin-right:-1rem;}"
                ".content h1.rounded-left,.content h2.rounded-left,.content h3.rounded-left{border-left:4px solid #79bb93;padding-left:1.5rem;background:rgba(121,187,147,0.12);}"
                ".content h1.banner,.content h2.banner,.content h3.banner{background:#79bb93;color:white;padding:0.75rem 1rem 0.75rem 1.5rem;border-radius:6px;margin-left:-1rem;margin-right:-1rem;}"
                ".paper{font-size:11.5pt;line-height:1.7;}"
                ".paper h1{font-size:1.55rem;}"
                ".paper a{text-decoration:underline;text-underline-offset:2px;}"
                ".paper .callout,.paper .callout-note{border-left:none;border:1px solid #90c3c6;background:rgba(144,195,198,0.08);}"
                ".paper h1.banner-info,.paper h2.banner-info,.paper h3.banner-info{background:transparent;color:#2c3e50;border-left:4px solid #90c3c6;padding:0.55rem 0.9rem 0.55rem 1.7rem;border-radius:4px;margin-left:-1rem;margin-right:-1rem;}"
                ".paper h1.rounded-info,.paper h2.rounded-info,.paper h3.rounded-info{background:rgba(144,195,198,0.10);border-left-color:#90c3c6;padding:0.35rem 0.9rem 0.35rem 1.7rem;border-radius:4px;}"
                ".content .callout-right{display:block;}"
                ".content .callout{border-left:4px solid #6c757d;background:#f8f9fa;padding:1rem 1.25rem;margin:1.5rem 0;border-radius:4px;}"
                ".content .callout p:last-child,.content .callout ul:last-child,.content .callout ol:last-child{margin-bottom:0;}"
                ".content .callout ul,.content .callout ol{margin-top:0.5rem;margin-bottom:0.5rem;}"
                ".content .callout-info{border-left-color:#0dcaf0;background:#e7f5f8;}"
                ".content .callout-warning{border-left-color:#ffc107;background:#fff8e1;}"
                ".content .callout-tip{border-left-color:#198754;background:#e8f5e9;}"
                ".content .callout-note{border-left-color:#6c757d;background:#f8f9fa;}"
                ".content .callout-narrow{max-width:66%;}"
                ".content .callout-right{margin-left:auto;}"
                ".content .callout-center{margin-left:auto;margin-right:auto;}"
                ".content .callout-heavy{border-left-width:6px!important;border-radius:0;}"
                ".content .callout-left-border{border-top:none;border-right:none;border-bottom:none;}"
                ".content .callout-rounded{border-left:none;border:2px solid #e5e5e5;border-radius:6px;}"
                ".content .callout-inverted{background:#79bb93!important;color:#ffffff;}"
                ".content .callout-info.callout-inverted{border-left-color:#0dcaf0!important;}"
                ".content .callout-warning.callout-inverted{border-left-color:#ffc107!important;}"
                ".content .callout-tip.callout-inverted{border-left-color:#198754!important;}"
                ".content .callout-note.callout-inverted{border-left-color:#6c757d!important;}"
                "mark{background:#d4edda;padding:0.1em 0.2em;border-radius:2px;}"
                ".content blockquote{page-break-inside:avoid;}"
                "}"
            )
            compact_css = (
                "table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:8.8pt;}"
                "th,td{border:1px solid #e5e5e5;padding:.2rem .35rem;font-size:8.4pt;vertical-align:top;word-break:break-word;}"
                "img{margin:18px 0!important;}"
            )
            pagep.add_style_tag(content=pdf_print_css)
            pagep.add_style_tag(content=compact_css)
            _wait_for_pdf_assets(pagep)

            # Footer
            today_str = date.today().strftime("%Y-%m-%d")
            chapter_label = top_folder_name or (page_title if page_title else strip_numeric_prefix(md_path.stem))
            chapter_label = (chapter_label or "").replace("--", "–")
            chapter_span = f"<span>{html.escape(chapter_label)}</span>"
            footer_html = (
                f"<div style=\"width:100%; font-size:8.5px; color:#999; font-family:Georgia, Cambria, 'Times New Roman', Times, serif; padding:0 10mm;\">"
                f"<div style=\"display:flex; justify-content:space-between; width:100%;\">"
                f"<span>{html.escape(today_str)}</span>"
                f"{chapter_span}"
                f"<span>© Causal Map Ltd {date.today().year} · <a href=\"https://causalmap.app\" style=\"color:#999; text-decoration:none;\">causalmap.app</a> · <a href=\"https://creativecommons.org/licenses/by-nc/4.0/\" style=\"color:#999; text-decoration:none;\">CC BY-NC 4.0</a></span>"
                f"</div></div>"
            )
            pagep.pdf(
                path=str(pdf_out_path),
                format="A4",
                margin={"top": "22mm", "right": "18mm", "bottom": "24mm", "left": "18mm"},
                print_background=True,
                display_header_footer=True,
                header_template=header_html,
                footer_template=footer_html,
            )
            browser.close()
    
    # enumerate markdown files with inclusion rules
    def _is_included_md(p: Path) -> bool:
        if p.name.startswith("."):
            return False
        rel = p.relative_to(input_root)
        # exclude folders containing '!' (but allow files with ! in filename)
        # Check all path segments except the filename itself
        if any('!' in part for part in rel.parts[:-1]):
            return False
        # root: only index.md (unless require_numbered_folders is False, then allow all)
        if rel.parent == Path("."):
            return True if not require_numbered_folders else rel.name.lower() == "index.md"
        # only include content under top-level folders that start with a number (if required)
        if require_numbered_folders:
            top = rel.parts[0]
            return top[:1].isdigit()
        return True  # Include all folders when numbering not required

    md_files = [p for p in input_root.rglob("*.md") if _is_included_md(p)]
    
    # In blog mode, if there's no index.md, create one showing recent posts
    index_md_path = input_root / "index.md"
    if blog_mode and not index_md_path.exists():
        # Sort by modification time (most recent first)
        posts_by_mtime = sorted(
            [p for p in md_files if p != index_md_path],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if posts_by_mtime:
            index_content = "# Recent Posts\n\n"
            for post in posts_by_mtime[:10]:  # Show 10 most recent
                post_link = post.stem
                index_content += f"- [[{post_link}]]\n"
            index_md_path.write_text(index_content, encoding="utf-8")
            print(f"[INFO] Generated index.md with {min(len(posts_by_mtime), 10)} recent posts")
            md_files.append(index_md_path)
    
    # Create Contents page for 999 folders if needed
    try:
        folders_999 = {p.relative_to(input_root).parts[0] for p in md_files if len(p.relative_to(input_root).parts) >= 2 and p.relative_to(input_root).parts[0].startswith("999")}
        for folder_999 in folders_999:
            contents_path = input_root / folder_999 / "000 Contents.md"
            if not contents_path.exists():
                contents_path.write_text("", encoding="utf-8")
                print(f"[INFO] Created Contents page for {folder_999}")
            # Ensure Contents page is included in md_files
            if contents_path not in md_files:
                md_files.append(contents_path)
    except Exception:
        pass
    
    print(f"Found {len(md_files)} markdown files to render.")
    # Prefer top-level index first (ensures Home exists for nav links)
    md_files.sort(key=lambda p: (0 if p.resolve() == (input_root / "index.md").resolve() else 1, str(p).lower()))
    # Draft files (with ! in filename) are rendered to HTML for local preview,
    # but should NOT appear in any PDF outputs.
    md_files_no_drafts = [p for p in md_files if "!" not in p.name]

    # Titles now derive from filenames (numbers stripped and page anchors removed)
    # In blog mode, use first H1/H2 from content instead
    title_map: Dict[Path, str] = {}
    metadata_map: Dict[Path, Dict[str, Any]] = {}  # Store front matter metadata
    page_anchor_map: Dict[Path, Optional[str]] = {}
    for p in md_files:
        page_anchor_map[p] = extract_page_anchor_from_stem(p.stem)
        
        # Always parse YAML front matter (used for case study styling and (in blog mode) metadata display)
        try:
            text = p.read_text(encoding="utf-8")
            metadata, content = extract_yaml_front_matter(text)
            metadata_map[p] = metadata
        except Exception:
            metadata_map[p] = {}
            content = ""
        
        if blog_mode:
            try:
                # Try to get title from first heading
                heading_title = extract_first_heading(content)
                if heading_title:
                    # Keep filename-style title normalization for heading titles too
                    # (e.g. allow "qq" as a shortcut for "?")
                    title_map[p] = convert_qq_to_question_mark(heading_title)
                    if args and getattr(args, "debug_titles", False):
                        try:
                            relp = p.relative_to(input_root).as_posix()
                        except Exception:
                            relp = str(p)
                        print(f"[DEBUG titles] {relp} source=heading raw={heading_title!r} normalized={title_map[p]!r}")
                else:
                    # Fallback to filename
                    title_map[p] = strip_numeric_prefix(p.stem)
                    if args and getattr(args, "debug_titles", False):
                        try:
                            relp = p.relative_to(input_root).as_posix()
                        except Exception:
                            relp = str(p)
                        print(f"[DEBUG titles] {relp} source=filename raw={p.stem!r} normalized={title_map[p]!r}")
            except Exception:
                title_map[p] = strip_numeric_prefix(p.stem)
                if args and getattr(args, "debug_titles", False):
                    try:
                        relp = p.relative_to(input_root).as_posix()
                    except Exception:
                        relp = str(p)
                    print(f"[DEBUG titles] {relp} source=filename(except) raw={p.stem!r} normalized={title_map[p]!r}")
        else:
            title_map[p] = strip_numeric_prefix(p.stem)
            if args and getattr(args, "debug_titles", False):
                try:
                    relp = p.relative_to(input_root).as_posix()
                except Exception:
                    relp = str(p)
                print(f"[DEBUG titles] {relp} source=filename raw={p.stem!r} normalized={title_map[p]!r}")
    _tmark("write_pages: scan md_files + parse YAML + build title_map")

    # Lazy embed html cache - only compute when actually needed for ![[embeds]]
    class LazyEmbedCache:
        def __init__(self, md_files: List[Path]):
            self._cache: Dict[Path, str] = {}
            self._md_files = md_files
        
        # Dict-like API: support get(key, default) because callers treat this like a mapping.
        def get(self, md_path: Path, default: str = "") -> str:
            if md_path not in self._cache:
                try:
                    text = md_path.read_text(encoding="utf-8")
                except Exception:
                    text = ""
                text = strip_yaml_front_matter(text)
                # Normalize heading anchors so embeds don't display raw {anchor}
                try:
                    text_norm, _ = normalize_heading_anchors(text)
                except Exception:
                    text_norm = text
                # Keep full content in embeds now
                self._cache[md_path] = convert_markdown_to_html(text_norm)
            return self._cache.get(md_path, default)
    
    embed_html_map = LazyEmbedCache(md_files)

    # Build wikilink index for resolution
    wikilink_index = build_wikilink_index(md_files, title_map)
    _tmark("write_pages: build_wikilink_index")

    # Tag index for breadcrumb "Tags" dropdown (tag -> pages)
    tags_index = build_tags_index(md_files_no_drafts, metadata_map)
    _tmark("write_pages: build_tags_index")

    # Track missing references while building the site
    missing_images: Dict[str, Set[str]] = defaultdict(set)
    missing_wikilinks: Dict[str, Set[str]] = defaultdict(set)
    missing_md_links: Dict[str, Set[str]] = defaultdict(set)

    # Build BibTeX index once for HTML citation conversion (if a bib is provided)
    bib_index_for_html: Optional[Dict[str, Tuple[List[str], str]]] = None
    bib_link_index_for_html: Optional[Dict[str, str]] = None
    try:
        bib_path_cfg = args.bib if args else None
        if bib_path_cfg and Path(bib_path_cfg).exists():
            bib_path_obj = Path(bib_path_cfg)
            bib_index_for_html = _build_bib_index_simple(bib_path_obj)
            bib_link_index_for_html = _build_bib_link_index(bib_path_obj)
    except Exception:
        bib_index_for_html = None
        bib_link_index_for_html = None

    # Build signature: used ONLY to force rebuilds when the conversion pipeline changes.
    # (Do NOT include the nav tree here, otherwise adding a page forces re-render of all pages.)
    build_signature_json = json.dumps([("__pipeline__", PIPELINE_VERSION)], ensure_ascii=False)
    build_hash = hashlib.md5(build_signature_json.encode("utf-8")).hexdigest()
    prev_nav_hash_path = output_root / "assets" / "nav_hash.txt"
    try:
        prev_hash = prev_nav_hash_path.read_text(encoding="utf-8")
    except Exception:
        prev_hash = ""
    build_changed = (build_hash != prev_hash)
    if build_changed:
        print("[BUILD] Pipeline signature changed; pages will be re-rendered.")

    # Sidebar signature: drives generated_site/assets/sidebar.js (paths + titles only).
    sidebar_signature_items: List[Tuple[str, str]] = []
    for p in md_files:
        rel = p.relative_to(input_root).as_posix()
        sidebar_signature_items.append((rel, title_map.get(p, strip_numeric_prefix(p.stem))))
    sidebar_signature_items.sort()
    sidebar_signature_json = json.dumps(sidebar_signature_items, ensure_ascii=False)
    sidebar_hash = hashlib.md5(sidebar_signature_json.encode("utf-8")).hexdigest()
    prev_sidebar_hash_path = output_root / "assets" / "sidebar_hash.txt"
    try:
        prev_sidebar_hash = prev_sidebar_hash_path.read_text(encoding="utf-8")
    except Exception:
        prev_sidebar_hash = ""
    sidebar_changed = (sidebar_hash != prev_sidebar_hash)
    if sidebar_changed:
        print("[SIDEBAR] Sidebar signature changed; sidebar.js will be regenerated.")

    # Always ensure sidebar.js exists/updated (even in incremental mode with 0 changed pages).
    try:
        shared_nav_html = render_nav_html_shared(
            nav_root=nav_root,
            output_root=output_root,
            title_map=title_map,
            config=config,
            page_anchor_map=page_anchor_map,
        )
        write_sidebar_js(output_root=output_root, nav_html=shared_nav_html)
    except Exception as e:
        _warn("sidebar_js", f"Failed to write sidebar.js: {e}")
    _tmark("write_pages: render + write assets/sidebar.js")
    sidebar_footer_html = build_sidebar_footer_html(config)

    # Ensure referenced images are copied to output as well, and capture expected files
    expected_image_paths = copy_referenced_images(md_files, input_root, output_root, missing_images)
    _tmark("write_pages: copy_referenced_images")

    # Build outgoing links and backlinks for rightbar sections
    outgoing_map, backlinks_map = build_links_maps(
        md_files,
        input_root,
        title_map,
        wikilink_index,
        missing_wikilinks=missing_wikilinks,
        missing_md_links=missing_md_links,
    )
    _tmark("write_pages: build_links_maps (outgoing/backlinks)")

    # Filter to only changed/new files if incremental mode (after building indexes for embeds)
    # Nav is always rebuilt (fast), but HTML only regenerated for changed files
    files_to_process = md_files
    changed_files_for_pdf: Set[Path] = set()  # When incremental+page_pdf: only gen PDF for these
    if args and getattr(args, 'incremental', False):
        original_count = len(md_files)
        changed_files = []
        new_count = 0
        modified_count = 0
        modified_hash_count = 0
        empty_read_count = 0
        debug_missing = []  # Track first few missing files

        # Some file systems / sync providers (notably Google Drive) can update file contents without
        # reliably bumping mtime. To avoid missing edits, also track a per-file content hash.
        md_hashes_path = output_root / "assets" / "md_hashes.json"
        prev_md_hashes: Dict[str, str] = {}
        try:
            if md_hashes_path.exists():
                prev_md_hashes = json.loads(md_hashes_path.read_text(encoding="utf-8")) or {}
                if not isinstance(prev_md_hashes, dict):
                    prev_md_hashes = {}
        except Exception:
            prev_md_hashes = {}
        new_md_hashes: Dict[str, str] = dict(prev_md_hashes)

        for md_path in md_files:
            # Skip if source file doesn't exist (deleted/renamed)
            if not md_path.exists():
                continue
            out_html_path = relative_output_html(input_root, output_root, md_path)
            rel_key = md_path.relative_to(input_root).as_posix()

            # Hash current content (for stale-mtime files). If we get an empty/partial read (mid-save/sync),
            # retry once; if still empty, do not update the stored hash and do not hash-compare.
            txt = _read_text_windows_safe(md_path, encoding="utf-8", errors="ignore")
            if not txt.strip():
                try:
                    time.sleep(0.15)
                    txt = _read_text_windows_safe(md_path, encoding="utf-8", errors="ignore")
                except Exception:
                    txt = txt or ""
            h: Optional[str] = None
            if txt.strip():
                h = hashlib.md5(txt.encode("utf-8", errors="ignore")).hexdigest()
                new_md_hashes[rel_key] = h
            else:
                empty_read_count += 1

            # Include if output doesn't exist or is older than source
            if not out_html_path.exists():
                changed_files.append(md_path)
                new_count += 1
                if len(debug_missing) < 3:
                    debug_missing.append(f"  Missing: {out_html_path}")
            elif md_path.stat().st_mtime > out_html_path.stat().st_mtime:
                changed_files.append(md_path)
                modified_count += 1

            # Hash-based change detection (covers stale mtimes). Only compare if we had a non-empty read
            # AND we have a previous hash to compare against (avoid forcing a rebuild the first time).
            if h is not None:
                prev_h = prev_md_hashes.get(rel_key)
                if prev_h is not None and prev_h != h:
                    changed_files.append(md_path)
                    modified_hash_count += 1

        for dm in debug_missing:
            print(dm)

        # Persist hashes so future incremental runs can detect content changes even when mtime is stale.
        try:
            (output_root / "assets").mkdir(parents=True, exist_ok=True)
            md_hashes_path.write_text(json.dumps(new_md_hashes, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

        # Dependency-aware incremental:
        # Chapter intro pages embed "Pages in this Chapter" which depends on sibling pages in that folder,
        # so we must also re-render the chapter intro when any non-draft page in that chapter changes.
        affected: Set[Path] = set(changed_files)
        added_due_to_deps = 0
        try:
            # Build map: top-level folder -> intro page (first non-draft file in that folder)
            folder_to_intro: Dict[str, Path] = {}
            folder_groups: Dict[str, List[Path]] = defaultdict(list)
            for p in md_files_no_drafts:
                rel = p.relative_to(input_root)
                if len(rel.parts) >= 2:
                    folder_groups[rel.parts[0]].append(p)
            for top, pages in folder_groups.items():
                pages.sort(key=_path_file_key)
                if pages:
                    folder_to_intro[top] = pages[0]

            for p in changed_files:
                # Draft pages ('!') are excluded from chapter ToCs and shouldn't force intro refresh.
                if "!" in p.name:
                    continue
                rel = p.relative_to(input_root)
                if len(rel.parts) >= 2:
                    intro = folder_to_intro.get(rel.parts[0])
                    if intro and intro not in affected:
                        affected.add(intro)
                        added_due_to_deps += 1

            # The root index includes a "Chapters" block derived from the intro page of each top-level folder.
            # Re-render it when nav changes or when any chapter intro is impacted.
            root_index = (input_root / "index.md")
            if root_index.exists() and (sidebar_changed or any(intro in affected for intro in folder_to_intro.values())):
                if root_index not in affected:
                    affected.add(root_index)
                    added_due_to_deps += 1
        except Exception:
            pass

        files_to_process = sorted(affected, key=lambda p: str(p).lower())
        changed_files_for_pdf = set(changed_files)  # Per-page PDF only for actually changed, not deps
        # Note: "modified" counts include mtime-detected changes; "hash-modified" catches content changes with stale mtimes.
        print(f"[INCREMENTAL] {new_count} new, {modified_count} modified, {modified_hash_count} hash-modified (+{added_due_to_deps} deps) (from {original_count} total).")
        if empty_read_count:
            _warn("incremental", f"Incremental hash check saw {empty_read_count} empty reads (likely mid-save/sync). Those files were not hash-compared this run.")
        if sidebar_changed:
            print(f"[INCREMENTAL] Sidebar signature also changed.")
        if build_changed:
            print(f"[INCREMENTAL] Pipeline signature also changed.")
        _tmark("write_pages: incremental detect/filter")

    # Preflight: fail early if any output paths are too long for Windows.
    _preflight_check_windows_path_lengths(
        input_root=input_root,
        output_root=output_root,
        md_files_to_process=files_to_process,
    )
    _tmark("write_pages: preflight path length check")

    # Collect heading anchor ids → target page for root-level short routes (also page-level anchors)
    anchor_to_target: Dict[str, Path] = {}

    for idx, md_path in enumerate(files_to_process):
        out_html_path = relative_output_html(input_root, output_root, md_path)
        out_dir = out_html_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # Read source once to collect anchors for redirect stubs (even if page is skipped).
        # NOTE: On some sync providers (notably Google Drive on Windows), files can transiently read as empty
        # while they're being hydrated/synced. We retry once to avoid false "empty" reads.
        _md_src = _read_text_windows_safe(md_path, encoding="utf-8", errors="ignore")
        if not _md_src.strip():
            try:
                time.sleep(0.25)
                _md_src = _read_text_windows_safe(md_path, encoding="utf-8", errors="ignore")
            except Exception:
                _md_src = _md_src or ""

        # Avoid clobbering a previously-good HTML page with an empty/partial read.
        if not _md_src.strip():
            try:
                relp = md_path.relative_to(input_root)
            except Exception:
                relp = md_path
            _warn("incremental", f"Empty source read (after retry); skipping render this run: {relp}")
            continue
        _md_src = strip_yaml_front_matter(_md_src)
        try:
            md_text_norm_for_build, ids_in_page = normalize_heading_anchors(_md_src)
        except Exception:
            md_text_norm_for_build = _md_src
            ids_in_page = set()
        # Record anchors early to ensure redirect stubs are created
        try:
            for ident in ids_in_page:
                anchor_to_target.setdefault(ident, out_html_path)
        except Exception:
            pass
        # Also record page-level anchor from filename ((id)) if present
        try:
            page_id = page_anchor_map.get(md_path)
            if page_id:
                anchor_to_target.setdefault(page_id, out_html_path)
        except Exception:
            pass

        # Detect if this is a chapter start page (needed for PDF TOC decision)
        is_chapter_start_for_pdf = False
        try:
            is_root_index_path = (md_path.resolve() == (input_root / "index.md").resolve())
            if not is_root_index_path:
                rel_parts = md_path.relative_to(input_root).parts
                if len(rel_parts) >= 2:
                    top = rel_parts[0]
                    # Use nav order: chapter start is the first file in the top folder (non-recursive)
                    top_node = nav_root.subdirs.get(top)
                    if top_node and top_node.files:
                        first_file = sorted(top_node.files, key=_nav_file_key)[0].src_md
                        if md_path.resolve() == first_file.resolve():
                            is_chapter_start_for_pdf = True
        except Exception:
            pass

        # Chapter-level PDF for each top-level folder: generate on the first page in the folder.
        # IMPORTANT: run this BEFORE the cache-hit early-continue, otherwise incremental builds
        # can skip the intro page and never regenerate the chapter PDF.
        rel = md_path.relative_to(input_root)
        if (
            args
            and args.chapters_pdf
            and _PLAYWRIGHT_AVAILABLE
            and is_chapter_start_for_pdf
            and len(rel.parts) >= 2
        ):
            top_folder = rel.parts[0]
            # find first page in this folder (non-recursive ordering used earlier)
            top_node = nav_root.subdirs.get(top_folder)
            folder_md = _flatten_nav_files_in_order(top_node) if top_node else [p for p in md_files_no_drafts if p.relative_to(input_root).parts[0] == top_folder]
            if folder_md and folder_md[0].resolve() == md_path.resolve():
                # build chapter PDF path next to first page's html (use actual output dir from first page)
                first_page_html = relative_output_html(input_root, output_root, folder_md[0])
                # Use a short PDF filename to avoid Windows path length issues
                safe_pdf_name = _sanitize_stem_for_windows(top_folder, top_folder, max_len=30)
                chapter_pdf_name = f"Chapter -- {safe_pdf_name}.pdf"
                chapter_pdf = first_page_html.parent / chapter_pdf_name
                # stale check: if any md in folder newer than (or equal timestamp to) chapter_pdf
                chapter_pdf_mtime: Optional[float] = None
                if chapter_pdf.exists():
                    try:
                        chapter_pdf_mtime = chapter_pdf.stat().st_mtime
                    except Exception:
                        chapter_pdf_mtime = None
                folder_newer = chapter_pdf_mtime is None
                if not folder_newer:
                    for m in folder_md:
                        try:
                            mtime = m.stat().st_mtime
                        except FileNotFoundError:
                            continue
                        if mtime >= chapter_pdf_mtime:  # type: ignore[arg-type]
                            folder_newer = True
                            break
                if folder_newer:
                    # Compile sections: use already-converted HTML per page, but we need fresh conversions to ensure consistency with image rewriting
                    sections: List[Tuple[str, str]] = []
                    for page_md in folder_md:
                        try:
                            ttext = page_md.read_text(encoding="utf-8")
                        except Exception:
                            ttext = ""
                        # Keep YAML metadata (date badge) but strip front matter from body
                        metadata_sec, body_sec = extract_yaml_front_matter(ttext)
                        ttext = body_sec
                        # Auto-styling in chapter PDFs (based on YAML tag)
                        try:
                            if _metadata_has_tag(metadata_sec, "case_study"):
                                ttext = preprocess_case_study_styles(ttext)
                            elif _metadata_has_tag(metadata_sec, "paper"):
                                ttext = preprocess_paper_styles(ttext)
                        except Exception:
                            pass
                        ttext = replace_image_wikilinks(ttext, current_md_path=page_md, input_root=input_root, output_root=output_root)
                        # Convert citations to APA and collect keys
                        used_keys_sec: Set[str] = set()
                        try:
                            bib_path_cfg = args.bib if args else None
                            if bib_path_cfg and Path(bib_path_cfg).exists():
                                bib_index = _build_bib_index_simple(Path(bib_path_cfg))
                                bib_links = _build_bib_link_index(Path(bib_path_cfg))
                                ttext, used_keys_sec = _convert_citations_bracket_to_apa(ttext, bib_index, bib_links)
                        except Exception:
                            used_keys_sec = set()
                        ttext = replace_wikilinks_with_embeds(ttext, current_md_path=page_md, input_root=input_root, output_root=output_root, title_map=title_map, embed_html_map=embed_html_map, wikilink_index=wikilink_index, md_files=md_files, page_anchor_map=page_anchor_map)
                        ttext = normalize_alpha_ordered_lists(ttext)
                        ttext = rewrite_standard_image_refs(ttext, current_md_path=page_md, input_root=input_root, output_root=output_root)
                        thtml, _ = convert_markdown_with_toc(ttext)
                        thtml = postprocess_alpha_ol_html(thtml)
                        # Convert HTML links to internal PDF anchors or online links
                        try:
                            import bs4  # type: ignore
                            soup2 = bs4.BeautifulSoup(thtml, "html.parser")
                            # Process wikilinks - convert to internal anchors if target is in chapter, else online link
                            for link in soup2.select("a.wikilink"):
                                href = link.get("href", "")
                                if not href or href.startswith("#"):
                                    continue
                                # Extract target page from href
                                # href format: relative/path/to/page.html or /anchor-id
                                if href.startswith("/") and not href.endswith(".html"):
                                    # Page-level anchor, keep as is for now
                                    continue
                                # Check if target page is in this chapter
                                target_found = False
                                page_out_dir = relative_output_html(input_root, output_root, page_md).parent
                                for target_md in folder_md:
                                    target_out = relative_output_html(input_root, output_root, target_md)
                                    target_rel = os.path.relpath(target_out, start=page_out_dir).replace(os.sep, "/")
                                    if href.startswith(target_rel) or target_rel in href:
                                        # Target is in chapter - convert to internal anchor
                                        if "#" in href:
                                            anchor = href.split("#")[-1]
                                            link["href"] = f"#{anchor}"
                                        else:
                                            # Link to page title anchor
                                            page_title_slug = strip_numeric_prefix(target_md.stem).lower().replace(" ", "-")
                                            link["href"] = f"#{page_title_slug}"
                                        target_found = True
                                        break
                                if not target_found:
                                    # Convert to online link
                                    # Extract page name from href
                                    page_name = href.split("/")[-1].replace(".html", "").replace("#", "-")
                                    online_url = f"https://garden.causalmap.app/{page_name}"
                                    if "#" in href:
                                        anchor = href.split("#")[-1]
                                        online_url += f"#{anchor}"
                                    link["href"] = online_url
                            # Remove anchor links from headings
                            for hx in soup2.select("h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]"):
                                for anchor_link in hx.select("a.anchor-link"):
                                    anchor_link.decompose()
                            thtml = str(soup2)
                        except Exception:
                            pass
                        # Append references for this section if any
                        try:
                            bib_path_cfg = args.bib if args else None
                            if used_keys_sec and bib_path_cfg and Path(bib_path_cfg).exists():
                                refs_html = _format_reference_list(used_keys_sec, _build_bib_index_simple(Path(bib_path_cfg)), Path(bib_path_cfg))
                                if refs_html:
                                    thtml = thtml + "\n" + refs_html
                        except Exception:
                            pass
                        # Top date badge for this section
                        try:
                            badge_html = render_date_badge_html(metadata_sec)
                            if badge_html:
                                thtml = badge_html + "\n" + thtml
                        except Exception:
                            pass
                        # Paper pages: wrap section content for paper-specific CSS
                        try:
                            if _metadata_has_tag(metadata_sec, "paper"):
                                thtml = f'<div class="paper">{thtml}</div>'
                        except Exception:
                            pass
                        # Make <img> src absolute file URIs relative to that page's output dir for Playwright
                        p_out_dir = relative_output_html(input_root, output_root, page_md).parent
                        thtml_abs = absolutize_img_srcs(thtml, base_dir=p_out_dir)
                        # Keep title punctuation consistent with HTML output (Obsidian convention: "--" -> "–")
                        sec_title = title_map.get(page_md, strip_numeric_prefix(page_md.stem)) or strip_numeric_prefix(page_md.stem)
                        sec_title = sec_title.replace("--", "–")
                        sections.append((sec_title, thtml_abs))

                    # Keep title punctuation consistent with HTML output (Obsidian convention: "--" -> "–")
                    chapter_title = strip_numeric_prefix(top_folder).replace("--", "–")
                    # Chapter PDFs: no "Chapter" label and no special "first section" highlight box
                    chapter_html = render_compilation_pdf_html(f"{chapter_title}", sections, show_chapter_label=False, highlight_first_section=False)

                    # generate PDF via Playwright
                    chapter_pdf.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        print(f"[PDF chapter] {top_folder}/{top_folder}.pdf")
                        from playwright.sync_api import sync_playwright  # type: ignore
                        import tempfile
                        from datetime import date
                        with sync_playwright() as pweb:
                            browser = pweb.chromium.launch()
                            pagep = browser.new_page()
                            pagep.set_viewport_size({"width": 1600, "height": 1200})
                            tmpf = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
                            try:
                                tmpf.write(chapter_html)
                                tmpf.flush()
                                tmp_path = Path(tmpf.name).resolve()
                            finally:
                                tmpf.close()
                            pagep.goto(tmp_path.as_uri(), wait_until="load")
                            try:
                                pagep.emulate_media(media="print")
                            except Exception:
                                pass
                            _wait_for_pdf_assets(pagep)
                            # Chapter PDFs: include the standard footer (date · chapter · page numbers · copyright)
                            today_str = date.today().strftime("%Y-%m-%d")
                            chapter_span = f"<span>{html.escape(chapter_title)}</span>" if chapter_title else "<span></span>"
                            footer_html = (
                                f"<div style=\"width:100%; font-size:8.5px; color:#999; font-family:Georgia, Cambria, 'Times New Roman', Times, serif; padding:0 10mm;\">"
                                f"<div style=\"display:flex; justify-content:space-between; width:100%;\">"
                                f"<span>{html.escape(today_str)}</span>"
                                f"{chapter_span}"
                                f"<span style=\"display:flex; gap:1em;\">"
                                f"<span><span class=\"pageNumber\"></span> / <span class=\"totalPages\"></span></span>"
                                f"<span>© Causal Map Ltd {date.today().year} · <a href=\"https://causalmap.app\" style=\"color:#999; text-decoration:none;\">causalmap.app</a> · <a href=\"https://creativecommons.org/licenses/by-nc/4.0/\" style=\"color:#999; text-decoration:none;\">CC BY-NC 4.0</a></span>"
                                f"</span></div></div>"
                            )
                            pagep.pdf(
                                path=str(chapter_pdf),
                                format="A4",
                                margin={"top": "22mm", "right": "18mm", "bottom": "24mm", "left": "18mm"},
                                print_background=True,
                                display_header_footer=True,
                                header_template="<div></div>",
                                footer_template=footer_html,
                            )
                            browser.close()
                    except Exception as e:
                        print(f"[ERROR] Chapter PDF failed for {top_folder}: {e}")
                        import traceback
                        traceback.print_exc()

        # Fast skip: if output HTML exists and is newer than source MD and nav hasn't changed, skip re-rendering
        try:
            # For root index, also depend on the first file in each top-level folder (used for the index chapters block)
            latest_dep_mtime: Optional[float] = None
            if is_root_index_path:
                try:
                    top_folders = sorted({p.relative_to(input_root).parts[0] for p in md_files_no_drafts if len(p.relative_to(input_root).parts) >= 2})
                    first_files: List[Path] = []
                    for folder in top_folders:
                        folder_pages = [p for p in md_files_no_drafts if p.relative_to(input_root).parts[0] == folder]
                        folder_pages.sort(key=_path_file_key)
                        if folder_pages:
                            first_files.append(folder_pages[0])
                    if first_files:
                        latest_dep_mtime = max(p.stat().st_mtime for p in first_files)
                except Exception:
                    latest_dep_mtime = None

            # Compute required freshness threshold
            required_mtime = md_path.stat().st_mtime
            if latest_dep_mtime is not None and latest_dep_mtime > required_mtime:
                required_mtime = latest_dep_mtime

            cache_hit = (not build_changed) and out_html_path.exists() and (out_html_path.stat().st_mtime >= required_mtime)
            if cache_hit:
                # Skip expensive markdown->HTML pipeline
                # Optionally generate per-page PDF only if requested
                if args and args.page_pdf and _PLAYWRIGHT_AVAILABLE:
                    # Incremental: only gen PDF for actually changed files, not deps
                    if getattr(args, "incremental", False) and md_path not in changed_files_for_pdf:
                        pass
                    else:
                        pdf_out_path = out_html_path.with_suffix(".pdf")
                        needs_pdf_fast = (not pdf_out_path.exists()) or (md_path.stat().st_mtime >= pdf_out_path.stat().st_mtime)
                        if needs_pdf_fast:
                            try:
                                page_title_fast = title_map.get(md_path, strip_numeric_prefix(md_path.stem))
                                _generate_page_pdf_from_html(out_html_path, pdf_out_path, md_path, page_title_fast)
                            except Exception:
                                pass
                # Chapter/all PDFs read markdown directly, so they don't need HTML regeneration
                # Skip this page unless it's needed for other reasons
                continue
        except Exception:
            pass

        # Sidebar is injected at runtime by generated_site/assets/sidebar.js (shared across all pages).
        nav_html = ""

        # Use normalized source computed earlier
        md_text = md_text_norm_for_build
        # Replace image wikilinks first so <img> tags point to copied assets
        md_text_images = replace_image_wikilinks(
            md_text,
            current_md_path=md_path,
            input_root=input_root,
            output_root=output_root,
        )
        # Convert bracket citations to APA in HTML too (using same bib as PDFs) if tools available
        # Convert citations BEFORE markdown conversion so they become plain text
        used_citation_keys: Set[str] = set()
        if bib_index_for_html is not None:
            try:
                md_text_images, used_citation_keys = _convert_citations_bracket_to_apa(md_text_images, bib_index_for_html, bib_link_index_for_html)
            except Exception:
                pass
        # Replace [[wikilinks]] with collapsible embeds before converting to HTML (preserving #anchors)
        md_text_embeds = replace_wikilinks_with_embeds(
            md_text_images,
            current_md_path=md_path,
            input_root=input_root,
            output_root=output_root,
            title_map=title_map,
            embed_html_map=embed_html_map,
            wikilink_index=wikilink_index,
            md_files=md_files,
            page_anchor_map=page_anchor_map,
            missing_wikilinks=missing_wikilinks,
        )
        # Normalize alphabetic ordered lists to numeric
        md_text_alpha_norm = normalize_alpha_ordered_lists(md_text_embeds)
        # Rewrite standard image references to the correct output-relative paths
        md_text_fixed_images = rewrite_standard_image_refs(
            md_text_alpha_norm,
            current_md_path=md_path,
            input_root=input_root,
            output_root=output_root,
        )
        # Auto-styling (based on YAML tag)
        try:
            meta = metadata_map.get(md_path, {}) or {}
            if _metadata_has_tag(meta, "case_study"):
                md_text_fixed_images = preprocess_case_study_styles(md_text_fixed_images)
            elif _metadata_has_tag(meta, "paper"):
                md_text_fixed_images = preprocess_paper_styles(md_text_fixed_images)
        except Exception:
            pass
        # Convert with ToC for page content
        content_html, toc_html = convert_markdown_with_toc(md_text_fixed_images)
        # Strip HTML comments from converted content
        content_html = strip_html_comments(content_html)
        # Set alpha-ordered lists to alphabetic numbering in HTML
        content_html = postprocess_alpha_ol_html(content_html)
        # Inject per-heading anchor links and add image loading attributes
        try:
            import bs4  # type: ignore
            soup = bs4.BeautifulSoup(content_html, "html.parser")
            # Drop empty headings (they render as a confusing blank "header", sometimes showing only the anchor-link '#')
            for hx in soup.select("h1, h2, h3, h4, h5, h6"):
                # Only treat as empty if there's no visible text at all
                if not hx.get_text(strip=True):
                    hx.decompose()
            for hx in soup.select("h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]"):
                hid = hx.get("id")
                if not hid:
                    continue
                # Same-page anchor (keeps correct folder/filename in the URL)
                a = soup.new_tag("a", href=f"#{hid}", **{"class": "anchor-link", "aria-label": "Permalink"})
                a.string = "#"
                hx.append(a)
            # Add loading attr to all images
            for img in soup.select("img"):
                if not img.get("loading"):
                    img["loading"] = "lazy"
                # Keep image aspect ratios intact: don't set min-height.
                # If a background is needed (transparent PNGs), keep it plain white.
                existing_style = (img.get("style", "") or "").strip()
                if "background-color" not in existing_style:
                    new_style = "background-color: #fff;"
                    img["style"] = f"{existing_style}; {new_style}" if existing_style else new_style
            # Convert double hyphen to em dash in visible text (but never inside code/pre blocks)
            for text_node in soup.find_all(string=True):
                if isinstance(text_node, bs4.element.Comment):
                    continue
                parent_name = (text_node.parent.name if text_node.parent else "")
                if parent_name in {"code", "pre", "script", "style"}:
                    continue
                # Mermaid source is plain text inside <div class="mermaid">; never mutate it.
                if text_node.parent and text_node.parent.find_parent(class_="mermaid"):
                    continue
                if text_node.parent and "mermaid" in (text_node.parent.get("class") or []):
                    continue
                if "--" in text_node:
                    text_node.replace_with(text_node.replace("--", "—"))
            content_html = str(soup)
        except Exception:
            pass
        
        # Append reference list if citations were used
        if used_citation_keys and bib_index_for_html is not None:
            try:
                ref_list_html = _format_reference_list(used_citation_keys, bib_index_for_html, args.bib if args else None)
                if ref_list_html:
                    content_html += "\n" + ref_list_html
            except Exception:
                pass
        
        # In blog mode, prepend nice metadata display (author, tags)
        if blog_mode and md_path in metadata_map:
            metadata = metadata_map[md_path]
            meta_parts = []
            if "Author" in metadata or "author" in metadata:
                author_val = metadata.get("Author") or metadata.get("author")
                meta_parts.append(f'<span class="blog-meta-author"><i class="far fa-user"></i> {html.escape(str(author_val))}</span>')
            if "Tags" in metadata or "tags" in metadata:
                tags_val = metadata.get("Tags") or metadata.get("tags")
                if isinstance(tags_val, list):
                    tags_str = ", ".join(str(t) for t in tags_val)
                else:
                    tags_str = str(tags_val)
                meta_parts.append(f'<span class="blog-meta-tags"><i class="far fa-tags"></i> {html.escape(tags_str)}</span>')
            if meta_parts:
                meta_html = f'<div class="blog-metadata mb-3">{" · ".join(meta_parts)}</div>'
                content_html = meta_html + content_html

        # Top date badge (YAML: date:) — shown in HTML and PDFs (via compilation)
        try:
            badge_html = render_date_badge_html(metadata_map.get(md_path, {}))
            if badge_html:
                content_html = badge_html + "\n" + content_html
        except Exception:
            pass

        # Paper pages: wrap content so CSS can apply a slightly more academic look
        try:
            if _metadata_has_tag(metadata_map.get(md_path, {}) or {}, "paper"):
                content_html = f'<div class="paper">{content_html}</div>'
        except Exception:
            pass
        
        # Only show right ToC if there are at least 2 entries
        has_toc = toc_html.count("<a ") >= 2

        # title from filename (numbers stripped); suppress extra H1 for root index.md
        is_root_index = md_path.resolve() == (input_root / "index.md").resolve()
        page_title = None if is_root_index else strip_numeric_prefix(title_map.get(md_path, md_path.stem))
        page_anchor = page_anchor_map.get(md_path)
        if page_title:
            # Normalize double hyphen to en dash for display (filenames → page titles)
            page_title = page_title.replace("--", "–")
        if args and getattr(args, "debug_titles", False):
            try:
                relp = md_path.relative_to(input_root).as_posix()
            except Exception:
                relp = str(md_path)
            print(f"[DEBUG titles] render {relp} page_title={page_title!r}")

        # If root index, build a subtle chapters list with first paragraph snippets
        index_chapters_html = ""
        if is_root_index:
            try:
                items: List[str] = []
                # top-level folders only (already filtered in nav build); get their first NON-draft file
                top_folders = sorted({p.relative_to(input_root).parts[0] for p in md_files_no_drafts if len(p.relative_to(input_root).parts) >= 2})
                for folder in top_folders:
                    folder_pages = [p for p in md_files_no_drafts if p.relative_to(input_root).parts[0] == folder]
                    folder_pages.sort(key=_path_file_key)
                    if not folder_pages:
                        continue
                    first_md = folder_pages[0]
                    # link to that folder's index (first page's html)
                    first_href = os.path.relpath(relative_output_html(input_root, output_root, first_md), start=out_dir).replace(os.sep, "/")
                    chapter_title = strip_numeric_prefix(folder).replace("--", "–")
                    # extract first non-heading paragraph snippet from the first file
                    try:
                        first_md_text = first_md.read_text(encoding="utf-8")
                    except Exception:
                        first_md_text = ""
                    snippet_html = _first_non_heading_paragraph_html(first_md_text) or ""
                    # wrap in clearer styles: distinct title vs snippet
                    items.append(
                        f"<div class=\"mb-3 pb-2 border-bottom\">"
                        f"<a class=\"fw-semibold link-dark text-decoration-none chapter-page-link\" href=\"{html.escape(first_href)}\">"
                        f"<i class=\"fas fa-book-open me-2\" style=\"color:#90c3c6;\"></i>{html.escape(chapter_title)}</a>"
                        + (f"<div class=\"small text-muted mt-1 ps-2 border-start\" style=\"border-color:#e5e5e5!important\">{snippet_html}</div>" if snippet_html else "")
                        + "</div>"
                    )
                if items:
                    index_chapters_html = (
                        '<div class="mt-4 pt-3">'
                        '<div class="small text-uppercase text-muted mb-2">Chapters</div>'
                        + "".join(items) +
                        '</div>'
                    )
                # Append after the index.md content
                if index_chapters_html:
                    content_html = content_html + "\n" + index_chapters_html
            except Exception:
                pass

        # Chapter intro overview: if this is the first page of a top-level folder, list other pages in that folder
        try:
            if not is_root_index:
                rel_parts = md_path.relative_to(input_root).parts
                if len(rel_parts) >= 2:
                    top = rel_parts[0]
                    # Determine chapter intro page from nav order (avoids inconsistent sorting vs sidebar)
                    top_node = nav_root.subdirs.get(top)
                    if top_node and top_node.files:
                        intro_md = sorted(top_node.files, key=_nav_file_key)[0].src_md
                        # Only show overview on the intro page, and only if there are other nav-visible pages
                        all_pages_in_chapter = _flatten_nav_files_in_order(top_node)
                        other_pages = [p for p in all_pages_in_chapter if p.resolve() != intro_md.resolve()]
                        if other_pages and md_path.resolve() == intro_md.resolve():
                            blocks: List[str] = []
                            for p in other_pages:
                                href = os.path.relpath(relative_output_html(input_root, output_root, p), start=out_dir).replace(os.sep, "/")
                                title_p = title_map.get(p, strip_numeric_prefix(p.stem)) or strip_numeric_prefix(p.stem)
                                title_p = (title_p or "").replace("--", "–")
                                try:
                                    srcp = p.read_text(encoding="utf-8")
                                except Exception:
                                    srcp = ""
                                snippet = _first_non_heading_paragraph_html(srcp) or ""
                                blocks.append(
                                    f"<div class=\"mb-3 pb-2 border-bottom\">"
                                    f"<a class=\"fw-semibold link-dark text-decoration-none chapter-page-link\" href=\"{html.escape(href)}\">"
                                    f"<i class=\"fas fa-file-alt me-2\" style=\"color:#90c3c6;\"></i>{html.escape(title_p)}</a>"
                                    + (f"<div class=\"small text-muted mt-1 ps-2 border-start\" style=\"border-color:#e5e5e5!important\">{snippet}</div>" if snippet else "")
                                    + "</div>"
                                )
                            content_html += (
                                '<div class="mt-4 pt-3">'
                                '<div class="small text-uppercase text-muted mb-2">Pages in this Chapter</div>'
                                + "".join(blocks) +
                                '</div>'
                            )
        except Exception:
            pass

        # determine prev/next across all included pages (cross-folder)
        #
        # IMPORTANT: drafts (files with "!" in the filename) are rendered locally for preview,
        # but are not part of the published nav and typically aren't deployed. If we include
        # drafts in the prev/next sequence, then published pages can end up linking to draft
        # pages, breaking navigation on the deployed site.
        #
        # Policy:
        # - For non-draft pages: prev/next uses ONLY non-draft pages.
        # - For draft pages: prev/next uses the full local list (including drafts).
        prev_next_files = md_files if ("!" in md_path.name) else md_files_no_drafts
        md_idx = prev_next_files.index(md_path) if md_path in prev_next_files else idx
        prev_md: Optional[Path] = prev_next_files[md_idx - 1] if md_idx > 0 else None
        next_md: Optional[Path] = prev_next_files[md_idx + 1] if md_idx + 1 < len(prev_next_files) else None

        def _rel_href(target_md: Optional[Path]) -> Optional[str]:
            if not target_md:
                return None
            target_out = relative_output_html(input_root, output_root, target_md)
            return os.path.relpath(target_out, start=out_dir).replace(os.sep, "/")

        prev_href = _rel_href(prev_md)
        next_href = _rel_href(next_md)
        prev_title = title_map.get(prev_md, strip_numeric_prefix(prev_md.stem)) if prev_md else None
        next_title = title_map.get(next_md, strip_numeric_prefix(next_md.stem)) if next_md else None

        # Build links and backlinks HTML lists for this page
        links_html = render_links_list_html(sorted(outgoing_map.get(md_path, set())), out_dir, input_root, output_root, title_map)
        backlinks_html = render_links_list_html(sorted(backlinks_map.get(md_path, set())), out_dir, input_root, output_root, title_map)

        # PDF path and stale-check
        pdf_out_path = out_html_path.with_suffix(".pdf")
        pdf_link_html: Optional[str] = None
        # compute if PDF needs rebuild: if missing or md newer than pdf
        needs_pdf = False
        try:
            if not pdf_out_path.exists():
                needs_pdf = True
            else:
                needs_pdf = md_path.stat().st_mtime >= pdf_out_path.stat().st_mtime
        except Exception:
            needs_pdf = False

        # Only create per-page PDF link if (a) not a draft and (b) PDF exists or will be generated
        if ("!" not in md_path.name) and (pdf_out_path.exists() or (args and args.page_pdf)):
            pdf_href_rel = os.path.relpath(pdf_out_path, start=out_dir).replace(os.sep, "/")
            pdf_link_html = f'<a class="tr-float link-secondary small" href="{html.escape(pdf_href_rel)}" download>PDF</a>'

        # Add chapter/global PDF links on special pages (now that per-page link is defined)
        extra_links: List[str] = []
        # If this is the first page of a top-level folder, link to chapter PDF (only if exists or will be generated)
        rel_parts = md_path.relative_to(input_root).parts
        if len(rel_parts) >= 2:
            top_folder = rel_parts[0]
            top_node = nav_root.subdirs.get(top_folder)
            folder_md = _flatten_nav_files_in_order(top_node) if top_node else [p for p in md_files_no_drafts if p.relative_to(input_root).parts[0] == top_folder]
            if folder_md and folder_md[0].resolve() == md_path.resolve():
                # Use same sanitized name as when generating the PDF
                safe_pdf_name = _sanitize_stem_for_windows(top_folder, top_folder, max_len=30)
                chapter_pdf_name = f"Chapter -- {safe_pdf_name}.pdf"
                chap_pdf_path = (output_root / top_folder / chapter_pdf_name)
                # Only show link if PDF exists or will be generated this run
                if chap_pdf_path.exists() or (args and args.chapters_pdf):
                    chap_href_rel = os.path.relpath(chap_pdf_path, start=out_dir).replace(os.sep, "/")
                    extra_links.append(f'<a class="link-secondary small" href="{html.escape(chap_href_rel)}" download>PDF (chapter)</a>')
        # If root index, link to global PDF (only if exists or will be generated)
        if is_root_index:
            site_pdf = output_root / "site.pdf"
            if site_pdf.exists() or (args and args.all_pdf):
                site_href_rel = os.path.relpath(site_pdf, start=out_dir).replace(os.sep, "/")
                extra_links.append(f'<a class="link-secondary small" href="{html.escape(site_href_rel)}" download>PDF (all)</a>')

        # Existing per-page PDF link
        if pdf_link_html:
            extra_links.insert(0, pdf_link_html)
        pdf_link_html_combined = None
        if extra_links:
            pdf_link_html_combined = "<div class=\"pdf-links\">" + " &middot; ".join(extra_links) + "</div>"

        # Record anchor → page mapping (first occurrence wins)
        try:
            for ident in ids_in_page:
                anchor_to_target.setdefault(ident, out_html_path)
        except Exception:
            pass
        # And page-level anchor
        try:
            page_id = page_anchor_map.get(md_path)
            if page_id:
                anchor_to_target.setdefault(page_id, out_html_path)
        except Exception:
            pass

        # render template
        # compute page-relative assets path (from this page's directory to /assets)
        assets_href = html.escape(os.path.relpath(output_root / "assets", start=out_dir).replace(os.sep, "/") + "/")

        # Build breadcrumb navigation with siblings
        breadcrumb_data = build_breadcrumb_data(md_path, input_root, output_root, md_files, title_map, out_dir)
        tags_dropdown_html = render_tags_dropdown_html(tags_index, out_dir, input_root, output_root, title_map)
        breadcrumb_html = render_breadcrumb_html(breadcrumb_data, tags_dropdown_html=tags_dropdown_html)

        # Detect if this is the first page in a chapter (for special styling)
        is_chapter_start = False
        chapter_subtitle = None
        try:
            if not is_root_index:
                rel_parts = md_path.relative_to(input_root).parts
                if len(rel_parts) >= 2:
                    top = rel_parts[0]
                    top_node = nav_root.subdirs.get(top)
                    if top_node and top_node.files:
                        intro_md = sorted(top_node.files, key=_nav_file_key)[0].src_md
                        if md_path.resolve() == intro_md.resolve():
                            is_chapter_start = True
                            # Keep page_title consistent with sidebar; only add a subtitle label.
                            chapter_subtitle = "Chapter contents."
        except Exception as e:
            _warn("chapter_detection", f"Chapter detection error for {md_path}: {e}")

        # Build page anchor routing map for root index (only page-level anchors from 999 folder)
        page_anchor_routing_map: Optional[Dict[str, str]] = None
        if is_root_index:
            try:
                routing_map: Dict[str, str] = {}
                for p in md_files:
                    # Only include pages from "999" folder
                    rel_parts = p.relative_to(input_root).parts
                    if len(rel_parts) >= 2 and rel_parts[0].startswith("999"):
                        page_id = page_anchor_map.get(p)
                        if page_id:
                            # Route to short URL /{id}/ (stub iframe) so the bar stays clean.
                            routing_map[page_id] = f"/{page_id}/"
                if routing_map:
                    page_anchor_routing_map = routing_map
            except Exception:
                pass

        # Page-level meta (Open Graph / Twitter card) for LinkedIn previews.
        rel_out_html = os.path.relpath(out_html_path, start=output_root).replace(os.sep, "/")
        page_url = f"{site_url}/{rel_out_html}"
        page_desc = _html_text_snippet_for_meta(content_html, max_len=220)
        safe_og_title = html.escape(page_title or site_title or "")
        safe_og_desc = html.escape(page_desc)
        safe_og_url = html.escape(page_url)
        # If the page has images, use the first one. Otherwise fall back to the configured default/logo.
        img_src = _extract_first_img_src(content_html)
        if img_src:
            if img_src.lower().startswith("http://") or img_src.lower().startswith("https://"):
                page_og_img_url = img_src
            elif img_src.startswith("/"):
                page_og_img_url = f"{site_url}{img_src}"
            else:
                # Resolve relative to the page URL (important for nested folders).
                base_url = page_url.rsplit("/", 1)[0] + "/"
                page_og_img_url = urljoin(base_url, img_src)
        else:
            page_og_img_url = og_image_url
        safe_og_img = html.escape(page_og_img_url)
        og_type = "website" if is_root_index else "article"
        head_meta_html = (
            f'    <meta name="description" content="{safe_og_desc}">\n'
            f'    <link rel="canonical" href="{safe_og_url}">\n'
            f'    <meta property="og:title" content="{safe_og_title}">\n'
            f'    <meta property="og:description" content="{safe_og_desc}">\n'
            f'    <meta property="og:type" content="{og_type}">\n'
            f'    <meta property="og:url" content="{safe_og_url}">\n'
            f'    <meta property="og:site_name" content="{html.escape(site_title or "")}">\n'
            f'    <meta property="og:image" content="{safe_og_img}">\n'
            f'    <meta name="twitter:card" content="summary_large_image">\n'
            f'    <meta name="twitter:title" content="{safe_og_title}">\n'
            f'    <meta name="twitter:description" content="{safe_og_desc}">\n'
            f'    <meta name="twitter:image" content="{safe_og_img}">\n'
        )

        # Save meta for possible redirect stubs pointing at this page.
        try:
            out_html_meta[out_html_path.resolve()] = {
                "title": (page_title or site_title or ""),
                "description": page_desc,
                "image": page_og_img_url,
            }
        except Exception:
            pass

        full_html = render_page_html(
            page_title=page_title,
            page_anchor=page_anchor,
            content_html=content_html,
            site_title=site_title,
            toc_html=(toc_html if has_toc else None),
            links_html=links_html,
            backlinks_html=backlinks_html,
            prev_href=prev_href,
            next_href=next_href,
            prev_title=prev_title,
            next_title=next_title,
            pdf_link_html=pdf_link_html_combined,
            assets_href=assets_href,
            breadcrumb_html=breadcrumb_html,
            is_chapter_start=is_chapter_start,
            chapter_subtitle=chapter_subtitle,
            page_anchor_routing_map=page_anchor_routing_map,
            head_meta_html=head_meta_html,
            page_icon=_extract_icon_override_from_metadata(metadata_map.get(md_path, {}) or {}),
            page_layout=_extract_page_layout_from_metadata(metadata_map.get(md_path, {}) or {}),
            sidebar_footer_html=sidebar_footer_html,
        )

        # Only write if changed to avoid touching timestamps unnecessarily
        old = out_html_path.read_text(encoding="utf-8") if out_html_path.exists() else None
        if old != full_html:
            out_html_path.write_text(full_html, encoding="utf-8")
            try:
                rel_in = md_path.relative_to(input_root)
                rel_out = out_html_path.relative_to(output_root)
                print(f"[HTML] {rel_in} -> {rel_out}")
            except Exception:
                pass

        # Optionally generate per-page PDF using Playwright (after HTML is written)
        # Incremental: only gen PDF for actually changed files, not deps
        # Note: is_chapter_start is already determined above
        pdf_ok = not (args and getattr(args, "incremental", False)) or (md_path in changed_files_for_pdf)
        if ("!" not in md_path.name) and args and args.page_pdf and needs_pdf and pdf_ok and _PLAYWRIGHT_AVAILABLE:
            try:
                _generate_page_pdf_from_html(out_html_path, pdf_out_path, md_path, page_title)
            except Exception:
                pass

        # Chapter PDFs are generated above (before cache-hit skips), so we don't do it here.
    _tmark("write_pages: render HTML loop (and per-page PDFs if enabled)")

    # After writing content pages, write search index and search page
    write_search_assets(input_root, output_root, title_map)
    _tmark("write_pages: write_search_assets")
    # Save build + sidebar signatures (ensures assets dir exists due to write_search_assets)
    try:
        (output_root / "assets").mkdir(parents=True, exist_ok=True)
        prev_nav_hash_path.write_text(build_hash, encoding="utf-8")
        prev_sidebar_hash_path.write_text(sidebar_hash, encoding="utf-8")
    except Exception:
        pass

    # Create root-level redirect stubs for anchors: /{id}/index.html → target#id (includes page-level anchors from ((id)))
    try:
        # Ensure page-level aliases ((id)) always get stubs, even in incremental builds where a page
        # may not be re-rendered (stubs are cheap and depend only on filenames).
        try:
            for p, page_id in (page_anchor_map or {}).items():  # type: ignore[union-attr]
                if not page_id:
                    continue
                try:
                    anchor_to_target.setdefault(page_id, relative_output_html(input_root, output_root, p))
                except Exception:
                    continue
        except Exception:
            pass

        # Ensure heading-level anchors also get stubs reliably.
        #
        # IMPORTANT:
        # - We only create stubs for EXPLICIT anchors: "## Title {#bar}" (or "{bar}") -> /bar/
        # - We do NOT create stubs for implicit "## Foo" headings because that would create
        #   hundreds of stub directories and cause constant collisions (many pages share headings
        #   like "Intro", "Summary", etc).
        #
        # This is intentionally lightweight (regex over markdown) so it works even if the build
        # crashes mid-way through HTML rendering.
        try:
            heading_re = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
            trailing_attr_re = re.compile(r"\{([^}]*)\}\s*$")
            collisions: List[Tuple[str, str, str]] = []

            for p in md_files:
                try:
                    raw = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    raw = ""
                raw = strip_yaml_front_matter(raw)
                for line in raw.splitlines():
                    m = heading_re.match(line)
                    if not m:
                        continue
                    title = m.group(1).strip()

                    # If there's a trailing {...} attr block, prefer an explicit #id inside it.
                    ident: Optional[str] = None
                    m_attr = trailing_attr_re.search(title)
                    if m_attr:
                        inner = m_attr.group(1).strip()
                        # Look for "#id" or "id" (allow both styles)
                        m_id = re.search(r"(?:^|\s)#([A-Za-z][A-Za-z0-9_-]*)", inner)
                        if m_id:
                            ident = m_id.group(1).lower()
                        else:
                            # No explicit anchor in attr block; skip (avoid implicit /foo/ stubs).
                            continue

                    # Support legacy "{id}" / "{#id}" at end with no other attrs
                    if ident is None:
                        m_end = re.search(r"\{#?([A-Za-z][A-Za-z0-9_-]*)\}\s*$", title)
                        if m_end:
                            ident = m_end.group(1).lower()
                        else:
                            # No explicit anchor, skip.
                            continue

                    if not ident:
                        continue

                    try:
                        target = relative_output_html(input_root, output_root, p)
                        existing = anchor_to_target.get(ident)
                        if existing is not None and existing.resolve() != target.resolve():
                            try:
                                collisions.append((ident, str(existing), str(target)))
                            except Exception:
                                pass
                        else:
                            anchor_to_target.setdefault(ident, target)
                    except Exception:
                        continue

            if collisions:
                # Write collisions to warnings file (don't spam terminal)
                try:
                    for ident, a, b in collisions:
                        _warn("duplicate_heading_anchors", f"{ident}: {a} vs {b}")
                except Exception:
                    pass
        except Exception:
            pass

        reserved_stub_dirs = {"assets", "img"}
        stubs_created = 0
        for ident, target_html in anchor_to_target.items():
            stub_dir = output_root / ident
            # avoid clobbering important existing folders
            if ident in reserved_stub_dirs:
                continue
            stub_dir.mkdir(parents=True, exist_ok=True)
            stub_url_abs = f"{site_url.rstrip('/')}/{ident}/"
            try:
                stub_html = _short_route_stub_html(
                    target_html=target_html,
                    output_root=output_root,
                    site_url=site_url,
                    ident=ident,
                    stub_url_abs=stub_url_abs,
                )
                (stub_dir / "index.html").write_text(stub_html, encoding="utf-8")
                stubs_created += 1
            except Exception as ex:
                _warn("short_route_stub", f"{ident}: {ex}")
        if stubs_created:
            print(f"[STUB] Created {stubs_created} short-route stubs.")
    except Exception:
        pass
    _tmark("write_pages: create short-route stubs")

    # Global PDF (compiled from all md_files) at the site root
    if args and args.all_pdf and _PLAYWRIGHT_AVAILABLE:
        print("[PDF all] requested")
        global_pdf = output_root / "site.pdf"
        needs_global = False
        try:
            if not global_pdf.exists():
                needs_global = True
            else:
                # Ignore transient missing files during mtime scan; they should not suppress site.pdf generation.
                mtimes: List[float] = []
                for p in md_files_no_drafts:
                    try:
                        mtimes.append(p.stat().st_mtime)
                    except FileNotFoundError:
                        continue
                newest_md_mtime = max(mtimes, default=0)
                needs_global = newest_md_mtime >= global_pdf.stat().st_mtime
        except Exception as e:
            print(f"[PDF all][WARN] mtime check failed, forcing rebuild: {e}")
            needs_global = True

        if needs_global:
            sections: List[Tuple[str, str]] = []
            for p in md_files_no_drafts:
                try:
                    ttext = p.read_text(encoding="utf-8")
                except Exception:
                    ttext = ""
                # Keep YAML metadata (date badge) but strip front matter from body
                metadata_sec, body_sec = extract_yaml_front_matter(ttext)
                ttext = body_sec
                # Auto-styling in global PDF (based on YAML tag)
                try:
                    if _metadata_has_tag(metadata_sec, "case_study"):
                        ttext = preprocess_case_study_styles(ttext)
                    elif _metadata_has_tag(metadata_sec, "paper"):
                        ttext = preprocess_paper_styles(ttext)
                except Exception:
                    pass
                ttext = replace_image_wikilinks(ttext, current_md_path=p, input_root=input_root, output_root=output_root)
                # Convert citations to APA and collect keys
                used_keys_sec: Set[str] = set()
                try:
                    bib_path_cfg = args.bib if args else None
                    if bib_path_cfg and Path(bib_path_cfg).exists():
                        bib_index = _build_bib_index_simple(Path(bib_path_cfg))
                        bib_links = _build_bib_link_index(Path(bib_path_cfg))
                        ttext, used_keys_sec = _convert_citations_bracket_to_apa(ttext, bib_index, bib_links)
                except Exception:
                    used_keys_sec = set()
                ttext = replace_wikilinks_with_embeds(ttext, current_md_path=p, input_root=input_root, output_root=output_root, title_map=title_map, embed_html_map=embed_html_map, wikilink_index=wikilink_index, md_files=md_files_no_drafts, page_anchor_map=page_anchor_map)
                ttext = normalize_alpha_ordered_lists(ttext)
                ttext = rewrite_standard_image_refs(ttext, current_md_path=p, input_root=input_root, output_root=output_root)
                thtml, _ = convert_markdown_with_toc(ttext)
                thtml = postprocess_alpha_ol_html(thtml)
                # Convert HTML links to internal PDF anchors or online links
                try:
                    import bs4  # type: ignore
                    soup3 = bs4.BeautifulSoup(thtml, "html.parser")
                    # Process wikilinks - convert to internal anchors if target exists in site, else online link
                    for link in soup3.select("a.wikilink"):
                        href = link.get("href", "")
                        if not href or href.startswith("#"):
                            continue
                        # Extract target page from href
                        if href.startswith("/") and not href.endswith(".html"):
                            # Page-level anchor, keep as is
                            continue
                        # Check if target page is in md_files (site scope)
                        target_found = False
                        for p_target in md_files_no_drafts:
                            target_out = relative_output_html(input_root, output_root, p_target)
                            target_rel = os.path.relpath(target_out, start=output_root).replace(os.sep, "/")
                            if href.startswith(target_rel) or target_rel in href or target_rel.replace("index.html", "") in href:
                                # Target is in site - convert to internal anchor
                                if "#" in href:
                                    anchor = href.split("#")[-1]
                                    link["href"] = f"#{anchor}"
                                else:
                                    # Link to page title anchor
                                    page_title_slug = strip_numeric_prefix(p_target.stem).lower().replace(" ", "-")
                                    link["href"] = f"#{page_title_slug}"
                                target_found = True
                                break
                        if not target_found:
                            # Convert to online link
                            page_name = href.split("/")[-1].replace(".html", "").replace("#", "-")
                            online_url = f"{site_url}/{page_name}"
                            if "#" in href:
                                anchor = href.split("#")[-1]
                                online_url += f"#{anchor}"
                            link["href"] = online_url
                    # Remove anchor links from headings
                    for hx in soup3.select("h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]"):
                        for anchor_link in hx.select("a.anchor-link"):
                            anchor_link.decompose()
                    thtml = str(soup3)
                except Exception:
                    pass
                # Append references for this section if any
                try:
                    bib_path_cfg = args.bib if args else None
                    if used_keys_sec and bib_path_cfg and Path(bib_path_cfg).exists():
                        refs_html = _format_reference_list(used_keys_sec, _build_bib_index_simple(Path(bib_path_cfg)), Path(bib_path_cfg))
                        if refs_html:
                            thtml = thtml + "\n" + refs_html
                except Exception:
                    pass
                # Top date badge for this section
                try:
                    badge_html = render_date_badge_html(metadata_sec)
                    if badge_html:
                        thtml = badge_html + "\n" + thtml
                except Exception:
                    pass
                # Paper pages: wrap section content for paper-specific CSS
                try:
                    if _metadata_has_tag(metadata_sec, "paper"):
                        thtml = f'<div class="paper">{thtml}</div>'
                except Exception:
                    pass
                p_out_dir = relative_output_html(input_root, output_root, p).parent
                thtml_abs = absolutize_img_srcs(thtml, base_dir=p_out_dir)
                sections.append((title_map.get(p, strip_numeric_prefix(p.stem)), thtml_abs))

            global_title = "Causal Mapping: 97 ideas"
            combined_html = render_compilation_pdf_html(global_title, sections, highlight_first_section=False)

            try:
                print("[PDF all] site.pdf")
                from playwright.sync_api import sync_playwright  # type: ignore
                import tempfile
                from datetime import date
                with sync_playwright() as pweb:
                    browser = pweb.chromium.launch()
                    pagep = browser.new_page()
                    tmpf = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
                    try:
                        tmpf.write(combined_html)
                        tmpf.flush()
                        tmp_path = Path(tmpf.name).resolve()
                    finally:
                        tmpf.close()
                    pagep.goto(tmp_path.as_uri(), wait_until="load")
                    try:
                        pagep.emulate_media(media="print")
                    except Exception:
                        pass
                    _wait_for_pdf_assets(pagep)
                    today_str = date.today().strftime("%Y-%m-%d")
                    global_footer_span = (
                        f"<span>{html.escape(site_title or global_title)}</span>"
                        if (site_title or global_title) else "<span></span>"
                    )
                    footer_html = (
                        f"<div style=\"width:100%; font-size:8.5px; color:#999; font-family:Georgia, Cambria, 'Times New Roman', Times, serif; padding:0 10mm;\">"
                        f"<div style=\"display:flex; justify-content:space-between; width:100%;\">"
                        f"<span>{html.escape(today_str)}</span>"
                        f"{global_footer_span}"
                        f"<span style=\"display:flex; gap:1em;\">"
                        f"<span><span class=\"pageNumber\"></span> / <span class=\"totalPages\"></span></span>"
                        f"<span>© Causal Map Ltd {date.today().year} · <a href=\"https://causalmap.app\" style=\"color:#999; text-decoration:none;\">causalmap.app</a> · <a href=\"https://creativecommons.org/licenses/by-nc/4.0/\" style=\"color:#999; text-decoration:none;\">CC BY-NC 4.0</a></span>"
                        f"</span></div></div>"
                    )
                    pagep.pdf(path=str(global_pdf), format="A4", margin={"top":"22mm","right":"18mm","bottom":"24mm","left":"18mm"}, print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=footer_html)
                    browser.close()
            except Exception as e:
                print(f"[PDF all][ERROR] Failed to generate site.pdf: {e}")
                try:
                    import traceback
                    traceback.print_exc()
                except Exception:
                    pass
        else:
            print("[PDF all] skipped (up to date)")
        _tmark("write_pages: global site.pdf")
    elif args and args.all_pdf and not _PLAYWRIGHT_AVAILABLE:
        print("[PDF all][SKIP] Playwright unavailable. Install with: pip install playwright && python -m playwright install chromium")

    # Cleanup: remove unused images under output_root/img and any nested img folders
    try:
        removed = 0
        media_exts = _MEDIA_EXTS
        for p in (output_root / "img").rglob("*") if (output_root / "img").exists() else []:
            if p.is_file() and p.suffix.lower() in media_exts:
                if p not in expected_image_paths:
                    try:
                        p.unlink()
                        removed += 1
                    except Exception:
                        pass
        # Also remove empty directories left behind
        for dirpath, dirnames, filenames in os.walk(output_root / "img", topdown=False):
            d = Path(dirpath)
            try:
                if not any(d.iterdir()):
                    d.rmdir()
            except Exception:
                pass
        if removed:
            print(f"[CLEAN] Removed {removed} unreferenced images from output.")
    except Exception:
        pass
    _tmark("write_pages: cleanup unused images")

    # Only emit missing references if --missing flag is set
    if args and getattr(args, 'missing', False):
        def _emit_missing_to_file(category: str, data: Dict[str, Set[str]]) -> None:
            # One file per missing-type in repo root: missing_<type>.txt
            lines: List[str] = []
            for page in sorted(data):
                refs = sorted(r for r in data[page] if r)
                if not refs:
                    continue
                for ref in refs:
                    lines.append(f"{page} -> {ref}")
            if _WARN_COLLECTOR is not None:
                safe = re.sub(r"[^a-z0-9_-]+", "_", category.strip().lower()).strip("_") or "missing"
                _WARN_COLLECTOR.write_lines(f"missing_{safe}.txt", lines)

        if missing_images:
            _emit_missing_to_file("image", missing_images)
        if missing_wikilinks:
            _emit_missing_to_file("wikilink", missing_wikilinks)
        if missing_md_links:
            _emit_missing_to_file("markdown_link", missing_md_links)

    if timing_enabled:
        total = time.perf_counter() - _t_start
        print("[TIMING] write_pages breakdown:")
        for label, secs in _timings:
            print(f"[TIMING] {label}: {secs:.3f}s")
        print(f"[TIMING] write_pages total: {total:.3f}s")

# -- README splitting for external chapter --
def split_readme_into_chapter(readme_path: Path, input_root: Path) -> Optional[Path]:
    """
    Split a README file by H2 headings into separate markdown files.
    Creates a numbered folder in input_root with one file per H2 section.
    Only regenerates if README has changed since last generation.
    Returns the created folder path, or None if unsuccessful.
    """
    if not readme_path.exists():
        _warn("readme", f"README not found at {readme_path}, skipping.")
        return None
    
    try:
        readme_content = readme_path.read_text(encoding="utf-8")
    except Exception as e:
        _warn("readme", f"Failed to read README at {readme_path}: {e}")
        return None
    
    # Extract H1 heading (folder name)
    h1_match = re.search(r'^#\s+(.+)$', readme_content, re.MULTILINE)
    if not h1_match:
        _warn("readme", "No H1 heading found in README, skipping.")
        return None
    
    folder_name = h1_match.group(1).strip()
    
    # Remove {#anchor} syntax from folder name
    folder_name = re.sub(r'\s*\{#[^}]+\}', '', folder_name)
    
    # Check if folder already exists and if README has changed
    folder_num = 999
    folder_path = input_root / f"{folder_num} {folder_name}"
    
    if folder_path.exists() and folder_path.is_dir():
        try:
            readme_mtime = readme_path.stat().st_mtime
            # Check the oldest file in the folder (first created)
            existing_files = list(folder_path.glob("*.md"))
            if existing_files:
                oldest_file_mtime = min(f.stat().st_mtime for f in existing_files)
                if readme_mtime <= oldest_file_mtime:
                    print(f"[INFO] README unchanged, skipping regeneration of {folder_path.name}")
                    return folder_path
        except Exception:
            pass  # If we can't check, regenerate to be safe
    
    # Only process content until the second H1 heading
    first_h1_end = readme_content.find('\n# ', h1_match.end())
    if first_h1_end != -1:
        readme_content = readme_content[:first_h1_end]
        print(f"[INFO] Processing only first H1 section, ignoring content after line ~{readme_content[:first_h1_end].count(chr(10))}")
    
    # Remove existing folder if it exists (README has changed)
    if folder_path.exists():
        try:
            def _handle_remove_readonly(func, path, exc_info):
                try:
                    os.chmod(path, stat.S_IWRITE)
                except Exception:
                    pass
                try:
                    func(path)
                except Exception:
                    pass
            shutil.rmtree(folder_path, onerror=_handle_remove_readonly)
            print(f"[CLEAN] Removed existing folder {folder_path.name} for regeneration")
        except Exception as e:
            _warn("readme_cleanup", f"Could not remove {folder_path.name}: {e}")
    
    # Create the folder
    folder_path.mkdir(parents=True)
    
    # Split by H2 headings
    # Pattern to match H2 headings and capture content until next H2 or end
    sections = re.split(r'^##\s+(.+)$', readme_content, flags=re.MULTILINE)
    
    # sections[0] is content before first H2 (intro text after H1)
    # sections[1], sections[2], sections[3], sections[4], ... are H2 title, H2 content, H2 title, H2 content, ...
    
    file_num = 0
    
    # Don't create intro page - first H2 section will get the ((app)) anchor
    
    # First pass: collect all anchors from H2 sections and their content
    all_anchors = set()
    for i in range(1, len(sections), 2):
        if i + 1 > len(sections):
            break
        h2_title = sections[i].strip()
        h2_content = sections[i + 1].strip()
        
        # Extract H2 anchor
        h2_anchor_match = re.search(r'\{#([^}]+)\}', h2_title)
        if h2_anchor_match:
            all_anchors.add(h2_anchor_match.group(1))
        
        # Extract all other anchors from headings within the content
        for heading_match in re.finditer(r'^#{2,6}\s+.*?\{#([^}]+)\}', h2_content, re.MULTILINE):
            all_anchors.add(heading_match.group(1))
    
    # Process H2 sections
    for i in range(1, len(sections), 2):
        if i + 1 > len(sections):
            break
        
        h2_title = sections[i].strip()
        h2_content = sections[i + 1].strip()
        
        # Extract anchor if present in the title: {#anchor}
        anchor_match = re.search(r'\{#([^}]+)\}', h2_title)
        
        # Convert internal anchor links to stub links
        # Replace [text](#anchor) with [text](../anchor/) for cross-page links
        # Use relative path since pages are one level deep in folder structure
        def replace_anchor_link(match):
            link_text = match.group(1)
            anchor = match.group(2)
            # Convert to relative stub path from pages (which are one level deep)
            return f'[{link_text}](../{anchor}/)'
        
        h2_content = re.sub(r'\[([^\]]+)\]\(#([^)]+)\)', replace_anchor_link, h2_content)
        
        # Clean title for filename - first strip HTML tags
        clean_title = h2_title
        # Remove HTML tags like <i class="fas fa-table"></i>
        clean_title = re.sub(r'<[^>]+>', '', clean_title)
        # Convert {#anchor} to ((anchor)) for our anchor system
        if anchor_match:
            anchor = anchor_match.group(1)
            clean_title = re.sub(r'\{#[^}]+\}', f'(({anchor}))', clean_title)
        
        # Remove remaining special chars for filename (but keep spaces, hyphens, and our (()) syntax)
        clean_title = re.sub(r'[^\w\s\-()]+', '', clean_title)
        clean_title = clean_title.strip()
        
        # For the first H2, use ((app)) as the anchor instead of its original anchor
        if i == 1:
            # Remove existing anchor and use ((app))
            clean_title = re.sub(r'\s*\(\([^)]+\)\)\s*$', '', clean_title).strip()
            clean_title = f"{clean_title} ((app))"
        
        # Limit length but preserve the anchor part if present
        if len(clean_title) > 100:
            # If there's an anchor at the end, preserve it
            anchor_at_end = re.search(r'\(\([^)]+\)\)$', clean_title)
            if anchor_at_end:
                main_part = clean_title[:anchor_at_end.start()].strip()[:70]
                clean_title = f"{main_part} {anchor_at_end.group(0)}"
            else:
                clean_title = clean_title[:100]
        
        # Create file with just the content (title comes from filename)
        file_content = h2_content
        file_path = folder_path / f"{file_num:03d} {clean_title}.md"
        file_path.write_text(file_content, encoding="utf-8")
        file_num += 10
    
    print(f"[INFO] Split README into {(file_num // 10)} files in {folder_path.name}")
    return folder_path


# -- CLI --
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a simple static site from an Obsidian content folder.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("./content"),
        help="Path to the Obsidian content folder (default: user's content path)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./generated_site"),
        help="Output folder for generated site",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="Optional site title appended to page titles",
    )
    parser.add_argument(
        "--bib",
        type=Path,
        default=Path("C:/Users/Zoom/Zotero-cm/My Library.bib"),
        help="Path to a BibTeX library for APA citation conversion in PDFs",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean the output folder before building (full rebuild)",
    )
    parser.add_argument(
        "--chapters-pdf",
        action="store_true",
        help="Also build chapter PDFs (first page in each top-level folder)",
    )
    parser.add_argument(
        "--all-pdf",
        action="store_true",
        help="Also build a single global PDF containing all pages",
    )
    parser.add_argument(
        "--page-pdf",
        action="store_true",
        help="Also build per-page PDFs for changed files",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Build all PDFs (page, chapters, and all-site PDFs)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.yml (overrides defaults when set)",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=None,
        help="Path to external README to split into final chapter (can also be set in config.yml)",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only rebuild changed or new files (skip unchanged files)",
    )
    parser.add_argument(
        "--timing",
        action="store_true",
        help="Print a timing breakdown of build steps",
    )
    parser.add_argument(
        "--missing",
        action="store_true",
        help="Show missing images and links warnings (suppressed by default)",
    )
    parser.add_argument(
        "--debug-titles",
        action="store_true",
        help="Print page title derivation/normalization debug logs",
    )
    parser.add_argument(
        "--sync-created-dates",
        action="store_true",
        help="Update/insert YAML front matter 'date' from filesystem created date (then exit)",
    )
    return parser.parse_args()


def main() -> None:
    # parse CLI args
    args = parse_args()
    # If --pdf flag is set, enable all PDF generation options
    if args.pdf:
        args.page_pdf = True
        args.chapters_pdf = True
        args.all_pdf = True
    
    # Debug: show PDF flags
    print(f"[DEBUG] PDF flags: page_pdf={getattr(args, 'page_pdf', False)}, chapters_pdf={getattr(args, 'chapters_pdf', False)}, all_pdf={getattr(args, 'all_pdf', False)}")
    timing_enabled = bool(getattr(args, "timing", False))
    _main_timings: List[Tuple[str, float]] = []
    _main_start = time.perf_counter()
    _main_last = _main_start
    def _main_mark(label: str) -> None:
        nonlocal _main_last
        if not timing_enabled:
            return
        now = time.perf_counter()
        _main_timings.append((label, now - _main_last))
        _main_last = now

    # Collect warnings into text files in the repo root (where this script lives)
    global _WARN_COLLECTOR
    _WARN_COLLECTOR = WarningCollector(Path(__file__).parent.resolve())
    # Load config.yml if provided or found at project root
    config: Dict[str, object] = {}
    config_path: Optional[Path] = args.config if args.config else (Path("config.yml") if Path("config.yml").exists() else None)
    if config_path:
        try:
            import yaml  # type: ignore
        except Exception:
            raise SystemExit("PyYAML not installed. Install with: pip install pyyaml")
        try:
            cfg_text = Path(config_path).read_text(encoding="utf-8")
            loaded = yaml.safe_load(cfg_text) or {}
            if isinstance(loaded, dict):
                config = loaded
        except Exception as e:
            raise SystemExit(f"Failed to read config: {e}")
    _main_mark("main: load config.yml")

    def cfg_get_path(key: str, fallback: Path) -> Path:
        v = config.get(key)
        return Path(str(v)).expanduser().resolve() if isinstance(v, (str, os.PathLike)) else fallback

    def cfg_get_str(key: str, fallback: str) -> str:
        v = config.get(key)
        return str(v) if isinstance(v, (str, int, float)) else fallback

    input_root: Path = cfg_get_path("input", args.input).resolve()
    
    # Auto-derive output path from input path if not specified
    if config.get("output") is None and args.output == Path("./generated_site"):
        # Create a hash-based directory name from the input path
        input_hash = hashlib.md5(str(input_root).encode()).hexdigest()[:8]
        output_root = Path(f"./generated_site_{input_hash}").resolve()
    else:
        output_root: Path = cfg_get_path("output", args.output).resolve()
    
    site_title: str = cfg_get_str("site_title", args.title)
    # Get README path from config or use CLI arg default
    readme_config = config.get("readme")
    if readme_config == "":  # Explicitly disabled in config
        readme_path = None
    elif readme_config:  # Specified in config
        readme_path = Path(str(readme_config)).expanduser().resolve()
    else:  # Use CLI arg or default
        readme_path = args.readme if args.readme else Path("C:/dev/causal-map-extension/webapp/README.md")

    if not input_root.exists() or not input_root.is_dir():
        raise SystemExit(f"Input directory not found: {input_root}")

    # One-off maintenance: sync YAML date from filesystem created time, then exit.
    if getattr(args, "sync_created_dates", False):
        sync_created_dates_in_content(input_root)
        return

    # prepare output directory
    if args.clean and output_root.exists():
        # Clean rebuild should not crash if a PDF is open (WinError 32).
        # We preserve PDFs by NEVER attempting to delete them in the first place.
        print("[CLEAN] Removing non-PDF outputs (preserving PDFs)...")

        locked_or_failed = 0
        removed_files = 0

        # Delete files first (bottom-up so nested content is removed before we try to remove empty dirs).
        for p in sorted(output_root.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            try:
                if p.is_file():
                    if p.suffix.lower() == ".pdf":
                        continue
                    try:
                        os.chmod(p, stat.S_IWRITE)  # Windows: clear read-only bit if present
                    except Exception:
                        pass
                    p.unlink()
                    removed_files += 1
                elif p.is_dir():
                    # Best-effort: remove directory if empty after file deletions.
                    try:
                        p.rmdir()
                    except OSError:
                        pass
            except PermissionError:
                locked_or_failed += 1
            except Exception:
                locked_or_failed += 1

        if locked_or_failed:
            _warn("clean", f"Could not remove {locked_or_failed} output path(s) (likely open/locked). Clean rebuild will continue but may leave stale files.")
    else:
        output_root.mkdir(parents=True, exist_ok=True)
    _main_mark("main: prepare output dir")

    # Split external README into chapter if provided
    if readme_path and readme_path.exists():
        split_readme_into_chapter(readme_path, input_root)
    _main_mark("main: split README (if enabled)")
    
    # copy non-md assets first
    copy_assets(input_root, output_root)
    _main_mark("main: copy_assets")

    # write all pages (md -> html)
    write_pages(input_root, output_root, site_title=site_title, config=config, args=args)
    _main_mark("main: write_pages")

    # Post-step: merge per-folder 919*.pdf into a single convenience PDF (if present).
    _merge_prefixed_pdfs_in_each_folder(
        output_root,
        prefix="919",
        merged_name="How we can work together.pdf",
    )
    _main_mark("main: merge 919 PDFs (if any)")

    # Flush any warnings to warnings_*.txt / missing_*.txt
    try:
        if _WARN_COLLECTOR is not None:
            _WARN_COLLECTOR.flush()
    except Exception:
        pass
    _main_mark("main: flush warnings")

    print(f"Site generated at: {output_root}")
    if timing_enabled:
        total = time.perf_counter() - _main_start
        print("[TIMING] main breakdown:")
        for label, secs in _main_timings:
            print(f"[TIMING] {label}: {secs:.3f}s")
        print(f"[TIMING] main total: {total:.3f}s")


if __name__ == "__main__":
    main()
