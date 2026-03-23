<div class="user-guide-callout">
<strong>🗂️ What you can do here:</strong> Choose which Project (project) you want to work on. Use the File menu for quick actions like creating new Projects, uploading documents, or sharing your work with others.
</div>

- A small locked indicator at the top-right of `#project-selector-header` shows only when a project is read-only.
- An archived icon appears only when the project is archived. Archived projects are automatically read-only and only visible to owners, collaborators, and admins (not visible to the public even if marked public).
- **New Project or Upload Sources** <i class="fas fa-plus"></i>: Opens a modal to create a new project or add sources to the current project. Choose files, then Continue. A **Show Advanced** switch (default off) skips the [Confirm Upload](../upload-documents/) screen and uses defaults (keep filenames as IDs, no custom columns, no split). When on, the Confirm Upload modal appears for adjusting filenames, adding custom columns, or splitting sources.


### File menu {#file-menu}
Quick access to common actions:

#### **Manage the Current Project**{#manage-current-project}
- **Edit** <i class="fas fa-pencil-alt"></i>: Modify settings and sharing
- **Upload sources** <i class="fas fa-plus"></i>: Add documents (PDF, DOCX, RTF, TXT) or XLSX with a `statements` tab to the current Project
- **Clone** <i class="far fa-clone"></i>: Create a complete copy of the Project under a new name
- **Merge** <i class="fas fa-code-merge"></i>: Copy sources and links from selected projects into this one
- **Clone filtered** <i class="far fa-clone"></i>: Create a copy of the current Project but only containing the sources and links as currently filtered
- **Archive** <i class="fas fa-archive"></i>: Hide from main list
- **Delete all links** <i class="fas fa-trash"></i>: Remove every causal link in this Project (sources remain)
- **Download** <i class="fas fa-download"></i>: Export as XLSX
- **Versions** <i class="fas fa-history"></i>: Restore and create backups of this Project
- **Update sources (Excel)** <i class="fas fa-file-excel"></i>: Upload an XLSX to update sources in-place ("round-tripping").
  - **Tabs**: Must contain a `sources` tab (lowercase). Other tabs are ignored.
  - **Required** (**case-insensitive headers**): Must include an `id` column. IDs must exist in the current project.
  - **Columns**: You can include only the columns you want to change. Any missing columns are left unchanged.
  - **Updates**: `title`, `filename`, `content` (if those columns exist). Any other columns are merged into `metadata.custom_columns`.
- **Manage projects** <i class="fas fa-folder-open"></i>: Opens the [Projects](../projects-panel/) tab as a shortcut

#### **Create new project**{#manage-projects}
- **Quick upload** <i class="fas fa-plus"></i>: Create a new project or add sources to the current project (same as the green + button in the Files bar)
- **New Project** <i class="fas fa-plus"></i>: Create an empty Project which you can then import sources into
- **Import XLSX** <i class="fas fa-file-excel"></i>: Import a complete new Project from Excel ("round-tripping").
  - **Tabs**: If the XLSX has 1 tab, it is treated as the sources tab (whatever its name). If it has multiple tabs, it must contain `sources` (lowercase); `links` (lowercase) is optional.
  - **Long source text**: If the XLSX contains a `source_content_chunks` tab (exported by this app when source content exceeds spreadsheet per-cell limits), imports will rehydrate `sources.content` from it.
  - **Format note**: CausalMap can import many document/file formats elsewhere in the app, but a BathSDR-style QuIP Excel workbook is not supported by this XLSX importer.
  - **`sources` columns** (**case-insensitive headers**): source id comes from `id` (preferred) or `source_id`; source text comes from `content` (preferred) or `text`. Any other (non-empty) columns are imported as custom columns (into `metadata.custom_columns`).
  - **`links` columns (optional)**: uses `cause`, `effect`, `sentiment`, `tags`, `source_id`, `selected_text` (and remaps `source_id` based on the old ids from the sources sheet).
    - Any other non-empty `links` columns are imported into `links.metadata.custom_columns`.
    - For round-trip consistency, incoming `custom_<name>` headers are normalized to `<name>` before writing `links.metadata.custom_columns`.
