"""Regenerate sections of the garden bibliography page from Zotero.

Zotero is the single source for our publication lists. JobCat's
`tools/build_publications_md.py` already derives Steve's canonical list that way;
this is the garden's equivalent for

    content/990 Finally/Causal mapping - a bibliography ((bibliography)).md

Each heading on that page maps to one Zotero collection, by NAME rather than id,
so renumbering collections cannot quietly point a section at the wrong list.

    python build_bibliography_md.py                    # report every section
    python build_bibliography_md.py --write            # rewrite the default section
    python build_bibliography_md.py --all --write      # rewrite all four

Source. The Zotero web API is the default, because it is what Zotero itself
calls current: the local `zotero.sqlite` lags until the app next syncs, so a
page built from it can silently miss an item filed minutes ago on the other
laptop. `--source local` reads a copy of that sqlite instead, which is the
fallback when there is no API key. Either way it never writes to Zotero, and the
local route copies the database before reading, so running it with Zotero open
is safe.

Scope. It rewrites one section at a time, in place, and leaves the rest of the
page alone. Only `causal-map-our-theory` is currently clean enough to publish
unread, which is why it is the only section on by default. The three report
collections still hold working items that have no business on a public page: the
run lists them under "read as working notes", and they want clearing in Zotero
before those sections are turned on.

Two things it will not hide. Items in the parent collection
`causal-mapping-biblio` but in none of the four children reach no section at all,
so they are listed as orphans on every run. And every entry a rewrite adds or
drops is printed before anything is written, so a collection emptied by accident
shows up as a long removal list rather than a quietly shorter page.
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "content" / "990 Finally" / "Causal mapping - a bibliography ((bibliography)).md"

PARENT_COLLECTION = "causal-mapping-biblio"

# Page heading -> Zotero collection name.
SECTIONS = {
    "Our publications on causal mapping": "causal-map-our-theory",
    "Quip / Bath SDR reports and papers": "causal-map-used-in-QuIP-bsdr-studies",
    "Other reports and papers using Causal Map": "causal-map-reports-not-QuIP-ours-and-others",
    "Key works related to causal mapping": "causal-mapping-key-works-not-us",
}
DEFAULT_SECTIONS = ["Our publications on causal mapping"]

ZOTERO_USER_ID = 17133746
KEY_FILES = [
    ROOT / ".env",
    ROOT.parents[1] / "20-29 Platforms and Documentation" / "20 all platforms" / "JobCat" / ".env",
]

SKIP_TYPES = {"attachment", "note", "annotation"}
# Types where APA carries a month or a day, not just a year.
DATED_TYPES = {"webpage", "blogPost", "newspaperArticle", "forumPost", "post", "videoRecording"}
# Types whose own title is italicised, having no larger container.
STANDALONE = {"book", "report", "thesis", "webpage", "blogPost", "manuscript",
              "document", "preprint", "dataset", "computerProgram", "videoRecording"}

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


# --- formatting ---------------------------------------------------------------

def apa_names(people, initials_first=False):
    def one(last, first):
        inits = " ".join(w[0] + "." for w in re.split(r"[ -]+", first or "") if w)
        if not inits:
            return last
        return f"{inits} {last}" if initials_first else f"{last}, {inits}"

    names = [one(ln, fn) for _, ln, fn in people]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        # APA joins a pair with "&" alone; the serial comma starts at three.
        return f"{names[0]} & {names[1]}" if initials_first else f"{names[0]}, & {names[1]}"
    return ", ".join(names[:-1]) + ", & " + names[-1]


def date_shown(fields, item_type):
    """The two sources spell dates differently, so read both.

    sqlite stores 'YYYY-MM-DD whatever the user typed'. The API gives the user's
    own string in `date` and an ISO reading of it in `meta.parsedDate`, which
    api_items copies in as `_parsed`. Either way a missing year means the item is
    forthcoming or undated, and the user's own words decide which.
    """
    raw = (fields.get("date") or "").strip()
    iso = (fields.get("_parsed") or "").strip() or raw.split(" ", 1)[0]
    m = re.match(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", iso)
    year = m.group(1) if m else ""
    month = (m.group(2) or "00") if m else "00"
    day = (m.group(3) or "00") if m else "00"
    if not year or year == "0000":
        m2 = re.search(r"\b([12]\d{3})\b", raw)
        if m2:
            year, month, day = m2.group(1), "00", "00"
        elif re.search(r"forthcoming|in press", raw, re.I):
            return "Forthcoming"
        else:
            return "n.d."
    if item_type not in DATED_TYPES or month == "00":
        return year
    if day != "00":
        return f"{year}, {MONTHS[int(month) - 1]} {int(day)}"
    return f"{year}, {MONTHS[int(month) - 1]}"


def link(fields):
    doi = (fields.get("DOI") or "").strip()
    if doi:
        url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
    else:
        url = (fields.get("url") or "").strip()
    return f" [{url}]({url})" if url else ""


def sentence(bits):
    """Join fragments without doubling the stop after an initial."""
    return re.sub(r"\.\.+(?=\s|$)", ".", " ".join(b for b in bits if b))


def entry(item_type, fields, people):
    authors = [p for p in people if p[0] == "author"]
    editors = [p for p in people if p[0] == "editor"]
    if not authors:
        authors = [p for p in people if p[0] not in ("editor", "translator", "seriesEditor")]
    shown = date_shown(fields, item_type)
    title = (fields.get("title") or "Untitled").strip().rstrip(".")
    who = apa_names(authors)

    italicise = item_type in STANDALONE or (
        item_type == "journalArticle" and not fields.get("publicationTitle"))
    shown_title = f"_{title}_" if italicise else title

    if who:
        bits = [sentence([f"{who}.", f"({shown})."]), f"{shown_title}."]
    else:
        # No author: APA moves the title into the author slot and does not repeat it.
        bits = [sentence([f"{shown_title}.", f"({shown})."])]

    if item_type == "journalArticle":
        pub = fields.get("publicationTitle", "")
        vol = fields.get("volume", "")
        issue = f"({fields['issue']})" if fields.get("issue") else ""
        pages = (fields.get("pages") or "").replace("-", "–")
        tail = ", ".join(x for x in [(f"_{vol}_{issue}" if vol else issue), pages] if x)
        if pub:
            bits.append(f"_{pub}_" + (f", {tail}" if tail else "") + ".")
    elif item_type == "bookSection":
        book = fields.get("bookTitle", "")
        eds = f"{apa_names(editors, initials_first=True)} (Eds.), " if editors else ""
        pages = (fields.get("pages") or "").replace("-", "–")
        pages = f" (pp. {pages})" if pages else ""
        if book:
            bits.append(f"In {eds}_{book}_{pages}.")
        if fields.get("publisher"):
            bits.append(f"{fields['publisher']}.")
    elif item_type == "thesis":
        if fields.get("thesisType"):
            bits[-1] = bits[-1].rstrip(".") + f" [{fields['thesisType']}]."
        if fields.get("university"):
            bits.append(f"{fields['university']}.")
    else:
        series = fields.get("seriesTitle") or fields.get("series") or ""
        number = fields.get("reportNumber") or fields.get("number") or ""
        paren = ", ".join(x for x in [series, f"No. {number}" if number else ""] if x)
        if paren and bits[-1].endswith("."):
            bits[-1] = bits[-1][:-1] + f" ({paren})."
        place = (fields.get("publisher") or fields.get("institution")
                 or fields.get("repository") or fields.get("websiteTitle")
                 or fields.get("blogTitle") or fields.get("university") or "")
        if place:
            bits.append(f"{place}.")

    return sentence(bits) + link(fields)


def sort_key(text):
    s = unicodedata.normalize("NFKD", text).lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"^(the|a|an) ", "", s).strip()


def looks_unpublishable(item_type, fields, people):
    """Working items that should not reach a public bibliography."""
    url = (fields.get("url") or "").lower()
    if "localhost" in url or "127.0.0.1" in url:
        return "local URL"
    if "linkedin.com" in url:
        return "LinkedIn post"
    if re.match(r"^\(\d+\)\s", (fields.get("title") or "").strip()):
        return "browser tab title"
    if not people and not (fields.get("publisher") or fields.get("institution")
                           or fields.get("publicationTitle") or fields.get("websiteTitle")):
        return "no author and no publisher"
    return None


# --- reading Zotero -----------------------------------------------------------

def api_key():
    """ZOTERO_API_KEY from the environment, else the first .env carrying it."""
    if os.environ.get("ZOTERO_API_KEY"):
        return os.environ["ZOTERO_API_KEY"], "environment"
    for f in KEY_FILES:
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip().startswith("ZOTERO_API_KEY="):
                return line.split("=", 1)[1].strip().strip("\"'"), str(f)
    return None, None


def api_get(path, key):
    req = urllib.request.Request(
        "https://api.zotero.org" + path,
        headers={"Zotero-API-Key": key, "Zotero-API-Version": "3"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def api_collections(key):
    out, start = {}, 0
    while True:
        page = api_get(f"/users/{ZOTERO_USER_ID}/collections?limit=100&start={start}", key)
        if not page:
            return out
        out.update({c["data"]["name"]: c["key"] for c in page})
        start += 100


def api_items(key, ckey):
    rows, start = [], 0
    while True:
        page = api_get(
            f"/users/{ZOTERO_USER_ID}/collections/{ckey}/items/top?limit=100&start={start}", key)
        if not page:
            return rows
        for it in page:
            d = it["data"]
            if d.get("itemType") in SKIP_TYPES:
                continue
            fields = {k: re.sub(r"\s+", " ", v.strip())
                      for k, v in d.items() if isinstance(v, str) and v.strip()}
            fields["_parsed"] = (it.get("meta") or {}).get("parsedDate", "")
            people = [(c.get("creatorType", "author"),
                       c.get("lastName") or c.get("name", ""),
                       c.get("firstName", "")) for c in d.get("creators", [])]
            rows.append((it["key"], d["itemType"], fields, people))
        start += 100


def zotero_data_dir():
    for p in Path.home().glob("AppData/Roaming/Zotero/Zotero/Profiles/*/prefs.js"):
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'"extensions\.zotero\.dataDir",\s*"([^"]+)"', text)
        if m:
            return Path(m.group(1).replace("\\\\", "\\"))
    return Path.home() / "Zotero"


SQL_FIELDS = (
    "SELECT f.fieldName, v.value FROM itemData d "
    "JOIN itemDataValues v ON d.valueID=v.valueID "
    "JOIN fieldsCombined f ON d.fieldID=f.fieldID WHERE d.itemID=?"
)
SQL_CREATORS = (
    "SELECT ct.creatorType, c.lastName, c.firstName FROM itemCreators ic "
    "JOIN creators c ON ic.creatorID=c.creatorID "
    "JOIN creatorTypes ct ON ic.creatorTypeID=ct.creatorTypeID "
    "WHERE ic.itemID=? ORDER BY ic.orderIndex"
)
SQL_IN_COLLECTION = (
    "SELECT i.itemID, it.typeName FROM collectionItems ci "
    "JOIN items i ON ci.itemID=i.itemID "
    "JOIN itemTypes it ON i.itemTypeID=it.itemTypeID "
    "LEFT JOIN deletedItems di ON di.itemID=i.itemID "
    "WHERE ci.collectionID=? AND di.itemID IS NULL"
)


def local_rows(con, cid):
    rows = []
    for iid, typ in con.execute(SQL_IN_COLLECTION, (cid,)):
        if typ in SKIP_TYPES:
            continue
        fields = {k: re.sub(r"\s+", " ", (v or "").strip())
                  for k, v in con.execute(SQL_FIELDS, (iid,))}
        people = list(con.execute(SQL_CREATORS, (iid,)))
        rows.append((iid, typ, fields, people))
    return rows


def load(args):
    """Return (source_label, {collection_name: [(id, type, fields, people)]})."""
    want = list(SECTIONS.values()) + [PARENT_COLLECTION]

    if args.source != "local":
        key, whence = api_key()
        if key:
            cols = api_collections(key)
            gone = [c for c in want if c not in cols]
            if gone:
                sys.exit("Zotero collection(s) missing from the online library, so a section "
                         "would be written short: " + ", ".join(gone))
            return (f"Zotero web API (key from {whence})",
                    {c: api_items(key, cols[c]) for c in want})
        if args.source == "api":
            sys.exit("no ZOTERO_API_KEY in the environment or in "
                     + ", ".join(str(f) for f in KEY_FILES))
        print("no ZOTERO_API_KEY found, falling back to the local library")

    db = Path(args.db) if args.db else zotero_data_dir() / "zotero.sqlite"
    if not db.exists():
        sys.exit(f"zotero.sqlite not found at {db}")
    snap = Path(tempfile.gettempdir()) / "garden_zotero_snapshot.sqlite"
    shutil.copyfile(db, snap)
    con = sqlite3.connect(snap)
    ids = {name: cid for cid, name in con.execute("SELECT collectionID, collectionName FROM collections")}
    gone = [c for c in want if c not in ids]
    if gone:
        sys.exit("Zotero collection(s) not found, so a section would be written short: "
                 + ", ".join(gone) + ". Rename them back, or update SECTIONS here.")
    return (f"local zotero.sqlite snapshot of {db}", {c: local_rows(con, ids[c]) for c in want})


# --- the page -----------------------------------------------------------------

def split_sections(text):
    blocks, head, body = [], None, []
    for line in text.splitlines():
        if re.match(r"^#{2,3} ", line):
            blocks.append((head, body))
            head, body = line, []
        else:
            body.append(line)
    blocks.append((head, body))
    return blocks


def section_of(text, line):
    """Which heading an existing line sits under."""
    head = None
    for ln in text.splitlines():
        if re.match(r"^#{2,3} ", ln):
            head = ln.lstrip("# ").strip()
        elif ln.strip() == line:
            return head
    return None


def replace_section(text, heading, entries):
    blocks, out, hit = split_sections(text), [], False
    for head, body in blocks:
        if head and head.lstrip("# ").strip() == heading:
            hit = True
            keep = [ln for ln in body if ln.strip().startswith(">")]
            new = [""] + ([*keep, ""] if keep else [])
            for e in entries:
                new += [e, ""]
            out.append((head, new))
        else:
            out.append((head, body))
    if not hit:
        sys.exit(f"heading not found on the page: {heading!r}")
    lines = []
    for head, body in out:
        if head:
            lines.append(head)
        lines += body
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite the page; otherwise report only")
    ap.add_argument("--all", action="store_true", help="every section, not just the default one")
    ap.add_argument("--section", action="append", help="a heading to rebuild; repeatable")
    ap.add_argument("--source", choices=["api", "local", "auto"], default="auto",
                    help="where to read Zotero (default: the web API, falling back to local)")
    ap.add_argument("--db", help="path to zotero.sqlite when reading locally")
    args = ap.parse_args()

    chosen = args.section or (list(SECTIONS) if args.all else DEFAULT_SECTIONS)
    unknown = [c for c in chosen if c not in SECTIONS]
    if unknown:
        sys.exit("unknown section(s): " + ", ".join(unknown))

    source, data = load(args)
    print("source: " + source + "\n")

    text = PAGE.read_text(encoding="utf-8")
    on_page = {ln.strip() for ln in text.splitlines()
               if ln.strip() and not ln.startswith(("#", ">", "-", "date", "<!--"))}

    used, suspect = set(), []
    for heading, coll in SECTIONS.items():
        rows = data[coll]
        used.update(r[0] for r in rows)
        built = []
        for iid, typ, fields, people in rows:
            why = looks_unpublishable(typ, fields, people)
            if why:
                suspect.append((heading, iid, why, fields.get("title", "?")))
            built.append(entry(typ, fields, people))
        built.sort(key=sort_key)
        flag = "REBUILD" if heading in chosen else "       "
        print(f"{flag} {len(built):4d}  {heading}   <- {coll}")
        if heading in chosen:
            for a in [e for e in built if e not in on_page]:
                print("      +", a[:150])
            for d in [ln for ln in on_page if ln not in built and section_of(text, ln) == heading]:
                print("      -", d[:150])
            text = replace_section(text, heading, built)

    orphans = [r for r in data[PARENT_COLLECTION] if r[0] not in used]
    if orphans:
        print(f"\n{len(orphans)} item(s) in '{PARENT_COLLECTION}' but in none of its four child "
              "collections, so they reach NO section of the page:")
        for iid, typ, fields, _ in sorted(orphans, key=lambda r: str(r[0])):
            print(f"    id={iid} [{typ}] {fields.get('title', '?')[:88]}")
        print("  File each into a child collection in Zotero, or leave it out on purpose.")

    if suspect:
        print(f"\n{len(suspect)} item(s) that read as working notes rather than publications. "
              "Clear these from Zotero before turning their section on:")
        for heading, iid, why, title in suspect:
            print(f"    [{heading[:34]:34s}] id={iid} ({why}) {title[:60]}")

    if args.write:
        PAGE.write_text(text, encoding="utf-8")
        print("\nwrote " + PAGE.name + ": " + ", ".join(chosen))
    else:
        print("\nreport only. Rerun with --write to change the page.")


if __name__ == "__main__":
    main()
