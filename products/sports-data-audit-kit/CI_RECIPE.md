# Customer CI recipe

Run tests on pull requests first. Use a synthetic or properly authorized canonical input. Never log or commit credentials. Do not grant this audit write permissions or provider access.

Add these commands to an existing trusted Python 3.12 job after checkout/setup:

```yaml
- name: Test sports audit
  run: python products/sports-data-audit-kit/check_demo.py
- name: Audit synthetic clean fixture
  run: python products/sports-data-audit-kit/audit.py products/sports-data-audit-kit/examples/clean.json --output audit-results --asof 2026-01-02T00:00:00Z
```

The output directory must not exist. For customer data, supply the actual cutoff and schema adapter; do not reuse the synthetic `--asof`. Preserve a report even if the audit exits 1 using your approved artifact upload step with `if: always()`. Decide retention and access before uploading customer reports. No upload action is bundled or automatically enabled by this recipe.

The product-demos repository already invokes the test suite via `scripts/validate_demos.py`; adding another parallel validation job is unnecessary.
