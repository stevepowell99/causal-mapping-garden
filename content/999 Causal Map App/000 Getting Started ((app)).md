🎉 **Welcome to CausalMap!!** 

📺 If you like learning through video, there are some short Causal Map videos to get you started: [here](https://www.youtube.com/watch?v=YskPTmWfADw&list=PLSCKdSxlLlfGfcab5njcT57xzU0hOURc-). Or keep reading this Guide!

### Try this: code the short example project: {#try-short-example-project}
- We've created a practice project for you called `example-short-[your-username]`. This gives you your own copy of our tutorial project to experiment with freely. (If you selected the AI option during onboarding, you will receive an uncoded version of this project so you can try running the AI yourself). **You should see it** in the [Project Dropdown Menu](../project-selector-dropdown/) at top left of the app. 
- **Select source `1`** in the source selector. This will display the text from this source. (If you have the standard example project, this source is already partially coded for you).
- **Practice highlighting causal claims** in the [Source Text Viewer](../text-viewer-content/) to **create links** in the [Create Links tab](../create-link-tab/).
- **View, edit or delete existing links** in the [Source Text Viewer](../text-viewer-content/) in the [Create Links tab](../create-link-tab/) by clicking on the highlighted sections of text or on the corresponding links in the Map.
- **Watch** the causal relationships grow in the [Map panel](../map-panel/)

### Try this: view some examples of what you can do. {#bookmarked-examples}

These examples are views of a real-life, anonymised [QuIP](https://bathsdr.org) project in the field of international development. 

- Main factors [map](bookmark=266).
- Main factors [table](bookmark=257).
- Consequences of increased knowledge [map](bookmark=262).
- Comparing groups (pivot heatmap) [table](bookmark=267).


You can find them in the [Project Dropdown Menu](../project-selector-dropdown/). 

### Get help / read the documentation {#get-help-documentation}
The documentation you are reading now is embedded in the app via the [Help System](../help-system/) and is also available as a standalone [Guide](garden.causalmap.app).

Each section corresponds to a different part of the interface. 

Within the app, you can:
 - click the blue help buttons to find out more about the different parts of the app
 - use the top bar buttons described in [Navbar](../navbar/) (Help, Guide, Bookmark, and Support chat).

<!--
TECH NOTES (support chat)
- UX: `#support-btn` opens `#support-modal`. User sees `#support-chat-history` + compose box.
- Backend: user messages call Supabase Edge Function `support-slack` (env `SLACK_WEBHOOK_URL`).
- Persistence: messages stored in `public.support_messages` (see `supabase/support_messages.sql` for table + RLS).
- Admin UI: Admin tab → "Support Inbox" reads from `support_messages` and inserts admin replies.
- Polling:
  - Admin inbox refreshes every ~5s while Support Inbox accordion is open.
  - User client polls every ~6s for latest admin reply; highlights support button on unseen replies.
- Slack formatting: uses `<url|open>` so the link text is compact.
-->

### But what even is causal mapping?

This Guide is all about how to use the app. For example it tells you how to use the different [filters](../filter-system-overview/). If you want to find out more about the ideas behind those filters, we have a new "[Ideas Garden](https://causal-mapping-garden.netlify.app/)" with a more discursive look at the theory and everything that surrounds causal mapping. It's a work in progress but we are adding material every day, please bear with us.

### Someone shared their work with you?

If they have to a particular map (or table), click the link and you will be automatically taken to view the corresponding map (or table), providing they have given you the correct permissions.

Alternatively if they have just asked you to log in at the app to explore a file name, say "project-x", log in and click on the dropdown list on the left-hand side and click on `project-x` to load it. If you can't find that file name, it means they haven't correctly shared it with the email address you logged in with.