# Prospective Principle R Protocol Scaffold

This directory contains a prospective model-level test scaffold for
realizability criteria R1--R7. It is intentionally isolated from the published
v1.2.13 theorem boundary.

Status:

```text
PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED
```

This scaffold freezes a future protocol only. It does not execute an R6
search, does not produce a certificate, and does not change any frozen source,
certificate, tag, Release, manuscript, or Zenodo asset.

The isolated R7 positive-control certificate is post-protocol prospective
evidence only. The current certificate is
`certificates/r7_positive_control_v1_1.json`; the PR #53 v1.0 certificate is
superseded because it used an incomplete centered enclosure of the declared
path.

## Files

```text
README.md
CLAIM_BOUNDARY.md
frozen_protocol_v1_0.json
verify_frozen_protocol.py
requirements.txt
R7_CERTIFICATE_BOUNDARY.md
certify_r7_positive_control.py
verify_r7_certificate.py
certificates/r7_positive_control_v1_0.json  # superseded
certificates/r7_positive_control_v1_1.json  # current R7 positive control
```

## Verification

Run:

```bash
python research/realizability_r1_r7/verify_frozen_protocol.py
python research/realizability_r1_r7/verify_r7_certificate.py --mutation-tests
```

The verifier checks schema, required fields, declared file hashes, R1--R5/R7
declarations, absence of R6 result fields, and the exact frozen status string.
It does not run Arb, Krawczyk, Picard, Lohner, or any R6 search.

The R7 verifier checks the stored v1.1 certificate, including full
`eta_delta(s)=theta_0+s*delta*n` path endpoint containment for every frozen
delta. It does not run R5 or R6.

## Scope

The published Geometric-Flow theorem remains the v1.2.13 local quantum-control
result. Existing v0.7.4 and v0.9.3 artifacts may inform this protocol design,
but they are not imported as new prospective R6 evidence.
