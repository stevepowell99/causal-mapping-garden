The [yellow button in the navbar](../navbar-bookmark/) is the fastest way to save useful views of your current project: maps or tables. 
From that one entry point you can quickly save views, update existing bookmarks, and copy links, images, legends, or a combined HTML block (link + image + legend) for reporting.

The bookmarks table itself is not shown for users below Pro level, i.e. to users only on Free or Private plans. 

### Bookmarks Panel {#bookmarks-panel}

In this section you can learn about bookmarking and how to manage bookmarks.

<span class="badge bg-warning text-dark" style="margin-left:6px;">Requires Pro subscription</span>

<div class="user-guide-callout">
<strong>🔖 What you can do here:</strong> Save and organize your favorite views of your data. Bookmark specific filter combinations, map layouts, or analysis states so you can quickly return to important insights later, share clean links, and build reports from saved views.
</div>

To create a bookmark from anywhere, use the [Navbar bookmark button](../navbar-bookmark/). This adds a bookmark to the [Bookmarks table](../bookmarks-table/).

After saving, the navbar bookmark button briefly shows a green tick to confirm the save.

When you save a bookmark in the session, 
- a small popover opens near the button with a Description textarea and a **Save** button (description is optional, but useful).
- inside **Existing bookmarks**, you can pick a bookmark and **Overwrite** it with the current screen state (keeping the same bookmark number/link).
- each bookmark can then be used to copy:
  - a short plain link (`?bookmark=ID`)
  - a formatted link (HTML)
  - the bookmark image
  - combined HTML that includes the bookmark link, image, and legend



#### The Bookmarks Table {#bookmarks-table}

Use the full table / report workflow when:
- you want to work across different projects
- you need more detailed tools for managing many bookmarks
- you want to build a full report from some or all bookmarks

- Each row is one bookmark.
- Click the checkbox  to select rows.
- Click Load  to recall that bookmark, restoring tabs and outputs.
- Quick load: at the very top of the Bookmarks / Reporting tab, you can type a bookmark number and press **Load** (or Enter) to load it directly.
- Click Copy Formatted Link  to copy the bookmark's URL to the clipboard.
- Double-click on the Description field to edit it.
- Click Delete  to remove the bookmark.
- Click the badge at top right  when viewing a map or table to add a new bookmark to it.
- When a new current project is loaded from a URL or by changing the project dropdown, the "Project" filter in the table is pre-filled with the name of the current project.

**Main Features:**
- **Bookmark badge** <i class="fas fa-star"></i> - Save/remove current URL state from navbar
- **Bookmarks table** - Manage saved views with sorting and filtering
- **Bulk operations** - Select multiple bookmarks for deletion
- **Editable descriptions** - Double-click to edit bookmark names
- **Auto-normalization** - URLs cleaned and standardized for consistency

**Bookmarks Table:**
- **Actions** - Load URL, Copy link (plain), Copy formatted link (HTML), Edit URL, Delete individual bookmarks
- **Copy buttons** - Both create short `?bookmark=ID` URLs instead of full parameter strings
- **Columns** - Project, Description (editable), User, URL, Created, ID
- **Bulk delete** - Select multiple with checkboxes, delete with "Bulk:" trash button
- **Badge integration** - Shows bookmark ID when current view is bookmarked

**URL Editor:** 

Click the Edit button <i class="fas fa-pencil-alt"></i> next to any bookmark to open the URL Editor. You can edit the bookmark description (Markdown supported). The editor also provides a user-friendly interface to understand complex bookmark parameters. Instead of viewing raw query strings, you see a structured breakdown with proper labels and grouping - showing your selected project, sources, active filters (displayed as individual cards), table settings, and map configurations. The editor categorizes parameters into logical groups (Navigation, Data Selection, Filters & Processing, etc.) and displays filter pipeline details with sequential numbering and status indicators. This makes it easy to understand exactly what state each bookmark preserves without needing technical knowledge of URL parameters.

<!---

**Complete state preservation** - Your entire analysis view is saved in the URL for easy bookmarking and sharing.

**What gets saved:**
- Active tabs and panel selections
- Window layout (pane width)
- Selected project and sources
- All filter pipeline settings
- Custom column configurations
- Table states (sorting, pagination, filters)

