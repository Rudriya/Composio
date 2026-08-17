# Agent-readiness research case study

This repository is a reproducible take-home submission for the Composio AI Product Ops assignment. It researches the supplied 100 apps, normalizes agent-toolkit readiness, records evidence, and produces a single self-contained case-study page.

## Quick start

```bash
python3 src/research_pipeline.py --mode demo
open outputs/index.html
```

The demo is deterministic and creates `outputs/apps.json`, `outputs/apps.csv`, `outputs/audit.json`, and `outputs/index.html`. It has no API key requirement, so a reviewer can inspect the exact submitted result. It uses the curated official-doc registry in the source as a resilient fallback when a live lookup fails.

## Deploy on GitHub Pages

After pushing this repository to GitHub, open **Settings → Pages**, select **Deploy from a branch**, choose your branch (usually `main`), and select the **`/docs`** folder. The pipeline generates the identical case study at `docs/index.html` specifically because GitHub Pages cannot publish from `outputs/`.

## Live research mode

```bash
python3 src/research_pipeline.py --mode live --workers 6
```

`live` fetches the canonical official-documentation candidates concurrently (with exponential retry/backoff), records a source-content hash, and raises confidence only when the retrieved page corroborates an auth signal. It falls back to the curated registry when retrieval fails. It never silently turns a missing source into a positive claim: those rows remain `Needs verification`.

## What is deliberately human-reviewed

Credential eligibility and partner/product-approval gates change frequently and cannot be proved solely by an API reference. The audit prioritizes low-confidence, enterprise, ads, finance, and unusual/MCP rows. The submitted audit checks 20 stratified records against first-party pages, reports initial versus corrected field accuracy, and retains every miss.

## Structure

* `src/research_pipeline.py` — runnable research, normalization, scoring, retry/fallback, audit and HTML generation.
* `outputs/index.html` — the standalone two-minute case study.
* `outputs/apps.json` / `outputs/apps.csv` — machine-readable 100-app matrix.
* `outputs/audit.json` — reproducible human verification log.

## Important limitations

This is a point-in-time (2026-08-17) discovery assessment, not legal or commercial advice. “Self-serve” means a developer can usually create credentials without contacting sales; it does not guarantee production approval, data access, or a free paid-plan feature. “MCP” distinguishes a first-party offering from community/third-party implementations. All “Yes” claims link to first-party documentation; uncertain apps are intentionally marked as such rather than guessed.
