---
date: 2026-02-09
tags: ['filters']
---

## Summary

Path tracing is for answering questions like:

- “**How does A lead to B** (through what intermediate steps)?”
- “What are the **main routes** from an intervention to an outcome?”
- “If we start from this driver, what downstream consequences show up **within K steps**?”

It’s best thought of as:

1) a **filter** (keep only links that participate in the traced pathways), plus  
2) an **interpretation rule** (what counts as evidence for a pathway).

## What you get (in plain terms)

You choose:

- a **From** factor (or leave it blank)
- a **To** factor (or leave it blank)
- a maximum number of steps (how long a “chain” you want to allow)

Then the result is a *sub-map* containing only the links that sit on at least one allowed pathway.

## When to use it (practitioner-friendly)

- **Explaining mechanisms**: not just “what matters”, but “how it connects”.
- **Finding mediators**: what sits between A and B?
- **Generating hypotheses**: “these are the plausible routes people describe”, then you go back to quotes to check.

## Source tracing (recommended when you care about coherent stories)

Without source tracing, a pathway can be a *composite*: one source says A→X and another says X→B, so the map can show A→…→B even if no single respondent told the full chain.

**Source tracing** is the stricter version: it keeps only pathways that can be realised **within at least one single source** (a coherent within-source narrative).

Use it when you want to avoid the “stitched together across respondents” problem.

## Practical tips

- **Keep K small**: in interviews, chains longer than ~4 steps are uncommon and get hard to interpret.
- **Be careful with transforms**: if you change labels (Zoom, Collapse, Combine Opposites, clustering), you can change which pathways exist *as labels*. That’s often fine for presentation, but it changes what you are “counting as the same thing”.

## Order matters (a conservative workflow)

If you care about coherent pathways *and* you want a cleaner, summarised map:

- first do **source tracing** (to keep within-source chains)
- then apply label-rewrite transforms (e.g. Zoom / Collapse / Combine Opposites) for presentation

## Formal notes (optional)

If you want the precise definition, here it is.

Given one or more start factors \(S\), one or more end factors \(T\), and a maximum path length \(K\):

- keep a link \(x \rightarrow y\) iff it lies on at least one directed path of length \(\le K\) that starts in \(S\) and ends in \(T\)
- if \(S\) is empty, interpret this as “paths that end in \(T\)”
- if \(T\) is empty, interpret this as “paths that start in \(S\)”

The key is: **path tracing is link-based**. It should not “fill in” extra links between surviving factors.

## Transformation and interpretation rules {.banner}### Transformation rule {.rounded}- **Input:** a links table/graph, optional `From` and `To` factors, max path length `K`, and optional source-tracing mode.
- **Transformation:** retain only links that lie on qualifying directed paths; with source tracing, keep only paths realizable within a single source.
- **Output:** a links table/map containing traced pathway links only.### Interpretation rule {.rounded}- Path tracing shows plausible reported routes under your constraints.
- With source tracing on, routes represent within-source narrative coherence rather than stitched cross-source chains.
