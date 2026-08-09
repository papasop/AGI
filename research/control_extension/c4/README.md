# C4 controlled-attraction extension

This directory is a post-publication research extension. It does not modify or
enlarge the theorem proved by the published Zenodo paper.

Evidence layers:

- `c4_d0_product_chart_residence_preflight_v1_0.py` is a floating-point,
  sampled product-chart preflight. It is not an interval proof.
- `c4_d1_arb_product_tube_residence_v1_0.py` is a 256-bit Arb certificate of a
  strictly positive finite residence time for an unsaturated controlled flow
  in one fixed 6D tangent x 8D normal product tube.

The D1 certificate proves neither positive invariance nor continuation beyond
its single certified residence window.

- `c4_e0_moving_chart_overlap_preflight_v1_0.py` is a floating-point,
  sampled-trajectory moving-chart overlap/recentring preflight. It completes
  eight pointwise chart transitions in the documented real 14-phase model, but
  it is not an interval proof.
- `c4_e1a_arb_first_chart_overlap_certificate_v1_0.py` and
  `c4_e2a_arb_multichart_overlap_chain_v1_0.py` archive the Arb-certified
  moving-atlas overlap chain: 9 charts, 8 adjacent transitions, and 8/8
  positive-volume overlap boxes. The frozen E2a report records maximum
  Neumann-defect upper bound `0.018601705183309603`, minimum local
  residence-time lower bound `6.050195285542712e-10`, and aggregate local
  residence budget `4.844642545380921e-09`.

The E2a aggregate budget is not a continuation time. C4-E2b validated-flowpipe
continuation remains the next required step. No positive invariance, global
continuation, K=1, Pulser, cloud, hardware, or QPU claim is made.

Run from the repository root:

```bash
python -m pip install -r requirements-formal.txt
python research/control_extension/c4/c4_d0_product_chart_residence_preflight_v1_0.py \
  --report /tmp/c4_d0.json
python research/control_extension/c4/c4_d1_arb_product_tube_residence_v1_0.py \
  --report /tmp/c4_d1.json
python research/control_extension/c4/verify_c4_control_extension.py \
  --d0 /tmp/c4_d0.json --d1 /tmp/c4_d1.json
cd research/control_extension/c4
python c4_e0_moving_chart_overlap_preflight_v1_0.py \
  --report /tmp/c4_e0.json
python -m json.tool ../../../results/post_publication/control_extension/c4/c4_e2a_arb_multichart_overlap_chain_v1_0.json >/dev/null
```
