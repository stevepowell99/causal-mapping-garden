---
date: 2025-09-22
---

## Summary

Causal mapping doesn’t usually deal with the kind of non-causal themes which are the focus of ordinary QDA (like in NVivo!). However sometimes it can be really useful to be able to simply note the presence of something without any causal connection.

We call this “plain coding”. You can use it for:

1. Noting the presence of something which is not mentioned as part of a causal link in the statement you are coding but does appear *elsewhere* as a causal factor as part of a causal link.
2. …Or noting the presence of something which is “nothing but” a theme and never appears in causal coding.

Causal Map makes this possible in a simple way: we define a “plain coding” as simply a link from a factor to itself with has the hashtag `#plain_coding`.

Factors involved in plain codings (whether some of the time or all of the time) can of course still be involved in hierarchies and opposites coding just like any other factor.

So by default, plain codings will still appear in maps, as self-loops from the factor to itself, although it is possible to exclude such links by using the appropriate transforms filter.

Doing plain coding like this has the big advantage that factors coded with plain codings will still appear in the tables in the ordinary way, so for example the plain coding to (and from) the factor increased income will still count towards its source and citation counts.

It also means that you can easily delete a plain coding from a map by clicking on the link.

The hashtag `#plain_coding` distinguishes plain codings from actual causal links where a factor indeed influences itself, for example if someone says that increased income led to even more increased income – in this case the hashtag is not used. This hashtag can also be used together with other hashtags for the same link in the usual way.

## How the Causal Map app implements this:

See the in-app help section on the Link Editor (Plain coding): https://app.causalmap.app/help-docs#causal-overlay

## Transformation and interpretation rules {.banner}

### Transformation rule {.rounded}

- **Input:** a factor mention you want to record without asserting a causal relation.
- **Transformation:** encode it as a self-link (`factor -> factor`) tagged `#plain_coding`.
- **Output:** a links table/map entry that is filterable/countable but distinguishable from ordinary causal links.

### Interpretation rule {.rounded}

- Plain coding marks presence/theme evidence, not mechanism.
- Keep it separate from real self-causation claims by using the `#plain_coding` tag.



