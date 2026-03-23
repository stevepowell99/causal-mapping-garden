- A mobile-only two-button toggle (Left side / Right side) sits next to the brand.
- Tapping Right side opens the offcanvas that contains the right pane (tabs and content).
- Tapping Left side closes it. The active side shows a tick.
- The offcanvas shows a "Back to left side" button at the top to close it.
- On desktop (≥ lg), the right pane behaves exactly as before; offcanvas visuals are disabled via CSS.
- A mobile-only Menu consolidates: About, Guide, Help, Bookmark, and Account/Login/Logout.
<!--
Technical notes
- HTML: `right-pane` is now `offcanvas offcanvas-end` with `id="right-pane-offcanvas"`; navbar includes a `d-lg-none` button with `data-bs-target="#right-pane-offcanvas"`.
- CSS: Below lg, the offcanvas is full-width and the central resizer is hidden; above lg, offcanvas positioning/animation is neutralized so layout is unchanged.
-->