# TODO

## Pass 1 — CI Pipeline

- [x] Pipeline added
- [x] DRC: FAIL — 2 clearance violations (zone clearance 0.5mm, actual ~0.475-0.488mm)
- [x] ERC: PASS
- [ ] Fab: SKIPPED (blocked by DRC pre-flight)
- [ ] gen-kibot-index: SKIPPED
- [ ] deploy-pages: SKIPPED

## Pass 2 — Pre-Fab Review

- [ ] Fix 2x zone clearance violations (increase spacing or reduce zone clearance rule)
- [ ] Verify BOM completeness and sourcing
- [ ] Confirm board outline and mounting holes
- [ ] Footprint verification against datasheets
- [ ] Design review sign-off
