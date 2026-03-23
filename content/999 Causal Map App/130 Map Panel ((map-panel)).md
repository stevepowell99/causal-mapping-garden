<div class="user-guide-callout">
<strong>🗺️ What you can do here:</strong> See your causal relationships as an interactive network map. Drag nodes around, click on links to edit them, and use the controls to customize how the map looks. You can even drag one factor onto another to quickly create new links. This is where your data comes to life visually.
</div>

### Map Controls <i class="fas fa-sliders-h"></i> {#map-controls}
- 👉🏼 **Jump to factor** (type-to-search dropdown): quickly find and select factors on the map (supports multiple selections).
- 👉🏼 <i class="fas fa-redo"></i> **Refresh layout** (button): reset the map layout after zooming/moving.
- 👉🏼 <i class="fas fa-camera"></i> **Copy image to clipboard** (button): copy a high-quality map image for reports/slides.
- 👉🏼 <i class="fas fa-clipboard"></i> **Copy legend** (button): copy the map legend text.
- 👉🏼 **Zoom in/out** (controls): zoom the map view.
- 👉🏼 **Double-click** (gesture): zoom in to that point on the background.

### Map Legend <i class="fas fa-list"></i> {#map-legend}
Discrete text legend showing:
- projectname and included sources
- Citation coverage percentage
- Visual encoding explanations (link sizes, colors, numbers)
- Applied filters summary
  - 💡Tip: Click [Copy legend](../map-controls/) to copy this text to clipboard.
  - You can drag the legend box to reposition it on the map.

<!---

Legend only reports filters that differ from default values. Always ignores text filters with blank fields and path tracing with both fields blank.

Legend format example:
- projectname: foo. Sources included: FX-1, FX-2, FY-3.
- Citation coverage 17%: 135 citations shown out of 786 total for filtered sources
- Link sizes: citation count. Numbers on links: source count. Numbers on factors: source count. Factor sizes: citation count
- Factor colours: outcomeness
- Filters applied: Tracing paths, matching anywhere, 4 steps from `Increased knowledge` (purple borders) to anywhere. Zooming to level 1. Top 10 factors by citation count.

--->

### Map Formatting <i class="fas fa-sliders-h"></i> {#map-formatting-card}

#### Customisable formatting (Things you can tweak)

**Layout and interaction**

- 👉🏼 **Layout** (dropdown): choose how the map is laid out.  
  - Interactive and most other layouts are good while you are conducting your research (fast + supports the [interactive features](../interactive-features/)).  
  - Print/Graphviz is best for static images (reports/journal articles). In Graphviz SVG you can still pan/zoom (mouse wheel, double-click, Shift+double-click).
- 👉🏼 **Groups** (switch): layout maps with top-level factors as boxes which group together their "children".
- 👉🏼 **Initials** (dropdown): add distinctive coloured badges to factor labels in Interactive and Print layouts. Choose which part of the label is used for the badge: Off / Full label / Level 1 (;) / First colon (:) / Square brackets [] / Round brackets (). Uses the same extraction rules as Groups. In Print layout, badges use a gradient for visual distinctiveness.
- 👉🏼 **Direction** (dropdown): LR (default), TB, or BT (for Interactive and Print/Graphviz layouts).
- 👉🏼 **Link direction** (dropdown): Normal (directed arrows) vs Undirected (dots at both ends).  
  - In Undirected mode, dots use the same colours as arrowheads (including sentiment colouring). When sentiment is neutral (0), they use **Link Colour**.  
  - Note: when the [Combine Opposites filter](../combine-opposites-filter/) is active, tail/head can still have different colours.

**Factors**

- 👉🏼 **Factor labels** (dropdown): what to show next to each factor (same data as the [Factors Panel](../factors-panel/)).  
  - Source count (default) / Citation count / Sentiment (mean incoming) / None
- 👉🏼 **Factor colours** (dropdown): Outcomeness (default) / Source count / Citation count / None
- 👉🏼 **Factor sizes** (dropdown): Citation count (default) / Source count / None

**Links**

- 👉🏼 **Link labels** (dropdown): what to show on each link.  
  - Source count (default) / Citation count / Sentiment / Label by Group / Unique Sources / All Sources / Unique Tags / Unique Tags (Tally) / All Tags / None
