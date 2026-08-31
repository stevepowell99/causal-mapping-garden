# WFP-Forcier draft: injected Related + mangled copy

`content/800 Case studies/!Copy of World Food Programme, Forcier Consulting ((WFP-Forcier-Consulting)).md`

The garden-wide `<!-- xrefs-v1 -->` "Related" cleanup (2026-06-24) handled every page except this one. It is a draft (`!` prefix, so excluded from nav/search/PDF) but still builds to HTML and to the short route `/wfp-forcier-consulting`, where it shows a stray `## Related`.

Two problems:
- It looks like **two case studies concatenated**: the WFP-Forcier note (2022-09-19, `## Summary`) then, from line ~26, a second article ("Summarised from AI-assisted causal mapping: a validation study", 2026-03-03).
- An injected `## Related` + `[[... case-studies|chapter intro]]` bullet sits between them (lines ~22-24), so it is mid-document, not trailing, and the cleaner correctly left it alone.

It carries a `<!-- mist:banner -->` "open for collaborative review on mist; avoid editing in Obsidian" warning, so it was left untouched to avoid clobbering the mist review.

xkWAITING (mist review). When the mist review is done, decide: delete this stale "Copy of" duplicate outright, or strip the injected `## Related` block (lines ~22-24) and split/repair the two merged articles.
