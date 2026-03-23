---
date: 2025-04-09
---

# Recoding labels temporarily

Sometimes you want to improve your factor labels (cause/effect text) without changing the original data. You might want to:

- **Experiment safely** — try different prompts or AI settings without overwriting what you coded
- **Iterate** — run factor relabelling several times, refining the prompt each time, until you’re happy
- **Compare** — switch between original and improved labels to see the difference
- **Review before committing** — only merge into the main cause/effect fields when you’re satisfied

The app supports this with two features that work together: **Temporary Cause/Effect Fields** (a filter) and **Target suffix** (in AI Answers → Factors).




## How it works

1. **Create temporary columns.** When you run factor relabelling, you can choose a “Target suffix” (e.g. `_temp` or `_version1`). Instead of overwriting `cause` and `effect`, the AI writes to `cause_temp`/`effect_temp` (or `cause_version1`/`effect_version1`). Your original labels stay untouched.

2. **Show them on the map.** Add the **Temporary Cause/Effect Fields** filter in the Filter Links tab. Point it at those same columns (e.g. cause_temp, effect_temp). The map will display the recoded labels instead of the originals.

3. **Iterate.** With the filter active, you can run factor relabelling again. The AI will work on the *current* temp labels (what you see on the map), not the originals. So you can refine prompts, fix odd results, and run again — all without touching the underlying data.

4. **When you’re happy**, you can
	1. leave one or more sets of temporary columns as a separate view for analysis. You can switch between different sets and the permanent labels with the Temporary filter.
	2. or rewrite the permanent cause/effect labels with these temporary labels if you want to make the changes permanent. The easiest way to do that is to apply just the Temporary filter and then Save As Currently Filtered. 

## Summary

- **Why:** Experiment, iterate, and compare label improvements without changing your original coding.
- **How:** Use a Target suffix when running factor relabelling, then add the Temporary Cause/Effect Fields filter to display those labels on the map. You can then run factor relabelling again to refine the temp labels further.
