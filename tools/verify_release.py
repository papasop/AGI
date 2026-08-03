#!/usr/bin/env python3
"""Fail-closed structural/hash verification for the v0.9.23 milestone."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V074_SOURCE = ROOT / "src" / "response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
V092_SOURCE = ROOT / "src" / "response_fibre_centered_mean_value_krawczyk_v0_9_2.py"
V093_SOURCE = ROOT / "src" / "response_fibre_intrinsic_picard_microstep_v0_9_3.py"
INPUTS = ROOT / "inputs" / "response_fibre_v0_6_2_backend_inputs.zip"
V074_SUMMARY = ROOT / "results" / "reference_run_summary.json"
V093_DIR = ROOT / "results" / "v0_9_3_reference"
V093_PROTOCOL = V093_DIR / "protocol.json"
V093_CERTIFICATE = V093_DIR / "intrinsic_picard_microstep_certificate.json"
V093_REPORT = V093_DIR / "report.json"
SHA256SUMS = ROOT / "SHA256SUMS.txt"
README = ROOT / "README.md"
CLAIM_SCOPE = ROOT / "docs" / "CLAIM_SCOPE.md"
V0923_RELEASE_NOTES = ROOT / "RELEASE_NOTES_v0.9.23.md"
SUPERSEDED_RESULTS = ROOT / "SUPERSEDED_RESULTS.md"

EXPECTED = {
    V074_SOURCE: "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8",
    V092_SOURCE: "844e62e63d97d6845ed62c0c66597e246fd021b21aed31e22609cdaaec5a269d",
    V093_SOURCE: "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c",
    INPUTS: "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666",
    V093_PROTOCOL: "a7593131084e804985edc27fbea664d95999011da97b1fff2dc41940d24f1d4c",
    V093_CERTIFICATE: "96cd24d34d1b426eef74696c83441510890b50902ae6cbe60fed3fc741bfbf3c",
    V093_REPORT: "a29199d71b01a063f044b813be1fa1be806cdffe8c3c38741a697c82b8842ca8",
}
EXPECTED_ATLAS_SHA256 = (
    "c02acc1c76e0b670793340150d1a875fdc373e0ac7c46d3360a7824b66a3a5ef"
)
EXPECTED_PROTOCOL_SHA256 = (
    "6d0aaefabd71f1d2986515ed84673f0083ae90d0344b9a1e92d7697ac08d061a"
)
EXPECTED_V0923_SCRIPTS = {
    "response_fibre_validated_continuation_v0_9_4_1_oneclick.py",
    "response_fibre_two_step_continuation_v0_9_5_oneclick.py",
    "response_fibre_recenter_preflight_v0_9_6_oneclick.py",
    "response_fibre_normal_root_v0_9_7_oneclick.py",
    "response_fibre_arb_normal_root_v0_9_8_oneclick.py",
    "response_fibre_recentered_frame_v0_9_9_oneclick.py",
    "response_fibre_second_chart_v0_9_10_oneclick.py",
    "response_fibre_finite_continuation_v0_9_11_oneclick.py",
    "response_fibre_transition_preflight_v0_9_12_oneclick.py",
    "response_fibre_route_correction_v0_9_13_oneclick.py",
    "response_fibre_endpoint_identifiability_v0_9_14_oneclick.py",
    "response_fibre_validated_lohner_v0_9_15_oneclick.py",
    "response_fibre_adapter_hardening_v0_9_16_oneclick.py",
    "response_fibre_executable_adapter_v0_9_17_oneclick.py",
    "response_fibre_lohner_stress_v0_9_18_oneclick.py",
    "response_fibre_local_dx_target_v0_9_19_oneclick.py",
    "response_fibre_cauchy_norm_correction_v0_9_20_oneclick.py",
    "response_fibre_six_component_endpoint_v0_9_21_oneclick.py",
    "response_fibre_signed_field_export_v0_9_22_oneclick.py",
    "response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py",
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


def read_sha256sums(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        entries[name] = digest
    return entries


def main() -> int:
    checks: dict[str, bool] = {}
    for path, expected in EXPECTED.items():
        label = str(path.relative_to(ROOT)).replace("/", "_")
        checks[f"{label}_exists"] = path.is_file()
        checks[f"{label}_sha256"] = path.is_file() and sha256(path) == expected

    if INPUTS.is_file():
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

    checks["v074_summary_exists"] = V074_SUMMARY.is_file()
    if V074_SUMMARY.is_file():
        v074 = json.loads(V074_SUMMARY.read_text(encoding="utf-8"))
        checks["v074_stage_a_preserved"] = (
            v074.get("stage_a_rank_descent_cover_certified") is True
            and v074.get("validated_ODE_claimed") is False
        )

    if V093_PROTOCOL.is_file() and V093_REPORT.is_file() and V093_CERTIFICATE.is_file():
        protocol = json.loads(V093_PROTOCOL.read_text(encoding="utf-8"))
        certificate = json.loads(V093_CERTIFICATE.read_text(encoding="utf-8"))
        report = json.loads(V093_REPORT.read_text(encoding="utf-8"))
        checks["protocol_canonical_sha256"] = (
            hashlib.sha256(canonical_json(protocol)).hexdigest()
            == EXPECTED_PROTOCOL_SHA256
        )
        checks["report_binds_protocol"] = (
            report.get("protocol_sha256") == EXPECTED_PROTOCOL_SHA256
        )
        checks["report_binds_generator"] = (
            report.get("generator_source_sha256") == EXPECTED[V093_SOURCE]
        )
        checks["certificate_all_gates_pass"] = (
            certificate.get("all_gates_pass") is True
            and report.get("all_gates_pass") is True
        )
        checks["validated_ode_claim_is_scoped"] = (
            report.get("validated_ODE_claimed") is True
            and report.get("ODE_existence_certified") is True
            and report.get("ODE_uniqueness_certified") is True
            and report.get("global_flow_claimed") is False
            and report.get("certified_time_step") == 1e-14
        )
        checks["response_and_lyapunov_certified"] = (
            report.get("exact_response_preservation_certified") is True
            and report.get("uniform_L6_descent_certified_for_validated_solution")
            is True
            and report.get("uniform_dL6_dt_upper", 0.0) < -0.55
        )

    checks["v0923_sha256sums_exists"] = SHA256SUMS.is_file()
    if SHA256SUMS.is_file():
        sums = read_sha256sums(SHA256SUMS)
        checks["v0923_all_expected_scripts_listed"] = (
            EXPECTED_V0923_SCRIPTS <= set(sums)
        )
        for name, expected in sums.items():
            path = ROOT / name
            label = f"v0923_{name.replace('/', '_')}"
            checks[f"{label}_exists"] = path.is_file()
            checks[f"{label}_sha256"] = path.is_file() and sha256(path) == expected

    checks["v0923_readme_exists"] = README.is_file()
    if README.is_file():
        text = README.read_text(encoding="utf-8")
        checks["v0923_readme_states_endpoint"] = (
            "signed endpoint and parametric-root milestone v0.9.23" in text
            and "six signed intrinsic-field component intervals" in text
            and "nonzero six-dimensional endpoint box after 557 microsteps" in text
            and "This package is a formal-development milestone, not a global-flow theorem." in text
        )
        checks["v0923_readme_supersedes_v0918_limit"] = (
            "the formal continuation is limited to 172 steps" in text
            and "They must not be cited as current capability bounds." in text
        )

    checks["v0923_claim_scope_exists"] = CLAIM_SCOPE.is_file()
    if CLAIM_SCOPE.is_file():
        scope = CLAIM_SCOPE.read_text(encoding="utf-8")
        checks["v0923_claim_scope_rejects_global_flow"] = (
            "does not establish" in scope
            and "global flow" in scope
        )
        checks["v0923_claim_scope_states_correction"] = (
            "a second factor of six" in scope
            and "current limits on the flow" in scope
        )

    checks["v0923_release_notes_exists"] = V0923_RELEASE_NOTES.is_file()
    checks["v0923_superseded_results_exists"] = SUPERSEDED_RESULTS.is_file()
    if SUPERSEDED_RESULTS.is_file():
        superseded = SUPERSEDED_RESULTS.read_text(encoding="utf-8")
        checks["v0923_superseded_results_states_resolution"] = (
            "v0.9.18" in superseded
            and "v0.9.19" in superseded
            and "Resolution in v0.9.20" in superseded
            and "step 557" in superseded
        )

    print(json.dumps(checks, indent=2, sort_keys=True))
    passed = bool(checks) and all(checks.values())
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
