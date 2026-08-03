#!/usr/bin/env python3
"""Geometric-Flow local-DX closure-target audit v0.9.19.

This is a fail-closed bridge between v0.9.18 and a future point/box-dependent
Arb Taylor/automatic-differentiation backend.  It does NOT certify the
557-step endpoint.  It independently reproduces the v0.9.18 scalar recurrence
and computes the largest uniform induced-infinity Jacobian bound that would
make all 557 steps remain strictly inside the certified local domain.

Notebook safe: unknown Jupyter ``-f kernel.json`` arguments are ignored and
SystemExit is suppressed in IPython/Colab.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from decimal import Decimal, getcontext
from pathlib import Path

VERSION = "0.9.19"
TITLE = "GEOMETRIC-FLOW LOCAL-JACOBIAN 557-STEP CLOSURE-TARGET AUDIT"
getcontext().prec = 80

# Frozen directly from the successful v0.9.18 run.  These constants are
# capability bounds, not a new representation of the underlying vector field.
FROZEN = {
    "target_steps": 557,
    "reported_maximum_certified_steps": 172,
    "reported_first_failing_step": 173,
    "component_field_upper": "0.5813098605722189",
    "global_entry_jacobian_upper": "348785916416.0",
    "global_induced_infinity_jacobian_upper": "2092715498496.0",
    "domain_radius": "1e-11",
    "time_step": "1e-14",
    # v0.9.18 starts its second-chart propagation from the guarded old
    # endpoint overlap radius reported by v0.9.10, not the normal-root radius.
    "initial_radius": "3.187e-15",
    "reported_last_safe_radius": "9.896544289388568e-12",
    "reported_first_failing_radius": "1.0111646175560874e-11",
    "reported_target_557_radius": "3.209734154981215e-08",
    "v093_source_sha256": "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c",
    "v074_source_sha256": "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8",
    "inputs_zip_sha256": "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666",
}


def atomic_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tmp.replace(path)


def propagated_radius(L: Decimal, steps: int) -> Decimal:
    """Outward-guarded scalar recurrence r[k+1]=exp(Lh)r[k]+hM."""
    h = Decimal(FROZEN["time_step"])
    M = Decimal(FROZEN["component_field_upper"])
    r = Decimal(FROZEN["initial_radius"])
    g = (L * h).exp()
    for _ in range(steps):
        r = g * r + h * M
    # Decimal transcendental arithmetic is not Arb-directed rounding.  The
    # guard is deliberately much larger than the 80-digit rounding scale.
    return r * (Decimal(1) + Decimal("1e-60")) + Decimal("1e-70")


def maximum_safe_steps(L: Decimal, cap: int = 10000) -> tuple[int, Decimal, Decimal]:
    R = Decimal(FROZEN["domain_radius"])
    previous = Decimal(FROZEN["initial_radius"])
    for k in range(1, cap + 1):
        current = propagated_radius(L, k)
        if not current < R:
            return k - 1, previous, current
        previous = current
    return cap, previous, previous


def solve_uniform_L_target(steps: int) -> tuple[Decimal, Decimal, Decimal]:
    """Bracket the supremal L for which r_steps < R by monotone bisection."""
    R = Decimal(FROZEN["domain_radius"])
    lo = Decimal(0)
    hi = Decimal(FROZEN["global_induced_infinity_jacobian_upper"])
    if not propagated_radius(lo, steps) < R:
        raise RuntimeError("even L=0 cannot close target; field-width budget alone fails")
    if propagated_radius(hi, steps) < R:
        raise RuntimeError("frozen global Jacobian unexpectedly closes target")
    for _ in range(320):
        mid = (lo + hi) / 2
        if propagated_radius(mid, steps) < R:
            lo = mid
        else:
            hi = mid
    return lo, hi, propagated_radius(lo, steps)


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(description=TITLE)
    p.add_argument("--outdir", default="response_fibre_local_dx_target_v0_9_19_results")
    p.add_argument("--target-steps", type=int, default=557)
    p.add_argument("--candidate-local-induced-bound", type=str, default=None,
                   help="optional candidate uniform ||DX||_inf bound to audit")
    return p.parse_known_args()


def run(args: argparse.Namespace) -> dict:
    started = time.time()
    if args.target_steps < 1:
        raise ValueError("--target-steps must be positive")
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    L_global = Decimal(FROZEN["global_induced_infinity_jacobian_upper"])
    safe, r_safe, r_fail = maximum_safe_steps(L_global)
    r557 = propagated_radius(L_global, args.target_steps)
    L_pass, L_fail, r_at_pass = solve_uniform_L_target(args.target_steps)
    reduction = Decimal(1) - L_pass / L_global
    factor = L_global / L_pass

    candidate = None
    if args.candidate_local_induced_bound is not None:
        Lc = Decimal(args.candidate_local_induced_bound)
        if Lc < 0 or not Lc.is_finite():
            raise ValueError("candidate local induced bound must be finite and nonnegative")
        rc = propagated_radius(Lc, args.target_steps)
        candidate = {
            "induced_infinity_bound": str(Lc),
            "target_radius": str(rc),
            "strictly_inside_domain": rc < Decimal(FROZEN["domain_radius"]),
            "maximum_safe_steps": maximum_safe_steps(Lc)[0],
            "informational_only": True,
            "reason": "a number supplied on the command line is not an Arb enclosure certificate",
        }

    contract = {
        "schema": "geometric-flow/local-box-jacobian-adapter/v0.9.19",
        "required_backend": "python-flint/Arb at >=192 bits or equivalent directed interval backend",
        "required_callable": "formal_local_jacobian_DX(a_box)",
        "input": {"dimension": 6, "type": "six outward-rounded Arb intervals"},
        "output": {"shape": [6, 6], "type": "outward-rounded Arb matrix"},
        "mandatory_gates": [
            "each returned interval encloses DX_ij over the complete input box",
            "input boxes remain inside the hash-bound v0.9.10 fibre graph domain",
            "implicit normal root is re-certified or transported for every accepted box",
            "response invariance is enclosed at every step",
            "strict L6 descent is enclosed at every step",
            "all 557 endpoint-box inclusions are strict",
            "the adapter is rejected if it merely repeats the global symmetric Cauchy box",
        ],
        "uniform_sufficient_target_induced_infinity_norm_strictly_below": str(L_fail),
        "note": "This uniform target is sufficient for the frozen scalar recurrence, not necessary for a matrix Lohner/QR proof.",
        "frozen_repository_hashes": {
            "v093_source": FROZEN["v093_source_sha256"],
            "v074_source": FROZEN["v074_source_sha256"],
            "inputs_zip": FROZEN["inputs_zip_sha256"],
        },
    }
    atomic_json(out / "local_dx_backend_contract.json", contract)

    # v0.9.18 printed binary-float values; allow only their last displayed
    # decimal-place discrepancy when comparing the 80-digit recomputation.
    display_abs_tol = Decimal("2e-25")
    gates = {
        "frozen_v0918_step_boundary_reproduced": safe == 172,
        "frozen_v0918_last_safe_radius_reproduced": abs(r_safe - Decimal(FROZEN["reported_last_safe_radius"])) <= display_abs_tol,
        "frozen_v0918_first_failure_reproduced": r_fail >= Decimal(FROZEN["domain_radius"]),
        "global_bound_fails_target": r557 >= Decimal(FROZEN["domain_radius"]),
        "zero_jacobian_bound_closes_target": propagated_radius(Decimal(0), args.target_steps) < Decimal(FROZEN["domain_radius"]),
        "uniform_local_dx_target_bracketed": L_pass < L_fail and propagated_radius(L_pass, args.target_steps) < Decimal(FROZEN["domain_radius"]) and propagated_radius(L_fail, args.target_steps) >= Decimal(FROZEN["domain_radius"]),
        "local_backend_contract_emitted": (out / "local_dx_backend_contract.json").is_file(),
    }
    audit_pass = all(gates.values())
    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": "LOCAL_DX_557_STEP_CLOSURE_TARGET_CERTIFIED_BACKEND_IMPLEMENTATION_OPEN" if audit_pass else "V0919_AUDIT_INCONCLUSIVE_FAIL_CLOSED",
        "frozen_v0918_reproduction": {
            "maximum_certified_steps": safe,
            "first_failing_step": safe + 1,
            "last_safe_radius": str(r_safe),
            "first_failing_radius": str(r_fail),
            "target_radius_under_global_bound": str(r557),
        },
        "local_dx_requirement": {
            "target_steps": args.target_steps,
            "uniform_induced_infinity_bound_pass_lower": str(L_pass),
            "uniform_induced_infinity_bound_fail_upper": str(L_fail),
            "radius_at_pass_lower": str(r_at_pass),
            "global_to_required_tightening_factor": str(factor),
            "minimum_relative_reduction_from_global_bound": str(reduction),
            "interpretation": "a uniform bound below the fail upper closes the frozen scalar recurrence; box-dependent matrix propagation may use a less restrictive nonuniform condition",
        },
        "candidate_audit": candidate,
        "gates": gates,
        "audit_pass": audit_pass,
        "all_scientific_gates_pass": False,
        "geometric_flow_557_step_endpoint_certified": False,
        "complete_child_certified": False,
        "global_flow_claimed": False,
        "backend_contract": str(out / "local_dx_backend_contract.json"),
        "next_required_step": "implement repository-native point/box-dependent Arb DX enclosures, then run 557 stepwise endpoint inclusions",
        "claim_boundary": "certifies only the quantitative local-Jacobian closure target and backend contract; no 557-step trajectory endpoint or global flow",
        "elapsed_seconds": time.time() - started,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    payload = json.dumps(result, sort_keys=True, allow_nan=False).encode()
    result["report_sha256_before_self_field"] = hashlib.sha256(payload).hexdigest()
    atomic_json(out / "run_summary.json", result)
    return result


def main() -> int:
    args, ignored = parse_args()
    if ignored:
        print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    try:
        result = run(args)
        print("=" * 112)
        print(f"{TITLE} v{VERSION}")
        print("=" * 112)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result["audit_pass"] else 2
    except Exception as exc:
        print(json.dumps({
            "scientific_status": "V0919_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
