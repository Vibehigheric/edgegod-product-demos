# EdgeGod Sports Data Audit Kit

**Full offline v1 kit: original source, synthetic fixtures, tests, HTML/JSON reports and a GitHub CI recipe.** Python 3.12+, standard library only. No API calls, telemetry, credentials, model weights or real sports records.

The public code uses the repository's existing [license](../../LICENSE.txt). The paid offer is scoped implementation and support, not exclusive access to this public code.

## Quick start

From this directory:

```sh
python audit.py examples/clean.json --output audit-clean --asof 2026-01-02T00:00:00Z
python audit.py examples/problems.csv --output audit-problems --asof 2026-01-02T00:00:00Z
python check_demo.py
```

The second command intentionally returns exit **1** and still writes a report. Open `audit-problems/report.html`. Use a new output directory each run; previous reports are never overwritten. Exit 0 means no structural errors, 1 means audit errors, 2 means input/output/configuration failure. Warnings and informational unresolved states do not fail CI.

Optional arguments: `--max-age-hours 24` controls feature age **at cutoff**, not current file age; `--expected-sha256 HEX` requires the exact input bytes. `--asof` defaults to current UTC and is used to flag future feature timestamps. Record explicit timestamps for reproducible runs.

## Checks included

- Required columns; malformed CSV widths/duplicate headers; duplicate JSON keys/non-finite JSON.
- Exact target identity, including sport, event/date, subject, team/opponent, market, side, numeric line, period, participation, overtime rule and model version.
- Duplicate targets and conflicting observations; numeric line spellings normalize. Different models/periods remain separate.
- Same-team/opponent conflicts, invalid dates, unsupported side/period and overtime combinations.
- Finite probabilities in [0,1], finite lines/observations, final records missing observations.
- Timezone-aware timestamps, features after cutoff, future features, stale features at cutoff.
- FINAL/PENDING/DNP/POSTPONED/ABANDONED/UNRESOLVED/VOID retained separately. Zero is valid only as an explicitly supplied observation; missing outcomes are not losses.
- Input SHA256, append-only output directory, JSON results, escaped HTML findings and output hashes.

## Contract and scope

See [SCHEMA.md](SCHEMA.md). Input is a canonical model research table, **not raw sportsbook quotes**. Normalize book aliases before this audit or keep them in another table. It does not fetch data, resolve names, independently confirm identities, validate final scores, grade bets, calculate ROI, authenticate timestamps, certify licensing/security, or demonstrate prediction accuracy. `PASS` means the implemented structural checks found no errors, not that the records are true or admissible.

No silent repairs. Fix issues upstream in a new version, retain the original and rerun. Historical and live populations must remain separate in the caller's pipeline. There is no source-code or prediction modification step.

## GitHub integration

This repository's existing validator discovers `check_demo.py` and runs the regression suite on PRs and main updates. See [CI_RECIPE.md](CI_RECIPE.md) for integrating a customer's canonical table. The recipe is documentation, not an activated customer workflow.

## $200 repository setup

[Read the fixed-scope offer](SETUP_OFFER.md). Deliverables: one repository, one existing schema adapter, CI wiring, fixtures, tests, handoff and one review revision. No automatic payment, subscription or service booking is enabled.
