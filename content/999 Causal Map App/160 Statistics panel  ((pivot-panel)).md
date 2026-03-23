Use this panel to build pivot tables and charts from your project data with a simple drag‑and‑drop interface. Three subtabs: **Pivot table**, **Summary** (one-dimensional heatmaps for categorical vars with &lt;10 categories, mean/median for continuous), and **All-by-all checks** (pairwise significance tests).

Example bookmark:
- [Comparing groups (gender) — heatmap pivot table](bookmark=267)

### Quick start
This panel is powered by PivotTable.js, which generates most of the UI dynamically. These are the **actual widgets** you can see/use:

1. 👉🏼 **(`Links` / `Factors` / `Sources`)** (Dropdown): `Which table to analyse?` — chooses which dataset to pivot.
2. 👉🏼 **(`After pipeline` / `Before pipeline`)** (Radio buttons): `Which stage to analyse?` — chooses post‑pipeline (matches other panels) vs raw data for the chosen dataset.
3. 👉🏼 **(`Refresh`)** (Button): reloads + re-renders the pivot with latest data.
4. 👉🏼 **(`Sig level`)** (Dropdown): significance threshold for 2-way table tests (0.10, 0.05, 0.01, 0.001).
5. 👉🏼 **(`Copy to Clipboard`)** (Button): copies the current pivot table/chart as an image.
6. 👉🏼 **(`Copy as Table`)** (Button): copies the pivot as tab-separated text — paste into Excel/Sheets to get a properly aligned table (**Table renderer only**).
7. 👉🏼 **(`Download XLSX`)** (Button): downloads the current pivot as `.xlsx` (**Table renderer only**). Merged cells (rowspan/colspan) are expanded so columns align correctly.
7. 👉🏼 **(Help)** (Button): opens help for the Statistics panel.
8. 👉🏼 **Drag-and-drop fields** (field chip list): shows available fields (columns). Drag a field chip into `Rows`, `Cols`, or `Vals`.
9. 👉🏼 **(`Rows` / `Cols` / `Vals`)** (Drag-and-drop drop zones): defines how the pivot is laid out and what values are summarised.
10. 👉🏼 **(`Aggregator`)** (Dropdown): chooses the aggregation function (e.g. `Count`, `Sum`, `Average`).
11. 👉🏼 **(`Vals`)** (Dropdown): chooses the numeric field to aggregate (only appears for aggregators that need it).
12. 👉🏼 **(`Renderer`)** (Dropdown): chooses the output type (table, heatmaps, Plotly charts).
13. 👉🏼 **(`Row Order` / `Col Order`)** (Dropdowns): chooses how row/column keys are sorted.
14. 👉🏼 **(Filter popup on each field chip)** (Popup): include/exclude values for that field.
   - 👉🏼 **(Search)** (Text field): searches within the field’s value list.
   - 👉🏼 **(Checkbox list)**: ticks/unticks specific values.
15. 👉🏼 **(`×` on a field chip)** (Button): removes that field from `Rows`/`Cols`/`Vals`.

### Arrange fields (drag and drop)
- 👉🏼 **`Drag-and-drop list`**: the “pool” of fields you can use.
- 👉🏼 **(`Rows`)** (Drop zone): fields listed down the left side of the output.
- 👉🏼 **(`Cols`)** (Drop zone): fields listed across the top of the output.
- 👉🏼 **(`Vals`)** (Drop zone): numeric field(s) to summarise (when needed by the chosen aggregator).
- 👉🏼 **(Drag within a zone)**: reorders fields.
- 👉🏼 **(`×`)** (Button): removes a field from a zone.

### Choose the calculation ("Aggregator")
- 👉🏼 **(`Aggregator`)** (Dropdown): chooses how each cell is calculated. **Optional** — you can leave this at the default `Count` (no additional variable needed).
  - 👉🏼 **(`Count`)**: how many rows fall into each cell.
  - 👉🏼 **(`Sum` / `Average` / `Min` / `Max`)**: summarises a numeric field.
  - 👉🏼 **(`Unique Count`)**: counts distinct values of a field.
- 👉🏼 **(`Vals`)** (Dropdown): choose which numeric field to summarise (**optional**, only shown when needed).

### Filter or exclude values
- 👉🏼 **(Filter popup on a field chip)** (Popup): include/exclude values for that field.
- 👉🏼 **(Search)** (Text field): narrows the value list.
- 👉🏼 **(Checkbox list)**: include/exclude specific values (includes a “select all” control).

### Sorting
- 👉🏼 **(`Row Order`)** (Dropdown): sorts row keys (e.g. by key or by value, depending on the option).
- 👉🏼 **(`Col Order`)** (Dropdown): sorts column keys.

### Heatmaps and charts
- 👉🏼 **(`Renderer`)** (Dropdown): switches between:
  - 👉🏼 **Heatmaps** (e.g. `Heatmap`, `Row Heatmap`, `Col Heatmap`)
  - 👉🏼 **Plotly charts** (e.g. `Bar`, `Line`, `Scatter`, `Stacked Bar`, `Area`, `Multiple Pie`)

### Export and sharing
- 👉🏼 **(`Copy to Clipboard`)** (Button): copies the current pivot output as an image.
- 👉🏼 **(`Copy as Table`)** (Button): copies the pivot as TSV — pastes as a correctly aligned table in Excel or Google Sheets (**Table renderer only**).
- 👉🏼 **(`Download XLSX`)** (Button): exports the pivot table to `.xlsx` with merged cells expanded so columns align (**Table renderer only**).
- 👉🏼 **(URL state)**: the pivot configuration is saved to the URL automatically, so you can bookmark/share it.

### Significance testing
When you build a **2-way count table** (one field in Rows, one in Cols, Count aggregator), the app runs a statistical test and shows the result below the table.

- **Sig level** (dropdown): choose your significance threshold (0.10, 0.05, 0.01, or 0.001). The test result shows whether the association is significant at that level.
- **Which test?** The app picks the right test for your data:
  - **Chi-squared** when both variables are nominal (e.g. categories with no natural order).
  - **Mantel** (linear-by-linear) when one or both variables are ordinal (e.g. Likert scales, age bands). This test is more sensitive to ordered trends.
- **All-by-all checks**: below the pivot, tick **Run all-by-all checks** and click **Run**. The app tests every pair of categorical variables with 2–10 values, lists them by p-value, and shows heatmap tables for the significant ones. Useful for exploratory analysis when you have several group or rating variables.

### Notes on the datasets
- **Links**: every causal link plus metadata; includes AI fields (e.g. confidence) and reserved columns like `original_cause`, `original_effect`.
- **Factors**: unique factors with frequency, source count, citations, and `original_label` (ALL underlying original labels for the displayed factor, concatenated with line breaks, derived from the current stage's links like `original_cause/effect`).
- **Sources**: document metadata and flattened custom fields (`custom_*`).

💡Tip: For results that match other panels, use **After Analysis Pipeline**.