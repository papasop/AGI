#!/usr/bin/env python3
"""Geometric-Flow third-recentered tangent/normal-frame audit v0.9.24.

The driver reruns the hash-locked v0.9.23 endpoint-box/parametric-root chain,
freezes the third-recenter target, emits an executable proof contract, and
audits an optional Arb certificate produced by a repository-native backend.

Without a genuine third-centre Arb certificate this program deliberately
finishes at BACKEND_IMPLEMENTATION_OPEN.  It never reuses v0.9.9 frame numbers
as evidence for a different centre and never claims a third Picard chart,
complete-child traversal, or global flow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
import urllib.request
import importlib.util
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

VERSION = "0.9.24"
TITLE = "GEOMETRIC-FLOW FORMAL THIRD-RECENTERED TANGENT-NORMAL FRAME AUDIT"
REPOSITORY = "https://github.com/papasop/Geometric-Flow"
FROZEN_COMMIT = "7e4a17e7fa8de859660694fef85ecd0990a9f577"
V0923_NAME = "archive/milestones/04_third_chart/response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py"
V0923_URL = (
    "https://raw.githubusercontent.com/papasop/Geometric-Flow/"
    f"{FROZEN_COMMIT}/{V0923_NAME}"
)
# SHA-256 of the exact raw GitHub bytes at FROZEN_COMMIT.  Do not calculate
# this from a rewritten text copy: adding one terminal newline changes it.
V0923_SHA256 = "c4099345b0479bc52fffbc9a5e1b376261ec1c49d64d606505d5ac50a3b6db22"

DIM_TANGENT = 6
DIM_RESPONSE = 8
DIM_CONTROL = 14
PRECISION_BITS = 192
ORTHOGONALITY_TOLERANCE = Decimal("1e-12")
FRAME_DOMAIN_RADIUS = Decimal("1e-11")
getcontext().prec = 80


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_json(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def ensure_formal_backend() -> None:
    """Make the nested frozen subprocess chain genuinely one-click in notebooks."""
    if importlib.util.find_spec("flint") is not None:
        return
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise RuntimeError("Install the frozen formal backend: pip install python-flint==0.8.0")
    print("[setup] installing frozen formal backend python-flint==0.8.0")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "python-flint==0.8.0"]
    )


def locate_or_download_v0923(explicit: str | None, destination: Path) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend([Path.cwd() / V0923_NAME, Path("/content") / V0923_NAME])
    script = globals().get("__file__")
    if script:
        candidates.append(Path(script).resolve().parent / V0923_NAME)

    for candidate in candidates:
        if candidate.is_file():
            digest = sha256_file(candidate)
            if digest != V0923_SHA256:
                raise RuntimeError(
                    f"v0.9.23 source hash mismatch at {candidate}: {digest}"
                )
            return candidate.resolve()

    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"[repository] downloading frozen {V0923_NAME}")
    urllib.request.urlretrieve(V0923_URL, destination)
    digest = sha256_file(destination)
    if digest != V0923_SHA256:
        destination.unlink(missing_ok=True)
        raise RuntimeError(
            f"downloaded v0.9.23 source hash mismatch: {digest}"
        )
    return destination.resolve()


def as_decimal_list(values: Any, expected: int, label: str) -> list[Decimal]:
    if not isinstance(values, list) or len(values) != expected:
        raise ValueError(f"{label} must contain exactly {expected} entries")
    result: list[Decimal] = []
    for item in values:
        value = Decimal(str(item))
        if not value.is_finite():
            raise ValueError(f"{label} contains a non-finite value")
        result.append(value)
    return result


def matrix_decimal(
    value: Any, rows: int, cols: int, label: str
) -> list[list[Decimal]]:
    if not isinstance(value, list) or len(value) != rows:
        raise ValueError(f"{label} must have shape {rows}x{cols}")
    return [as_decimal_list(row, cols, f"{label}[{i}]") for i, row in enumerate(value)]


def interval_box(value: Any, dimension: int, label: str) -> tuple[list[Decimal], list[Decimal]]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    lower = as_decimal_list(value.get("lower"), dimension, f"{label}.lower")
    upper = as_decimal_list(value.get("upper"), dimension, f"{label}.upper")
    if any(lo > hi for lo, hi in zip(lower, upper)):
        raise ValueError(f"{label} has an inverted interval")
    return lower, upper


def box_inside(
    inner_lower: list[Decimal],
    inner_upper: list[Decimal],
    outer_lower: list[Decimal],
    outer_upper: list[Decimal],
    *,
    strict: bool,
) -> bool:
    if strict:
        return all(
            olo < ilo and ihi < ohi
            for ilo, ihi, olo, ohi in zip(
                inner_lower, inner_upper, outer_lower, outer_upper
            )
        )
    return all(
        olo <= ilo and ihi <= ohi
        for ilo, ihi, olo, ohi in zip(
            inner_lower, inner_upper, outer_lower, outer_upper
        )
    )


def write_backend_contract(
    path: Path,
    target: dict[str, Any],
    target_certificate_sha256: str,
    target_semantic_sha256: str,
) -> dict[str, Any]:
    contract = {
        "schema": "geometric-flow/third-recentered-frame-backend-contract/v0.9.24",
        "formal_backend": "python-flint/Arb",
        "minimum_precision_bits": PRECISION_BITS,
        "frozen_repository": REPOSITORY,
        "frozen_commit": FROZEN_COMMIT,
        "frozen_v0923_source_sha256": V0923_SHA256,
        "frozen_target_certificate_sha256": target_certificate_sha256,
        "frozen_target_semantic_sha256": target_semantic_sha256,
        "coordinate_system": target.get("coordinate_system"),
        "dimensions": {
            "control": DIM_CONTROL,
            "response": DIM_RESPONSE,
            "tangent": DIM_TANGENT,
            "normal": DIM_RESPONSE,
        },
        "third_recenter_tangent_box": {
            "center": target["tangent_target_center"],
            "component_radius": target["tangent_target_component_radius"],
        },
        "required_backend_operations": [
            "solve the eight-dimensional implicit normal equation at the frozen third-centre tangent midpoint using Arb/Krawczyk",
            "enclose the corrected fourteen-dimensional phase centre",
            "evaluate the complete 8x14 response-Jacobian interval box on the corrected centre/root box",
            "construct midpoint-SVD tangent and normal preconditioner matrices",
            "prove full response row rank by a strict interval defect below one",
            "prove the 14x14 combined frame is orthogonally complete",
            "prove the 8x8 normal derivative is uniformly invertible",
            "transform the complete v0.9.23 endpoint box into the new tangent frame with outward rounding",
            "prove the transformed endpoint box is strictly inside the declared new-frame start domain",
        ],
        "required_certificate_fields": {
            "schema": "geometric-flow/third-recentered-frame/v0.9.24",
            "formal_backend": "python-flint/Arb",
            "precision_bits": ">=192",
            "frozen_v0923_source_sha256": V0923_SHA256,
            "frozen_target_certificate_sha256": target_certificate_sha256,
            "frozen_target_semantic_sha256": target_semantic_sha256,
            "coordinate_system_from": target.get("coordinate_system"),
            "coordinate_system_to": "nonempty unique identifier",
            "corrected_phase_center_box": "lower[14], upper[14]",
            "response_jacobian_box": "lower[8][14], upper[8][14]",
            "tangent_frame_midpoint": "matrix[14][6]",
            "normal_frame_midpoint": "matrix[14][8]",
            "frame_orthogonal_completeness_defect_upper": "nonnegative scalar < 1e-12",
            "normal_identity_defect_upper": "nonnegative scalar < 1",
            "minimum_response_singular_value_lower": "positive scalar",
            "transformed_endpoint_box": "lower[6], upper[6]",
            "new_start_domain_box": "lower[6], upper[6]",
            "unique_normal_root_certified": True,
            "full_response_row_rank_certified": True,
            "frame_orthogonal_complete_certified": True,
            "normal_derivative_invertible_certified": True,
            "endpoint_overlap_in_new_frame_certified": True,
        },
        "prohibited_shortcuts": [
            "do not reuse v0.9.9 singular values or frame defects as third-centre evidence",
            "do not use floating-point residuals as theorem gates",
            "do not replace complete endpoint-box inclusion with midpoint-only inclusion",
            "do not set certificate booleans without the corresponding interval quantities",
        ],
        "claim_rule": (
            "third_tangent_normal_frame_certified may be true only when every "
            "audited interval gate passes; third_local_picard_chart_certified, "
            "complete_child_certified and global_flow_claimed remain false"
        ),
    }
    atomic_json(path, contract)
    return contract


def audit_frame_certificate(
    certificate_path: Path | None,
    target: dict[str, Any],
    target_certificate_sha256: str,
    target_semantic_sha256: str,
) -> tuple[dict[str, Any], dict[str, bool]]:
    if certificate_path is None:
        return {"reason": "No third-centre Arb frame certificate was supplied."}, {
            "formal_arb_frame_certificate_present": False,
            "certificate_schema_exact": False,
            "certificate_bound_to_v0923_source": False,
            "certificate_bound_to_target": False,
            "formal_precision_at_least_192_bits": False,
            "corrected_phase_center_box_present": False,
            "response_jacobian_box_present": False,
            "third_response_full_row_rank": False,
            "third_frame_orthogonal_complete": False,
            "third_normal_derivative_invertible": False,
            "complete_endpoint_box_overlap_in_new_frame": False,
            "all_declared_backend_booleans_true": False,
        }
    if not certificate_path.is_file():
        raise FileNotFoundError(f"frame certificate not found: {certificate_path}")

    cert = json.loads(certificate_path.read_text(encoding="utf-8"))
    precision = int(cert.get("precision_bits", 0))
    orth = Decimal(str(cert.get("frame_orthogonal_completeness_defect_upper", "Infinity")))
    normal_defect = Decimal(str(cert.get("normal_identity_defect_upper", "Infinity")))
    sigma_lower = Decimal(str(cert.get("minimum_response_singular_value_lower", "-Infinity")))

    phase_box_ok = jacobian_box_ok = False
    try:
        interval_box(cert.get("corrected_phase_center_box"), DIM_CONTROL, "corrected_phase_center_box")
        phase_box_ok = True
    except (ValueError, TypeError, ArithmeticError):
        pass
    try:
        jac = cert.get("response_jacobian_box", {})
        matrix_decimal(jac.get("lower"), DIM_RESPONSE, DIM_CONTROL, "response_jacobian_box.lower")
        matrix_decimal(jac.get("upper"), DIM_RESPONSE, DIM_CONTROL, "response_jacobian_box.upper")
        jacobian_box_ok = True
    except (ValueError, TypeError, ArithmeticError):
        pass

    endpoint_overlap = False
    try:
        endpoint_lo, endpoint_hi = interval_box(
            cert.get("transformed_endpoint_box"), DIM_TANGENT, "transformed_endpoint_box"
        )
        domain_lo, domain_hi = interval_box(
            cert.get("new_start_domain_box"), DIM_TANGENT, "new_start_domain_box"
        )
        endpoint_overlap = box_inside(
            endpoint_lo, endpoint_hi, domain_lo, domain_hi, strict=True
        )
    except (ValueError, TypeError, ArithmeticError):
        pass

    declared = [
        cert.get("unique_normal_root_certified") is True,
        cert.get("full_response_row_rank_certified") is True,
        cert.get("frame_orthogonal_complete_certified") is True,
        cert.get("normal_derivative_invertible_certified") is True,
        cert.get("endpoint_overlap_in_new_frame_certified") is True,
    ]
    gates = {
        "formal_arb_frame_certificate_present": True,
        "certificate_schema_exact": cert.get("schema") == "geometric-flow/third-recentered-frame/v0.9.24",
        "certificate_bound_to_v0923_source": cert.get("frozen_v0923_source_sha256") == V0923_SHA256,
        "certificate_bound_to_target": cert.get("frozen_target_semantic_sha256") == target_semantic_sha256,
        "formal_precision_at_least_192_bits": precision >= PRECISION_BITS,
        "corrected_phase_center_box_present": phase_box_ok,
        "response_jacobian_box_present": jacobian_box_ok,
        "third_response_full_row_rank": sigma_lower > 0 and normal_defect < 1,
        "third_frame_orthogonal_complete": Decimal(0) <= orth < ORTHOGONALITY_TOLERANCE,
        "third_normal_derivative_invertible": Decimal(0) <= normal_defect < 1,
        "complete_endpoint_box_overlap_in_new_frame": endpoint_overlap,
        "all_declared_backend_booleans_true": all(declared),
    }
    metrics = {
        "certificate": str(certificate_path),
        "certificate_sha256": sha256_file(certificate_path),
        "precision_bits": precision,
        "minimum_response_singular_value_lower": str(sigma_lower),
        "frame_orthogonal_completeness_defect_upper": str(orth),
        "normal_identity_defect_upper": str(normal_defect),
        "endpoint_overlap_recomputed_by_auditor": endpoint_overlap,
    }
    return metrics, gates


def parse() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outdir", default="response_fibre_third_frame_v0_9_24_results"
    )
    parser.add_argument("--v0923", help="optional local frozen v0.9.23 one-click source")
    parser.add_argument(
        "--frame-certificate",
        help="optional repository-native Arb third-frame certificate JSON",
    )
    parser.add_argument("--root-radius", default="2e-18")
    return parser.parse_known_args()


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    ensure_formal_backend()
    source = locate_or_download_v0923(
        args.v0923, out / "frozen_sources" / V0923_NAME
    )

    child = out / "v0923_chain"
    completed = subprocess.run(
        [
            sys.executable,
            str(source),
            "--outdir",
            str(child),
            "--root-radius",
            str(args.root_radius),
        ],
        text=True,
        capture_output=True,
    )
    (out / "v0923_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (out / "v0923_stderr.txt").write_text(completed.stderr, encoding="utf-8")

    summary_path = child / "run_summary.json"
    target_path = child / "third_recenter_target_certificate.json"
    if not (summary_path.is_file() and target_path.is_file()):
        raise RuntimeError(
            f"frozen v0.9.23 exit={completed.returncode}; expected outputs missing; inspect logs"
        )
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    target = json.loads(target_path.read_text(encoding="utf-8"))
    target_sha = sha256_file(target_path)
    target_semantic_sha = sha256_json({
        "coordinate_system": target.get("coordinate_system"),
        "tangent_target_center": target.get("tangent_target_center"),
        "tangent_target_component_radius": target.get("tangent_target_component_radius"),
        "certified_parametric_domain": target.get("certified_parametric_domain"),
        "normal_root_enclosure_radius": target.get("normal_root_enclosure_radius"),
    })

    centers = as_decimal_list(
        target.get("tangent_target_center"), DIM_TANGENT, "tangent_target_center"
    )
    radii = as_decimal_list(
        target.get("tangent_target_component_radius"),
        DIM_TANGENT,
        "tangent_target_component_radius",
    )
    max_abs = max(abs(c) + r for c, r in zip(centers, radii))
    inherited_inner = Decimal(
        str(target["certified_parametric_domain"]["inner_real_radius"])
    )

    contract_path = out / "third_frame_backend_contract.json"
    contract = write_backend_contract(
        contract_path, target, target_sha, target_semantic_sha
    )
    backend_path = Path(args.frame_certificate) if args.frame_certificate else None
    backend_metrics, backend_gates = audit_frame_certificate(
        backend_path, target, target_sha, target_semantic_sha
    )

    base_gates = {
        "frozen_v0923_source_hash_exact": sha256_file(source) == V0923_SHA256,
        "frozen_v0923_exit_zero": completed.returncode == 0,
        "v0923_all_scientific_gates_pass": summary.get("all_scientific_gates_pass") is True,
        "third_recenter_target_certified": summary.get("third_recenter_target_certified") is True,
        "unique_parametric_normal_root_over_endpoint_box": summary.get("unique_normal_root_over_complete_endpoint_box_certified") is True,
        "target_is_six_dimensional": len(centers) == DIM_TANGENT and len(radii) == DIM_TANGENT,
        "target_box_strictly_inside_inherited_inner_domain": max_abs < inherited_inner,
        "backend_contract_emitted": contract_path.is_file(),
    }
    base_pass = all(base_gates.values())
    frame_pass = base_pass and all(backend_gates.values())
    status = (
        "VALIDATED_THIRD_RECENTERED_TANGENT_NORMAL_FRAME_CERTIFIED"
        if frame_pass
        else "THIRD_FRAME_TARGET_CERTIFIED_BACKEND_IMPLEMENTATION_OPEN"
        if base_pass and backend_path is None
        else "THIRD_FRAME_AUDIT_INCONCLUSIVE_FAIL_CLOSED"
    )

    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": status,
        "repository": REPOSITORY,
        "frozen_commit": FROZEN_COMMIT,
        "formal_backend_required": "python-flint/Arb >=192-bit",
        "v0923": {
            "source": str(source),
            "source_sha256": sha256_file(source),
            "summary": str(summary_path),
            "target_certificate": str(target_path),
            "target_certificate_sha256": target_sha,
            "target_semantic_sha256": target_semantic_sha,
        },
        "third_recenter_target": {
            "coordinate_system": target.get("coordinate_system"),
            "center": [str(x) for x in centers],
            "component_radius": [str(x) for x in radii],
            "maximum_absolute_coordinate": str(max_abs),
            "inherited_inner_domain_radius": str(inherited_inner),
            "inherited_inner_margin": str(inherited_inner - max_abs),
        },
        "base_gates": base_gates,
        "backend_certificate_audit": backend_metrics,
        "frame_gates": backend_gates,
        "preflight_complete": base_pass,
        "third_tangent_normal_frame_certified": frame_pass,
        "third_local_picard_chart_certified": False,
        "complete_child_certified": False,
        "ten_chart_continuation_certified": False,
        "global_flow_claimed": False,
        "all_scientific_gates_pass": frame_pass,
        "backend_contract": str(contract_path),
        "backend_contract_sha256": sha256_json(contract),
        "next_required_step": (
            "implement the repository-native Arb operations in third_frame_backend_contract.json and rerun this auditor with --frame-certificate"
            if not frame_pass
            else "construct and certify the third complex fibre graph, pullback metric, endpoint overlap and Picard microstep"
        ),
        "claim_boundary": (
            "without a supplied passing Arb certificate this result freezes only the third-frame proof target and executable audit contract; "
            "even with a passing frame certificate it does not establish a third Picard chart, complete child, or global flow"
        ),
        "elapsed_seconds": time.time() - started,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    result["report_sha256_before_self_field"] = sha256_json(result)
    atomic_json(out / "run_summary.json", result)
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
        # A completed target/contract preflight is a successful program run even
        # though the theorem gate remains false until a real Arb certificate exists.
        return 0 if result["preflight_complete"] else 2
    except Exception as exc:
        result = {
            "scientific_status": "V0924_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        print(json.dumps(result, indent=2))
        return 2


if __name__ == "__main__":
    exit_code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(exit_code)
