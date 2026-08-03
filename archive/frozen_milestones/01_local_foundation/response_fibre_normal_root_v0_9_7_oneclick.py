#!/usr/bin/env python3
"""Fail-closed recentered normal-root audit for Geometric-Flow v0.9.7.

This one-click driver continues the repository-native v0.9.6 preflight and
validates an Arb-emitted Krawczyk certificate for

    B(R(theta0 + T a_c + N b) - c) = 0.

It never upgrades numerical diagnostics into a theorem.  Without a formal
backend certificate it writes the exact backend contract and exits with the
scientifically honest OPEN status.  With a certificate, every interval gate
below must pass before existence and uniqueness of the normal root is claimed.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import time
import zlib
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Any

VERSION = "0.9.7"
TITLE = "GEOMETRIC-FLOW RECENTERED NORMAL-ROOT KRAWCZYK AUDIT"
REPOSITORY = "https://github.com/papasop/Geometric-Flow"
V096_NAME = "archive/frozen_milestones/01_local_foundation/response_fibre_recenter_preflight_v0_9_6_oneclick.py"
# Frozen, zlib-compressed source of v0.9.6.  This makes v0.9.7 genuinely
# standalone in Colab while retaining the same repository/hash checks.
EMBEDDED_V096_ZLIB_B64 = """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"""
EXPECTED_HASHES = {
    "v093_source": "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c",
    "v074_source": "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8",
    "inputs_zip": "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666",
}
getcontext().prec = 90


def canonical_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tmp.replace(path)


def dec(value: Any) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"not a finite decimal: {value!r}") from exc
    if not result.is_finite():
        raise ValueError(f"not a finite decimal: {value!r}")
    return result


def vector(value: Any, size: int, label: str) -> list[Decimal]:
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"{label} must contain exactly {size} entries")
    return [dec(x) for x in value]


def matrix(value: Any, size: int, label: str) -> list[list[Decimal]]:
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"{label} must be {size}x{size}")
    return [vector(row, size, f"{label}[{i}]") for i, row in enumerate(value)]


def locate_v096(explicit: str | None, embedded_destination: Path) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    # ``__file__`` is absent when the complete program is pasted into a
    # Colab/Jupyter cell.  Resolve the script directory only when available.
    candidates += [Path.cwd() / V096_NAME, Path("/content") / V096_NAME]
    script_name = globals().get("__file__")
    if script_name:
        candidates.append(Path(script_name).resolve().parent / V096_NAME)
    for path in candidates:
        if path.is_file():
            return path.resolve()
    embedded_destination.parent.mkdir(parents=True, exist_ok=True)
    source = zlib.decompress(base64.b64decode(EMBEDDED_V096_ZLIB_B64))
    digest = hashlib.sha256(source).hexdigest()
    expected = "014d265a818bbd82c8aa8805317e61222ccf13136df871947a71ffa9e0e38291"
    if digest != expected:
        raise RuntimeError(f"embedded v0.9.6 source hash mismatch: {digest}")
    embedded_destination.write_bytes(source)
    return embedded_destination.resolve()


def run_v096(script: Path, output: Path, recenter_radius: str) -> dict[str, Any]:
    summary = output / "run_summary.json"
    cmd = [sys.executable, str(script), "--outdir", str(output),
           "--recenter-radius", recenter_radius]
    completed = subprocess.run(cmd, text=True, capture_output=True)
    (output.parent / "v096_stdout.txt").write_text(completed.stdout)
    (output.parent / "v096_stderr.txt").write_text(completed.stderr)
    if completed.returncode != 0 or not summary.is_file():
        raise RuntimeError(
            f"v0.9.6 preflight failed with exit={completed.returncode}; inspect v096 logs"
        )
    result = json.loads(summary.read_text())
    if result.get("scientific_status") != "REPOSITORY_NATIVE_RECENTER_TARGET_EXTRACTED_FORMAL_NORMAL_ROOT_OPEN":
        raise RuntimeError("v0.9.6 did not reach its frozen target-extracted status")
    if not all(result.get("base_gates", {}).values()):
        raise RuntimeError("one or more v0.9.6 formal base gates failed")
    files = result.get("repository_dependency", {}).get("files", {})
    for key, digest in EXPECTED_HASHES.items():
        if files.get(key, {}).get("sha256") != digest or files.get(key, {}).get("hash_match") is not True:
            raise RuntimeError(f"frozen dependency mismatch: {key}")
    return result


def backend_contract(v096: dict[str, Any], radius: str) -> dict[str, Any]:
    candidate = v096["recenter_candidate"]
    return {
        "schema": "geometric-flow/recentered-normal-root-krawczyk/v0.9.7",
        "repository": REPOSITORY,
        "frozen_repository_hashes": EXPECTED_HASHES,
        "coordinate_system": candidate["coordinate_system"],
        "tangent_coordinate_midpoint_a_c": candidate["euler_recenter_midpoint"],
        "normal_root_box": {"center": ["0"] * 8, "radius": str(radius)},
        "equation": "B(R(theta0+T*a_c+N*b)-R(theta0))=0",
        "required_arithmetic": "python-flint Arb/Acb outward-rounded intervals",
        "required_output_fields": [
            "schema", "formal_backend", "precision_bits", "dimension",
            "frozen_repository_hashes", "a_c", "normal_box_center",
            "normal_box_radius", "root_residual_contains_zero",
            "normal_derivative_invertible", "krawczyk_image_center",
            "krawczyk_image_radius", "krawczyk_strict_interior_margin",
            "response_difference_contains_zero", "all_backend_gates_pass",
        ],
        "proof_obligation": "K(X) is a strict subset of interior(X); then a unique normal root exists in X",
    }


def audit_certificate(cert: dict[str, Any], contract: dict[str, Any]) -> tuple[dict[str, bool], dict[str, Any]]:
    dim = 8
    if cert.get("schema") != contract["schema"]:
        raise ValueError("backend certificate schema mismatch")
    if cert.get("dimension") != dim:
        raise ValueError("normal-root dimension must be 8")
    if cert.get("formal_backend") not in {"Arb", "python-flint/Arb", "python-flint Arb"}:
        raise ValueError("certificate must declare an Arb formal backend")
    if int(cert.get("precision_bits", 0)) < 128:
        raise ValueError("formal precision must be at least 128 bits")
    if cert.get("frozen_repository_hashes") != EXPECTED_HASHES:
        raise ValueError("certificate frozen hashes do not match the protocol")
    a_c = vector(cert.get("a_c"), 6, "a_c")
    expected_a = vector(contract["tangent_coordinate_midpoint_a_c"], 6, "contract a_c")
    center = vector(cert.get("normal_box_center"), dim, "normal_box_center")
    radius = vector(cert.get("normal_box_radius"), dim, "normal_box_radius")
    image_center = vector(cert.get("krawczyk_image_center"), dim, "krawczyk_image_center")
    image_radius = vector(cert.get("krawczyk_image_radius"), dim, "krawczyk_image_radius")
    margins = vector(cert.get("krawczyk_strict_interior_margin"), dim,
                     "krawczyk_strict_interior_margin")
    component_interior = [
        abs(image_center[i] - center[i]) + image_radius[i] < radius[i]
        for i in range(dim)
    ]
    recomputed_margin = [
        radius[i] - abs(image_center[i] - center[i]) - image_radius[i]
        for i in range(dim)
    ]
    gates = {
        "frozen_repository_hashes_match": True,
        "candidate_tangent_point_exactly_matches_v096": a_c == expected_a,
        "all_normal_box_radii_strictly_positive": all(x > 0 for x in radius),
        "all_krawczyk_image_radii_nonnegative": all(x >= 0 for x in image_radius),
        "reported_margins_strictly_positive": all(x > 0 for x in margins),
        "reported_margins_do_not_exceed_recomputed": all(
            Decimal(0) < margins[i] <= recomputed_margin[i] for i in range(dim)
        ),
        "krawczyk_image_strictly_inside_normal_box": all(component_interior),
        "root_residual_contains_zero": cert.get("root_residual_contains_zero") is True,
        "normal_derivative_invertible": cert.get("normal_derivative_invertible") is True,
        "response_difference_contains_zero": cert.get("response_difference_contains_zero") is True,
        "all_backend_gates_pass": cert.get("all_backend_gates_pass") is True,
    }
    details = {
        "recomputed_strict_interior_margin": [format(x, ".40E") for x in recomputed_margin],
        "minimum_recomputed_margin": format(min(recomputed_margin), ".40E"),
        "maximum_component_utilization": format(max(
            (abs(image_center[i] - center[i]) + image_radius[i]) / radius[i]
            for i in range(dim)
        ), ".40E"),
    }
    return gates, details


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="response_fibre_normal_root_v0_9_7_results")
    parser.add_argument("--v096")
    parser.add_argument("--normal-root-radius", default="2e-18")
    parser.add_argument("--recenter-radius", default="2e-14")
    parser.add_argument("--backend-certificate")
    parser.add_argument("--skip-v096-rerun", action="store_true")
    return parser.parse_known_args()


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    v096_out = out / "v096_formal_preflight"
    if args.skip_v096_rerun and (v096_out / "run_summary.json").is_file():
        v096 = json.loads((v096_out / "run_summary.json").read_text())
        if not all(v096.get("base_gates", {}).values()):
            raise RuntimeError("cached v0.9.6 base gates are not all true")
        v096_script = locate_v096(args.v096, out / "embedded_backend" / V096_NAME)
    else:
        v096_script = locate_v096(args.v096, out / "embedded_backend" / V096_NAME)
        v096 = run_v096(v096_script, v096_out, args.recenter_radius)

    contract = backend_contract(v096, args.normal_root_radius)
    contract_path = out / "normal_root_backend_contract.json"
    atomic_json(contract_path, contract)
    certificate_path = Path(args.backend_certificate) if args.backend_certificate else out / "normal_root_arb_certificate.json"

    if certificate_path.is_file():
        certificate = json.loads(certificate_path.read_text())
        gates, audit = audit_certificate(certificate, contract)
        certified = all(gates.values())
        status = ("VALIDATED_RECENTERED_NORMAL_ROOT_KRAWCZYK_CERTIFIED" if certified
                  else "RECENTERED_NORMAL_ROOT_CERTIFICATE_REJECTED_FAIL_CLOSED")
    else:
        certificate = None
        audit = {"reason": "No Arb normal-root certificate was supplied or emitted."}
        gates = {
            "v096_repository_native_preflight_passed": True,
            "formal_arb_normal_root_certificate_present": False,
            "krawczyk_image_strictly_inside_normal_box": False,
            "unique_recentered_normal_root_certified": False,
        }
        certified = False
        status = "RECENTER_TARGET_READY_FORMAL_NORMAL_ROOT_BACKEND_CERTIFICATE_OPEN"

    protocol = {
        "version": VERSION, "repository": REPOSITORY,
        "frozen_repository_hashes": EXPECTED_HASHES,
        "normal_root_radius": str(args.normal_root_radius),
        "v096_protocol_sha256": v096.get("protocol_sha256"),
        "contract_sha256": canonical_hash(contract),
    }
    result = {
        "title": TITLE, "version": VERSION, "scientific_status": status,
        "repository_dependency": {"repository": REPOSITORY,
                                  "explicitly_calls_v096_repository_native_preflight": True,
                                  "v096_script": str(v096_script)},
        "v096_status": v096.get("scientific_status"),
        "v096_all_base_gates_pass": all(v096.get("base_gates", {}).values()),
        "backend_contract": str(contract_path),
        "backend_certificate": str(certificate_path) if certificate else None,
        "normal_root_audit": audit, "gates": gates,
        "normal_root_krawczyk_certified": certified,
        "recentered_tangent_normal_frame_certified": False,
        "second_local_picard_chart_certified": False,
        "global_flow_claimed": False,
        "all_scientific_gates_pass": certified,
        "protocol_sha256": canonical_hash(protocol),
        "next_required_step": (
            "Construct and run the Arb normal-root backend specified by normal_root_backend_contract.json."
            if not certificate else
            "Recompute the Jacobian SVD tangent/normal frame at the certified corrected centre."
        ),
        "claim_boundary": (
            "Only existence and uniqueness of the recentered normal root may be claimed when every gate passes; "
            "no second-chart or global-flow claim is made."
        ),
        "elapsed_seconds": time.time() - started,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    result["report_sha256_before_self_field"] = canonical_hash(result)
    atomic_json(out / "protocol.json", protocol)
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
        # OPEN is an expected, successful preflight. A supplied invalid certificate is an error.
        return 2 if "REJECTED" in result["scientific_status"] else 0
    except Exception as exc:
        print(json.dumps({"scientific_status": "V097_FAILED_CLOSED",
                          "error_type": type(exc).__name__, "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
