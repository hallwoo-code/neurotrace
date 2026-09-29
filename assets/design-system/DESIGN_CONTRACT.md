# NeuroTrace Visual Asset Contract

This package is the implementation source for the frozen low-pixel NeuroTrace review set. It intentionally converts visual rules into tokens and primitives, so implementation does not have to repeatedly infer details from raster mockups.

## Fixed decisions

- Logo: use `neurotrace-logo.svg` everywhere. It wraps `neurotrace-logo-source.png`, a transparent extraction from the approved entry-screen logo lockup; do not redraw or typeset the wordmark independently.
- Canvas: midnight navy. Panels are navy, not glass. Evidence cards are warm grey paper.
- Geometry: 8px base unit, 2px hard pixel borders, square corners, 4px offset pixel shadow only where a sheet is above the canvas.
- Status semantics: teal = supporting/verified, amber = qualified/pending, dark red = counter/rejected. Always pair colour with a tag label and icon/marker.
- Trace: use the existing four PNG posture sprites. Hats remain intentional; pipe, deerstalker, Baker Street and other traditional detective signals remain prohibited.
- Typography: `fonts/z-labs-pixel-12px-cn.woff2` is the bundled Chinese pixel typeface, including its OFL notice. It is the first choice for the wordmark-adjacent UI, status, labels, controls and screenshot-matched UI copy; keep pixel-size usage at 12px or integer multiples where possible.
- Motion: only operational feedback — scan/progress, delayed loader, modal, toast. Honour `prefers-reduced-motion`.

## Fidelity map

| Screen element | Implementation asset |
| --- | --- |
| Header logo | `neurotrace-logo.svg` → `neurotrace-logo-source.png` |
| Low-pixel dimensions / colour | `tokens.css` and `tokens.json` |
| Buttons, Tag, fields, cards, progress, dialogs, toast | `components.css` |
| Trace poses | `../trace-postures/*.png` |
| Interaction examples / responsive usage | `../component-showcase/index.html` |

## Implementation order

1. Import `tokens.css`, then `components.css`; do not replace the bundled pixel font with an OS-only font stack.
2. Use semantic component classes without adding local colours, radii, or shadows.
3. Build `/neural-trace` and `/workbench` using the existing review mockups as layout references, not as production UI assets.
4. Keep true execution logs limited to actual system events; never render model chain-of-thought.

The target is visual parity through reusable primitives, not pixel-for-pixel embedding of a static design image.

