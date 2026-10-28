---
name: drug-info
description: Look up FDA drug label text, NDC product details, and recall records through the free openFDA API (no key). Reference information only, never medical advice.
---

# drug-info

Drug reference lookups from the FDA's free public openFDA API
(api.fda.gov, no key, no auth). Label text, NDC product details, and
recall records for prescription and OTC drugs.

## IMPORTANT DISCLAIMER

**Reference information only. This is NOT medical advice.** Everything
comes from FDA records and is provided so the user can read it and take
it to a professional. If anything is consequential (a dosage question,
a warning, a possible interaction, whether to start or stop a drug),
he should verify it with his doctor or pharmacist. Never present this
output as a recommendation or a safety verdict.

## Tool

`druginfo.py` in this skill folder: a small Python CLI that
uses only the Python standard library (urllib + json), so there is no
virtualenv to maintain. Run it directly:

```
druginfo.py <command> <name>
```

## Commands

Output is plain-language human-readable text, ready to paste into
chat. Every command makes one request; anonymous openFDA requests are
limited to roughly 1,000 per day, so ask one question per command and
stop when answered.

- `label <brand or generic name>`
  Approved FDA label: what it is for, warnings and cautions, and
  dosage/administration. Examples:
  `druginfo.py label "acetaminophen"`
  `druginfo.py label "ibuprofen"`
  Verified live: a label lookup returns the drug's indications, warnings,
  and dosage and administration sections from the current FDA label.
- `ndc <name or product NDC>`
  NDC directory entry: brand/generic names, product NDC, dosage form,
  labeler, active ingredients with strengths, package sizes.
  Examples:
  `druginfo.py ndc corlanor`
  `druginfo.py ndc 55513-810`
  Verified live Oct 11, 2026: `ndc corlanor` returned Amgen Inc,
  product NDC 55513-810, 7.5 mg tablets, 60-count bottle packaging.
- `recalls <brand or generic name>`
  Most recent FDA recall matching the product, with reason,
  classification, status, and distribution. Example:
  `druginfo.py recalls corlanor`
  Verified live Oct 11, 2026: returned recall D-0615-2026 for Corlanor
  7.5 mg 60-count bottles, "Presence of Foreign Substance," Class II,
  status Ongoing, nationwide distribution (the most recent of 2
  matching recalls).

Unknown drugs print a clear "no results" error rather than guessing.

## Known limitations

- openFDA has label text and recalls, but **no drug-drug interaction
  checker**. Labels sometimes mention interaction-related warnings, but
  do not treat that as a complete interaction check. For real
  interaction questions, use a proper reference (Drugs.com, Lexicomp,
  or a pharmacist) and say so.
- Labels are manufacturer-authored SPL text: long, technical, and
  sometimes dated. The `label effective` date is printed with each
  result so the user can judge freshness.
- Recall records can be incomplete or under-reported; absence of a
  recall does not prove a product is problem-free.
- openFDA data can lag behind the manufacturer's newest label.
- This is reference data for a layperson, not a clinician. Keep the disclaimer attached whenever the output matters.

## Attribution

Data: openFDA drug endpoints (api.fda.gov/drug), maintained by the
U.S. Food and Drug Administration. Anonymous access verified
Oct 11, 2026 (HTTP 200, no key required).
## Available connectors

Use `muse.connector_search` to find the current connector docs before following
recovered instructions.
