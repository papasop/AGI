#!/usr/bin/env python3
"""Fail-closed structural and hash verification for the frozen v0.7.4 release."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
INPUTS = ROOT / "inputs" / "response_fibre_v0_6_2_backend_inputs.zip"
SUMMARY = ROOT / "results" / "reference_run_summary.json"
REFERENCE = ROOT / "results" / "reference"
PROTOCOL = REFERENCE / "protocol.json"
CERTIFICATE = REFERENCE / "certificate.json"
REPORT = REFERENCE / "report.json"
README = ROOT / "README.md"

EXPECTED_SOURCE_SHA256 = (
    "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"
)
EXPECTED_INPUTS_SHA256 = (
    "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
)
EXPECTED_ATLAS_SHA256 = (
    "c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
)
EXPECTED_PROTOCOL_SHA256 = (
    "d935fb83f1676697aa9fa2294b2c5f40bfaa3c297802fd26082e4f0b3759af13"
)
EXPECTED_CERTIFICATE_SHA256 = (
    "ed302725c03b66f2bbe7363e901842f07790bd895b4cf95261ebe3d172d400f9"
)
EXPECTED_FIELDS = {
    "scientific_status": "FORMAL_ARB_ORIENTED_DESCENT_CERTIFIED_ALIGNMENT_INCONCLUSIVE",
    "all_gates_pass": False,
    "formal_interval_arithmetic": True,
    "arb_precision_bits": 192,
    "validated_ODE_claimed": False,
    "stage_a_rank_descent_cover_certified": True,
    "formal_response_rank_cover_certified": True,
    "formal_response_tangency_cover_certified": True,
    "formal_negative_projected_pairing_cover_certified": True,
    "formal_projected_gradient_nonstationary_cover_certified": True,
    "kkt_witness_alignment_cover_certified": False,
    "uniform_single_box_L6_descent_certified": True,
    "formal_single_box_projected_gradient_alignment_certified": False,
    "global_flow_claimed": False,
    "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
    "corrected_atlas_sha256": EXPECTED_ATLAS_SHA256,
    "chart": 9,
    "subdivision": 32,
    "box_center": 0.015625,
    "box_half_width": 0.015625,
    "cover_is_exact_and_contiguous": True,
    "child_boxes_declared": 16,
    "child_boxes_tested": 16,
    "child_boxes_passing": 0,
    "child_boxes_passing_stage_a": 16,
    "child_boxes_passing_stage_b": 0,
    "maximum_right_inverse_defect_upper": 0.1299344388400178,
    "minimum_projected_gradient_norm_lower": 0.6530784748107296,
    "minimum_alignment_scale": 0.6530911830790997,
    "maximum_response_tangency_norm_upper": 2.3071147819354663e-09,
    "maximum_parallel_relative_residual_upper": 0.008935710125297152,
    "maximum_dL6_dell_upper": -0.6530784697700559,
    "minimum_alignment_cosine_lower": 0.9999600757453052,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha256(path: Path) -> str:
    return hashlib.sha256(
        canonical_json(json.loads(path.read_text(encoding="utf-8")))
    ).hexdigest()


def main() -> int:
    checks = {
        "source_exists": SOURCE.is_file(),
        "inputs_exist": INPUTS.is_file(),
        "summary_exists": SUMMARY.is_file(),
        "protocol_exists": PROTOCOL.is_file(),
        "certificate_exists": CERTIFICATE.is_file(),
        "report_exists": REPORT.is_file(),
    }
    if not all(checks.values()):
        print(json.dumps(checks, indent=2))
        return 1

    checks["source_sha256"] = sha256(SOURCE) == EXPECTED_SOURCE_SHA256
    checks["inputs_sha256"] = sha256(INPUTS) == EXPECTED_INPUTS_SHA256
    checks["protocol_canonical_sha256"] = (
        canonical_sha256(PROTOCOL) == EXPECTED_PROTOCOL_SHA256
    )
    checks["certificate_file_sha256"] = (
        sha256(CERTIFICATE) == EXPECTED_CERTIFICATE_SHA256
    )

    with zipfile.ZipFile(INPUTS) as archive:
        atlas_names = [
            name for name in archive.namelist()
            if name.endswith("/corrected_atlas.json")
            or name == "corrected_atlas.json"
        ]
        checks["one_corrected_atlas"] = len(atlas_names) == 1
        if atlas_names:
            atlas = json.loads(archive.read(atlas_names[0]))
            checks["canonical_atlas_sha256"] = (
                hashlib.sha256(canonical_json(atlas)).hexdigest()
                == EXPECTED_ATLAS_SHA256
            )

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    checks["report_certificate_sha256"] = (
        report.get("certificate_sha256") == EXPECTED_CERTIFICATE_SHA256
    )
    checks["summary_certificate_sha256"] = (
        summary.get("certificate_sha256_from_reference_run")
        == EXPECTED_CERTIFICATE_SHA256
    )
    checks["certificate_has_16_children"] = (
        len(certificate.get("child_box_records", [])) == 16
    )
    checks["certificate_stage_a_all_pass"] = all(
        record.get("stage_a_pass") is True
        for record in certificate.get("child_box_records", [])
    )
    checks["certificate_stage_b_all_fail"] = all(
        record.get("stage_b_pass") is False
        for record in certificate.get("child_box_records", [])
    )

    for key, expected in EXPECTED_FIELDS.items():
        checks[f"report_{key}"] = report.get(key) == expected
        checks[f"summary_{key}"] = summary.get(key) == expected

    checks["summary_parameter_note"] = (
        summary.get("certified_curve_parameter") == "local Chebyshev coordinate s"
    )
    checks["summary_legacy_field_note"] = (
        summary.get("legacy_field_name_note")
        == (
            "maximum_dL6_dell_upper is retained for frozen-source compatibility; "
            "the certified derivative is with respect to s"
        )
    )

    readme = README.read_text(encoding="utf-8")
    checks["readme_defect_value"] = "0.1299344388400178" in readme
    checks["readme_projected_gradient_value"] = "0.6530784748107296" in readme
    checks["readme_tangency_value"] = "2.3071147819354663e-09" in readme
    checks["readme_descent_value"] = "-0.6530784697700559" in readme
    checks["readme_residual_value"] = "0.008935710125297152" in readme
    checks["readme_derivative_parameter"] = "dL_6/ds<0" in readme

    print(json.dumps(checks, indent=2, sort_keys=True))
    passed = all(checks.values())
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
