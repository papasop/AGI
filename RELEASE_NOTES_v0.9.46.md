# Geometric-Flow v0.9.46 backend-refactor update

This package begins the repository-native point/box Arb field refactor needed
after the v0.9.44 identifiability audit.

## Scientific status

`IMPLEMENTATION_OPEN`.  This package must not be described as a certified
point-dependent field, a formal Jacobian, a QR/Lohner flowpipe, a fifth frame,
or a global-flow theorem.

The v0.9.44 audit established that the exported v0.9.43.3 adapter returns one
fixed signed enclosure for all 24 admissible displaced boxes.  That proves the
adapter is position-insensitive; it does **not** prove that the geometric field
is constant or that `DX = 0`.

## Contents

- `src/geometric_flow_native_point_field_candidate_v0_9_46.py`: typed backend
  module to implement.
- `src/response_fibre_native_binding_harness_v0_9_46_standalone.py`: strict
  acceptance harness.
- `tests/test_v0946_contract.py`: structural fail-closed tests.
- `docs/BACKEND_BINDING.md`: exact binding and claim requirements.
- `frozen/`: the source/audits to which the refactor is hash-bound.

## Required dependency chain

The implementation must preserve one input `a_box` through the complete chain:

```text
a_box
  -> implicit_fibre_root_solver(a_box)
  -> pullback_metric(a_box, root_box)
  -> projected_gradient(a_box, root_box, metric_box)
  -> analytic normalization
  -> formal_vector_field_X(a_box)
```

Merely using `a_box` for dimension or domain validation is insufficient.

## Run

Install the frozen formal backend:

```bash
python -m pip install python-flint==0.8.0
```

Preflight the harness:

```bash
python src/response_fibre_native_binding_harness_v0_9_46_standalone.py
```

After implementing the candidate:

```bash
python src/response_fibre_native_binding_harness_v0_9_46_standalone.py \
  --candidate src/geometric_flow_native_point_field_candidate_v0_9_46.py
```

The unimplemented package is expected to report
`NATIVE_POINT_FIELD_BINDING_HARNESS_READY_IMPLEMENTATION_OPEN`.  A candidate is
accepted only when all 25 Arb probes execute, at least one displaced enclosure
differs from the centre enclosure, invalid inputs are rejected, and no
`NotImplementedError` remains.

## Merge policy

This package is safe to merge as an **implementation branch or open backend
contract**.  Do not label it as a completed theorem milestone until
`candidate_all_gates_pass=true` and an independent certificate audit exists.
