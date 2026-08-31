# 19aCMgarden

This repo is the source and build tooling for **garden.causalmap.app** — a public knowledge garden about causal mapping in evaluation and research.

GitHub: `stevepowell99/causal-mapping-garden` · Deployed by Netlify from `dist/`

## Role

You are a writing partner on a public knowledge garden about causal mapping. Governing virtue: an argument that holds. Think freely, then make the thinking stand up.

Priorities, in order:
1. Argue from something. A claim about method, evidence or practice needs a reason or a source a reader can check.
2. Write as Steve, not as a machine. Follow the hub writing rules and run `style-review` before publishing.
3. Speculate where speculating is the point, and mark it as speculation.
4. Netlify publishes from `dist/`, so treat a build as going public and say when a page will be live.

Ledger: `_role.md`.

## Structure

```
19aCMgarden/
├── content/              Obsidian vault — all source Markdown (NOT committed to git — local only)
├── dist/                 Generated HTML site — Netlify publish target (auto-committed by watcher)
├── build_static_site.py  Site generator script
├── config.yml            Build config (input → content/, output → dist/)
├── watch_and_build.ps1   File watcher: rebuilds ~1 min after changes, commits & pushes dist/
├── run_build_scheduled.bat  Full clean rebuild (run via Task Scheduler daily)
├── netlify.toml          Netlify config: publish = "dist"
└── serve.py              Local dev server for previewing the generated site
```

## What gets pushed where

- `dist/` — auto-committed and pushed by the watcher/scheduled scripts (triggers Netlify deploy)
- `content/` — NOT committed; local only (gitignored by the `*` rule in `.gitignore`)
- Source build tooling is versioned too, for recovery: `build_static_site.py`, `garden-compose.css`, `config.yml`, `watch_and_build.ps1`, `run_build_scheduled.bat`, `serve.py`, plus `netlify.toml`, `README.md`, `docs/`, `.gitignore` (see the allowlist comment at the top of `.gitignore`). The watcher only auto-commits `dist/`, so generator edits do NOT get committed automatically: commit `build_static_site.py` changes yourself (bundled with the next `dist` push is fine) rather than letting fixes sit only in the working tree.




## Build commands

```bash
# Incremental build (normal use, run from repo root). After bumping `PIPELINE_VERSION`, unchanged pages stay on old HTML until you add `--incremental-strict-pipeline` once or run `--clean` (the watcher passes strict pipeline).
python build_static_site.py --incremental

# Same, with per-page PDFs for changed files only
python build_static_site.py --incremental --page-pdf

# Full clean rebuild, including PDFs
python build_static_site.py --clean --pdf

# Local preview
python serve.py
```

The watcher (`watch_and_build.ps1`) monitors `content/` and rebuilds automatically (`--incremental --incremental-strict-pipeline --page-pdf`), then does `git add dist && git commit && git push`.

PDFs are expensive and optional. A generator pipeline change should not by itself mark all PDFs stale; per-page PDFs rebuild only when missing or when their source Markdown is newer. Exception: `--clean --pdf` is explicit intent to rebuild all PDF outputs, including preserved existing per-page PDFs.

## Making a polished branded PDF (briefs, one-pagers, case studies)

**The Garden is our tool for a standalone Causal-Map-branded PDF.** When Steve wants a nice PDF of a short document (a partner brief, a one-page pitch, a case study, an outreach handout), author it as a Garden page and let the build produce the PDF. Do **not** reach for Quarto/LaTeX or a hand-rolled Typst file for this kind of Causal Map deliverable; the Garden output is already branded and consistent, and keeping the doc in the Garden is single-source (one markdown, the PDF regenerates on every build). The `quarto-build` skill points here for exactly this reason.

What the per-page PDF gives you for free: a logo header (set `logo:` in YAML, or the folder default), a footer with the date, a Garden link and "Causal Map Ltd", page numbers, and a tidy print layout. Add `tags: [dual-column]` (optionally with `case_study` for the green section styling) for the two-column magazine look, `{.span-cols}` on any figure that should cross both columns. Full styling controls are under **Page styling (for authors)** below.

Two routes, by whether the doc should be public:

