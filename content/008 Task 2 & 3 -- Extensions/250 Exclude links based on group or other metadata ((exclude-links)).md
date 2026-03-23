---
date: 2025-09-22
---


## Summary

This extension is about filtering links using **metadata** (information attached to links and/or their sources), not just factor labels.

Typical examples:

- include only links from a particular **district / gender / age band**
- exclude links marked with a **caveat tag** (e.g. `?doubtful`)
- include only links with a particular **sentiment** band or code

## When to use it

- **Group comparison**: get a clean view of “group A only” vs “group B only”.
- **Quality control**: exclude links you tagged as weak/hypothetical/needs checking.
- **Scoping**: focus on a section of the material (e.g. a particular question, time period, or separator block) if that exists in your metadata.

## What it does (plain language)

It takes the current links table (already filtered by your chosen sources and any upstream filters) and keeps/removes rows based on:

- a chosen **field** (a column), and
- one or more **values** you want to include or exclude.

## Practical cautions

- **Know what the field means**: some fields live on links (tags, sentiment), others live on sources (custom columns), and some are derived.
- **Order matters**: if you apply transforms that rewrite labels earlier, you may change what you consider “the same” link/factor when comparing groups.

## Formal notes (optional)

This is a links-table filter. Given a predicate \(P(\text{link row})\), it returns:

- include-mode: \(L' = \{ \ell \in L \mid P(\ell) \}\)
- exclude-mode: \(L' = \{ \ell \in L \mid \neg P(\ell) \}\)

The predicate is usually defined by: (field = f) AND (value ∈ allowed set), with UI-specific matching rules (exact match vs substring, case rules, etc.).

## Transformation and interpretation rules {.banner}### Transformation rule {.rounded}- **Input:** a links table and a metadata predicate (field + include/exclude values).
- **Transformation:** apply the predicate row-wise to keep or remove matching links.
- **Output:** a filtered links table/map scoped to the chosen metadata condition.### Interpretation rule {.rounded}- This is a selection/scoping step, not a truth test.
- Result differences usually indicate contextual/group differences in reported claims.