**Smart filtering** - Only saves filters that differ from defaults to keep URLs clean and readable.

**Bookmark URL format** - Copy link functions create short URLs with `?bookmark=ID` parameter instead of long parameter strings. When visited, the system automatically loads the bookmark's full state.

**State restoration** - Page reload restores your complete analysis exactly as you left it.

When copying a formatted or unformatted URL using the File menu, the app copies the short form using the bookmark ID (e.g., `?bookmark=abc123`), and the URL state handler loads the full state from that ID.


**Bookmarking Support:**
Application state is preserved in URL parameters for:
- Active left and right tabs
- Left pane width
- Selected project and sources
- Filter pipeline configuration
- Custom column settings

**State Persistence:**
- URL serves as primary state storage
- LocalStorage provides secondary backup
- All sliders and interface controls included
- Table filter states, column sorting and pagination preserved
- Page reload restores complete application state

Filters are saved to the URL only when:
- They are enabled, and
- They differ from their default settings.
Disabled/inactive/default filters are omitted, keeping the URL clean.

**Bookmark Parameter Handling:**
- URLs with `?bookmark=ID` automatically redirect to the bookmark's full URL before app initialization
- File menu copy functions create short bookmark URLs instead of full parameter strings
- Bookmark IDs are used as display text in formatted links (e.g., `#abc123`)
- Page reload ensures proper widget initialization with complete state
- Provides clean, shareable URLs while preserving complete application state
- Backward compatible - existing full URLs continue to work normally
-->


#### Building reports from the Bookmarks table {#report-builder}

The Bookmarks table lets you create professional reports by combining multiple bookmarked views with custom descriptions and variant filtering.

<span class="badge bg-warning text-dark" style="margin-left:6px;">Requires Pro subscription</span>

<div class="user-guide-callout">
<strong>📊 What you can do here:</strong> Build multi-slide reports from your bookmarks. Add markdown descriptions, choose variant fields/values from your current filtered data, reorder slides, and export as formatted HTML or PDF. This is useful for producing stakeholder-ready outputs from saved app views.
</div>

**Key Features:**
- **Drag-and-drop reordering** - Arrange slides in any order
- **Markdown descriptions** - Add rich text titles and explanations with heading styles, lists, and formatting
- **Variant generation** - Create multiple versions of the same bookmark view filtered by selected field values
- **Include/Exclude toggles** - Selectively include slides in your export
- **HTML/PDF export** - Copy formatted HTML or export PDF with clickable bookmark links and legends
- **Persistent settings** - Your slide order, descriptions, and include/exclude states are saved automatically

Legends:
- For maps we use the full legend
- For tables we use the relevant parts of the legend, omitting material about link and factor colours, sizes and annotation. 

Variants:
- Variants simply add an extra filter on top of the bookmark’s existing filters (sources + filter pipeline). We do not change any other filters. For example, if the bookmark has 4 selected sources and you choose village=X and Y, then the X variant uses only those of the 4 sources with village=X, and the Y variant uses only those with village=Y. If a value has no data after the existing filters, no variant is produced.  


Where to find the variants: when the accordion section is open, the variants appear as thumbnails above the main bookmark image, each preceded by which variable/value it represents (e.g., village: Y). On PDF export and copy to clipboard, first the original bookmark image and its legend are shown, and then each variant with its fullsize image and legend.



**How to use:**
1. Create bookmarks of your maps and tables
2. Switch to the Report tab (yellow bookmark icon)
3. Click on slide descriptions to edit them (supports markdown: `# Heading`, `## Subheading`, `- List items`)
4. Drag slides to reorder them
5. Use the variant controls to generate multiple versions filtered by selected field values
6. Toggle "Include/Exclude" to control which slides appear in your export
7. Click "Copy HTML" (or "Export PDF") to export all included slides
8. Paste into Word/Google Docs - headings and links will be preserved

<!-- Technical: Report Builder is implemented in bookmark-manager.js as the ReportBuilder class. It loads bookmarks with their screenshots, allows inline markdown editing with live preview, stores settings in slide_content.report_settings JSONB column, and generates Word-compatible HTML with proper semantic heading tags. Variant metadata is collected from sources.metadata.custom_columns. -->