- **Public page** (fine to appear in nav and search): a normal numbered page. Its PDF builds automatically and is linked from the page. Reachable at `/<permalink>.pdf`.
- **Semi-invisible doc** (shareable but kept out of nav and search, the usual case for a client brief or pitch): make it a **draft** (`!` in the filename) with **`pdf: true`** in the YAML. The PDF builds on the normal `--page-pdf` run (so the watcher keeps it current) and lands in `dist` unlinked, reachable by URL but not indexed. The live example is `850 For consultants/! Causal Map and Qualia, a partner brief.md`.

To attach or share the PDF, take it from `dist/<folder>/<filename>.pdf` after a build (`python build_static_site.py --incremental --page-pdf`). Iterate on the markdown and rebuild; do not stage an intermediate copy elsewhere.

## Revising pages

For **substantive revisions** of an existing page (reworking arguments, restructuring, adding or cutting paragraphs), offer to use the **CriticMarkup** skill so Steve can accept or reject each change in review. If it is unclear whether a request is substantive, ask.

Do **not** use CriticMarkup when:

- Steve asks for a **new** page.
- Steve asks only to **correct** something, fix a reference, a typo, a link or other small mechanical fix.

Steve reviews CriticMarkup inside Obsidian (`content/` vault) with two plugins: **Track Changes** (Phil Baum) opens a side panel to accept/reject/reply to marks, and **Commentator** (`Fevol/obsidian-criticmarkup`, id `commentator`) inserts marks via hotkeyable commands and a suggest mode. Commentator is a beta plugin **installed manually** (files dropped into `content/.obsidian/plugins/commentator/` rather than through BRAT), so it does **not** auto-update; bump it by re-downloading the latest release from GitHub. Both decorate CriticMarkup, so if rendering looks doubled, disable display in one.

## Drafts and scratch

Do not use a `_tmp/` folder for drafts, and do not create subchapter (nested) folders in `content/` (this overrides the global scratch-folder rule). Keep a draft directly in the matching chapter folder, with `!` in the filename: it stays in the vault, gets local HTML preview, and is excluded from nav, search and PDF (its HTML is still built into `dist/`, so it is reachable by an unlinked URL).

**Unpublishing an already-published page needs `--clean`, not `--incremental`.** Adding `!` to (or otherwise renaming) a page that was previously published does not fully remove it on an incremental build: incremental re-renders only the changed page, so every sibling page that linked it in the chapter nav keeps its stale link, and the old-name `dist` files are left as orphans. Run `--clean` to re-render all pages and drop the link everywhere. `--clean` without `--pdf` preserves existing per-page PDFs (verified: count unchanged), so it is cheap, but it preserves an orphaned old-name PDF too, so delete that by hand from `dist/`.

Do not keep rendered binaries (`.docx`, `.pdf`) in the repo. A `!` in a filename does **not** stop the build copying non-markdown files to `dist/` (only a `!` folder would, and we do not use subfolders), so a stray `.docx` or `.bib` in a chapter folder would be published. Treat the `!`-prefixed markdown as the single source and regenerate other formats with pandoc on demand.

**Bibliography (single source).** The canonical library is one Zotero Better BibTeX auto-export living at the **root of the shared Causal Map Drive** as `MyLibrary.bib` (on this machine `…\Causal Map\MyLibrary.bib`). Because it sits inside the same synced Drive as this repo, everything references it by a **relative** path, so it works on any colleague's machine whatever their drive letter:

- Text & Talk manuscripts (`250 Causal Mapping as QDA/!manuscript.md` and `!extended-abstract.md`) set pandoc `bibliography:` to `../../../../MyLibrary.bib` (four levels up to the Causal Map root).
- The garden build's `--bib` default resolves to the same file via `Path(__file__).resolve().parents[2] / "MyLibrary.bib"`.

Do **not** keep a copy under `content/assets/` (a duplicate there drifts out of sync and gets published into `dist/`), and do not hard-code an absolute path. Only genuinely separate, hand-maintained bibs (e.g. `content/assets/extra-refs.bib` for refs not in Zotero) belong under `content/assets/`.

