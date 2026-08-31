# Tidy the Zotero collections behind the public bibliography

The bibliography page at [garden.causalmap.app/bibliography](https://garden.causalmap.app/bibliography/)
is now generated from Zotero by `build_bibliography_md.py`. Only its first
section is. The other three still hold whatever was pasted in by hand, because
their collections are not fit to publish unread.

Run `python build_bibliography_md.py` from the repo root at any time to see the
current version of both lists below.

## Four items that would embarrass us in public

All in `causal-map-used-in-QuIP-bsdr-studies`. Delete them from the collection,
or give them real metadata:

- a LinkedIn tab saved as "(1) Post | LinkedIn"
- "Enkidu", whose URL is `http://localhost:8888/`
- "Qualitative Study of the Social Cash Transfer Programme in Urban Zambia",
  no author and no publisher recorded
- "Pilot Universal Child Benefit Programme in Kenya | UNICEF Kenya", the same

## Twenty-six items that reach no section at all

They sit in the parent collection `causal-mapping-biblio` and in none of its
four children, so nothing on the page can show them. Several are QuIP papers by
Copestake and Remnant that look like they belong under one of the report
headings. Each one needs either filing into a child collection or leaving out on
purpose.

## Then turn the other three sections on

Once both lists above are dealt with:

    python build_bibliography_md.py --all --write

and rebuild the site. Until then the three report sections stay as they are. They
carry two known faults from the hand-maintained era. Four entries appear under
both "Quip / Bath SDR reports and papers" and "Other reports and papers using
Causal Map". A few entries have no blank line between them, so they run together
on the page.

## Also worth a look

Zotero holds duplicate records for the Goddard thesis (one filed as a thesis,
one as a journal article), the Powell, Cabral and Mishan workflow paper, the
Ackermann and Alexander paper, and the Zhang Pool2 paper. Merging each pair
would stop a future rebuild listing one of them twice.

Two publications in Steve's Zotero My Publications have never been on this page
and might belong on it: *Guide to Causal Mapping* (2021) and *An M&E time
machine* (2024). He looked at both on 31 August 2026 and left them off. The note
is here so nobody reopens the question by accident.
