#!/usr/bin/env python3
"""Audit the terminal correlated set in an actual fifth Arb SVD frame.

This program deliberately does not replace the nonlinear chart transition by
Q5.T @ Q4.  A proof-producing backend must enclose the complete map

    fourth intrinsic set -> phase box -> fifth intrinsic box

and bind that enclosure to the frozen v0.10.13.1 terminal flowpipe.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

TITLE = "GEOMETRIC-FLOW TERMINAL CORRELATED SET / ACTUAL FIFTH SVD FRAME INCLUSION"
VERSION = "0.10.14.1"
SCHEMA = "geometric-flow/fifth-frame-transition-arb-certificate/v0.10.14.1"


def clean(argv):
    out, ignored, i = [], [], 0
    while i < len(argv):
        if argv[i] == "-f" and i + 1 < len(argv):
            ignored += argv[i:i + 2]
            i += 2
        else:
            out.append(argv[i])
            i += 1
    if ignored:
        print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    return out


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def locate(explicit, candidates, label):
    paths = ([Path(explicit)] if explicit else []) + [Path(p) for p in candidates]
    for path in paths:
        if path.is_file():
            return path.resolve()
    raise FileNotFoundError(label)


_NUMBER = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


def arb_mid_rad(value):
    """Return conservative float midpoint/radius metadata for an Arb print string."""
    if isinstance(value, (int, float)):
        x = float(value)
        return x, 0.0
    text = str(value).strip()
    if text == "0":
        return 0.0, 0.0
    nums = [float(x) for x in _NUMBER.findall(text)]
    if not nums:
        raise ValueError(f"not an Arb scalar: {value!r}")
    if text.startswith("[+/-") or text.startswith("[-/+"):
        return 0.0, abs(nums[0])
    midpoint = nums[0]
    radius = abs(nums[1]) if "+/-" in text and len(nums) > 1 else 0.0
    return midpoint, radius


def finite_scalar(value):
    try:
        midpoint, radius = arb_mid_rad(value)
        return math.isfinite(midpoint) and math.isfinite(radius) and radius >= 0
    except Exception:
        return False


def finite_vector(value, n):
    try:
        return len(value) == n and all(finite_scalar(x) for x in value)
    except Exception:
        return False


def finite_matrix(value, rows, cols):
    return isinstance(value, list) and len(value) == rows and all(finite_vector(r, cols) for r in value)


def ordered_box(box, n=6):
    if not isinstance(box, dict):
        return False
    lo, hi = box.get("lower"), box.get("upper")
    return finite_vector(lo, n) and finite_vector(hi, n) and all(float(a) <= float(b) for a, b in zip(lo, hi))


def strict_box_in_radius(box, radius):
    if not ordered_box(box):
        return False
    return max(max(abs(float(a)), abs(float(b))) for a, b in zip(box["lower"], box["upper"])) < float(radius)


def find_terminal_record(records):
    if isinstance(records, dict):
        for key in ("records", "step_records", "flowpipe_records"):
            if isinstance(records.get(key), list):
                records = records[key]
                break
    if not isinstance(records, list) or not records:
        raise ValueError("v0.10.13.1 propagation records are empty or malformed")
    return records[-1]


def extract_terminal_set(record):
    center = record.get("center") or record.get("center_midpoint")
    shape = record.get("shape_matrix") or record.get("affine_shape") or record.get("shape")
    remainder = (record.get("interval_remainder_upper") or
                 record.get("remainder_upper") or record.get("remainder"))
    support = (record.get("formal_coordinate_support_upper") or
               record.get("coordinate_support_upper") or
               record.get("support_upper") or record.get("support"))
    return {"center": center, "shape_matrix": shape,
            "interval_remainder_upper": remainder, "support_upper": support}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v01013-summary")
    ap.add_argument("--v01013-records")
    ap.add_argument("--backend-certificate")
    ap.add_argument("--outdir", default="geometric_flow_fifth_frame_v0_10_14_results")
    args, _ = ap.parse_known_args(clean(sys.argv[1:]))
    out = Path(args.outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    summary_path = locate(args.v01013_summary, [
        "geometric_flow_reindexed_taylor_v0_10_13_results/run_summary.json",
        "/content/geometric_flow_reindexed_taylor_v0_10_13_results/run_summary.json",
    ], "v0.10.13.1 summary not found")
    summary = json.loads(summary_path.read_text())

    records_path = locate(args.v01013_records, [
        "geometric_flow_reindexed_taylor_v0_10_13_results/reindexed_taylor_propagation/centred_taylor_affine_lohner_records.json",
        "/content/geometric_flow_reindexed_taylor_v0_10_13_results/reindexed_taylor_propagation/centred_taylor_affine_lohner_records.json",
        "geometric_flow_reindexed_taylor_v0_10_13_results/reindexed_taylor_propagation/taylor_affine_lohner_records.json",
        "/content/geometric_flow_reindexed_taylor_v0_10_13_results/reindexed_taylor_propagation/taylor_affine_lohner_records.json",
    ], "v0.10.13.1 propagation records not found; pass --v01013-records")
    terminal = extract_terminal_set(find_terminal_record(json.loads(records_path.read_text())))
    terminal_valid = (finite_vector(terminal["center"], 6) and
                      finite_matrix(terminal["shape_matrix"], 6, 6) and
                      finite_vector(terminal["interval_remainder_upper"], 6) and
                      finite_vector(terminal["support_upper"], 6))
    terminal_semantic = {
        "summary_sha256": sha256(summary_path),
        "records_sha256": sha256(records_path),
        "terminal_set": terminal,
    }
    terminal_semantic_path = out / "frozen_terminal_correlated_set.json"
    terminal_semantic_path.write_text(json.dumps(terminal_semantic, indent=2) + "\n")
    terminal_hash = sha256(terminal_semantic_path)

    contract = {
        "schema": SCHEMA,
        "required_backend": "python-flint/Arb at precision_bits >= 192",
        "frozen_terminal_set_sha256": terminal_hash,
        "required_operations": [
            "lift the complete correlated fourth-intrinsic set through the certified fourth normal graph",
            "solve the fifth-centre normal equation by strict parametric Krawczyk inclusion",
            "construct an Arb-enclosed fifth tangent/normal SVD frame",
            "evaluate the complete nonlinear fourth-to-fifth intrinsic chart transition",
            "include its image box strictly in the fifth real Picard start domain",
        ],
        "required_fields": [
            "schema", "precision_bits", "frozen_terminal_set_sha256",
            "fifth_normal_root_box", "fifth_tangent_frame_midpoint",
            "fifth_frame_orthogonality_defect_upper",
            "fifth_response_minimum_singular_value_lower",
            "nonlinear_transition_image_box", "fifth_start_domain_radius",
            "backend_gates",
        ],
        "forbidden_shortcuts": [
            "midpoint-only transition", "Q5.T@Q4 without nonlinear remainder",
            "sampling-only containment", "finite-difference Jacobian",
        ],
    }
    contract_path = out / "fifth_frame_transition_backend_contract.json"
    contract_path.write_text(json.dumps(contract, indent=2) + "\n")

    cert = None
    cert_path = None
    if args.backend_certificate:
        cert_path = Path(args.backend_certificate).resolve()
        if not cert_path.is_file():
            raise FileNotFoundError(f"backend certificate not found: {cert_path}")
        cert = json.loads(cert_path.read_text())

    cg = (cert or {}).get("backend_gates", {})
    image_box = (cert or {}).get("nonlinear_transition_image_box")
    start_radius = (cert or {}).get("fifth_start_domain_radius", float("nan"))
    try:
        precision_ok = int((cert or {}).get("precision_bits", 0)) >= 192
        singular_ok = float((cert or {}).get("fifth_response_minimum_singular_value_lower", 0)) > 0
        orth_ok = float((cert or {}).get("fifth_frame_orthogonality_defect_upper", math.inf)) < 1e-10
        inclusion_ok = strict_box_in_radius(image_box, start_radius)
    except Exception:
        precision_ok = singular_ok = orth_ok = inclusion_ok = False

    base_gates = {
        "v01013_all_scientific_gates_pass": bool(summary.get("all_scientific_gates_pass")),
        "v01013_terminal_correlated_set_certified": bool(summary.get("terminal_correlated_set_certified")),
        "terminal_correlated_set_well_formed": terminal_valid,
        "terminal_set_hash_frozen": True,
        "backend_contract_emitted": True,
    }
    frame_gates = {
        "formal_Arb_backend_certificate_present": cert is not None,
        "certificate_schema_exact": (cert or {}).get("schema") == SCHEMA,
        "certificate_bound_to_terminal_set": (cert or {}).get("frozen_terminal_set_sha256") == terminal_hash,
        "formal_precision_at_least_192_bits": precision_ok,
        "unique_fifth_parametric_normal_root": bool(cg.get("unique_fifth_parametric_normal_root")),
        "fifth_response_full_row_rank": singular_ok and bool(cg.get("fifth_response_full_row_rank")),
        "fifth_frame_orthogonal_complete": orth_ok and bool(cg.get("fifth_frame_orthogonal_complete")),
        "complete_nonlinear_transition_image_box": ordered_box(image_box),
        "terminal_image_strictly_inside_fifth_start_domain": inclusion_ok,
        "no_linear_transition_shortcut": bool(cg.get("nonlinear_transition_with_formal_remainder")),
        "no_finite_difference": bool(cg.get("no_finite_difference")),
    }
    base_pass = all(base_gates.values())
    frame_pass = all(frame_gates.values())
    passed = base_pass and frame_pass
    status = ("VALIDATED_TERMINAL_CORRELATED_SET_IN_ACTUAL_FIFTH_SVD_FRAME_CERTIFIED"
              if passed else "FIFTH_FRAME_TARGET_FROZEN_ARB_TRANSITION_BACKEND_OPEN")
    report = {
        "title": TITLE, "version": VERSION, "scientific_status": status,
        "frozen_terminal_set": str(terminal_semantic_path),
        "frozen_terminal_set_sha256": terminal_hash,
        "backend_contract": str(contract_path),
        "backend_certificate": str(cert_path) if cert_path else None,
        "base_gates": base_gates, "frame_gates": frame_gates,
        "all_scientific_gates_pass": passed,
        "terminal_correlated_set_certified": bool(summary.get("terminal_correlated_set_certified")),
        "fifth_frame_certified": passed,
        "fifth_local_picard_chart_certified": False,
        "complete_child_certified": False,
        "global_flow_claimed": False,
        "next_required_step": ("construct the fifth complex fibre graph, pullback metric and Picard microstep"
                               if passed else "implement the Arb backend specified by fifth_frame_transition_backend_contract.json and rerun with --backend-certificate"),
        "claim_boundary": ("actual fifth normal root/frame and complete nonlinear terminal-set transition inclusion only; "
                           "no fifth Picard chart, complete child, or global flow"),
    }
    (out / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print("=" * 112)
    print(f"{TITLE} v{VERSION}")
    print("=" * 112)
    print(json.dumps(report, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "IPython" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
