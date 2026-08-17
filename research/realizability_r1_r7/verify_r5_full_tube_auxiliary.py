#!/usr/bin/env python3
"""Verify R5 full-tube auxiliary candidate data.

This verifier is fail-closed and structural. It validates deterministic
candidate serialization for a future R5-A Arb graph certificate; it does not
run that certificate or infer theorem-bearing gates from the candidate data.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUX_PATH = HERE / "data" / "r5_full_tube_auxiliary_v1_0.json"
PARENT_PROTOCOL_PATH = HERE / "frozen_protocol_v1_0.json"

EXPECTED_AUXILIARY_SHA256 = "434b8d58793b39462fc3dcf4e04f716b56e65de790e87daaecedf2e103e29037"
EXPECTED_STATUS = "R5_AUXILIARY_CANDIDATE_DATA_FROZEN_PENDING_ARB_VALIDATION"
EXPECTED_BASELINE = "350ddf6588082b5e175ba1ffcd0e6ddf51f9314a"
EXPECTED_PARENT_SHA256 = "e8519a644ab50a9989eb40bc34499055f83760563167d88da21d17b3c7539e1c"
EXPECTED_INPUTS_ZIP_SHA256 = "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
EXPECTED_ATLAS_SHA256 = "e1c816b9c69b6e4ca9e7018b9857ce04a7b6d12c639e51e6792376dbd28d7ec9"
EXPECTED_V074_SHA256 = "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"
EXPECTED_V092_SHA256 = "844e62e63d97d6845ed62c0c66597e246fd021b21aed31e22609cdaaec5a269d"
EXPECTED_V093_SHA256 = "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c"

EXPECTED_OBJECT_SHA256 = {
    "theta_0": "077a169644e33145b4f14c5aa29d4ac86cd2e69572c6f35ddab8af92f41d918a",
    "T": "aa1814d7257f84de3f4eeff3d3feb01fcaa7dfc5db4030d82cabfe06046dda2c",
    "N": "d24a90e45ebea1ea46b0d049757809dc5c42371a740a40ca6412fc5f64e81ba8",
    "B": "f1f9c0d26df1c8366a96fdeafd269660bc06f7e2dfdc4391948d15f13edda170",
    "c": "151762ada396ef62608698fb18090e0a443fef869f3f4d91543ad4dfc8e9312a",
    "P": "ae09f2d3343301b12e2b661fa7d50d2b004cd4d72333cbca1703c20890a2d82e",
    "midpoint_response_singular_values": "56000c155cca30568af2aab172acac65a19a4849ad96919df04bd3b3c47649e3",
    "midpoint_response_jacobian": "447949e425e663c7f7c57064ce98ff10ef174f393a6f8cf253fe980769aa5952",
    "normal_derivative_midpoint": "3f73fbc0885992cc232851d876f60e74b94ae6adaf4952b394c3a7d79a3adc4b",
}

EXPECTED_SHAPES = {
    "theta_0": [14],
    "T": [14, 6],
    "N": [14, 8],
    "B": [8, 8],
    "c": [8],
    "P": [8, 8],
    "midpoint_response_singular_values": [8],
    "midpoint_response_jacobian": [8, 14],
    "normal_derivative_midpoint": [8, 8],
}
EXPECTED_V = ["1", "0", "0", "0", "0", "0"]
EXPECTED_EPSILONS = ["1e-14", "3e-14", "1e-13", "3e-13", "1e-12"]
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


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def finite_decimal_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError, OverflowError):
        return False
    return parsed.is_finite()


def all_decimal_strings(value: Any) -> bool:
    if isinstance(value, str):
        return finite_decimal_string(value)
    if isinstance(value, list):
        return all(all_decimal_strings(item) for item in value)
    return False


def shape_of(value: Any) -> list[int] | None:
    if not isinstance(value, list):
        return None
    if not value:
        return [0]
    if all(not isinstance(item, list) for item in value):
        return [len(value)]
    if not all(isinstance(item, list) for item in value):
        return None
    row_lengths = {len(row) for row in value}
    if len(row_lengths) != 1:
        return None
    return [len(value), row_lengths.pop()]


def find_forbidden_keys(value: Any) -> list[str]:
    found: list[str] = []

    def walk(node: Any, prefix: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if key in FORBIDDEN_FIELDS:
                    found.append(path)
                walk(child, path)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{prefix}[{index}]")

    walk(value, "")
    return found


def repeat_hashes_match(first: str, second: str) -> bool:
    return (
        isinstance(first, str)
        and isinstance(second, str)
        and len(first) == 64
        and len(second) == 64
        and first == second
    )


def verify(data: dict[str, Any], *, check_file_hash: bool = True) -> dict[str, bool]:
    objects = data.get("objects", {})
    object_hashes = data.get("object_sha256", {})
    dimensions = data.get("dimensions", {})
    refs = data.get("source_files", {})
    method = data.get("construction_method", {})
    roles = data.get("object_roles", {})
    tube = data.get("tube", {})
    environment = data.get("environment", {})

    checks: dict[str, bool] = {
        "auxiliary_file_sha256": (
            not check_file_hash or sha256_file(AUX_PATH) == EXPECTED_AUXILIARY_SHA256
        ),
        "schema_version": data.get("schema_version") == "1.0",
        "dataset_id": data.get("dataset_id") == "r5_full_tube_auxiliary_v1_0",
        "scientific_status": data.get("scientific_status") == EXPECTED_STATUS,
        "baseline_commit": data.get("baseline_commit") == EXPECTED_BASELINE,
        "parent_protocol_sha256": data.get("parent_protocol_sha256") == EXPECTED_PARENT_SHA256,
        "live_parent_protocol_sha256": sha256_file(PARENT_PROTOCOL_PATH) == EXPECTED_PARENT_SHA256,
        "corrected_atlas_member_sha256": data.get("corrected_atlas_member_sha256") == EXPECTED_ATLAS_SHA256,
        "no_certificate_or_search": (
            data.get("r5_certificate_run") is False
            and data.get("r6_search_performed") is False
            and data.get("normal_K1_residual_recovery_performed") is False
            and data.get("theorem_certified") is False
        ),
        "binary64_candidate_only": data.get("binary64_candidate_construction_used") is True,
        "forbidden_result_fields_absent": not find_forbidden_keys(data),
        "source_hashes": (
            refs.get("v0_7_4_source", {}).get("path")
            == "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
            and refs.get("v0_7_4_source", {}).get("sha256") == EXPECTED_V074_SHA256
            and refs.get("v0_9_2_design_reference", {}).get("path")
            == "src/response_fibre_centered_mean_value_krawczyk_v0_9_2.py"
            and refs.get("v0_9_2_design_reference", {}).get("sha256") == EXPECTED_V092_SHA256
            and refs.get("v0_9_3_design_reference", {}).get("path")
            == "src/response_fibre_intrinsic_picard_microstep_v0_9_3.py"
            and refs.get("v0_9_3_design_reference", {}).get("sha256") == EXPECTED_V093_SHA256
            and refs.get("inputs_zip", {}).get("path")
            == "inputs/response_fibre_v0_6_2_backend_inputs.zip"
            and refs.get("inputs_zip", {}).get("sha256") == EXPECTED_INPUTS_ZIP_SHA256
        ),
        "design_references_not_certificates": (
            "not an R5 or R6 certificate"
            in refs.get("v0_9_2_design_reference", {}).get("role", "")
            and "not an R5 or R6 certificate"
            in refs.get("v0_9_3_design_reference", {}).get("role", "")
        ),
        "environment_declared": (
            environment.get("python_flint") == "0.8.0"
            and environment.get("arb_precision_bits") == "192"
            and isinstance(environment.get("python"), str)
            and isinstance(environment.get("numpy"), str)
        ),
        "construction_method_fixed": (
            method.get("source")
            == "deterministic replay of the v0.9.3 midpoint SVD frame construction"
            and method.get("chart") == "9"
            and method.get("subdivision") == "32"
            and method.get("child_index") == "15"
            and "largest-absolute component is positive" in method.get("svd_rule", "")
            and "pivot is zero, stop" in method.get("degeneracy_rule", "")
            and method.get("no_search_or_optimization") is True
            and method.get("candidate_only_not_theorem") is True
        ),
        "roles_distinguish_WPi_B_P": (
            "response-cost weight" in roles.get("W_Pi", "")
            and "graph equation" in roles.get("B", "")
            and "preconditioner" in roles.get("P", "")
            and roles.get("W_Pi") != roles.get("B") != roles.get("P")
        ),
        "tube_fixed": (
            tube.get("v") == EXPECTED_V
            and tube.get("t_interval") == ["-1e-12", "1e-12"]
            and tube.get("frozen_epsilons") == EXPECTED_EPSILONS
        ),
        "object_keys_complete": set(objects) == set(EXPECTED_OBJECT_SHA256),
        "object_hash_keys_complete": set(object_hashes) == set(EXPECTED_OBJECT_SHA256),
        "object_hashes_match_expected": object_hashes == EXPECTED_OBJECT_SHA256,
    }

    for name, expected_shape in EXPECTED_SHAPES.items():
        value = objects.get(name)
        checks[f"{name}_shape"] = shape_of(value) == expected_shape
        checks[f"{name}_decimal_strings"] = all_decimal_strings(value)
        checks[f"{name}_hash_recomputed"] = (
            hashlib.sha256(canonical_json(value)).hexdigest()
            == EXPECTED_OBJECT_SHA256[name]
            == object_hashes.get(name)
        )

    checks["dimension_fields_are_strings"] = (
        dimensions.get("control_dimension") == "14"
        and dimensions.get("response_dimension") == "8"
        and dimensions.get("tangent_dimension") == "6"
        and dimensions.get("normal_dimension") == "8"
        and dimensions.get("theta_0") == ["14"]
        and dimensions.get("T") == ["14", "6"]
        and dimensions.get("N") == ["14", "8"]
        and dimensions.get("B") == ["8", "8"]
        and dimensions.get("c") == ["8"]
        and dimensions.get("P") == ["8", "8"]
    )
    checks["future_arb_validation_required"] = set(
        data.get("future_arb_validation_required", [])
    ) == {
        "frame_rank",
        "T_N_transversality",
        "B_strict_invertibility",
        "P_preconditioner_defect",
        "full_tube_graph_existence",
        "full_tube_graph_uniqueness",
        "overlap_consistency",
        "exact_response_identity",
        "zero_total_response_cost",
        "positive_measure_nonconstancy",
    }
    checks["forbidden_interpretations_present"] = {
        "R5 certificate",
        "R6 search result",
        "normal K=1 residual recovery",
        "theorem-bearing Arb validation",
        "global flow claim",
    }.issubset(set(data.get("forbidden_interpretations", [])))
    return checks


def mutation_cases(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(data)
    mutated["objects"]["T"][0][0] = "0"
    cases["matrix_element_change_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["objects"]["theta_0"][0] = 0.0
    cases["json_number_element_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["objects"]["T"] = mutated["objects"]["T"][:13]
    cases["shape_mismatch_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["objects"]["B"], mutated["objects"]["P"] = (
        mutated["objects"]["P"],
        mutated["objects"]["B"],
    )
    cases["B_P_identity_swap_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["source_files"]["v0_9_3_design_reference"]["path"] = "src/other.py"
    cases["source_path_change_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["source_files"]["v0_9_3_design_reference"]["sha256"] = "0" * 64
    cases["source_hash_change_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["baseline_commit"] = "deadbeef"
    cases["baseline_change_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["parent_protocol_sha256"] = "0" * 64
    cases["parent_protocol_change_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["construction_method"].pop("svd_rule")
    cases["missing_svd_rule_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["theorem_certified"] = True
    cases["theorem_certified_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["object_sha256"]["T"] = None
    cases["partial_hash_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["R5_certificate"] = {"status": "R5_CERTIFIED"}
    cases["R5_certificate_field_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["R6_search_result"] = {"status": "found"}
    cases["R6_field_fails"] = mutated

    mutated = copy.deepcopy(data)
    mutated["normal_K1_recovery_result"] = {"status": "found"}
    cases["normal_K1_field_fails"] = mutated

    return cases


def run_mutation_tests(data: dict[str, Any]) -> dict[str, bool]:
    results = {
        name: not all(verify(mutated, check_file_hash=False).values())
        for name, mutated in mutation_cases(data).items()
    }
    results["two_run_hash_mismatch_fails"] = not repeat_hashes_match(
        EXPECTED_AUXILIARY_SHA256, "0" * 64
    )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-tests", action="store_true")
    args = parser.parse_args()

    data = read_json(AUX_PATH)
    checks = verify(data)
    if args.mutation_tests:
        checks.update(run_mutation_tests(data))
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not all(checks.values()):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
