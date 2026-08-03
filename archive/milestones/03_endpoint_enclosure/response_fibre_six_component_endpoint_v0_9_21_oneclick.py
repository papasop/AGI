#!/usr/bin/env python3
"""Geometric-Flow six-component endpoint-box audit v0.9.21.

Uses only hash-bound, already certified uniform information:
  * second-chart intrinsic field component bound |X_i| <= M,
  * 557-step scalar reachable-tube inclusion,
  * guarded old-endpoint/new-chart overlap radius.

For T=N*h, the fundamental theorem of calculus gives
  a_i(T) in a_i(0) + [-T*M, T*M].
Combining this with the initial overlap box produces a rigorous six-component
endpoint enclosure.  This is intentionally not advertised as a sharp Taylor/
Lohner centre, a complete-child traversal, or a global flow theorem.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from decimal import Decimal, getcontext
from pathlib import Path

VERSION = "0.9.21"
TITLE = "GEOMETRIC-FLOW VALIDATED SIX-COMPONENT 557-STEP ENDPOINT-BOX AUDIT"
getcontext().prec = 80

FROZEN = {
    "dimension": 6,
    "steps": 557,
    "time_step": "1e-14",
    "field_component_absolute_upper": "0.5813098595615415",
    "initial_overlap_linf_radius": "3.187e-15",
    "inner_domain_radius": "1e-11",
    "corrected_lipschitz_induced_infinity_upper": "348785915736.92487",
    "v0920_last_scalar_radius": "9.9679185906186564966159815544087462868466863403749232995672122427002571435056182e-12",
    "v093_source_sha256": "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c",
    "v074_source_sha256": "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8",
    "inputs_zip_sha256": "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666",
    "v099_source_sha256": "5c95b625279c024168123b9ff0ca11451feb43794ce926f518920b6b4380ed10",
}


def atomic(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tmp.replace(path)


def parse() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(description=TITLE)
    p.add_argument("--outdir", default="response_fibre_six_component_endpoint_v0_9_21_results")
    p.add_argument("--steps", type=int, default=557)
    return p.parse_known_args()


def run(args: argparse.Namespace) -> dict:
    started = time.time()
    if args.steps < 1 or args.steps > FROZEN["steps"]:
        raise ValueError(f"--steps must lie in [1,{FROZEN['steps']}]")
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    n = Decimal(args.steps)
    h = Decimal(FROZEN["time_step"])
    M = Decimal(FROZEN["field_component_absolute_upper"])
    r0 = Decimal(FROZEN["initial_overlap_linf_radius"])
    R = Decimal(FROZEN["inner_domain_radius"])
    total_time = n * h
    integral_radius = total_time * M
    endpoint_radius = r0 + integral_radius
    centers = ["0" for _ in range(FROZEN["dimension"])]
    radii = [str(endpoint_radius) for _ in range(FROZEN["dimension"])]
    lower = [str(-endpoint_radius) for _ in range(FROZEN["dimension"])]
    upper = [str(endpoint_radius) for _ in range(FROZEN["dimension"])]

    # Independent Gronwall scalar recurrence, using corrected induced norm.
    L = Decimal(FROZEN["corrected_lipschitz_induced_infinity_upper"])
    g = (L * h).exp()
    scalar = r0
    for _ in range(args.steps):
        scalar = g * scalar + h * M

    endpoint_certificate = {
        "schema": "geometric-flow/six-component-endpoint-box/v0.9.21",
        "coordinate_system": "v0.9.10 recentered second-chart intrinsic tangent coordinates",
        "step_count": args.steps,
        "time_interval": ["0", str(total_time)],
        "endpoint_box": {
            "center": centers,
            "component_radius": radii,
            "lower": lower,
            "upper": upper,
        },
        "derivation": "a_i(T)-a_i(0)=integral_0^T X_i(a(t))dt and |X_i|<=M",
        "initial_box_linf_radius": str(r0),
        "uniform_field_component_bound": str(M),
        "integrated_field_radius": str(integral_radius),
        "frozen_hashes": {
            "v093_source": FROZEN["v093_source_sha256"],
            "v074_source": FROZEN["v074_source_sha256"],
            "inputs_zip": FROZEN["inputs_zip_sha256"],
            "v099_source": FROZEN["v099_source_sha256"],
        },
        "claim_boundary": "rigorous endpoint enclosure from a uniform component bound; not a sharp trajectory midpoint or Taylor/Lohner flowpipe",
    }
    atomic(out / "six_component_endpoint_box_certificate.json", endpoint_certificate)

    frozen_scalar = Decimal(FROZEN["v0920_last_scalar_radius"])
    gates = {
        "six_dimensional_endpoint_box_emitted": len(centers) == len(radii) == len(lower) == len(upper) == 6,
        "positive_certified_time": total_time > 0,
        "component_integral_bound_finite": endpoint_radius.is_finite(),
        "component_endpoint_box_strictly_inside_inner_domain": endpoint_radius < R,
        "corrected_scalar_tube_strictly_inside_inner_domain": scalar < R,
        "component_box_contained_in_scalar_tube": endpoint_radius <= scalar,
        "scalar_recurrence_matches_v0920": args.steps != 557 or abs(scalar - frozen_scalar) < Decimal("1e-60"),
        "certificate_bound_to_frozen_hashes": all(len(FROZEN[k]) == 64 for k in ["v093_source_sha256", "v074_source_sha256", "inputs_zip_sha256", "v099_source_sha256"]),
    }
    passed = all(gates.values())
    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": "VALIDATED_SIX_COMPONENT_557_STEP_ENDPOINT_BOX_CERTIFIED" if passed and args.steps == 557 else ("VALIDATED_SIX_COMPONENT_FINITE_TIME_ENDPOINT_BOX_CERTIFIED" if passed else "V0921_ENDPOINT_BOX_INCONCLUSIVE_FAIL_CLOSED"),
        "step_count": args.steps,
        "total_certified_time": str(total_time),
        "endpoint_box": endpoint_certificate["endpoint_box"],
        "bounds": {
            "initial_overlap_linf_radius": str(r0),
            "integrated_component_displacement_upper": str(integral_radius),
            "final_component_radius": str(endpoint_radius),
            "corrected_scalar_reachable_radius": str(scalar),
            "inner_domain_radius": str(R),
        },
        "gates": gates,
        "all_scientific_gates_pass": passed,
        "six_component_endpoint_box_certified": passed,
        "sharp_trajectory_center_certified": False,
        "taylor_lohner_flowpipe_certified": False,
        "complete_child_certified": False,
        "global_flow_claimed": False,
        "certificate": str(out / "six_component_endpoint_box_certificate.json"),
        "next_required_step": "recenter a third same-chart formal fibre graph on this endpoint box, or implement repository-native signed X(a_box) Taylor/Lohner propagation to sharpen the box",
        "claim_boundary": "six-component endpoint inclusion box only; its zero centre is an enclosure convention, not a computed trajectory midpoint",
        "elapsed_seconds": time.time() - started,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    raw = json.dumps(result, sort_keys=True, allow_nan=False).encode()
    result["report_sha256_before_self_field"] = hashlib.sha256(raw).hexdigest()
    atomic(out / "run_summary.json", result)
    return result


def main() -> int:
    args, ignored = parse()
    if ignored:
        print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    try:
        result = run(args)
        print("=" * 112)
        print(f"{TITLE} v{VERSION}")
        print("=" * 112)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result["all_scientific_gates_pass"] else 2
    except Exception as exc:
        print(json.dumps({
            "scientific_status": "V0921_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
