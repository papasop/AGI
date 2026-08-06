# Reviewer Reproduction

The archived manuscript theorem boundary consists of the v0.7.4
complete-parent-box geometry certificate and the v0.9.3 validated local
intrinsic ODE microstep. Later v0.10.x continuation artifacts are not part of
this reproduction.

## Environment

- Python 3.12
- `numpy==2.0.2`
- `python-flint==0.8.0`
- no QPU, vendor account, API token, or cloud credential is required

## Fast Verification

From a clean checkout of the immutable paper tag:

```bash
python -m pip install -r requirements.txt
python reproduce/published_paper.py
```

The default command verifies the frozen SHA-256 bindings and stored theorem
artifacts. It does not rerun the full interval computations.

## Full Theorem Recomputation

```bash
python reproduce/published_paper.py --run
```

This recomputes the v0.7.4 parent-box certificate and the v0.9.3 local ODE
certificate from the frozen source and input archive.

The release gate must report:

```text
STAGE_A_PARENT_BOX_GEOMETRY_CERTIFIED = true
STAGE_B_LOCAL_ODE_MICROSTEP_CERTIFIED = true
GLOBAL_FLOW_CLAIMED = false
PUBLISHED_LOCAL_PAPER_RELEASE_GATE = true
```

The v0.7.4 `atlas all_gates_pass` flag is expected to remain false because it
contains a separate unresolved alignment diagnostic. The theorem-bearing
Stage-A rank/descent gates must nevertheless all pass. This is not a failure of
the v0.9.3 intrinsic ODE theorem.

## Independent Checks

```bash
python tools/verify_release.py
python scripts/verify_reference_results.py
python -m compileall -q src tools scripts reproduce
sha256sum -c SHA256SUMS.txt
```

## Scope

Successful reproduction establishes only the frozen local theorem. It does not
establish complete-atlas continuation, arbitrary endpoint connection,
long-time existence, physical-hardware performance, or a global response-fibre
flow.
