#!/usr/bin/env python3
"""Fail-closed structural/hash verification for the current release package."""

from __future__ import annotations

import ast
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
V0932_RELEASE_NOTES = ROOT / "RELEASE_NOTES_v0.9.32.md"
V0946_RELEASE_NOTES = ROOT / "RELEASE_NOTES_v0.9.46.md"
V0105_RELEASE_NOTES = ROOT / "RELEASE_NOTES_v0.10.5.md"
V0106_RELEASE_NOTES = ROOT / "RELEASE_NOTES_v0.10.6.md"
V010141_RELEASE_NOTES = ROOT / "RELEASE_NOTES_v0.10.14.1.md"
SUPERSEDED_RESULTS = ROOT / "SUPERSEDED_RESULTS.md"
BACKEND_BINDING = ROOT / "docs" / "BACKEND_BINDING.md"
ARTIFACT_INDEX = ROOT / "docs" / "ARTIFACT_INDEX.md"
MILESTONES = ROOT / "docs" / "MILESTONES.md"
PROOF_GRAPH = ROOT / "docs" / "PROOF_GRAPH.md"
REPRODUCIBILITY = ROOT / "docs" / "REPRODUCIBILITY.md"
PAPER_WORDING = ROOT / "docs" / "PAPER_WORDING.md"
V010141_INTEGRATION = ROOT / "docs" / "archive" / "INTEGRATION_v0.10.14.1.md"
SCRIPT_ENTRYPOINT_UTILS = ROOT / "scripts" / "_entrypoint_utils.py"
SCRIPT_LOCAL_ODE = ROOT / "scripts" / "reproduce_local_ode.py"
SCRIPT_FINITE_CONTINUATION = ROOT / "scripts" / "reproduce_finite_continuation.py"
SCRIPT_FIELD_JACOBIAN = ROOT / "scripts" / "reproduce_field_jacobian.py"
SCRIPT_LOHNER_FLOWPIPE = ROOT / "scripts" / "reproduce_lohner_flowpipe.py"
SCRIPT_AUDIT_FIFTH_FRAME = ROOT / "scripts" / "audit_fifth_frame.py"
SCRIPT_REPRODUCE_V093 = ROOT / "scripts" / "reproduce_v093.py"
SCRIPT_VERIFY_REFERENCE = ROOT / "scripts" / "verify_reference_results.py"
SCRIPT_REPRODUCE_FINITE = ROOT / "scripts" / "reproduce_finite_chain.py"
V0946_CANDIDATE = ROOT / "src" / "geometric_flow_native_point_field_candidate_v0_9_46.py"
V0946_HARNESS = ROOT / "src" / "response_fibre_native_binding_harness_v0_9_46_standalone.py"
V0946_TEST = ROOT / "tests" / "test_v0946_contract.py"
V01013_SCRIPT = ROOT / "src" / "geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py"
V01014_SCRIPT = ROOT / "src" / "geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py"
V01015_SCRIPT = ROOT / "src" / "geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py"
V0105_SUMMARY = ROOT / "results" / "v0_10_5" / "run_summary.json"
V0105_CERTIFICATE = (
    ROOT / "results" / "v0_10_5" / "same_expression_X_DX_arb_certificate.json"
)
V0106_SUMMARY = ROOT / "results" / "v0_10_6" / "run_summary.json"
V0106_CERTIFICATE = (
    ROOT / "results" / "v0_10_6" / "fourth_chart_qr_lohner_support_certificate.json"
)
V0106_STEP_RECORDS = ROOT / "results" / "v0_10_6" / "qr_lohner_step_records.json"

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
EXPECTED_V0932_SCRIPTS = {
    "response_fibre_third_frame_v0_9_24_oneclick.py",
    "response_fibre_third_frame_backend_v0_9_25_oneclick.py",
    "response_fibre_third_picard_v0_9_26_oneclick.py",
    "response_fibre_third_chart_finite_continuation_v0_9_27_oneclick.py",
    "response_fibre_third_chart_signed_endpoint_v0_9_28_oneclick.py",
    "response_fibre_fourth_frame_v0_9_29_oneclick.py",
    "response_fibre_fourth_picard_v0_9_30_oneclick.py",
    "response_fibre_fourth_chart_finite_v0_9_31_oneclick.py",
    "response_fibre_fourth_chart_signed_endpoint_v0_9_32_oneclick.py",
}
EXPECTED_V0946_FILES = {
    "RELEASE_NOTES_v0.9.46.md",
    "docs/BACKEND_BINDING.md",
    "src/geometric_flow_native_point_field_candidate_v0_9_46.py",
    "src/response_fibre_native_binding_harness_v0_9_46_standalone.py",
    "frozen/response_fibre_center_box_field_v0_9_43_3_standalone.py",
    "frozen/response_fibre_displaced_box_diagnostic_v0_9_44_standalone.py",
    "frozen/response_fibre_fourth_picard_v0_9_30_standalone.py",
    "frozen/response_fibre_point_field_refactor_v0_9_45_standalone.py",
    "tests/test_v0946_contract.py",
}
EXPECTED_V0105_FILES = {
    "RELEASE_NOTES_v0.10.5.md",
    "PR_DESCRIPTION.md",
    "tools/verify_update.py",
    "src/geometric_flow_active_backend_export_v0_10_1_oneclick.py",
    "src/geometric_flow_scalar_primitives_extract_v0_10_2_oneclick.py",
    "src/geometric_flow_six_variable_jet_lift_v0_10_3_oneclick.py",
    "src/geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py",
    "src/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py",
    "results/v0_10_1/run_summary.json",
    "results/v0_10_2/run_summary.json",
    "results/v0_10_3/run_summary.json",
    "results/v0_10_4/run_summary.json",
    "results/v0_10_4/parametric_normal_graph_jet_arb_certificate.json",
    "results/v0_10_5/run_summary.json",
    "results/v0_10_5/same_expression_X_DX_arb_certificate.json",
}
EXPECTED_V0106_FILES = {
    "RELEASE_NOTES_v0.10.6.md",
    "src/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py",
    "results/v0_10_6/run_summary.json",
    "results/v0_10_6/fourth_chart_qr_lohner_support_certificate.json",
    "results/v0_10_6/qr_lohner_step_records.json",
}
EXPECTED_V010141_FILES = {
    "RELEASE_NOTES_v0.10.14.1.md",
    "docs/archive/INTEGRATION_v0.10.14.1.md",
    "src/geometric_flow_reindexed_taylor_chain_v0_10_13_oneclick.py",
    "src/geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py",
    "src/geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py",
}
EXPECTED_NAVIGATION_FILES = {
    "docs/ARTIFACT_INDEX.md",
    "docs/MILESTONES.md",
    "docs/PROOF_GRAPH.md",
    "docs/REPRODUCIBILITY.md",
    "scripts/_entrypoint_utils.py",
    "scripts/reproduce_local_ode.py",
    "scripts/reproduce_finite_continuation.py",
    "scripts/reproduce_field_jacobian.py",
    "scripts/reproduce_lohner_flowpipe.py",
    "scripts/audit_fifth_frame.py",
    "scripts/reproduce_v093.py",
    "scripts/verify_reference_results.py",
    "scripts/reproduce_finite_chain.py",
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

    checks["sha256sums_exists"] = SHA256SUMS.is_file()
    if SHA256SUMS.is_file():
        sums = read_sha256sums(SHA256SUMS)
        checks["v0923_all_expected_scripts_listed"] = (
            EXPECTED_V0923_SCRIPTS <= set(sums)
        )
        checks["v0932_all_expected_scripts_listed"] = (
            EXPECTED_V0932_SCRIPTS <= set(sums)
        )
        checks["v0946_all_expected_files_listed"] = (
            EXPECTED_V0946_FILES <= set(sums)
        )
        checks["v0105_all_expected_files_listed"] = (
            EXPECTED_V0105_FILES <= set(sums)
        )
        checks["v0106_all_expected_files_listed"] = (
            EXPECTED_V0106_FILES <= set(sums)
        )
        checks["v010141_all_expected_files_listed"] = (
            EXPECTED_V010141_FILES <= set(sums)
        )
        checks["navigation_all_expected_files_listed"] = (
            EXPECTED_NAVIGATION_FILES <= set(sums)
        )
        for name, expected in sums.items():
            path = ROOT / name
            label = name.replace("/", "_")
            checks[f"{label}_exists"] = path.is_file()
            checks[f"{label}_sha256"] = path.is_file() and sha256(path) == expected

    checks["readme_exists"] = README.is_file()
    if README.is_file():
        text = README.read_text(encoding="utf-8")
        checks["readme_has_single_status_table"] = (
            "## Status At A Glance" in text
            and "| Intrinsic ODE microstep | v0.9.3 | Certified reference theorem |" in text
            and "| Ten-step fourth-chart support flowpipe | v0.10.6 | Latest repository reference certificate |" in text
            and "| Reindexed Taylor/affine-Lohner terminal set | v0.10.13.1 | Source-certified chain; reference-result packaging pending |" in text
            and text.count("## Latest ") == 0
        )
        checks["readme_states_main_theorem_and_v0106_reference"] = (
            "## Main Theorem" in text
            and "dL_6/dt <= -0.6419529191591549 < 0" in text
            and "maximum terminal support       1.3938448261845923e-11" in text
            and "v0.10.6 is the latest\nindependent reference certificate" in text
        )
        checks["readme_states_source_vs_reference_boundary"] = (
            "VALIDATED_REINDEXED_TAYLOR_DIRECTIONAL_AFFINE_LOHNER_CERTIFIED" in text
            and "reference-result packaging pending" in text
            and "implementation-open" in text
            and "v0.10.15 backend harness" in text
        )
        checks["readme_has_three_reproduction_entrypoints"] = (
            "python scripts/reproduce_local_ode.py" in text
            and "python scripts/verify_reference_results.py" in text
            and "python scripts/reproduce_lohner_flowpipe.py" in text
        )
        checks["readme_lists_additional_stable_entrypoints"] = (
            "python scripts/reproduce_finite_continuation.py" in text
            and "python scripts/reproduce_field_jacobian.py" in text
            and "python scripts/audit_fifth_frame.py" in text
            and "check the relevant frozen SHA-256 entries" in text
        )
        checks["readme_next_milestone_is_not_stale_v0946"] = (
            "implicit_fibre_root_solver(a_box)" not in text
            and "projected_gradient(a_box, root_box, metric_box)" not in text
            and "Next milestone" not in text
        )

    checks["claim_scope_exists"] = CLAIM_SCOPE.is_file()
    if CLAIM_SCOPE.is_file():
        scope = CLAIM_SCOPE.read_text(encoding="utf-8")
        checks["claim_scope_states_v0932_boundary"] = (
            "v0.9.32 certifies a signed six-component fourth-chart terminal" in scope
            and "not a sharp trajectory midpoint" in scope
        )
        checks["claim_scope_has_three_layers"] = (
            "Layer I: Unconditional Local Theorem" in scope
            and "Layer II: Frozen-Instance Finite Continuation" in scope
            and "Layer III: Conditional / Next-Frame Work" in scope
        )
        checks["claim_scope_states_v0106_boundary"] = (
            "strongest repository reference result remains v0.10.6" in scope
            and "ten-step\nfourth-chart Arb Lohner support flowpipe" in scope
            and "This delta does not add new reference result certificates" in scope
        )
        checks["claim_scope_states_v010141_boundary"] = (
            "reindexed ten-step local-root,\nsecond-order Taylor" in scope
            and "does not certify a fifth recenter/frame" in scope
            and "v0.10.15 fifth-frame backend harness is also implementation-open" in scope
            and "reference-result packaging is\npending" in scope
            and "global flow theorem" in scope
        )
        checks["claim_scope_states_v0946_scaffold_only"] = (
            "fail-closed\nbinding scaffold only" in scope
            and "must not be described as a certified\npoint-dependent field" in scope
        )
        checks["claim_scope_rejects_global_flow"] = (
            "does not establish" in scope
            and "global flow" in scope
        )
        checks["claim_scope_states_correction"] = (
            "a second factor of six" in scope
            and "current limits on the flow" in scope
        )

    checks["v0923_release_notes_exists"] = V0923_RELEASE_NOTES.is_file()
    checks["v0932_release_notes_exists"] = V0932_RELEASE_NOTES.is_file()
    checks["v0946_release_notes_exists"] = V0946_RELEASE_NOTES.is_file()
    checks["v0105_release_notes_exists"] = V0105_RELEASE_NOTES.is_file()
    checks["v0106_release_notes_exists"] = V0106_RELEASE_NOTES.is_file()
    checks["v010141_release_notes_exists"] = V010141_RELEASE_NOTES.is_file()
    if V0946_RELEASE_NOTES.is_file():
        notes = V0946_RELEASE_NOTES.read_text(encoding="utf-8")
        checks["v0946_release_notes_state_implementation_open"] = (
            "`IMPLEMENTATION_OPEN`" in notes
            and "must not be described as a certified\npoint-dependent field" in notes
            and "NotImplementedError" in notes
        )
    if V0105_RELEASE_NOTES.is_file():
        notes = V0105_RELEASE_NOTES.read_text(encoding="utf-8")
        checks["v0105_release_notes_state_x_dx_only"] = (
            "VALIDATED_NATIVE_SAME_EXPRESSION_X_DX_CERTIFIED" in notes
            and "not a QR/Lohner\nflowpipe" in notes
            and "It is deliberately excluded from this update." in notes
        )
    if V0106_RELEASE_NOTES.is_file():
        notes = V0106_RELEASE_NOTES.read_text(encoding="utf-8")
        checks["v0106_release_notes_state_support_flowpipe_only"] = (
            "VALIDATED_TEN_STEP_FOURTH_CHART_LOHNER_SUPPORT_FLOWPIPE_CERTIFIED" in notes
            and "maximum terminal support      1.3938448261845923e-11" in notes
            and "not a directional QR-tightening result" in notes
            and "global-flow theorem" in notes
        )
    if V010141_RELEASE_NOTES.is_file():
        notes = V010141_RELEASE_NOTES.read_text(encoding="utf-8")
        checks["v010141_release_notes_state_delta_only"] = (
            "v0.10.13.1" in notes
            and "v0.10.14.1" in notes
            and "v0.10.15" in notes
            and "does not add reference result certificates" in notes
            and "Reference-result packaging for v0.10.13.1\nis pending" in notes
            and "No fifth frame, fifth Picard chart" in notes
        )

    checks["v0923_superseded_results_exists"] = SUPERSEDED_RESULTS.is_file()
    if SUPERSEDED_RESULTS.is_file():
        superseded = SUPERSEDED_RESULTS.read_text(encoding="utf-8")
        checks["v0923_superseded_results_states_resolution"] = (
            "v0.9.18" in superseded
            and "v0.9.19" in superseded
            and "Resolution in v0.9.20" in superseded
            and "step 557" in superseded
        )

    checks["v0946_backend_binding_exists"] = BACKEND_BINDING.is_file()
    if BACKEND_BINDING.is_file():
        binding = BACKEND_BINDING.read_text(encoding="utf-8")
        checks["v0946_backend_binding_forbids_shortcuts"] = (
            "Forbidden shortcuts" in binding
            and "Returning frozen `FIELD_MIDPOINTS/FIELD_RADII`" in binding
            and "formal Jacobian" in binding
        )

    checks["v0946_candidate_exists"] = V0946_CANDIDATE.is_file()
    if V0946_CANDIDATE.is_file():
        candidate = V0946_CANDIDATE.read_text(encoding="utf-8")
        tree = ast.parse(candidate)
        funcs = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        not_implemented_calls = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "NotImplementedError"
        ]
        checks["v0946_candidate_required_callbacks_exist"] = {
            "implicit_fibre_root_solver",
            "pullback_metric",
            "projected_gradient",
            "formal_vector_field_X",
        } <= funcs
        checks["v0946_candidate_remains_fail_closed"] = bool(not_implemented_calls)
        checks["v0946_candidate_has_no_fixed_field_shortcut"] = (
            "FIELD_MIDPOINTS" not in candidate
            and "FIELD_RADII" not in candidate
        )

    checks["v0946_harness_exists"] = V0946_HARNESS.is_file()
    if V0946_HARNESS.is_file():
        harness = V0946_HARNESS.read_text(encoding="utf-8")
        checks["v0946_harness_states_nonclaim"] = (
            "IMPLEMENTATION_OPEN" in harness
            and "formal_jacobian_DX_ready\":False" in harness
            and "global_flow_claimed\":False" in harness
        )

    checks["v0946_contract_test_exists"] = V0946_TEST.is_file()
    if V0946_TEST.is_file():
        test_text = V0946_TEST.read_text(encoding="utf-8")
        checks["v0946_contract_test_expects_fail_closed_scaffold"] = (
            "test_unimplemented_candidate_is_explicitly_fail_closed" in test_text
            and "assert calls" in test_text
        )

    checks["v010141_integration_exists"] = V010141_INTEGRATION.is_file()
    if V010141_INTEGRATION.is_file():
        integration = V010141_INTEGRATION.read_text(encoding="utf-8")
        checks["v010141_integration_states_nonclaim"] = (
            "Do not add reference certificates unless" in integration
            and "v0.10.15 is an implementation-open native adapter\n   harness" in integration
            and "No fifth frame, fifth Picard chart" in integration
        )

    checks["navigation_docs_exist"] = (
        ARTIFACT_INDEX.is_file()
        and MILESTONES.is_file()
        and PROOF_GRAPH.is_file()
        and REPRODUCIBILITY.is_file()
        and PAPER_WORDING.is_file()
    )
    if (
        ARTIFACT_INDEX.is_file()
        and MILESTONES.is_file()
        and PROOF_GRAPH.is_file()
        and REPRODUCIBILITY.is_file()
    ):
        artifact_index = ARTIFACT_INDEX.read_text(encoding="utf-8")
        milestones = MILESTONES.read_text(encoding="utf-8")
        proof_graph = PROOF_GRAPH.read_text(encoding="utf-8")
        reproducibility = REPRODUCIBILITY.read_text(encoding="utf-8")
        checks["artifact_index_maps_stable_entrypoints"] = (
            "scripts/reproduce_local_ode.py" in artifact_index
            and "scripts/reproduce_finite_continuation.py" in artifact_index
            and "scripts/reproduce_field_jacobian.py" in artifact_index
            and "scripts/reproduce_lohner_flowpipe.py" in artifact_index
            and "scripts/audit_fifth_frame.py" in artifact_index
            and "src/geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py" in artifact_index
            and "Each stable entry point verifies the relevant entries in `SHA256SUMS.txt`" in artifact_index
            and "Fail-closed fifth-frame backend harness" in artifact_index
        )
        checks["milestones_preserve_history_outside_readme"] = (
            "v0.9.18-v0.9.19" in milestones
            and "v0.10.13.1" in milestones
            and "reference-result packaging pending" in milestones
        )
        checks["proof_graph_states_three_layers"] = (
            "Layer I: Unconditional Local Theorem" in proof_graph
            and "Layer II: Frozen-Instance Finite Continuation" in proof_graph
            and "Layer III: Conditional / Next-Frame Continuation Work" in proof_graph
            and "not yet certified" in proof_graph
        )
        checks["reproducibility_lists_full_chain"] = (
            "python scripts/reproduce_local_ode.py" in reproducibility
            and "python scripts/verify_reference_results.py" in reproducibility
            and "python scripts/reproduce_lohner_flowpipe.py" in reproducibility
            and "python scripts/reproduce_finite_continuation.py --run" in reproducibility
            and "geometric_flow_fifth_frame_backend_v0_10_15_oneclick.py" in reproducibility
        )

    if PAPER_WORDING.is_file():
        paper = PAPER_WORDING.read_text(encoding="utf-8")
        checks["paper_wording_states_three_layer_safe_language"] = (
            "Layer I: Unconditional Local Theorem" in paper
            and "Layer II: Frozen-Instance Finite Continuation" in paper
            and "Layer III: Conditional / Next-Frame Work" in paper
            and "Reference-Certified Vs Source-Certified" in paper
            and "v0.10.15 harness certifies a fifth frame" in paper
        )

    checks["reproduction_scripts_exist"] = (
        SCRIPT_ENTRYPOINT_UTILS.is_file()
        and SCRIPT_LOCAL_ODE.is_file()
        and SCRIPT_FINITE_CONTINUATION.is_file()
        and SCRIPT_FIELD_JACOBIAN.is_file()
        and SCRIPT_LOHNER_FLOWPIPE.is_file()
        and SCRIPT_AUDIT_FIFTH_FRAME.is_file()
        and SCRIPT_REPRODUCE_V093.is_file()
        and SCRIPT_VERIFY_REFERENCE.is_file()
        and SCRIPT_REPRODUCE_FINITE.is_file()
    )
    if (
        SCRIPT_ENTRYPOINT_UTILS.is_file()
        and SCRIPT_LOCAL_ODE.is_file()
        and SCRIPT_FINITE_CONTINUATION.is_file()
        and SCRIPT_FIELD_JACOBIAN.is_file()
        and SCRIPT_LOHNER_FLOWPIPE.is_file()
        and SCRIPT_AUDIT_FIFTH_FRAME.is_file()
    ):
        entry_utils = SCRIPT_ENTRYPOINT_UTILS.read_text(encoding="utf-8")
        local_ode = SCRIPT_LOCAL_ODE.read_text(encoding="utf-8")
        finite = SCRIPT_FINITE_CONTINUATION.read_text(encoding="utf-8")
        field = SCRIPT_FIELD_JACOBIAN.read_text(encoding="utf-8")
        lohner = SCRIPT_LOHNER_FLOWPIPE.read_text(encoding="utf-8")
        fifth = SCRIPT_AUDIT_FIFTH_FRAME.read_text(encoding="utf-8")
        checks["stable_entrypoints_fail_closed_on_sha256"] = (
            "def fail_closed_sha256" in entry_utils
            and "SHA-256 mismatch" in entry_utils
            and "scripts/reproduce_v093.py" in local_ode
            and "scripts/reproduce_finite_chain.py" in finite
            and "geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py" in field
            and "geometric_flow_fourth_chart_qr_lohner_v0_10_6_oneclick.py" in lohner
            and "--run-backend" in fifth
            and "implementation-open fail-closed harness" in fifth
            and "global flow is certified" in fifth
        )

    checks["v01013_script_exists"] = V01013_SCRIPT.is_file()
    if V01013_SCRIPT.is_file():
        v01013 = V01013_SCRIPT.read_text(encoding="utf-8")
        checks["v01013_script_states_reindexed_cert_boundary"] = (
            "VERSION=\"0.10.13.1\"" in v01013
            and "VALIDATED_REINDEXED_TAYLOR_DIRECTIONAL_AFFINE_LOHNER_CERTIFIED" in v01013
            and "'fifth_frame_certified':False" in v01013
            and "'global_flow_claimed':False" in v01013
        )

    checks["v01014_script_exists"] = V01014_SCRIPT.is_file()
    if V01014_SCRIPT.is_file():
        v01014 = V01014_SCRIPT.read_text(encoding="utf-8")
        checks["v01014_script_requires_backend_certificate_for_fifth_frame"] = (
            "FIFTH_FRAME_TARGET_FROZEN_ARB_TRANSITION_BACKEND_OPEN" in v01014
            and '"fifth_frame_certified": passed' in v01014
            and '"global_flow_claimed": False' in v01014
            and "forbidden_shortcuts" in v01014
        )

    checks["v01015_script_exists"] = V01015_SCRIPT.is_file()
    if V01015_SCRIPT.is_file():
        v01015 = V01015_SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(v01015)
        required_callbacks = {
            "lift_fourth_correlated_set_to_phase_box",
            "solve_fifth_parametric_normal_root",
            "construct_fifth_arb_svd_frame",
            "map_phase_box_to_fifth_intrinsic_box",
        }
        checks["v01015_script_remains_fail_closed_harness"] = (
            "FIFTH_NATIVE_ADAPTER_IMPLEMENTATION_OPEN_FAIL_CLOSED" in v01015
            and required_callbacks <= set(ast.literal_eval(
                next(
                    node.value
                    for node in tree.body
                    if isinstance(node, ast.Assign)
                    and any(getattr(target, "id", None) == "REQUIRED" for target in node.targets)
                )
            ))
            and "raise NotImplementedError" in v01015
            and '"global_flow_claimed": False' in v01015
        )

    checks["v0105_summary_exists"] = V0105_SUMMARY.is_file()
    checks["v0105_certificate_exists"] = V0105_CERTIFICATE.is_file()
    if V0105_SUMMARY.is_file() and V0105_CERTIFICATE.is_file():
        summary = json.loads(V0105_SUMMARY.read_text(encoding="utf-8"))
        certificate = json.loads(V0105_CERTIFICATE.read_text(encoding="utf-8"))
        checks["v0105_summary_states_same_expression_x_dx"] = (
            summary.get("scientific_status")
            == "VALIDATED_NATIVE_SAME_EXPRESSION_X_DX_CERTIFIED"
            and summary.get("same_expression_X_ready") is True
            and summary.get("same_expression_DX_ready") is True
            and summary.get("qr_lohner_flowpipe_certified") is False
            and summary.get("fifth_frame_certified") is False
            and summary.get("complete_child_certified") is False
            and summary.get("global_flow_claimed") is False
        )
        checks["v0105_certificate_states_finite_dx_only"] = (
            certificate.get("schema")
            == "geometric-flow/same-expression-intrinsic-X-DX/v0.10.5"
            and certificate.get("all_certificate_gates_pass") is True
            and certificate.get("DX_nonzero_entry_certified") is False
            and certificate.get("maximum_DX_absolute_upper") == 7939.247695922852
        )

    checks["v0106_summary_exists"] = V0106_SUMMARY.is_file()
    checks["v0106_certificate_exists"] = V0106_CERTIFICATE.is_file()
    checks["v0106_step_records_exists"] = V0106_STEP_RECORDS.is_file()
    if (
        V0106_SUMMARY.is_file()
        and V0106_CERTIFICATE.is_file()
        and V0106_STEP_RECORDS.is_file()
    ):
        summary = json.loads(V0106_SUMMARY.read_text(encoding="utf-8"))
        certificate = json.loads(V0106_CERTIFICATE.read_text(encoding="utf-8"))
        step_records = json.loads(V0106_STEP_RECORDS.read_text(encoding="utf-8"))
        checks["v0106_summary_states_support_flowpipe"] = (
            summary.get("scientific_status")
            == "VALIDATED_TEN_STEP_FOURTH_CHART_LOHNER_SUPPORT_FLOWPIPE_CERTIFIED"
            and summary.get("qr_lohner_support_flowpipe_certified") is True
            and summary.get("directional_qr_tightening_certified") is False
            and summary.get("fifth_frame_certified") is False
            and summary.get("complete_child_certified") is False
            and summary.get("global_flow_claimed") is False
        )
        checks["v0106_certificate_states_ten_step_domain_bound"] = (
            certificate.get("schema")
            == "geometric-flow/fourth-chart-qr-lohner-support/v0.10.6"
            and certificate.get("all_certificate_gates_pass") is True
            and certificate.get("steps") == 10
            and certificate.get("maximum_final_support_upper")
            == 1.3938448261845923e-11
            and certificate.get("real_inner_domain_radius") == 1.5e-11
            and certificate.get("complex_outer_domain_radius") == 2e-11
            and certificate.get("directional_qr_tightening_certified") is False
        )
        checks["v0106_step_records_cover_ten_inside_steps"] = (
            len(step_records) == 10
            and all(record.get("strictly_inside_real_inner_domain") is True for record in step_records)
            and all(record.get("strictly_inside_complex_outer_domain") is True for record in step_records)
        )

    print(json.dumps(checks, indent=2, sort_keys=True))
    passed = bool(checks) and all(checks.values())
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
