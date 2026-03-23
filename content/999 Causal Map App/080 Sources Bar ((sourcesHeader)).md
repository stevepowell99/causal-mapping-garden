<div class="user-guide-callout">
<strong>📄 What you can do here:</strong> Choose which source documents (e.g. interviews or reports) from your current project you want to focus on. You can select one or more sources. Use this to narrow your analysis to specific interviews, reports, or other source materials. 
- The text of the selected source is shown below in the Create Links panel.
- Selecting these sources also fetches only their links and no others, starting off the [Links Pipeline](../links-pipeline/): only the links from the currently selected sources are available for further filtering, and are finally shown in the output tabs.
</div>

### Factor label set (global) {#factor-label-set}

Treat **label sets** like **different versions of the same document**: you keep a **default** “main” version (the usual factor labels on each link) and you can spin up **extra named versions** to experiment—try a different coding scheme, run [Simple AI Recode](../simple-ai-recode/) on a copy, or compare schemes—without changing the main story until you choose to. **Most people** finish by **copying one experimental version back into the default** so the map and tables show that version as the “real” one, while the other versions stay in the project if you need them later.

- **Which version am I using?** The **Label set** row sits under the Sources bar. Pick **default** for the standard labels; pick or create another name to view and edit **that** version’s labels in the [Links Pipeline](../links-pipeline/), map, links table, and link editor. Switching sets refreshes those outputs so they match.
- **New experimental version:** type a new name and confirm. The app fills a new column-pair for **every link** from what you were just looking at, then switches you to it — handy before Recode so the AI writes into the experiment, not the default.
- **Done experimenting — make it “official”:** if you want, open the **⋯** menu (only when a non-default set is selected) and choose **Promote to default**. That copies the **current** experimental set into the **default** columns for every link. Your other named versions are **not** deleted; they remain available if you switch back.
- **Temporary Factor Labels** (old filter in the pipeline): **deprecated** for new work—use this control instead; old bookmarks may still reference the filter.

<!--
Technical (implementers): URL state `factorLabelSet` / `fls`. Non-default labels live in `links.metadata.custom_columns` as `cause{suffix}` / `effect{suffix}`; enriched rows expose `l_cause{suffix}` / `l_effect{suffix}`. Top-level `links.cause` / `links.effect` hold the default pair (may be empty when a link was only coded in a suffix). `DataService.applyFactorLabelSetView` runs at the start of `applyAllPipelineFilters`; alternate sets do not fall back to top-level when suffix columns are empty. Output cache keys (`_computePipelineHash`) include the active suffix. `copyFactorLabelSet(project, from, to)` with `to === ''` implements Promote. Bulk label-set writes emit `linksUpdated` from the widget after `suppressLinksUpdatedEvent` batch updates.
-->

### Sources Dropdown {#sources-dropdown}

- 👉🏼 **Sources** (multi-select dropdown): pick one or more sources from the current project (typing searches the list).  
- 👉🏼 **Empty selection**: means “all sources”.

**Default behavior when switching projects:**
- When you load a project via the **Project Dropdown** or **Projects Panel**, and nothing else specifies which sources to load, the app auto-selects the **first source** so the Source Text Viewer shows something immediately.
- When loading from a **URL/bookmark**, we do **not** change the sources selection. An empty Sources selection means **all sources** (by design).
<!-->
- Ordering: alphabetically by source title (with any leading "Source " stripped),
  falling back to ID when title is missing. Next/Previous navigation uses the same order.
 
 - Opening behavior: if a source is currently selected, opening the dropdown will
   start at the next source after the current one (wrap-around at end). If no
   source is selected (empty dropdown), it starts at the first source.

 - The dropdown does not auto-open when sources are updated; it only opens on
   explicit user interaction (click/focus).

-->   

### Source Groups sub-panel{#source-groups-sub-panel}


<div class="user-guide-callout">
<strong><i class="fas fa-layer-group"></i> What this does:</strong> Filter your analysis by participant demographics or document characteristics, using the [custom columns](../custom-columns/) you have defined for your project. For example, show only responses from "women aged 25-35" or interviews from "urban areas." Perfect for comparing how different groups see causal relationships. 
</div>


**Controls**:  
- 👉🏼 **Field** (dropdown): choose which source metadata/custom column to group by (includes built-in fields like title/projectname).  
- 👉🏼 **Value** (multi-select dropdown): choose one or more values (list is filtered by Field).  
- 👉🏼 **Random N** (buttons): load a deterministic random sample of sources from the whole project (e.g. Random 5 / 10 / 20).  
- 👉🏼 **Random N / Group** (buttons): after choosing Field, load up to N deterministic random sources per value of that Field.  
- 👉🏼 **Clear** (button): reset the Source Groups selector.

The sampling buttons make a random selection, but deterministically, so the same sources are chosen again if you click the same button again.

The second, "Value" dropdown is filtered to show only valid values for the selected field. Previous/next buttons cycle through values of the selected group. 

The effect is to retain only links where the selected custom column has the selected values.

This dropdown is  NOT a filter and it does NOT get saved/restored in URL. It is a loader: when we click it, the app automatically loads corresponding sources into the sources selector. These sources then DO form part of the links pipeline and ARE restored from the URL.

There is a similar filter in the [Analysis Filters](../filter-link-tab/).