- 👉🏼 **Link widths** (dropdown): Citation count (default) / Source count / None
- 👉🏼 **Link label font size** (control): change link label font sizes.
- 👉🏼 **Arrowhead size** (control): scale arrowhead size (Interactive + Print/Graphviz). Default 100% keeps current appearance.
- 👉🏼 **Link colour** (colour picker): sets the default link line colour (Interactive + Print/Graphviz). When sentiment is neutral (0), this colour is also used for arrowheads and node borders.
- 👉🏼 **Links highlight** (dropdown): optional extra highlighting without changing the base colour scheme.  
  - Off (default)  
  - Reverse (backwards/same-rank in current layout direction)  
  - Significant (when Label by Group shows ⬆/⬇)  
  - Feedback loop (2 / ≤3 / ≤4 factors)  
  - Feedback loop + reverse (combine the above)

**Other**

- 👉🏼 **Show self-loops** (toggle, default on): show/hide A→A links on the map.



<!---

**Factor Count Display (#factor-count-type):**
Control to display count at end of each factor label in brackets. If set to source count (default), label becomes "foo label (nn)" showing nn sources mentioned this factor.

**Link Label Options (#link-label-type):**
- Source count (default)
- Citation count 
- Sentiment: Mean sentiment for the bundle (-1 to +1)
- Label by Group: Uses field and display mode from Label by Group
- Unique Sources: List unique source IDs in alphabetical order 
- All Sources: List ALL source IDs in order eg M1 M1 M2 M3 M4 M4 M4 etc
- Unique Tags: List unique link tags in alphabetical order eg #hypothetical suspicious
- Unique Tags (Tally): List unique link tags with per-bundle counts eg #hypothetical (3) suspicious (1)
- All Tags: List ALL link tags in order eg #hypothetical #hypothetical suspicious

**Factor Color Options:**
Colors factor backgrounds:
- outcomeness (default, current formatter)
- source count
- citation count
- none

**Self-loops Display:**
Toggle next to #link-label-type "Show self-loops" controls whether to show self-loops from foo to foo.  Default TRUE.

--->


#### Fixed visual appearance (things you can't tweak) {#visual-appearance}

Some parts of the map’s appearance are automatic (i.e. they are not controlled by the Map Formatting widgets above):

**Link geometry (bundling):**
- Links are bundled and drawn as curved edges for readability.

**Automatic colouring overlays:**
- Arrowhead colours reflect mean **sentiment** for that link bundle (neutral uses your chosen **Link colour**).
- When the [Combine Opposites filter](../combine-opposites-filter/) is active, arrowhead colours instead reflect **flipped share** (tail=cause, head=effect).

**Automatic highlighting:**
- Factors that match filters like [Factor Label](../factor-label-filter/) or [Path Tracing](../path-tracing-filter/) show dashed coloured borders.
- Factor border colour reflects mean incoming edge sentiment (but when Combine Opposites is active: average flipped share, blue→red).

<!---

**Link Appearance:**
- Arrowheads colored by mean sentiment of bundled edges
- Color scale: muted blue (+1) → grey (0) → muted red (-1)
- Bezier curved edges with bundling for clarity

**Node Appearance:**
- Size scaled by node degree (with min/max bounds)
- Border color reflects mean incoming edge sentiment (but when Combine Opposites is active: average flipped share, blue→red)
- Missing sentiment values treated as zero for calculations
- Factor background colour varies from white to mid-pale green according to "outcomeness" (in-degree/degree)
- If factors are matched by labels filter or path tracing filter, borders are dashed with special colour

--->



### Interactive Features {#interactive-features}

These work for all layouts except Print/Graphviz layout (which is mostly for static export, but does support clicking nodes/links now).

- **Drag factors** to temporarily reposition them
- **Drag factor to factor** to create new links
- **Shift+drag** for box selection of multiple factors (opens edit modal)
- **Ctrl+drag** for box selection of multiple factors (direct selection, no modal)
- **Click a link** to edit.
- **Click a factor** to edit; shift-click or ctrl-click to add to selection without opening modal.

#### Editing and deleting (multiple) factors
- Select factor(s) by clicking a factor, shift-click or ctrl-click to add more, or shift+drag/ctrl+drag a box around multiple factors, then:
  - Move selected factors together
  - Delete matching factors everywhere or in current view only
  - Rename matching factors everywhere or in current view only

**What does "everywhere or in current view only" mean?**
- **everywhere**: all links containing factors with exactly the selected labels will be deleted
- **in current view only**: all links containing factors with exactly the selected labels (and matching the current filters, i.e. those you can see in the current map) will be deleted


💡Tip: By control-clicking or shift-clicking multiple factors you can easily rename several at once, e.g. you can merge multiple factors as a single factor.


### Grid layout

Factors containing a tag of the form `(N.M)` or `(N,M)` anywhere in the label (where N and M are integers) are positioned on a grid layout. The grid coordinate tags are automatically stripped from displayed labels.
Grid tags can also be **partial**: `(N,)`, `(,M)`, `[N,M]`, `[N,]`, `[,M]` (same meaning; first number = rank direction, second = perpendicular).

**Grid layout toggle:** Enable/disable grid layout in Map Formatting. Defaults to enabled. Disabled automatically when no grid tags are present.

**Interactive Layout:**
- Grid-tagged factors are positioned at their grid coordinates and locked in place
- Other factors with no grid tag are positioned freely within the grid bounds
- Grid bounds: from smallest x -1 to largest x +1, and smallest y -1 to largest y +1

**Print/Graphviz Layout:**
- Grid-tagged factors anchor the initial and final ranks:
  - Factors with minimum rank coordinate (first number) are anchored at `rank=min` (initial rank)
  - Factors with maximum rank coordinate are anchored at `rank=max` (final rank)
- This improves layout stability while allowing Graphviz to position other nodes optimally
- Grid coordinate tags are stripped from labels in the output
- The **perpendicular coordinate** (second number) is not an absolute y-position in Graphviz; it is only used as a **best-effort ordering hint within a fixed rank** (so y-only tags like `(,M)` cannot be enforced unless the rank coordinate is also specified).

**Grid coordinates respect layout direction:**
- **First number (N)** always maps to the rank direction (main flow direction)
- **Second number (M)** always maps to the perpendicular direction
- **BT (Bottom-Top)**: First number = y (rank), y starts at bottom (flip y), second = x
- **TB (Top-Bottom)**: First number = y (rank), y starts at top (normal), second = x
- **LR (Left-Right)**: First number = x (rank), x starts at left (normal), second = y, y starts at top
- **RL (Right-Left)**: First number = x (rank), x starts at right (flip x), second = y, y starts at top

<!---

**Graph Layout:**
- Left-to-right orientation using Cytoscape
- Clickable links open editor or chooser modal
- Visual feedback during selection
- Edge handles for drag-and-drop link creation

**Link Interactions:**
- Clicking on link opens modal with selector to choose specific link to edit
- Causal overlay for editing (from map and links table) has button to open sources panel and textviewer, scrolling to relevant highlight

**Factor Interactions:**
- Factor click opens modal with options:
- Delete factor everywhere (all projects)
  - Delete factor in current filters only
- Rename factor everywhere (all projects)  
- Rename factor in current filters only
- Shift + drag to select multiple factors, then move by clicking and dragging one selected factor
- Box selection: Hold Shift and drag to select multiple nodes, opens same modal as single node selection
- Box selection: Hold Ctrl and drag to select multiple nodes directly without opening modal

**Creation Mode:**
- Drag-and-drop one factor towards another creates new links (using cytoscape "edge handles")
- Causal overlay opens with prefilled cause and effect boxes
- Editable selected_text field prefilled with "manual"
- Toggle between creation mode and normal mode

--->


### Vignettes <i class="fas fa-pen"></i> {#vignette-card}

<div class="user-guide-callout">
<strong>📝 What you can do here:</strong> Generate AI-powered narrative summaries of your causal maps. Choose between a "whole map" summary that covers all the relationships, or a "typical source" story that focuses on one representative case. Perfect for creating reports or explaining your findings in plain language.
</div>

**How to use:**
1. Select your **model** and **region** settings
2. (Optional) Leave **Enable checking (second AI pass)** on to have a checker review and correct the vignette, with its notes shown in a collapsed panel.
3. Choose **Whole Map** or **Typical Source** 
4. Enter or edit your **prompt** (use the navigation buttons to browse previous prompts)
5. Click **Write Vignette** to generate

**Tip (optional): tell the AI which links matter most**
- If you want the vignette to focus on particular connections, go to **Map Formatting → Links highlight** and choose **Significant** or **Feedback loop**.
- When you click **Write Vignette**, the app will include a small list of those highlighted links in the data sent to the AI (so it can focus on them).
- If **Links highlight** is **Off** (or set to **Reverse**), or if no links end up highlighted, **nothing extra is sent**.

**Whole Map**: Creates a summary of all relationships in your current map view. the app provides the following data which is appended to the prompt:
- The overall map (same as you can see) including factor frequencies and bundled causal links with average sentiment
- Up to 30 "typical sources" that tell the most common stories within the current map, with their quotes and metadata including source ID, Title and Filename.

**Typical Source**: Focuses on the single most representative source, showing individual links with quotes and sentiment.

**Output format**: Results are displayed as markdown with support for:
- Headers, bold, italic text
- Bulleted and numbered lists
- Callouts/quotes (using `>`)
- Code blocks

You can edit your prompt to change the tone, audience, or focus before generating. See the [tips on using prompt history](../tips-prompts/) for more details.

**Bookmarking & restore:**
- Each time you click **Write Vignette**, the app automatically saves a **bookmark** for the current view (description: `Vignette (whole|typical): <your prompt>`), and appends the bookmark link at the bottom of the vignette.
- The bookmark footer prints the **model name** used.
- Vignette settings are saved into the **URL state**, so bookmarks restore them (model, region, thinking settings, checking toggle, and prompts).

<!---

**Technical Implementation:**

**Whole Map Payload:**
- Node frequencies and average effect sentiment
- Bundled edges with frequencies and average sentiment
- Typical sources selection: identifies up to 30 sources with "the most typical stories" using a weighted score combining:
  - Number of bundles where the source is represented in at least one link
  - Source count of the bundles they are represented in (weighted by bundle frequency)
- Typical sources JSON includes:
  - Source IDs with custom metadata columns (title, filename, and any custom columns)
  - For each source: list of bundles they participate in (cause, effect)
  - Within each bundle: actual links including quote (selected_text), sentiment, original_cause, original_effect, original_bundle (if present and non-empty), and other metadata fields (ai_sentiment, ai_foo, etc.)
  - If more than 5 links per source per bundle, samples 5 randomly
- Data appended to main map JSON with markdown heading "# Data for typical sources"
- Warning message appended: "Important: do not make anything up. If you don't have all the data you need to carry out the rest of this prompt, say so!"

**Typical Source Payload:**
- Selection normalizes link count by text length (per 1000 characters) to avoid bias towards longer sources
- Selection includes a 50% weight based on the proportion of bundles the source covers
- Includes the full source text (content or text field from sources table)
- Includes individual links with quotes (which are extracts from the full text) and sentiment plus node frequencies

**UI Components:**
- Model dropdown (saved per-project to localStorage)
- Region selection
- Prompt textArea with previous/next buttons and dropdown (saves to prompts table)
- Thinking budget slider (for supported models)
- Write Vignette button sends to AI service, returns markdown result
- Status indicator with spinner during generation

**Default Prompts:**
- Whole map: "This is parts of stories told by several respondents. write a) a local-newspaper style heading (markdown h2) summarising the stories, then a three-sentence summary in simple, straightforward language illustrated with key quotes, and then a one-paragraph more technical summary like in a social science blog, also illustrated with quotes. Note the sentiment field gives the sentiment of the effect of the causal link, from -1 to +1. Note the node labels may not be quite appropriate especially in terms of sentiment / valence so don't get too misled by them."

- Typical source: "This is a typical respondent telling their story. The full source text is provided, and the link quotes are verbatim extracts from that text. write a) a local-newspaper style heading (markdown h2) summarising the story, then a three-sentence summary in simple, straightforward language illustrated with key quotes, and then a one-paragraph more technical summary like in a social science blog, also illustrated with quotes. Note the sentiment field gives the sentiment of the effect of the causal link, from -1 to +1. Note the node labels may not be quite appropriate especially in terms of sentiment / valence so you should definitely mention them if you can but don't worry if they don't fit, find other words instead."

**Markdown Rendering:**
- Custom converter handles callouts (`>`), lists, headers, code blocks, bold/italic
- Callouts styled with left border and background (same font size as body text)
- Lists properly wrapped in `<ul>`/`<ol>` tags
- HTML escaping uses placeholder system to protect generated tags

--->