- **Import cm3** <i class="fas fa-upload"></i>: Import a complete new Project downloaded from CausalMap3.
  - **Tabs**: Requires `links` and `statements` (lowercase). Optional: `sources`, `questions`.
  - **`statements` columns** (**case-insensitive headers**): requires `source_id` and `text` (optional `statement_id`/`id`, optional `question_id`).
  - **`links` columns used**: `from_label`, `to_label`, `quote`, `hashtags`, `sentiment`, `statement_id` (used to map links to sources via the statements sheet).




### Project Dropdown {#project-selector-dropdown}
- 👉🏼 **Project** (dropdown): lists all the projects you have created or been invited to; selecting one opens it.
- 👉🏼 **On change**: the rest of the app resets to defaults (sources selection + analysis filters pipeline).

- On startup, the app auto-selects the most recent **viewable** project (owned by you, shared with you, or public). 
- Admins can see all projects in the Projects table, but the dropdown never auto-selects or loads a non-viewable project; admins may open the Edit Project modal for non-viewable projects from the table only.


### Project Details button {#project-details}

- A small pencil button sits to the right of the [Project Dropdown](../project-selector-dropdown/).
- Clicking it opens the Project Details screen, the same as you get by clicking the first item in the [File menu](../file-menu/)<!--(alias of `#share-project-btn`)-->, which we describe next:



<!---

**Excel Import/Export ("round-tripping"):**
- Download button exports selected Project as Excel Project with separate tabs for sources and links
- Import button allows uploading Excel Projects to create new Projects
- Upload uses same format as download for consistency
- **Smart ID processing**: 
  - ID: Uses `id` column if available, otherwise falls back to `source_id` column
  - If provided IDs are 8 characters or less, uses them directly (ensuring uniqueness)
  - If provided IDs are longer than 8 characters, applies smart trimming algorithm that removes common prefixes and creates optimal 8-character IDs
  - Falls back to title-based generation if no ID column is provided
- **Content mapping**: Uses `content` column if available, otherwise falls back to `text` column
- Additional columns are imported as custom metadata

**cm3 Format Import:**
- Specialized import for cm3 Excel Projects using "links" and "statements" tabs
- Column mapping: from_label→cause, to_label→effect, quote→selected_text
- Hashtags converted to comma-separated tags
- Sentiment values (defaults to 0 if missing)
- Statement_id joins to statements tab for source_id lookup
- Auto-generated timestamps for created_at field
- Source content created by concatenating text from each source_id and inserting the statement_id (and question_id if present):

statement_id: xyz
question_id: foobar
text text text

etc


also, if there is a tab in the excel sheet called questions and it has columns for question_id and question_text, also join to that data and add question_text: foobar as well

statement_id: xyz
question_id: foobar
question_text: blah blah
text text text

etc

**cm3 Sources handling:**
- When uploading cm3 xlsx, import additional columns in sources tab as custom columns (JSON format)
- Assumes xlsx has sources tab, otherwise skip
- When concatenating statements with same source_id, source_id corresponds to sources tab for additional metadata


--->


### Project Details screen {#edit-project-modal}
Manage every aspect of the current project. You can reach this management pane by clicking Edit from the [File menu](../file-menu/). Manage other projects by clicking the edit button in the corresponding row of the [Projects Panel](../projects-panel/).

<div class="user-guide-callout">
<strong>📄 What you can do here:</strong>

- <strong>Open it</strong>: File → Edit, or the edit icon in the Projects table.
- <strong>When it appears</strong>: Also opens on project load/change unless you turn it off for this project.
- <strong>Save vs instant changes</strong>:
  - Use the <em>Save</em> button to apply changes to <strong>Name</strong>, <strong>Tags</strong>, and <strong>Description</strong>.
  - <strong>Archived</strong>, <strong>Locked</strong>, <strong>Public</strong>, and <strong>Collaborators</strong> update instantly.
</div>

