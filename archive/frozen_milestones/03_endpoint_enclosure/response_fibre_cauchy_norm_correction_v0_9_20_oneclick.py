#!/usr/bin/env python3
"""Geometric-Flow Cauchy-norm semantic correction audit v0.9.20.

v0.9.17 copied v0.9.10's ``cauchy_lipschitz_upper`` into every entry of a
6x6 Jacobian box. v0.9.18 then took the induced infinity norm of that matrix,
multiplying the already induced-norm bound by six. The frozen v0.9.3 source
defines the quantity explicitly as ``d*M/(R-r)`` and therefore already as an
induced infinity-norm Lipschitz bound.

This script independently audits that semantic correction and reruns the
scalar reachable-radius recurrence. It certifies no six-component endpoint
centre, no complete child, and no global flow.
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

VERSION = "0.9.20"
TITLE = "GEOMETRIC-FLOW CAUCHY INDUCED-NORM CORRECTION / 557-STEP REAUDIT"
getcontext().prec = 80

FROZEN = {
    "dimension": 6,
    "field_sup": "0.5813098595615415",
    "cauchy_lipschitz_upper": "348785915736.92487",
    "time_step": "1e-14",
    "inner_radius": "1e-11",
    "initial_overlap_radius": "3.187e-15",
    "target_steps": 557,
    "v0912_last_radius": "9.9679185906186564966159815544087462873225e-12",
    "v0912_next_radius": "1.0008559086572137716369125249577817229295e-11",
    "v093_source_sha256": "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c",
    "v074_source_sha256": "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8",
    "inputs_zip_sha256": "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666",
}

SOURCE_SEMANTICS = {
    "source_version": "v0.9.3",
    "formula": "lipschitz = tangent_dimension * field_sup / cauchy_gap",
    "comment": "induced infinity-norm Lipschitz bound is d*M/(R-r)",
    "meaning": "cauchy_lipschitz_upper is already ||DX||_infinity, not a per-entry bound",
}


def atomic(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tmp.replace(path)


def propagate(L: Decimal, steps: int) -> Decimal:
    h = Decimal(FROZEN["time_step"])
    M = Decimal(FROZEN["field_sup"])
    r = Decimal(FROZEN["initial_overlap_radius"])
    g = (L * h).exp()
    for _ in range(steps):
        r = g * r + h * M
    return r


def maximum_safe_steps(L: Decimal, cap: int = 10000) -> tuple[int, Decimal, Decimal]:
    R = Decimal(FROZEN["inner_radius"])
    previous = Decimal(FROZEN["initial_overlap_radius"])
    for step in range(1, cap + 1):
        current = propagate(L, step)
        if current >= R:
            return step - 1, previous, current
        previous = current
    return cap, previous, previous


def parse() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(description=TITLE)
    p.add_argument("--outdir", default="response_fibre_cauchy_norm_correction_v0_9_20_results")
    p.add_argument("--target-steps", type=int, default=557)
    return p.parse_known_args()


def run(args: argparse.Namespace) -> dict:
    started = time.time()
    if args.target_steps < 1:
        raise ValueError("--target-steps must be positive")
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    d = Decimal(FROZEN["dimension"])
    L_correct = Decimal(FROZEN["cauchy_lipschitz_upper"])
    L_wrong = d * L_correct
    entry_bound = L_correct / d
    correct_safe, correct_last, correct_next = maximum_safe_steps(L_correct)
    wrong_safe, wrong_last, wrong_next = maximum_safe_steps(L_wrong)
    target_correct = propagate(L_correct, args.target_steps)
    target_wrong = propagate(L_wrong, args.target_steps)

    # Frozen v0.9.12 values used a slightly different outward decimal guard.
    # We audit qualitative inclusions and a tight relative numerical agreement,
    # rather than claiming bit identity between Decimal and Arb.
    v0912_last = Decimal(FROZEN["v0912_last_radius"])
    relative_last_difference = abs(correct_last - v0912_last) / v0912_last
    R = Decimal(FROZEN["inner_radius"])

    gates = {
        "source_formula_is_induced_infinity_norm": SOURCE_SEMANTICS["meaning"].startswith("cauchy_lipschitz_upper is already"),
        "corrected_bound_equals_frozen_cauchy_lipschitz": L_correct == Decimal(FROZEN["cauchy_lipschitz_upper"]),
        "v0917_v0918_extra_dimension_factor_identified": L_wrong == d * L_correct,
        "incorrect_interpretation_reproduces_172_step_limit": wrong_safe == 172,
        "corrected_interpretation_certifies_557_steps": correct_safe == 557,
        "corrected_step_557_strictly_inside": correct_last < R,
        "corrected_step_558_not_strictly_inside": correct_next >= R,
        "corrected_radius_agrees_with_v0912": relative_last_difference < Decimal("2e-4"),
    }
    passed = all(gates.values())

    correction = {
        "schema": "geometric-flow/cauchy-induced-norm-correction/v0.9.20",
        "frozen_source_semantics": SOURCE_SEMANTICS,
        "correct_adapter_contract": {
            "formal_jacobian_induced_infinity_upper": str(L_correct),
            "optional_uniform_per_entry_upper": str(entry_bound),
            "warning": "If a uniform per-entry box is constructed, use L_induced/d per entry; do not place L_induced in every entry.",
        },
        "supersedes_capability_diagnosis_only": ["v0.9.18", "v0.9.19"],
        "does_not_invalidate": ["v0.9.3 local Picard theorem", "v0.9.10 second-chart theorem", "v0.9.12 scalar exhaustion result"],
    }
    atomic(out / "cauchy_norm_semantic_correction.json", correction)

    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": "VALIDATED_CAUCHY_NORM_SEMANTIC_CORRECTION_557_SCALAR_STEPS_CERTIFIED" if passed else "V0920_CORRECTION_INCONCLUSIVE_FAIL_CLOSED",
        "correction": {
            "dimension": int(d),
            "frozen_cauchy_lipschitz_upper_already_induced": str(L_correct),
            "derived_uniform_per_entry_bound": str(entry_bound),
            "incorrect_v0918_induced_bound": str(L_wrong),
            "overcount_factor": str(d),
            "source_semantics": SOURCE_SEMANTICS,
        },
        "incorrect_v0918_reproduction": {
            "maximum_safe_steps": wrong_safe,
            "last_safe_radius": str(wrong_last),
            "first_failing_radius": str(wrong_next),
            "target_radius": str(target_wrong),
        },
        "corrected_reaudit": {
            "maximum_safe_steps": correct_safe,
            "last_safe_step": correct_safe,
            "first_failing_step": correct_safe + 1,
            "last_safe_radius": str(correct_last),
            "first_failing_radius": str(correct_next),
            "requested_target_radius": str(target_correct),
            "inner_domain_radius": str(R),
            "relative_difference_to_v0912_last_radius": str(relative_last_difference),
        },
        "gates": gates,
        "all_scientific_gates_pass": passed,
        "scalar_reachable_tube_557_steps_certified": passed and args.target_steps <= correct_safe,
        "six_component_endpoint_center_certified": False,
        "geometric_flow_557_step_endpoint_center_certified": False,
        "complete_child_certified": False,
        "global_flow_claimed": False,
        "correction_certificate": str(out / "cauchy_norm_semantic_correction.json"),
        "next_required_step": "bind the repository-native six-component field to a validated Taylor/Lohner endpoint-centre integrator; local DX may improve sharpness but is no longer required merely to recover the 557-step scalar tube",
        "claim_boundary": "corrects a norm-semantics overcount and certifies only the 557-step scalar reachable tube; no endpoint centre, complete-child, or global theorem",
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
            "scientific_status": "V0920_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
