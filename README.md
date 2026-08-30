# Cloggle Solver

The deployable app is a static site in `docs/`: `index.html` loads `data/items.json`, then runs the JavaScript comparator and solver locally. It has no runtime Python server or API dependency.

## Local use

Serve the repository root with any static server and open `docs/` (for example, `python -m http.server`). Opening `index.html` directly is not supported because browsers block `fetch` from local files.

`docs/data/items.json` is the complete, enriched static item export. Regenerate it after data changes with `python scripts/export_static_data.py` from the repository root.

The Python implementation in `cloggle/` remains the reference/data-generation implementation. Its client-side equivalents are `docs/js/models.js`, `docs/js/comparator.js`, and `docs/js/solver.js`. The opening recommendation only considers untradeable, unequippable items; subsequent recommendations use all remaining candidates, including tradeable ones. The source/region hard-bucket ranking that addresses the 15-guess risk is retained.

## Tests

Run Python tests from the repository root: `python -m pytest tests -q`.

Run browser-logic tests: `npm run test:js` (Node 22+).

## GitHub Pages

The workflow in `.github/workflows/pages.yml` deploys `docs/` on pushes to `main`. In the repository settings, set Pages source to **GitHub Actions**. All asset and data paths are relative, so project-site subpaths work.
