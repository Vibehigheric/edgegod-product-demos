# EdgeGod product demos

Original synthetic, browser-based learning examples. No private engines, real picks, provider data, API keys or paid packages are included.

Seven days is a suggested learning schedule, not an expiring license. All lessons are accessible immediately. Download once if you want an offline copy; return for the next exercise or a genuine update. Stars and repeated downloads are never required.

These are shared workflow demonstrations, not full trials of each product. Concept products have concept walkthroughs only.

## Download and validation

Download the ZIP and SHA256 checksum from [GitHub Releases](https://github.com/Vibehigheric/edgegod-product-demos/releases/latest). Extract it and open `demo.html` in a browser.

From a Git checkout with Python 3.12, run `python scripts/validate_demos.py`. This parses the tracked JSON fixtures and executes all five offline Python demo checks without provider calls or dependencies.

The `python-publish.yml` workflow validates pull requests and main-branch updates. Pushing a new `v*` tag publishes the committed public repository as a ZIP and checksum only after validation succeeds. This repository is not a Python distribution and does not publish to PyPI. Reuse neither an existing release tag nor an existing release asset name to replace a published version; publish a new version instead.

- [EdgeGod Sports Research Starter](products/research-starter/README.md)
- [EdgeGod Chronological Model Lab](products/model-lab/README.md)
- [EdgeGod Parlay Survival Lab](products/parlay-survival-lab/README.md)
- [EdgeGod AI Research Builder](products/ai-research-builder/README.md)
- [EdgeGod CFBD API Launch Kit](products/api-launch-kit/README.md)
- [EdgeGod Season Research Bundle](products/season-research-bundle/README.md)
- [EdgeGod American Football Research Edition](products/sport-0/README.md)
- [EdgeGod Aussie Rules Research Edition](products/sport-1/README.md)
- [EdgeGod Baseball Research Edition](products/sport-2/README.md)
- [EdgeGod Basketball Research Edition](products/sport-3/README.md)
- [EdgeGod Boxing Research Edition](products/sport-4/README.md)
- [EdgeGod Cricket Research Edition](products/sport-5/README.md)
- [EdgeGod Golf Research Edition](products/sport-6/README.md)
- [EdgeGod Handball Research Edition](products/sport-7/README.md)
- [EdgeGod Ice Hockey Research Edition](products/sport-8/README.md)
- [EdgeGod Lacrosse Research Edition](products/sport-9/README.md)
- [EdgeGod Mixed Martial Arts Research Edition](products/sport-10/README.md)
- [EdgeGod Rugby League Research Edition](products/sport-11/README.md)
- [EdgeGod Rugby Union Research Edition](products/sport-12/README.md)
- [EdgeGod Soccer Research Edition](products/sport-13/README.md)
- [EdgeGod Tennis Research Edition](products/sport-14/README.md)
- [EdgeGod Creator Desk](products/creator-desk/README.md)
- [EDGE UI](products/edge-ui/README.md)
- [EDGE Creator](products/edge-creator/README.md)
- [EDGE Weave](products/edge-weave/README.md)
- [EdgeGod Command Center](products/command-center/README.md)
- [EdgeGod Research Desktop](products/desktop/README.md)
- [EdgeGod SDK](products/sdk/README.md)

## Sports analytics and research automation

- [Sports Data Audit Kit — full offline v1](products/sports-data-audit-kit/README.md): CSV/JSON structural checks, synthetic fixtures, tests and HTML/JSON reports. [Open demo](products/sports-data-audit-kit/index.html).
- [$200 repository setup offer](products/sports-data-audit-kit/SETUP_OFFER.md): one schema adapter, up to three custom rules, CI wiring and handoff. No checkout or booking activated. Public kit code remains reusable under the repository license.

## EdgeGod AI workflow kits
- [EdgeGod Research Prompt Studio](products/prompt-studio/README.md)
- [EdgeGod Copilot Evidence Pack](products/copilot-pack/README.md)
- [EdgeGod Codex Workflow Kit](products/codex-workflows/README.md)
- [EdgeGod VS Code Research Desk](products/vscode-system/README.md)
- [EdgeGod GPT Framework Library](products/gpt-frameworks/README.md)
