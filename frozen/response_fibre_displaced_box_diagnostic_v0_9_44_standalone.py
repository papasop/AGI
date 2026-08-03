#!/usr/bin/env python3
"""Geometric-Flow v0.9.44 — symmetric displaced-box identifiability audit.

This is deliberately a diagnostic, not a Jacobian certificate.  It consumes
the frozen numerical enclosure certified by v0.9.43.3 and probes the exact
public adapter semantics on symmetric Arb boxes.  Equal output boxes imply
that the exported adapter is position-insensitive; they do *not* imply DX=0.
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

getcontext().prec = 80

TITLE = "GEOMETRIC-FLOW SYMMETRIC DISPLACED-BOX FIELD IDENTIFIABILITY AUDIT"
VERSION = "0.9.44"
V09433_SOURCE_SHA256 = "ef8cc30b3cde528a6cd94d1192ce7a4a360c4635c5e675e2166dd198b969fe46"
V09433_PROBE_CERTIFICATE_SHA256 = "1e8a83e640d599ac4702e1db0e111cc300cadf234b992f90a59325f3c8200a44"
PROBE_RADIUS = Decimal("1e-15")
FIELD_LOWER = tuple(map(Decimal, (
    "-0.054257814333446494", "0.250807076651539",
    "0.36684463493136943", "0.4609128764089135",
    "0.44866279893482147", "-0.5705898839322309")))
FIELD_UPPER = tuple(map(Decimal, (
    "-0.032846579209340906", "0.3012176569490054",
    "0.42730335763033733", "0.53300164907276",
    "0.5186358609602045", "-0.49519036196110944")))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default="response_fibre_displaced_box_v0_9_44_results")
    p.add_argument("--radii", nargs=2, default=("2.5e-16", "5e-16"))
    p.add_argument("--box-radius-fraction", default="0.25")
    p.add_argument("--v09433", default=None,
                   help="optional v0.9.43.3 source; if supplied its frozen SHA-256 is checked")
    return p.parse_known_args()


def enclosure_for_exported_adapter(a_box):
    # Exact semantics of the v0.9.43.3 exported adapter: validate the input,
    # then return the frozen uniform signed enclosure.
    if not isinstance(a_box, (list, tuple)) or len(a_box) != 6:
        raise ValueError("expected six coordinates")
    for lo, hi in a_box:
        if lo > hi or lo <= -PROBE_RADIUS or hi >= PROBE_RADIUS:
            raise ValueError("displaced box leaves certified centre probe domain")
    return tuple(zip(FIELD_LOWER, FIELD_UPPER))


def run(args):
    started = time.time()
    out = Path(args.outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    radii = tuple(Decimal(str(x)) for x in args.radii)
    frac = Decimal(str(args.box_radius_fraction))
    if not (len(radii) == 2 and Decimal(0) < radii[0] < radii[1] < PROBE_RADIUS):
        raise ValueError("require 0 < radius_1 < radius_2 < 1e-15")
    if not (Decimal(0) < frac < Decimal(1)):
        raise ValueError("box-radius-fraction must lie in (0,1)")

    source_checked = False
    source_hash_exact = None
    if args.v09433:
        q = Path(args.v09433).resolve()
        if not q.is_file():
            raise FileNotFoundError(q)
        source_checked = True
        source_hash_exact = sha256_file(q) == V09433_SOURCE_SHA256
        if not source_hash_exact:
            raise RuntimeError("supplied v0.9.43.3 source hash mismatch")

    zero = tuple((Decimal(0), Decimal(0)) for _ in range(6))
    centre_output = enclosure_for_exported_adapter(zero)
    records = []
    all_identical = True
    all_inside = True
    symmetry_exact = True
    for delta in radii:
        rho = delta * frac
        for axis in range(6):
            pair = {}
            for sign, label in ((Decimal(1), "plus"), (Decimal(-1), "minus")):
                c = sign * delta
                box = [(Decimal(0), Decimal(0)) for _ in range(6)]
                box[axis] = (c - rho, c + rho)
                inside = all(lo > -PROBE_RADIUS and hi < PROBE_RADIUS for lo, hi in box)
                all_inside &= inside
                output = enclosure_for_exported_adapter(box)
                same = output == centre_output
                all_identical &= same
                pair[label] = output
                records.append({
                    "radius": str(delta), "axis": axis, "sign": "+" if sign > 0 else "-",
                    "input_box": [[str(lo), str(hi)] for lo, hi in box],
                    "strictly_inside_probe": inside,
                    "output_lower": [str(x[0]) for x in output],
                    "output_upper": [str(x[1]) for x in output],
                    "identical_to_centre_output": same,
                })
            symmetry_exact &= pair["plus"] == pair["minus"]

    # A deliberately invalid box tests that the frozen domain boundary is real.
    outside_rejected = False
    try:
        bad = [(Decimal(0), Decimal(0)) for _ in range(6)]
        bad[0] = (PROBE_RADIUS, PROBE_RADIUS)
        enclosure_for_exported_adapter(bad)
    except ValueError:
        outside_rejected = True

    gates = {
        "frozen_v09433_identity_declared": True,
        "optional_v09433_source_hash_exact": (not source_checked) or source_hash_exact,
        "two_predeclared_displacement_radii": len(radii) == 2,
        "twelve_symmetric_direction_pairs_evaluated": len(records) == 24,
        "all_displaced_boxes_strictly_inside_probe": all_inside,
        "plus_minus_outputs_exactly_equal": symmetry_exact,
        "all_outputs_identical_to_centre_enclosure": all_identical,
        "outside_probe_box_rejected": outside_rejected,
        "finite_difference_not_promoted_to_formal_DX": True,
    }
    passed = all(gates.values())
    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": (
            "EXPORTED_UNIFORM_FIELD_ADAPTER_POSITION_INSENSITIVE_POINT_DX_NOT_IDENTIFIABLE"
            if passed else "V0944_INCONCLUSIVE_FAIL_CLOSED"),
        "audit_kind": "adapter-semantics displaced-Arb-box diagnostic; not a fresh repository-native field evaluation",
        "frozen_v09433": {
            "source_sha256": V09433_SOURCE_SHA256,
            "probe_certificate_sha256": V09433_PROBE_CERTIFICATE_SHA256,
            "source_supplied_and_checked": source_checked,
        },
        "coordinate_system": "v0.9.30-fourth-recentered-intrinsic-tangent",
        "certified_probe_radius": str(PROBE_RADIUS),
        "displacement_radii": [str(x) for x in radii],
        "displaced_box_radius_fraction": str(frac),
        "probe_count": len(records),
        "distinct_output_enclosures": 1 if all_identical else None,
        "records": records,
        "gates": gates,
        "all_scientific_gates_pass": passed,
        "exported_adapter_position_sensitive": not all_identical,
        "repository_native_displaced_box_X_ready": False,
        "formal_point_dependent_X_ready": False,
        "formal_jacobian_DX_ready": False,
        "finite_difference_DX_claimed": False,
        "qr_lohner_flowpipe_certified": False,
        "fifth_frame_certified": False,
        "global_flow_claimed": False,
        "interpretation": (
            "The v0.9.43.3 public adapter returns one frozen uniform enclosure for every admissible input box. "
            "Its symmetric displaced outputs therefore contain no identifiable position dependence. "
            "This does not establish that the geometric field is constant or that DX=0."
        ),
        "next_required_step": (
            "refactor the active repository-native Arb expression so that a_box enters the implicit root, "
            "metric, projected gradient, and normalized field calculations; then repeat these 24 probes"
        ),
        "claim_boundary": (
            "diagnosis of the exported v0.9.43.3 uniform-enclosure adapter only; no fresh displaced-box "
            "geometric field, formal derivative, directional QR/Lohner flowpipe, fifth frame, or global flow"
        ),
        "elapsed_seconds": time.time() - started,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    certificate = out / "displaced_box_identifiability_certificate.json"
    certificate.write_text(json.dumps(result, indent=2) + "\n")
    summary = dict(result)
    summary["records"] = str(certificate)
    summary["certificate_sha256"] = sha256_file(certificate)
    (out / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main():
    args, unknown = parse_args()
    if unknown:
        print(f"[notice] ignored notebook/kernel arguments: {unknown}")
    try:
        result = run(args)
        print("=" * 112)
        print(f"{TITLE} v{VERSION}")
        print("=" * 112)
        print(json.dumps(result, indent=2))
        return 0 if result["all_scientific_gates_pass"] else 2
    except Exception as exc:
        print(json.dumps({"scientific_status": "V0944_FAILED_CLOSED",
                          "error_type": type(exc).__name__, "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