**The public bibliography page is generated, so never hand-edit it.** `content/990 Finally/Causal mapping - a bibliography ((bibliography)).md`, published at [garden.causalmap.app/bibliography](https://garden.causalmap.app/bibliography/), is built by `build_bibliography_md.py` from four Zotero collections, one per heading:

| Page heading | Zotero collection |
|---|---|
| Our publications on causal mapping | `causal-map-our-theory` |
| Quip / Bath SDR reports and papers | `causal-map-used-in-QuIP-bsdr-studies` |
| Other reports and papers using Causal Map | `causal-map-reports-not-QuIP-ours-and-others` |
| Key works related to causal mapping | `causal-mapping-key-works-not-us` |

To change what the page lists, add or remove the item in the Zotero collection, then run `python build_bibliography_md.py --write` and rebuild the site. Corrections to an entry's wording are corrections to the Zotero record. This is the same rule JobCat follows for Steve's canonical publication list (hub memory `reference_steve_publications`). **Anything that changes our publications has to update both.** JobCat's list is Steve's own work; this page is Causal Map's causal-mapping list. They overlap without being the same set.

Three things about the script worth knowing before running it. It reads the **Zotero web API** by default, because the local `zotero.sqlite` lags until the app next syncs; `--source local` reads the sqlite copy instead. It rebuilds **only "Our publications on causal mapping"** unless told otherwise, because the three report collections still hold working items that would embarrass us in public (a `localhost` URL, a LinkedIn tab); it lists those every run, and `--all` turns them on once someone has tidied them. And it reports items filed in the parent `causal-mapping-biblio` but in none of the four children, which reach no section of the page at all: as of 31 August 2026 there are 26 of them.

## Content rules (brief)

- Only folders starting with a digit are published (e.g. `005 Topic/`).
- **Folders whose name contains `!`** (e.g. `991 !!! just my notes/`) are skipped entirely: not walked, not built, not copied, not searched.
- **Filenames containing `!`** are drafts: rendered to HTML for local preview but excluded from nav, search index and PDF output. Exception: a draft with `pdf: true` in its YAML gets a per-page PDF from the normal `--page-pdf` build (so the watcher keeps it current); like draft HTML it lands in `dist` unlinked, reachable by URL but not in nav or search. Use this for shareable docs kept semi-invisible (e.g. `850 For consultants/! Causal Map and Qualia, a partner brief.md`).
- `((anchor))` at end of filename creates short URL `/anchor/`
- `--` in filename → en dash; `qq` → `?`
- YAML front matter is stripped; filename becomes the page title. Display titles drop the `!` draft flag (it is workflow state rather than title text), so name a draft as you want its title to read.
- Wiki links use bare basenames (`[[page title|display]]`), no folder prefix; Obsidian resolves by basename across the vault
- Use Obsidian-style (pandoc) citation keys for literature references wherever possible. The build converts them to formatted citations plus a references list. Don't hand-write APA/Harvard prose citations when a key exists. Full syntax is in the **Citations** section below.
- **Mermaid diagrams (` ```mermaid ` fences) render anywhere, including nested inside `--{.panel}`/multi-column content.** The generator promotes any fenced Mermaid block to a live diagram even when a nested markdown pass renders the panel's inner content (which would otherwise leave it as a literal code block). Diagrams auto-scale to their container (`.content .mermaid svg { max-width: 100% }`); reorient a diagram vertically (`graph TD`) if it is in a narrow column so it doesn't overflow.
- **`[[wikilinks]]` do NOT resolve inside `--{.panel}`/column content** (the same nested-markdown-pass gap Mermaid had, but not fixed for links). Use a plain markdown link to the page's `/slug/` short URL instead (`[text](/slug/)`) for any link written inside a panel or column; an unresolved wikilink there doesn't just fail silently, it can break the surrounding list/paragraph structure.
- **Auto-injected `## Related` cruft, strip it before building.** Some source pages carry a generated `<!-- xrefs-v1 -->` marker followed by a trailing link-only `## Related` block. The build renders this as ordinary body content; it does **not** auto-generate body "Related" links (backlinks live in the right sidebar). Remove the marker and its trailing link-only `## Related` section from source. For pages transcluded elsewhere via `![[...]]`, run a `--clean` rebuild afterwards so the embeds drop the stale block (a per-page re-render alone keeps a cached copy). Nothing in this repo regenerates the marker, so removal is permanent. A throwaway cleaner that does exactly this (trailing link-only Related + every marker line, leaving real prose) was used once; re-derive it if the cruft reappears.

## Citations

Write citations with pandoc-style keys (`@authorYearTitle`). The build (`_convert_citations_bracket_to_apa` in `build_static_site.py`) turns them into APA-style text and appends an APA 7th reference list for every key used on the page. Use these forms.

### Supported forms

| What you type | What renders |
|---|---|
| `[@key]` | `(Smith et al. 2005)` |
| `@key` | `Smith et al. (2005)` (narrative: author outside, year in parens) |
| `[-@key]` | `(2005)` (author suppressed, year only) |
| `[@key1; @key2]` | `(Smith et al. 2005; Jones 2010)` (one pair of parens for the group) |
| `[@key, p. 5]` | `(Smith et al. 2005, p. 5)` |
| `[@key, pp. 10-15]` | `(Smith et al. 2005, pp. 10-15)` |
| `[@key, ch. 3]` | `(Smith et al. 2005, ch. 3)` |
| `[@key, p. 5, emphasis added]` | `(Smith et al. 2005, p. 5, emphasis added)` |
| `@key, pp. 10-15` | `Smith et al. (2005, pp. 10-15)` |
| `[see @key]` | `(see Smith et al. 2005)` |
| `[cf. @key, p. 5]` | `(cf. Smith et al. 2005, p. 5)` |
| `[see @key1; cf. @key2]` | `(see Smith et al. 2005; cf. Jones 2010)` |

### Rules

- **Brackets vs no brackets** is the parenthetical/narrative switch. `[@key]` wraps everything in parentheses; bare `@key` makes it narrative `Author (year)`.
- **Author suppression** uses `-` immediately before the key: `[-@key]` gives year only.
- **Prefix** is any text before the key inside the brackets (`see`, `cf.`, `e.g.`). It renders as plain text before the citation, and works per item in a group. Prefixes only work inside brackets, not on a bare `@key`.
- **Locator/suffix inside brackets** passes through verbatim: any page form (`p. 5`, `pp. 10-15`), section (`ch. 3`, `sec. 4.2`), or note (`p. 5, emphasis added`).
- **Locator on a bare `@key`** must start with a recognised label (`p.`, `pp.`, `ch.`, `chap.`, `sec.`, `§`) followed by a number or range, so it does not swallow the following prose. For anything more elaborate, use the bracketed form.
- **Author formatting**: one author shows the surname; two show `A & B`; three or more show `A et al.`
- **Unknown key** renders with `n.d.` for the year, so a typo is visible in the output rather than silent.
- If the bib entry has a link, the citation becomes a hyperlink (the prefix stays as plain text outside the link).

### Not supported

- Real en dash page ranges only work inside brackets (pass-through). On a bare `@key`, type an ASCII hyphen range (`10-15`).
- Formatting is a built-in simplified APA, not a full CSL processor. It is fine for normal author/year/page citing; it does not do citation disambiguation letters (`2005a`/`2005b`), `ibid`, or locale-specific styles.

## Cross-references and anchors

How to link to a page, and to a heading inside a page. Most of our pages use the `Foo Title ((permalink))` filename style, which publishes the page at the short URL `/permalink`.

### Link to a whole page

- `[[Foo Title]]` or the full basename `[[010 Foo Title ((permalink))]]`. Both resolve. The build indexes each page by its full basename, its basename with the leading number and the `((...))` stripped, and its title.
- For a page with `((permalink))`, the link renders as the short URL `/permalink`.
- You cannot link by the permalink slug: `[[permalink]]` does **not** resolve. The permalink is an output URL, not a link target.

### Link to a heading in another page

- Write `[[Foo Title#Some Heading]]`. The text after `#` is slugified to match the heading's id.
- For a `((permalink))` page this now renders as `/permalink#some-heading` (it keeps the short URL; the short route is a full copy of the page, so the heading id is present there).
- The slug uses python-markdown's own heading slugify, so accented, underscored and punctuated headings line up correctly (for example `Café`, `Step_1`, `A & B`).
- If a heading has an explicit id, link to the id: `## Methods {#methods}` then `[[Foo Title#methods]]`.

### Link to a heading in the same page

- Use a markdown fragment link with an explicit id: `## Methods {#methods}` then `[jump](#methods)`. This works on the page and on its `/permalink` copy.
- Obsidian-style `[[#Heading]]` (no page name) does **not** work in the build; it renders as literal text. Always include the page name, or use the markdown fragment form for same-page links.

### Limits

- Anchors are not validated. A wrong heading link fails silently, with no build warning. Check heading links by eye, or open the page.
- Duplicate headings on one page get `_1`, `_2` suffixes on later ids (python-markdown behaviour), which a `[[Page#Heading]]` link cannot target. Give repeated headings explicit ids and link to those.

## Themes (site navigation)

The breadcrumb **Themes** menu and the per-theme landing pages are driven by a dedicated YAML property, **not** by `tags:` (tags are overloaded for styling, so they do not group pages).

```yaml
theme: academic-case-studies
```

- `theme:` takes one value or a list (`theme: [academic-case-studies, methods]`). Values are kebab-case slugs; the menu label is the prettified slug (`academic-case-studies` shows as “Academic Case Studies”).
- Each theme gets a landing page at **`/theme/<slug>/`** listing its pages as search-result-style cards (title plus a short text preview), reachable from the **Themes** breadcrumb menu.
- Landing pages are rebuilt on every run from the `theme` property, so they stay current without a clean build. Drafts (`!` in the filename) are excluded.

## Page styling (for authors)

All of this is controlled from the **YAML block at the top** of a note (`---` … `---`) and from **Pandoc-style classes** on headings, e.g. `## My section {.banner}`.

### Special tags in YAML (`tags:`) -- Obsidian can handle this for you.

Use a list so each tag is one item (recommended):

```yaml
tags:
  - paper
```

| Tag | What it’s for |
|-----|----------------|
| `paper` | “Working paper / article” look: serif body text, calmer page title, no flower icon beside the title, subtle academic styling. |
| `case_study` | “Case study” look: different default colours for auto-styled headings and callouts. Use the **underscore** form `case_study`; `case study` as two words is **not** recognised. |
| `dual-column`, `dual_column`, `two-column`, `two_column` | Turns on **page-wide** two columns in **HTML** (and PDF). Without one of these, the web page stays a single column even if the page is a paper. |

You can also mark a paper-like page with **`type: article`** instead of tagging `paper`.

**If a page has both `case_study` and `paper`:** only **`case_study`** auto-styling runs on the markdown (`##` / `###` / quotes / callouts). The **`paper`** preprocessor is skipped. You can still get the paper **visual shell** (fonts, title band, PDF layout) from `paper` / `type: article`. Prefer **one tag** per page unless you mean to combine them on purpose.

**PDF vs HTML — two columns**

| Situation | Web (HTML) | PDF export |
|-----------|------------|------------|
| `paper` (or `type: article`) only | Single column for the main text | Two-column layout for the body (like a paper) |
| One of the `dual-column` / `two-column` tags | Two-column body | Two-column body |

Section-level two columns (next section) work in both HTML and PDF regardless.

### Automatic heading and quote styling (only with `paper` or `case_study`)

When the page is tagged **`paper`** (or `type: article`):

- Every **`##`** line gets a blue “banner” heading style: `{.banner-info}` (unless you already put `{.something}` with a **class** on that line).
- Every **`###`** line gets a soft rounded box style: `{.rounded-info}`.
- **`>` blockquotes** are turned into **note**-style callouts.

When the page is tagged **`case_study`**:

- **`##`** → green **`{.banner}`** (full-width bar).
- **`###`** → **`{.rounded}`** (rounded box with left accent).
- **`>` blockquotes** → **tip** callouts.
- Explicit **`--{.note}`** callouts are converted to **`--{.tip}`** (same “helpful aside” tone as blockquotes).

To put your own style on a heading, add a **class** in braces. If a class is present, the auto rules **skip** that heading. You can still add an id only with `{#my-id}` — the build will append the default class next to it.

### Manual classes on headings (any page)

You can always set styles explicitly, e.g.:

```markdown
## Methods {.banner}
### Subheading {.rounded-info}
```

Common patterns the CSS knows about (combine with colour suffixes where shown):

- **`banner`**, **`rounded`**, **`rounded-left`** — layout variants (green defaults on the site).
- **`banner-info`**, **`rounded-info`**, **`banner-warning`**, **`rounded-warning`**, **`banner-tip`**, **`rounded-tip`**, **`banner-danger`**, **`rounded-danger`** — Bootstrap-flavoured colour variants.
- Case study defaults use plain **`banner` / `rounded`**. Paper defaults use the **`*-info`** variants.

These affect **both** HTML and PDF (PDF uses print CSS so sizes may look slightly different).

### Images: width and two columns

The same rules apply to **`![](path.png)`** and **`![[path.png]]`** (after the build copies assets and normalises paths).

| Situation | Default | Override |
|-----------|---------|----------|
| **Single-column** page (no `.two-col` section, no page-level dual-column tags) | Image uses **full content width** (`width: 100%`, block). | Add **`{.inline}`** on the image to keep **natural** width (still `max-width: 100%`). |
| **Two-column** region (YAML `dual-column` / `two-column` / …, or a **`{.two-col}`** section, including paper-style PDF bodies) | Image stays **inside one column**. | Add **`{.span-cols}`** so the figure **spans both columns** (wrapper + print-friendly max height in PDF). |

**Size (native Python-Markdown `attr_list` on `![](...)`, same tokens on wikilinks):**

- **`{width=5cm}`** / **`{width=40%}`** → HTML `width` attribute (simple cases).
- **`{style="width:5cm;max-width:100%"}`** → inline style (best for full CSS: any unit, `min-width`, etc.).

Either form **opts out** of automatic full-bleed / in-column classes (same as setting dimensions yourself in HTML).

**Syntax (canonical, `attr_list`):**

- Markdown: `![](my.png){.span-cols}` or `![](my.png){.inline}` or `![](my.png){width=4cm}` or `![](my.png){style="width:40%"}`
- Wikilink: `![[my.png]]{.span-cols}` or `![[my.png|alt]]{width=4cm}` or `![[my.png]]{style="width:40%"}`

An italic-only line after an image is **not** treated specially anymore; use **`{.span-cols}`** when you need a full-bleed figure in a two-column block.

### Section-level two columns: `{.two-col}`

Add **`{.two-col}`** to **any heading** (`#`–`######`). Everything **after** that heading runs in **two columns** until the **next** heading of any level.

This is independent of `paper` and independent of the page-level `dual-column` tags. Use it for a short two-column segment without making the whole page two columns on the web.

### Page-level two columns (full article)

Add **one** of: `dual-column`, `dual_column`, `two-column`, `two_column` to YAML `tags`.

- **Major section breaks:** each **`#`** or **`##`** starts a new block; content below flows in two columns until the next `#` / `##`.
- **Figures that span both columns:** add **`{.span-cols}`** on the image (see **Images** above).

For **`paper`** pages, the PDF path uses two columns automatically even **without** the dual-column tag (see table under **Tags**).

## Notes

- Netlify build command must be **blank** — dist/ is pre-built locally; Netlify just serves it
- Analytics are injected via generated `dist/assets/analytics.js`; GoatCounter and Umami Cloud are configured in `config.yml` and disabled automatically on `file://`
- The output folder is named `dist/` (not `garden_generated_site/`) to keep Windows paths under 260 chars — the repo lives deep in Google Drive and the longer name pushed borderline paths over the limit
- `content/` is also opened as an Obsidian vault — don't alter its folder structure without checking Obsidian compatibility
- **Never rename or move a vault file with `mv`/`Move-Item`/Write.** It breaks `[[wikilinks]]` and `![[embeds]]` (they resolve by basename). Rename either inside the running Obsidian app or via the official CLI: `cmd /c "obsidian rename path=""<folder>/<file>.md"" name=""<new name>"""`. The vault has `alwaysUpdateLinks: true`, so both rewrite every backlink automatically. Editing file contents with Edit/Write is fine; only renames and moves are the problem.
- Right sidebar (TOC, backlinks) hides below 1800px; left sidebar hides below 1200px
- The `999 Causal Map App/` folder auto-generates a contents index page
- In-repo overview for **this garden**: this file (`CLAUDE.md`). **`app-readme.md`** is the long **Causal Map app** help text (different product), not garden authoring.

