#!/usr/bin/env python3
"""Verify the frozen subordinate R5-A full-tube protocol."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "r5_full_tube_protocol_v1_0.json"
PARENT_PROTOCOL_PATH = HERE / "frozen_protocol_v1_0.json"

EXPECTED_STATUS = "R5_FULL_TUBE_PROTOCOL_FROZEN_NO_CERTIFICATE_RUN"
EXPECTED_PARENT_STATUS = "PROTOCOL_FROZEN_NO_R6_SEARCH_PERFORMED"
EXPECTED_PARENT_SHA256 = "e8519a644ab50a9989eb40bc34499055f83760563167d88da21d17b3c7539e1c"
EXPECTED_INPUT_ZIP_SHA256 = "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
EXPECTED_ATLAS_SHA256 = "e1c816b9c69b6e4ca9e7018b9857ce04a7b6d12c639e51e6792376dbd28d7ec9"
EXPECTED_V092_SHA256 = "844e62e63d97d6845ed62c0c66597e246fd021b21aed31e22609cdaaec5a269d"
EXPECTED_V093_SHA256 = "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c"
EXPECTED_AUXILIARY_PATH = "research/realizability_r1_r7/data/r5_full_tube_auxiliary_v1_0.json"
EXPECTED_AUXILIARY_SHA256 = "434b8d58793b39462fc3dcf4e04f716b56e65de790e87daaecedf2e103e29037"
KNOWN_PLATFORM_VARIANT_SHA256 = "88e814702916e74a9963256f21a6fe7acdce5d806a88d25eebb5fb84a0f026fe"
EXPECTED_V = ["1", "0", "0", "0", "0", "0"]
EXPECTED_EPSILONS = ["1e-14", "3e-14", "1e-13", "3e-13", "1e-12"]

REQUIRED_DATA = {
    "theta0_vector": ("theta_0", "077a169644e33145b4f14c5aa29d4ac86cd2e69572c6f35ddab8af92f41d918a"),
    "T_matrix": ("T", "aa1814d7257f84de3f4eeff3d3feb01fcaa7dfc5db4030d82cabfe06046dda2c"),
    "N_matrix": ("N", "d24a90e45ebea1ea46b0d049757809dc5c42371a740a40ca6412fc5f64e81ba8"),
    "B_matrix": ("B", "f1f9c0d26df1c8366a96fdeafd269660bc06f7e2dfdc4391948d15f13edda170"),
    "c_vector": ("c", "151762ada396ef62608698fb18090e0a443fef869f3f4d91543ad4dfc8e9312a"),
    "normal_preconditioners": ("P", "ae09f2d3343301b12e2b661fa7d50d2b004cd4d72333cbca1703c20890a2d82e"),
}
REQUIRED_GATES = {
    "protocol_identity",
    "frame_rank",
    "T_N_dimensions_and_transversality",
    "B_strict_invertibility",
    "preconditioner_defect",
    "krawczyk_self_mapping",
    "krawczyk_contraction",
    "graph_existence",
    "graph_uniqueness",
    "overlap_consistency",
    "full_tube_coverage",
    "chart_residence",
    "no_phase_wrap",
    "exact_response_identity_logic",
    "same_R3_cost_meter",
    "zero_total_response_cost",
    "nonconstant_positive_measure",
    "epsilon_shrinking_family",
}
FORBIDDEN_FIELDS = {
    "R5_CERTIFIED",
    "R5_certificate",
    "R5_certificate_sha256",
    "R5_result",
    "R6_CERTIFIED",
    "R6_search_result",
    "R6_certificate",
    "normal_K1_recovery_result",
    "all_gates_pass",
}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "protocol_id",
    "title",
    "status",
    "parent_protocol",
    "boundary",
    "source_references",
    "required_frozen_data_before_certificate",
    "R5_full_tube_object",
    "subdivision_strategy",
    "arithmetic",
    "future_acceptance_gates",
    "future_rejection_statuses",
    "nonconstancy_design",
    "exact_response_identity_design",
    "forbidden_fields",
    "auxiliary_artifact_policy",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def decimal_string(value: Any) -> Decimal | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError, OverflowError):
        return None
    return parsed if parsed.is_finite() else None


def corrected_atlas_hash(zip_path: Path) -> str | None:
    try:
        with zipfile.ZipFile(zip_path) as archive:
            names = [
                name for name in archive.namelist()
                if name.endswith("/corrected_atlas.json") or name == "corrected_atlas.json"
            ]
            if len(names) != 1:
                return None
            return hashlib.sha256(archive.read(names[0])).hexdigest()
    except (OSError, zipfile.BadZipFile):
        return None


def find_forbidden_keys(value: Any, forbidden: set[str]) -> list[str]:
    found: list[str] = []

    def walk(node: Any, prefix: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if key in forbidden:
                    found.append(path)
                walk(child, path)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{prefix}[{index}]")

    walk(value, "")
    return found


def verify(protocol: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    parent = protocol.get("parent_protocol", {})
    boundary = protocol.get("boundary", {})
    refs = protocol.get("source_references", {})
    corrected_atlas = refs.get("corrected_atlas", {})
    theta0 = refs.get("theta0", {})
    required_data = protocol.get("required_frozen_data_before_certificate", [])
    tube = protocol.get("R5_full_tube_object", {})
    tube_parameter = tube.get("tube_parameter", {})
    subdivision = protocol.get("subdivision_strategy", {})
    arithmetic = protocol.get("arithmetic", {})
    auxiliary_policy = protocol.get("auxiliary_artifact_policy", {})
    gates = protocol.get("future_acceptance_gates", {})
    rejections = protocol.get("future_rejection_statuses", {})
    nonconstancy = protocol.get("nonconstancy_design", {})
    response_identity = protocol.get("exact_response_identity_design", {})

    checks["schema_version"] = protocol.get("schema_version") == "1.0"
    checks["required_top_level_fields"] = REQUIRED_TOP_LEVEL.issubset(protocol)
    checks["status_exact"] = protocol.get("status") == EXPECTED_STATUS
    checks["parent_protocol_bound"] = (
        parent.get("path") == "research/realizability_r1_r7/frozen_protocol_v1_0.json"
        and parent.get("sha256") == EXPECTED_PARENT_SHA256
        and parent.get("status") == EXPECTED_PARENT_STATUS
        and sha256_file(PARENT_PROTOCOL_PATH) == EXPECTED_PARENT_SHA256
    )
    checks["boundary_no_certificate_or_search"] = (
        boundary.get("kind") == "subordinate_protocol_only"
        and boundary.get("R5_certificate_generated") is False
        and boundary.get("R5_search_performed") is False
        and boundary.get("R6_search_performed") is False
        and boundary.get("R6_certificate_present") is False
        and boundary.get("normal_K1_residual_recovery_performed") is False
        and boundary.get("published_theorem_modified") is False
        and boundary.get("global_flow_claimed") is False
        and boundary.get("v0_9_2_or_v0_9_3_relabelled_as_R5_or_R6") is False
    )

    input_path = ROOT / corrected_atlas.get("container_path", "__invalid__")
    checks["corrected_atlas_bound"] = (
        input_path.is_file()
        and sha256_file(input_path) == EXPECTED_INPUT_ZIP_SHA256
        and corrected_atlas.get("container_sha256") == EXPECTED_INPUT_ZIP_SHA256
        and corrected_atlas.get("member_sha256") == EXPECTED_ATLAS_SHA256
        and corrected_atlas_hash(input_path) == EXPECTED_ATLAS_SHA256
    )
    checks["theta0_source_bound"] = (
        theta0.get("source_hash") == EXPECTED_ATLAS_SHA256
        and theta0.get("serialization_required_before_certificate") is True
    )
    checks["design_references_bound_and_scoped"] = (
        refs.get("v0_9_2_design_reference", {}).get("sha256") == EXPECTED_V092_SHA256
        and refs.get("v0_9_3_design_reference", {}).get("sha256") == EXPECTED_V093_SHA256
        and "not an R5 or R6 certificate" in refs.get("v0_9_2_design_reference", {}).get("role", "")
        and "not an R5 or R6 certificate" in refs.get("v0_9_3_design_reference", {}).get("role", "")
    )
    required_by_name = {
        item.get("name"): item for item in required_data if isinstance(item, dict)
    }
    auxiliary_path = ROOT / EXPECTED_AUXILIARY_PATH
    checks["required_auxiliary_data_bound"] = (
        set(required_by_name) == set(REQUIRED_DATA)
        and auxiliary_path.is_file()
        and sha256_file(auxiliary_path) == EXPECTED_AUXILIARY_SHA256
        and all(
            item.get("path") == EXPECTED_AUXILIARY_PATH
            and item.get("sha256") == EXPECTED_AUXILIARY_SHA256
            and item.get("required_sha256_state") == "BOUND_TO_AUXILIARY_CANDIDATE_DATA"
            and item.get("object_key") == REQUIRED_DATA[name][0]
            and item.get("object_sha256") == REQUIRED_DATA[name][1]
            for name, item in required_by_name.items()
        )
    )

    interval = tube_parameter.get("interval", [])
    left = decimal_string(interval[0]) if isinstance(interval, list) and len(interval) == 2 else None
    right = decimal_string(interval[1]) if isinstance(interval, list) and len(interval) == 2 else None
    checks["full_tube_object"] = (
        tube.get("intrinsic_graph") == "theta(t)=theta_0+T*(t*v)+N*psi(t*v)"
        and tube.get("fixed_v", {}).get("components") == EXPECTED_V
        and left == Decimal("-1e-12")
        and right == Decimal("1e-12")
        and left < Decimal(0) < right
        and tube_parameter.get("contains_all_frozen_R5_loops") is True
        and tube.get("frozen_R5_epsilons") == EXPECTED_EPSILONS
        and tube.get("subset_inference_only_after_full_tube_certification") is True
    )
    checks["subdivision_strategy_frozen"] = (
        subdivision.get("kind") == "fixed_bisection_of_t_interval"
        and subdivision.get("initial_interval") == ["-1e-12", "1e-12"]
        and subdivision.get("initial_subinterval_count") == 16
        and subdivision.get("maximum_refinement_depth") == 8
        and subdivision.get("result_adaptive_changes_allowed") is False
        and subdivision.get("certificate_must_record_every_leaf") is True
    )
    checks["arithmetic_boundary"] = (
        arithmetic.get("python_flint_version") == "0.8.0"
        and arithmetic.get("arb_precision_bits") == 192
        and arithmetic.get("outward_interval_arithmetic_required") is True
        and arithmetic.get("binary64_candidate_discovery_allowed") is True
        and arithmetic.get("binary64_theorem_decision_allowed") is False
    )
    checks["auxiliary_artifact_policy"] = (
        auxiliary_policy.get("artifact_path") == EXPECTED_AUXILIARY_PATH
        and auxiliary_policy.get("artifact_sha256") == EXPECTED_AUXILIARY_SHA256
        and auxiliary_policy.get("candidate_artifact_byte_frozen") is True
        and auxiliary_policy.get("cross_platform_regeneration_required") is False
        and auxiliary_policy.get("binary64_svd_construction_platform_sensitive") is True
        and auxiliary_policy.get("regeneration_diagnostic_only") is True
        and auxiliary_policy.get("accepted_artifact_hashes") == [EXPECTED_AUXILIARY_SHA256]
        and auxiliary_policy.get("known_nonaccepted_platform_variant_sha256")
        == KNOWN_PLATFORM_VARIANT_SHA256
        and auxiliary_policy.get("platform_variant_is_not_r5_failure") is True
        and auxiliary_policy.get("future_R5_B_certifies_frozen_candidate_objects_only") is True
        and auxiliary_policy.get("theorem_certified") is False
    )
    checks["future_acceptance_gates_complete"] = set(gates) == REQUIRED_GATES
    checks["rejection_statuses_declared"] = set(rejections) == {
        "protocol_or_hash_mismatch",
        "missing_required_frozen_data",
        "failed_strict_gate",
        "forbidden_R5_or_R6_result_present",
    }
    checks["nonconstancy_design_fixed"] = (
        nonconstancy.get("s_interval") == ["0", "1/12"]
        and "cos(2*pi*s) >= 1/2" in nonconstancy.get("required_cosine_bound", "")
        and "a_dot" in nonconstancy.get("intrinsic_speed", "")
        and "speed" in nonconstancy.get("environment_speed_gate", "")
    )
    checks["exact_response_logic_not_residual_zero"] = (
        response_identity.get("forbidden_substitute") == "residual interval contains zero"
        and "fixed B is strictly invertible" in response_identity.get("required_logic", [])
        and len(response_identity.get("required_logic", [])) == 5
    )
    checks["forbidden_fields_listed"] = set(protocol.get("forbidden_fields", [])) == FORBIDDEN_FIELDS
    checks["forbidden_result_fields_absent"] = not find_forbidden_keys(
        {key: value for key, value in protocol.items() if key != "forbidden_fields"},
        FORBIDDEN_FIELDS,
    )
    return checks


def run_mutation_tests(protocol: dict[str, Any]) -> dict[str, bool]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(protocol)
    mutated["status"] = "R5_CERTIFIED"
    cases["changed_status_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["parent_protocol"]["sha256"] = "0" * 64
    cases["parent_hash_mismatch_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["source_references"]["corrected_atlas"]["member_sha256"] = "0" * 64
    cases["atlas_hash_mismatch_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["R5_full_tube_object"]["fixed_v"]["components"][0] = "0"
    cases["changed_v_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["R5_full_tube_object"]["tube_parameter"]["interval"] = ["0", "1e-12"]
    cases["half_tube_interval_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["subdivision_strategy"]["maximum_refinement_depth"] = 9
    cases["changed_refinement_depth_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["arithmetic"]["binary64_theorem_decision_allowed"] = True
    cases["binary64_theorem_decision_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["future_acceptance_gates"].pop("overlap_consistency")
    cases["missing_overlap_gate_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["exact_response_identity_design"]["forbidden_substitute"] = (
        "residual interval contains zero is sufficient"
    )
    cases["residual_zero_substitute_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["nonconstancy_design"]["s_interval"] = ["0", "1"]
    cases["changed_nonconstancy_interval_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["boundary"]["R6_search_performed"] = True
    cases["R6_search_marked_run_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["normal_K1_recovery_result"] = {"status": "present"}
    cases["normal_K1_result_field_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["all_gates_pass"] = True
    cases["forged_all_gates_pass_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["required_frozen_data_before_certificate"][1]["object_sha256"] = "0" * 64
    cases["partial_auxiliary_object_hash_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["auxiliary_artifact_policy"]["artifact_sha256"] = KNOWN_PLATFORM_VARIANT_SHA256
    cases["frozen_artifact_sha_change_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["auxiliary_artifact_policy"]["cross_platform_regeneration_required"] = True
    cases["cross_platform_regeneration_required_true_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["auxiliary_artifact_policy"]["candidate_artifact_byte_frozen"] = False
    cases["candidate_artifact_byte_frozen_false_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["auxiliary_artifact_policy"]["platform_variant_is_not_r5_failure"] = False
    cases["platform_variant_as_r5_failure_fails"] = mutated

    mutated = copy.deepcopy(protocol)
    mutated["auxiliary_artifact_policy"]["accepted_artifact_hashes"] = [
        EXPECTED_AUXILIARY_SHA256,
        KNOWN_PLATFORM_VARIANT_SHA256,
    ]
    cases["two_platform_hashes_accepted_fails"] = mutated

    return {name: not all(verify(case).values()) for name, case in cases.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()

    protocol = read_json(PROTOCOL_PATH)
    checks = verify(protocol)
    if args.mutation_tests:
        checks.update(run_mutation_tests(protocol))
    print(json.dumps(checks, indent=2, sort_keys=True))
    passed = bool(checks) and all(checks.values())
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
