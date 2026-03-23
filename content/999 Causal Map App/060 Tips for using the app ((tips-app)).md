### Tips for Using the Dropdown Menus {#tips-dropdowns}

There are many dropdown menus throughout the app. 

- Most dropdowns allow multiple selections: you can select more than one thing at once
- Most dropdowns allow you to type and create new entries which are not already in the list. 
  - Type part of a word and click "Create new..." to add new items
  - Press Enter to complete selections
- Pressing Tab always moves you to the next field (doesn't complete selection). See also [Search/replace](../factors-search-replace/) for bulk editing patterns.



#### Edit an item

- **Backspace editing**: Position cursor after an existing selection and press backspace to edit it

Click to the right of the item, then press backspace to edit the label, and press tab to complete. 

![Dropdown editing tip (backspace)](https://live.staticflickr.com/65535/53300744438_69cc2478ac_o.gif)

#### Delete the first and subsequent items using the keyboard

Click after the last item, use the left arrow on your keyboard to go back to previous items, then press Delete on your keyboard to delete items after the cursor.

![Dropdown deletion tip (arrow keys + delete)](https://live.staticflickr.com/65535/53300507671_5e07b43240_o.gif)


### Tips for Using Tables {#tips-tables}

Most tables include:
- **Checkboxes** ☑️ for selecting multiple rows
- **Bulk action buttons** when you have selected one or more rows (edit, delete)
- **Action buttons** within individual rows to apply actions (edit, delete etc) just to that row
- **Filtering** using the filter row below headers
- **Pagination** with 10/25/50/100 items per page
- **Re-ordering columns** by dragging the column headers
- **Sorting** by clicking column headers; use **Shift+click** to sort by multiple columns. The column you Shift+click becomes the primary sort, and the previous column(s) break ties. Shift+click the same column again to reverse its order.

If you want to sort by source count and then by citation count, click first on citation count (click again to sort in the opposite direction) and then shift+click source_count. Shift+click again to reverse the order. Now, we have sorted by source_count but citation_count is used to break any ties. 


### Tips for Using Prompts and other text windows {#tips-prompts}

<span class="badge bg-info text-dark" style="margin-left:6px;">Require an AI subscription</span>

When you use text windows, your texts are automatically saved so you can reuse them later.

**Text history is available in:**
- **AI Coding** (Process Sources tab)
- **AI Answers** (Answers tab) 
- **Map Vignettes** (Vignettes tab)
- **Soft Recode filters** (both label prompts and magnet lists)
- **Auto Recode filter** 

**How to use text history:**
- **Dropdown menu**: Lists saved prompts (newest first). The first real entry is always the **most recently saved** text for that channel.
- **< and > buttons**: Navigate between newer and older prompts (tooltips note that running also auto-saves the current text).
- **Save (disk) button** (where shown): Saves the current text to project history; tooltips note that **running the action also auto-saves** the same way.
- **Text area**: Shows the selected prompt and lets you edit it.
- **Expand button**: Optionally edit your text in a larger editor (multiple cursors, search/replace, etc.).
- **Trigger button**: Runs the AI with your current prompt and saves it to history.

**What loads when you open a panel**
- If you **already have saved prompts** for that feature, the box loads the **newest** one and the dropdown points at it — not whatever happened to be in the field from a bookmark/URL default.
- If you have **no** saved prompts yet, you see the **built-in default** for that feature (from app defaults / `prompts.json` where applicable) until you save or run.
- The dropdown can include a row **— Not in history —**: that means you are **not** tied to a saved row (e.g. you picked that option after editing). Normal use does not require it.

**How prompts are organized:**
- Your current project's prompts appear first (most recent at top)
- Then prompts from other projects you can access
- Each prompt shows when it was last used
- Duplicate prompts are automatically removed

**Using the controls:**
- Select any prompt from the dropdown to load it
- Use < and > buttons to move through your text history
- Edit the prompt in the text area as needed
- Click the action button (Process, Ask, Generate, etc.) to run it

**Saving:** Manual save and run both persist the current text. If you try to save text that is **already identical** to the **newest** saved prompt (same wording), the app skips writing a duplicate row.

Tip: Any lines beginning with // in your prompt will be recorded in the history etc but not actually sent to the AI. You can use this to make notes e.g. at the top of your prompt: "//Sarah's version with tweaked summary"

<!---
#### ai coding prompts
Trigger:  Process Sources

####  auto labelling 
#dev-soft-recode-next-prompt
Trigger: Insert button

#### Magnets widgets 
(#dev-soft-recode-prev-magnets-filter etc) Trigger: Save button

#### AI answers
Trigger: ##rag-submit-btn
#### Map Vignettes (here we need two sets of widgets, remove the old one. )




Timestamps come from project metadata (metadata.aiPromptsTimes[prompt]), not local storage. If you see only "—" for older prompts, that means those prompts don't have a stored last-used timestamp yet in the DB. Once you use/save a prompt, its timestamp is written to metadata and will appear thereafter.

Pressing Process Sources upserts the prompt with new timestamp to the db. 

--->