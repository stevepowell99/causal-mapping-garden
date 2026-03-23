MapCat is the small chat helper at the bottom-right. **MapCat is available to all users**, even if you do not have an AI subscription or if AI is disabled in your account settings. It is the only AI feature that does not require a subscription or for AI to be enabled, because it does not see your project data.

### What MapCat is for

- Ask how UI controls and workflows work while you are using the app.
- Ask it to open help, highlight controls, and switch tabs/subtabs.
- If MapCat is wiggling, it has a suggested next step (a nudge). Open it to see the message.

### Header controls (top of MapCat panel)

- **Window controls** (group of 3 icons):
  - **Maximize icon**: open MapCat in large centered mode.
  - **Restore icon**: dock MapCat in the normal bottom-right position.
  - **Minus icon**: minimize back to the cat chat-head button.

### Footer controls (bottom of MapCat panel)

- **Contact support**: sends the latest question/answer context to support.
- **Superpowers** (AI plan only):
  - Default is **OFF** (safe mode).
  - When OFF, MapCat can still answer documentation questions and use non-data UI helpers (for example help/hints/tab switching).
  - When ON, MapCat can run data-aware actions (for example sources selection, filter pipeline edits, pivot config), which means project state data is sent to the AI.
- **Clear**: clears MapCat chat history.
- **Send**: sends the current prompt.

### Privacy and data-sharing behavior

- With **Superpowers OFF** (default), MapCat runs in safe mode intended for users who do not want project data sent for AI actions.
- With **Superpowers ON**, MapCat may send project-derived context needed to execute data-aware requests (such as source IDs, filtered link/factor context, and related view state) to the AI service.

### Safety rules

- UI actions are whitelist-only.
- Project deletion actions are explicitly blocked (`delete/remove/destroy/drop project`) even if requested by a tool directive.

<!--
TECH NOTES (MapCat)
- UI: `#docs-bot-toggle-btn` + `#docs-bot-panel` in `webapp/index.html`; styles in `webapp/css/styles.css`.
- Runtime: `webapp/js/docs-bot-manager.js` (chat, nudges, persistence, support handoff).
- Nudge copy source: `webapp/mapcat-nudges.md` (`### <nudge_id>` sections).
- Nudge cooldowns: global 10 minutes (`_nudgeCooldownMs`), same nudge 48 hours (`_sameNudgeCooldownMs`).
-->