The **Simple Mode** provides a streamlined AI coding workflow inside the normal left pane. It keeps the app structure familiar while reducing clutter.

<div class="user-guide-callout">
<strong>Quick start:</strong> If you have roughly 5–100 pages of text, you can usually **just run everything** and get decent results. Press **Run all** and let it run. You can then go back and adjust the coding (edit links, tweak prompts, re-run specific steps) if you want. For longer texts or high-stakes coding, work incrementally: use the **source limit** in Auto-code (1, 5, 20%, 50%, 100%) and the **Links limit** in Recode to process a sample first, check quality, then scale up.
</div>

You can activate it with the **"Simple AI coding"** switch just below the Sources bar. When you sign up and choose to have AI options switched on and active, Simple AI is turned on by default. Other users can switch it on later if they wish. 

AI usage consumes **credits** (see [Responses Panel](../responses-panel/)); credits renew monthly and do not roll over. Costs depend on model and workflow, but very roughly you might autocode around 30 pages for about 1 credit.

Users with dedicated AI plans receive a larger batch of AI credits each month; other users receive 10 free AI credits per month (the free credits do not stack with paid plans). 

### The Simple Workflow

When Simple Mode is active:
- the **Sources bar** is hidden (to keep focus),
- the right-hand output tabs stay available,
- the Create/Filter sub-tabs are replaced by one combined simple workflow panel.

The workflow is broken down into six straightforward sections:

1. **Run all**: Optional one-click runner. Press **Run all** to run Auto-code, then Revise codebook, then Recode in order.
   - Runner pre-steps: clears Filter Links, turns filter pipeline on, and (if links already exist) asks once whether to delete all links before starting. You always start fresh.
   - **Recode target suffix**: Choose blank (simpler — synthesised labels go straight into cause/effect) or e.g. _recoded (keeps raw labels, writes synthesised to temp columns so you can compare).
   - Runner uses one top-level confirmation and suppresses the extra per-step confirm dialogs.
2. **Background**: Give the AI project context before coding. A status tick indicates whether enough background text is set.
3. **Auto-code**: This is where the AI reads your documents and extracts causal links. 
   - You can choose to process a small sample first (e.g., `1` or `5` sources) to test your prompt, or process `100%` of them.
   - The "Skip coded" switch ensures you don't waste time and money re-processing documents that already have links.
   - Default model in Simple AI is **Qwen Flash**.
4. **Revise codebook**: Once you have some causal links, the AI can review them and suggest a cleaner, more consistent list of factor labels (a "codebook"). The header tick shows whether the Recode codebook area currently contains suggestions.
   - Includes a **Target clusters** slider (`2` to `50`, default `20`).
   - Optional **Use automatic pre-clustering** switch (default OFF).
   - When pre-clustering is OFF, the AI tries to find the clusters directly from the factor list using the standard Revise codebook prompt. This prompt supports macro replacement: use `[number]` (or `[cluster_count]`) and the slider value is injected at run time.
   - When pre-clustering is ON, the app first groups factor labels semantically using embeddings, then sends those clustered groups to the AI with a separate labelling prompt plus a **Representatives per cluster** slider (`8` to `20`, default `8`).
   - Pre-clustering is more systematic than asking the AI to find all clusters "in its head" from a long raw list. It reduces the black-box / WEIRD-data risk a bit, and may make it easier to preserve more unusual or divergent concepts instead of collapsing them into whatever the model finds most typical.
   - Default model in Simple AI is **Gemini 3 Flash Preview**.
