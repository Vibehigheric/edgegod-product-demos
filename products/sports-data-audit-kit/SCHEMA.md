# Canonical input v1

JSON: nonempty array of objects. CSV: one header row. UTF-8; optional BOM. All fields below must exist. Identifiers are stable, nonempty strings. Examples use invented identifiers only.

| Field | Meaning |
|---|---|
| sport | Sport namespace, e.g. NFL; supplied identity, not independently verified |
| event_id, event_date | Exact event ID and YYYY-MM-DD local sporting date; source timezone reconciliation is upstream |
| subject_id | Exact player/team target ID |
| team_id, opponent_id | Different participant IDs |
| market | Explicit statistic/target name; adapter defines units |
| side | OVER, UNDER, WIN, YES or NO |
| line | Finite number, or literal NA for targets without lines; OVER/UNDER require numeric line |
| period | FULL_GAME, REGULATION, H1, H2, Q1–Q4, P1–P3 |
| participation_rule | Explicit nonempty rule identifier; semantic validation belongs to adapter |
| ot_rule | INCLUDED, EXCLUDED or NOT_APPLICABLE; INCLUDED only with FULL_GAME |
| cutoff, feature_asof | ISO8601 timestamps with UTC offset |
| model_id | Immutable source/model version identifier |
| probability | Finite decimal 0–1, never percent 0–100 |
| status | FINAL, PENDING, DNP, POSTPONED, ABANDONED, UNRESOLVED, VOID |
| actual | Finite numeric observation for FINAL; empty CSV or null JSON otherwise |

Additional fields are preserved in the source but not copied into reports. Reports contain finding codes, row positions and an input hash rather than raw player rows. No guarantee of deidentification is made for caller-supplied field names. No credentials belong in input files.

For team-winner targets, upstream adapters may encode a documented binary observation. For counts/yards use numeric observations. Sport-specific nonnegative/range checks, official IDs, book rules and exact settlement remain adapter responsibilities. The generic kit accepts negative numeric outcomes because some valid statistics can be negative.