#### Details
- <strong>Name</strong>: Rename the project. Click <em>Rename</em> to save.
- <strong>Tags</strong>: Comma‑separated tags for quick grouping/searching.
- <strong>Description</strong>: Free‑text notes about the project.
- <strong>Edit codebook</strong>: Toggle to reveal a text area where you can list factor labels (one per line). These are added to the cause/effect dropdowns in the link editor; existing options are kept.
- <strong>AI Processing Region</strong>: Choose where AI processing occurs for GDPR/data residency compliance:
  - **EU (Belgium - europe-west1)** - Default. Recommended for EU data residency requirements.
  - **UK (London - europe-west2)** - UK has GDPR adequacy decision, suitable for EU/UK compliance.
  - **US (Virginia - us-east5)** - US East region.
  - Setting is saved per-project and auto-saves on change (with confirmation warning).
  - All subsequent AI coding for this project uses the selected region.
- <strong>Archived</strong>: Hide the project from the main list and make it read-only. Archived projects are only visible to owners, collaborators, and admins (hidden from public view even if marked public). Applied immediately. Unarchiving restores normal visibility and editability.
- <strong>Info line</strong>: Created / Modified / Owner, plus counts for links/sources/words, and quick actions:
  - <em>Versions</em>: Open the versions manager.
  - <em>Delete embeddings</em>: Remove factor embeddings for this project (advanced).
- <strong>Show on open</strong>: Toggle "Show this screen when opening this project" at the top to auto‑open or suppress this screen for this project.

<!-- Technical: AI region setting is stored in projects.metadata.ai_region as 'eu'/'uk'/'us' and mapped to Vertex AI regions ('europe-west1'/'europe-west2'/'us-east5') by AIManager._getVertexRegion(). Default is 'eu'. The setting is passed as vertex_region parameter to the vertex-ai edge function. Data retention: Google's zero data retention policy applies; in-memory caching up to 24 hours (can be disabled); prompt logging for abuse monitoring can be disabled with invoiced billing account. All compliant with GDPR when EU/UK regions selected. See https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/multimodal-faqs -->

#### Sharing
- <strong>Locked</strong>: Make the project read‑only. Editing is disabled until unlocked. Applied immediately.
- <strong>Public</strong>: Allow all signed‑in users to view the project (read‑only). Applied immediately.
- <strong>Collaborators</strong>: See current collaborators, add by email, and choose permission:
  - <em>Viewer</em>: Read‑only
  - <em>Editor</em>: Read & write

#### Bookmarks
- If available, view saved “bookmarked” views of your data and open the Bookmark Manager.

<!---
#### Footer
- <strong>Load Project</strong>: Loads the project into the app workspace.

The Load Project button loads the Project into the dropdown and triggers the Project loading process.
--->


This screen also shows when a project loads or is changed, except:
- for new users (the help drawer is still being opened to welcome them),
- if you have already clicked "don't show" for this project. 



<!---

- When it opens:
  - Automatically on project load/change if not suppressed and no other modal/help welcome is active.
  - From the Projects table (edit action) or other UI buttons.
- What is shown:
  - Header with current project name.
  - Basic Information card (Name, Tags, Description, Save button for these fields only).
  - Compact info line: Created, Modified, Owner. "Archived" switch lives here; "Locked" and "Public" are at the top of the Sharing section.
  - Sharing card (collaborators) and Bookmarks section (if any thumbnails exist).
  - Footer: "Don't show on load" + "Load Project" button only when opened from Projects table.
- Instant persistence (no Save needed):
  - Archived → saves immediately to `projects.archived`.
  - Locked → saves immediately to `projects.read_only`, then instantly re-applies enable/disable and show/hide rules.
  - Public → saves immediately via RPC and updates UI.
  - Collaborators (add/remove) → saves immediately and refreshes the list in place.
- Save button applies only to: Name, Tags, Description.
- Read-only enforcement rules:
  - canEdit = (permission ∈ {owner, editor}) AND not read_only.
  - If not canEdit: disable all inputs/"Don't show on load", "Open Bookmark Manager", context "Load Project", and the "Locked" switch; hide Save/Cancel; hide the Sharing card.
  - If canEdit: enable everything and show Sharing and Save/Cancel.
- Stacking order: the modal/backdrop z-index is raised above the pipeline "Preparing filters" overlay.

--->