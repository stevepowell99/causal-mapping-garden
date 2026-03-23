The Logs tab shows a concise history of what has happened in your projects – for example, when links or sources were edited or deleted, when projects were created, or when AI processing ran.

- Use the **scope buttons** (This project / All projects) to switch between seeing activity only for the current project or across all projects you have access to.
- Use the **filters above the table** to narrow by user, project name, action type, date, or text in the details column.
- Non-admin users see only activity for projects they own or can edit; admins can see activity across all projects.
- Navigation and other UI clicks are logged only very briefly and are hidden from non-admin users.

<!--
TECHNICAL DETAILS – LOGS PANEL

- Database: Logs are stored in the existing `user_analytics` table, which references `auth.users` (not `profiles`).
- Privacy architecture: Queries never join directly to user tables for display; email lookups are done in a separate step to keep data boundaries clear.
- Tracked actions (core set so far):
  - `navigation` (tab/page changes – logged only for the first 50 actions per user and never shown to non-admins)
  - `project_created`, `project_deleted`, `project_renamed`, `project_archived`, `project_unarchived`
  - `source_uploaded`, `source_updated`, `source_deleted`
  - `link_ai_inserted`, `link_manual_inserted`, `link_updated`, `link_deleted`, `links_deleted_all`
  - `ai_processing` and other AI-related events
- Implementation:
  - `ActionLogger` is the only class that writes to `user_analytics`. It:
    - enforces the 50-navigation limit per user (per browser) via `localStorage`,
    - skips logging for admins by default, unless called with `{ force: true }`,
    - fails silently so logging can never break the app.
  - For links/sources/projects, all logging now flows from centralized write helpers in `DataService`:
    - link updates/deletes go through `DataService.updateLink`, `DataService.deleteLinksByIds`, `DataService.deleteLinksBySourceIds`, `DataService.deleteAllLinksForProject`,
    - source updates/deletes go through `DataService.updateSource` and `DataService.deleteSourcesByIds`,
    - project-level changes will be migrated into `DataService.Projects.*` helpers.
- Logs panel UI:
  - Uses a Tabulator table in `admin-manager.js` with manual server-side pagination via `DataService.getAdminActionLogs`.
  - Filters are external inputs above the table, wired to `getAdminActionLogs`:
    - user (email, via `profiles` lookup),
    - project (from metadata or URL query param),
    - action (`event_type`),
    - date (day-range on `created_at`),
    - details (full-text search on anonymized metadata fields).
  - Scope buttons:
    - “This project” injects the current project name into the project filter.
    - “All projects” leaves the project filter as typed by the user.
  - Gating:
    - Logs tab is visible only for Team+ users (`capabilities.canViewLogs`),
    - Admins can see all projects; non-admins see only projects where they are owners or editors (enforced via RLS and server-side filters).
-->