5. **Recode**: Apply the AI's suggested, cleaned-up labels back to your existing causal links. Paste the codebook (from Revise codebook or your own), add a recode instruction, and run.
   - The AI returns index mappings (row → codebook item) rather than full label text, reducing tokens and improving reliability.
   - Default instruction: *"For each raw label give me the NUMBER of the best-matching codebook item by meaning. Use 0 when no codebook item fits. Return only codebook label numbers, never words. Never invent labels."*
   - **Skip recoded**: When on, only processes links that have at least one unrecoded label (cause or effect). Use this when recoding again to focus on remaining work.
   - **Links limit** (1, 5, 20%, 50%, 100%): When not 100%, a random sample of links is recoded. Non-sampled links keep their existing recoded values (or stay blank on first run).
   - The header progress bar is segmented: grey = empty recoded fields, orange = recoded equals original cause/effect, green = recoded non-empty and different.
   - Default model in Simple AI is **Qwen Flash**.
6. **Filter links**: The normal Filter Links panel appears as the final section of the same accordion, so filtering is part of one continuous simple flow.
   - After a successful **Run all**, filters are auto-set to: **Factor Frequency** (top `12`) → **Link Frequency** (top `30`). The global [Label set](../factor-label-set/) controls which `cause`/`effect` columns Recode writes to (no separate “recode suffix” in this panel).

### Run all (Simple AI) {#simple-ai-runner}
- Optional sequencer for the three main AI actions.
- When enabled, **Go** runs Auto-code → Revise codebook → Recode, stopping on the first non-successful stage.
- Before running, it clears filters, enables pipeline, and deletes all existing links (if any) after one confirmation — so you always start from a clean slate.
- **Recode target**: Use the global [Label set](../factor-label-set/) below the Sources bar. Create a new suffix there first if you want Recode to fill `cause_suffix` / `effect_suffix` instead of only the default columns.

### Background (Simple AI) {#simple-ai-background}
- Sets shared project context used by AI coding prompts.
- The status tick indicates whether enough background text is present.

### Auto-code (Simple AI) {#simple-ai-auto-code}
- Runs AI coding across selected/all sources using your prompt and model.
- Use source limit + skip coded options to test quickly and avoid rework.
- Default model is **Qwen Flash**.

### Revise codebook (Simple AI) {#simple-ai-revise-codebook}
- Suggests a cleaner consolidated codebook from existing links.
- Use this after you have enough coded links for a representative sample.
- Header tick indicates whether the Recode codebook area currently has content.
- Includes **Target clusters** slider (2-50, default 20).
- Optional **Use automatic pre-clustering** switch (default OFF).
- With pre-clustering OFF, the AI clusters the factor list directly from the Revise codebook prompt. That prompt supports `[number]` / `[cluster_count]`.
- With pre-clustering ON, embeddings are used first to group labels semantically, then the AI only has to label those grouped clusters. This is a bit more systematic, less dependent on the AI doing all clustering internally as a black box, and may help preserve unusual or divergent concepts.
- Pre-clustering also adds a **Representatives per cluster** slider (8-20, default 8) and uses a separate labelling prompt.
- Default model is **Gemini 3 Flash Preview**.

### Recode (Simple AI) {#simple-ai-recode}
- Applies your codebook back onto existing links, turning raw factor labels into cleaner synthesised ones.
- **Recode target**: the global [Label set](../factor-label-set/) (`default` = standard `cause`/`effect`; a suffix = read/write `cause_suffix` / `effect_suffix` in `metadata.custom_columns`, with top-level `cause`/`effect` holding the default-set pair).
- Supports sampled recoding and skip-recoded behavior (skip-recoded only applies when using a non-default label set).
- Header bar shows recode coverage mix across all cause/effect recoded fields.
- Default model is **Qwen Flash**.

### Filter links (Simple AI) {#simple-ai-filter-links}
- This is the same Filter Links workflow, embedded as the final simple-ai accordion section.
- Use it to refine/select links before reviewing outputs on the right.
- Run-all completion auto-applies top-12 factor frequency, then top-30 link frequency (no longer injects the deprecated Temporary Factor Labels filter).

### Advanced Settings
Each section header is clickable and opens/collapses its settings panel. Section headers also include contextual **Help** buttons. The advanced sections are inline (not flyouts), and only one section is expanded at a time.

