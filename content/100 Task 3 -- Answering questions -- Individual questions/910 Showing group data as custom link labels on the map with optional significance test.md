
Custom Links Label can use **any field that exists in the current links table**.
  

That includes:
- **existing fields** already in links (e.g. `sentiment`, tags, AI metadata you’ve stored)
- **source custom columns** that are joined onto links (e.g. `custom_gender`, `custom_village`, `custom_region`)
- **fields created by filters** (e.g. **Tribes** adds `custom_tribeId`)


That’s what **Custom Links Label** does: it configures the map’s **Link Labels** to show a compact summary per connection.

## What is being summarised?

The map groups links into **bundles** by cause→effect.  

For each bundle (say `Education → Employment`) Custom Links Label looks at the links inside that bundle and summarises the selected field.

Common choices:
- after Tribes: `custom_tribeId`
- for subgroup comparisons: `custom_gender`, `custom_village`, `custom_region`
- for link-level fields: `sentiment` (or any other link metadata you’ve added)

## Counts: Sources vs Citations

Before choosing a display mode, decide what a “count” means:
  - **Sources** (default): each source counts once per value in the bundle (unique `source_id`)
- **Citations**: each link counts (raw link count)

If some sources produce many more links than others, **Sources** is usually the more interpretable option.

## Display modes

Assume you pick field = `custom_tribeId` (or `custom_gender`) and Counts = Sources.

### Tally

Shows counts per value in the bundle.

Example label on an edge:
- `T1:4 T2:1`

Interpretation: 4 sources from tribe T1 and 1 source from tribe T2 contain at least one link in this cause→effect bundle.

International development-style example:
- Edge bundle: `Cash transfers → Food security`
- Label (Counts = Sources): `T1:9 T2:2`
- Interpretation: this connection is mainly supported by sources in tribe T1 (e.g. “economic buffering” story), with a smaller contribution from T2 (e.g. “market/price volatility” story).

Example using an existing source custom column (Counts = Sources):
- Field: `custom_gender`
- Edge bundle: `School fees → Dropout`
- Label: `Female:7 Male:2`
- Interpretation: more sources coded this link in the “Female” group than in the “Male” group (but you still need a baseline-aware view before calling it “a real difference” — see chi‑square).

### Percentage

For each value, shows:

\[

\text{percent} = \frac{\text{count of this value in this bundle}}{\text{total count of this value across all currently filtered links}} \times 100

\]

Example label:
- `T1:18% T2:6%`

  

Interpretation: 18% of T1’s total (source-based) participation in the *current filtered map* appears in this one bundle.

This is a “share of that group’s activity” view.

### Chi‑square (significance)


Where:
- `45` is the bundle size in the chosen Counts unit
- `4/5` means observed 4 out of value-total 5 (again in the chosen Counts unit)

International development-style example (Counts = Sources):
- Bundle: `Drought → Migration`
- Label: `18 (T3⬆, T1⬇)`
- Interpretation: the “climate shock” tribe (say T3) shows up in this link bundle more than expected given how often T3 appears in the filtered map overall, while T1 shows up less than expected.

## A worked mini-example (Sources)

Suppose in your current filtered map:
- grand total sources represented across all links = 50
- value total for T1 = 5 sources
- bundle size for `Education → Employment` = 45 sources
- observed T1 sources in that bundle = 4

  Expected T1 in bundle = \(45 × 5 / 50 = 4.5\).  
Observed (4) is slightly below expected, so it would *not* show as over‑represented.

  If instead observed were 5 with the same totals, it would skew upward and might appear as `T1⬆` depending on the chi‑square contribution.

  ## How to use (quick)

  

1. Add **Custom Links Label** to the filter pipeline
2. Pick **Field** (e.g. `custom_tribeId`)
3. Pick **Counts** (Sources/Citations)
4. Pick **Display mode**
5. In **Map Formatting → Link Labels**, select **Custom Links label**

  

That’s it: the map labels update immediately as you tweak the settings.