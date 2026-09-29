# NeuroTrace Component Showroom

Open `index.html` directly in a modern browser. No package install or local server is required.

The showroom is a developer-facing preview of the production primitives:

- Tokens, bundled pixel font, and source-derived fixed logo treatment
- Buttons, tags, form controls, evidence cards, execution progress and loading state
- Existing Trace posture PNGs, selected by real UI tabs
- Critical-verification reject/recalculate dialog and dossier export feedback
- A narrow-workbench information hierarchy, not just a reader drawer

Use `../design-system/components.css` together with `../design-system/tokens.css` in the frontend implementation. Do not copy preview-only layout classes from `showcase.css` into application pages.

The progress/log example is explicitly a Fixture. Production run logs must receive only real backend events; do not reuse its labels or values as a mock execution stream.