Inside advanced panels you can:
- Edit the exact **Prompt** the AI uses.
- View your prompt history and load previous prompts.
- Change the **AI Model** (e.g., switch to a "Pro" model for complex reasoning, or a "Flash" model for speed).
- Tweak technical settings like chunk size, concurrency, and temperature.

<!-- 
TECHNICAL DETAILS FOR DEVELOPERS:
- State & CSS: Toggled via `#ai-simple-toggle`. Applies the `ai-simple-mode` class to the `<body>`.
- Layout: Keeps left pane visible; hides `#sourcesHeader`; keeps RHS tabs visible. In simple mode, `#link-tabs` is hidden and `#ai-simple-panel` is shown.
- UI Components: Uses `.ai-simple-section` accordion sections with clickable headers (`setupAiSimpleHeaderCollapse` in `app.js`). Help buttons on each header call `window.helpManager.openToSection(...)`.
- Filter integration: In simple mode, children of `#filter-link-content` are moved into `#ai-simple-filter-content-host` (styled as the panel body; no nested `card` wrapper), then moved back when simple mode is turned off.
- Data Fetching: The coded % bar is updated by `updateAiSimpleCodedPct()` in `app.js`, which calls `DataService.getSourceCodedCounts(projectName)`. It listens to `projectSelected` and `linksUpdated` events via the EventBus.
- Prompts: The textareas in the advanced panels are fully wired into the `PromptHistoryService`, sharing the same history/expand-to-editor logic as the main AI panels. Allowed `public.prompts.type` values are enforced in Postgres (`prompts_type_check`); after pulling schema changes, apply `supabase/manual/expand_prompts_type_check.sql` to your Supabase project if needed. Field→type mapping lives in `DataService._promptHistoryFieldToDbTypeMap()`.
- Prompt history UI (single pattern): shared markup/tooltips in `js/prompt-history-chrome.js` (`promptHistoryChromeHtml`, `fillPromptHistoryChromeHosts` on boot in `app.js`). Filter-bound widgets register **only** via `FilterPipelineManager.syncFilterPipelinePromptHistoryWidgets()` at the end of `renderFilterPipeline` (not from tabs or ad-hoc hooks). See `webapp/!architecture-rules`.
- Simple AI: `RAGManager.setupAiSimplePromptHistoryWidgetsOnly()` **first** calls `AIManager.setupAiSimplePromptHistory()` so Auto-code registers whenever Revise/Recode/etc. do (URL restore, Create tab, toggle). Do not wire Auto-code prompt history only from `ai-manager` in isolation.
- `PromptHistoryService.loadHistory`: **no** textarea↔saved-row text matching on load. Rules: empty history → `defaultPrompt` only; non-empty → **newest (`index 0`)** on first load; `forceReload` → re-select prior row by `promptKey`/normalized text if still present, else newest. `savePrompt`: **no-op** when normalized text equals newest row; after a real save, selection forced to newest. Dropdown placeholder: **— Not in history —** (explicit unbound choice).
- AI subscription gating: `AIManager.applySubscriptionGating()` only clears `disabled` on controls marked `data-ai-subscription-gated` when the user gains AI access, then calls `updateAiSimpleSectionsState()` so Auto-code / Revise / Recode rules stay correct (blanket re-enabling of every `#ai-panel` button was removed).
- If a real edge case appears (e.g. must wire a filter before the first pipeline render), we can **add a targeted hook back** — but document it next to this bullet and prefer extending `syncFilterPipelinePromptHistoryWidgets` first.
- Safeguards: If a user tries to Auto-code >100K tokens but has coded <10% of their sources, `ai-manager.js` intercepts the action and injects a warning into the `showAIConfirmModal` to prevent accidental massive spends on untested prompts.
- Recode: Uses `scoreFactorsBatchForRelabel` with `codebookLines`. When codebook is provided, the AI returns `{"mappings":[[row,codebook],[row,codebook],...]}` (1-based indices; 0 = no match) instead of full label text. Fewer tokens, easier for models. ai-answers factor-by-factor (no codebook) still uses the full label/new_label format.
-->