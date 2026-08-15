# C4-E2b v0.3.5.1 Outward-Rounding Repair Chain

This directory contains the repository-native repair scripts for the documented
binary64 outward-rounding residual in the C4-E2b v0.3.5 zero-time handoff
driver.

The historical v0.3.5 report remains stored unchanged for audit history. It is
classified as `certified_with_documented_binary64_rounding_residual`, pending a
fresh v0.3.5.1 recertification run. This directory does not contain a new
certificate JSON and must not be cited as a completed recertification by itself.

## Run Order

Run these scripts in order in Colab or another environment with
`python-flint==0.8.0` and `numpy==2.0.2`:

```bash
python C4_E2B_TRANSITION_12_ARB_LADDER_RIGOROUS_v0_3_2_1.py --levels 32
python C4_E2B_LOCAL_RECENTER_AFFINE_HANDOFF_RIGOROUS_v0_3_3_1.py --level 32
python C4_E2B_HANDOFF_CONTROLLER_COVARIANCE_RIGOROUS_v0_3_4_2.py --level 32
python C4_E2B_AFFINE_CORRELATED_HANDOFF_RIGOROUS_v0_3_5_1.py --level 32
```

The v0.3.5.1 parent replaces the previously binary64-mediated quadratic-radius
and Neumann-tail helpers with Arb outward enclosures. Binary64 conversion is
reserved for JSON display fields only.

## Claim Boundary

Until a fresh v0.3.5.1 JSON report is generated and deposited, the repair chain
is `pending_recertification`.

It does not claim:

- positive-time flowpipe continuation;
- transition 2->3;
- eight-chart completion;
- K=1;
- Pulser, hardware, or QPU evidence;
- a global response-fibre flow.
