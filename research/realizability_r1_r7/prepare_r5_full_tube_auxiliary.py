#!/usr/bin/env python3
"""Prepare candidate data for the R5 full-tube protocol.

This script serializes candidate auxiliary data only. It does not run an R5
certificate, R6 search, Krawczyk/Picard acceptance audit, or normal K=1
recovery. The committed candidate artifact is byte-frozen and hash-bound.
Its binary64 SVD construction is platform-sensitive and is not a cross-platform
reproducibility or theorem-bearing gate.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import textwrap
import zipfile
import argparse
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "data" / "r5_full_tube_auxiliary_v1_0.json"

V074_SOURCE = ROOT / "src" / "response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
V092_SOURCE = ROOT / "src" / "response_fibre_centered_mean_value_krawczyk_v0_9_2.py"
V093_SOURCE = ROOT / "src" / "response_fibre_intrinsic_picard_microstep_v0_9_3.py"
INPUTS_ZIP = ROOT / "inputs" / "response_fibre_v0_6_2_backend_inputs.zip"
PARENT_PROTOCOL = HERE / "frozen_protocol_v1_0.json"

BASELINE_COMMIT = "350ddf6588082b5e175ba1ffcd0e6ddf51f9314a"
PARENT_PROTOCOL_SHA256 = "e8519a644ab50a9989eb40bc34499055f83760563167d88da21d17b3c7539e1c"
INPUTS_ZIP_SHA256 = "2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
CORRECTED_ATLAS_MEMBER_SHA256 = "e1c816b9c69b6e4ca9e7018b9857ce04a7b6d12c639e51e6792376dbd28d7ec9"
V074_SOURCE_SHA256 = "1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"
V092_SOURCE_SHA256 = "844e62e63d97d6845ed62c0c66597e246fd021b21aed31e22609cdaaec5a269d"
V093_SOURCE_SHA256 = "3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c"
EXPECTED_FROZEN_AUXILIARY_SHA256 = "434b8d58793b39462fc3dcf4e04f716b56e65de790e87daaecedf2e103e29037"
KNOWN_PLATFORM_VARIANT_SHA256 = "88e814702916e74a9963256f21a6fe7acdce5d806a88d25eebb5fb84a0f026fe"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def corrected_atlas_hash(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        names = [
            name
            for name in archive.namelist()
            if name == "corrected_atlas.json"
            or name.endswith("/corrected_atlas.json")
        ]
        if len(names) != 1:
            raise RuntimeError("inputs ZIP must contain exactly one corrected_atlas.json")
        return hashlib.sha256(archive.read(names[0])).hexdigest()


def check_inputs() -> None:
    expected = {
        PARENT_PROTOCOL: PARENT_PROTOCOL_SHA256,
        INPUTS_ZIP: INPUTS_ZIP_SHA256,
        V074_SOURCE: V074_SOURCE_SHA256,
        V092_SOURCE: V092_SOURCE_SHA256,
        V093_SOURCE: V093_SOURCE_SHA256,
    }
    for path, expected_hash in expected.items():
        actual = sha256_file(path)
        if actual != expected_hash:
            raise RuntimeError(f"hash mismatch for {path}: {actual} != {expected_hash}")
    actual_atlas = corrected_atlas_hash(INPUTS_ZIP)
    if actual_atlas != CORRECTED_ATLAS_MEMBER_SHA256:
        raise RuntimeError(
            "corrected_atlas member hash mismatch: "
            f"{actual_atlas} != {CORRECTED_ATLAS_MEMBER_SHA256}"
        )


def injection() -> str:
    code = r'''
import os
import platform

r5_output = Path(os.environ["R5_AUX_OUTPUT"])
r5_output.parent.mkdir(parents=True, exist_ok=True)


def r5_matmul(left, right):
    return [
        [
            sum((left[r][k] * right[k][c] for k in range(len(right))), acb(0))
            for c in range(len(right[0]))
        ]
        for r in range(len(left))
    ]


def r5_response(phases):
    z, _ = projective_jet_and_derivatives(phases, mirror=False)
    zbar, _ = projective_jet_and_derivatives(phases, mirror=True)
    values = []
    for order in range(RESPONSE_ORDER + 1):
        values.append((z.c[order] + zbar.c[order]) / 2)
    for order in range(RESPONSE_ORDER + 1):
        values.append((z.c[order] - zbar.c[order]) / (2 * I))
    return values


def r5_dec(value):
    if isinstance(value, acb):
        value = value.real
    mid, _rad = midpoint_radius(value)
    return repr(float(mid))


def r5_matrix_decimal(matrix):
    return [[r5_dec(value) for value in row] for row in matrix]


def r5_vector_decimal(vector):
    return [r5_dec(value) for value in vector]


def r5_svd_canonicalize(left, singular_values, right_t):
    # NumPy's SVD can vary by platform and BLAS/LAPACK backend, and each
    # singular vector sign is mathematically indeterminate. Canonicalize signs
    # for local diagnostics without treating regeneration as a release gate.
    left = left.copy()
    right_t = right_t.copy()
    for index in range(right_t.shape[0]):
        row = right_t[index, :]
        pivot = int(np.argmax(np.abs(row)))
        if row[pivot] < 0.0:
            right_t[index, :] *= -1.0
            if index < left.shape[1]:
                left[:, index] *= -1.0
        elif row[pivot] == 0.0:
            raise ArithmeticError("SVD sign canonicalization encountered zero pivot")
    return left, singular_values, right_t


def r5_float_matrix_strings(matrix):
    return [[repr(float(matrix[r, c])) for c in range(matrix.shape[1])]
            for r in range(matrix.shape[0])]


def r5_main():
    center = child_centers[15]
    base_phases, _ = phase_and_derivative_at(chart, acb(ap(center)), True)
    raw = unpack_raw_invariants(analytic_invariants(chart, acb(ap(center))))
    jacobian_float = np.asarray(
        [
            [midpoint_radius(raw["jacobian"][r][c].real)[0]
             for c in range(CONTROL_DIMENSION)]
            for r in range(RESPONSE_DIMENSION)
        ],
        dtype=float,
    )
    left, singular_values, right_t = np.linalg.svd(jacobian_float, full_matrices=True)
    left, singular_values, right_t = r5_svd_canonicalize(
        left, singular_values, right_t
    )
    normal_float = right_t[:RESPONSE_DIMENSION, :].T
    tangent_float = right_t[RESPONSE_DIMENSION:, :].T
    b_float = np.diag(1.0 / singular_values) @ left.T

    tangent = [
        [acb(ap(float(tangent_float[r, c])))
         for c in range(CONTROL_DIMENSION - RESPONSE_DIMENSION)]
        for r in range(CONTROL_DIMENSION)
    ]
    normal = [
        [acb(ap(float(normal_float[r, c])))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(CONTROL_DIMENSION)
    ]
    b_matrix = [
        [acb(ap(float(b_float[r, c])))
         for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)
    ]
    jw0 = r5_matmul(b_matrix, raw["jacobian"])
    fb0 = r5_matmul(jw0, normal)
    fb0_midpoint = np.asarray(
        [
            [midpoint_radius(fb0[r][c].real)[0]
             for c in range(RESPONSE_DIMENSION)]
            for r in range(RESPONSE_DIMENSION)
        ],
        dtype=float,
    )
    p_float = np.linalg.inv(fb0_midpoint)
    response_c = r5_response(base_phases)

    output = {
        "schema_version": "1.0",
        "dataset_id": "r5_full_tube_auxiliary_v1_0",
        "scientific_status": (
            "R5_AUXILIARY_CANDIDATE_DATA_FROZEN_PENDING_ARB_VALIDATION"
        ),
        "r5_certificate_run": False,
        "r6_search_performed": False,
        "normal_K1_residual_recovery_performed": False,
        "theorem_certified": False,
        "binary64_candidate_construction_used": True,
        "baseline_commit": os.environ["R5_BASELINE_COMMIT"],
        "parent_protocol_sha256": os.environ["R5_PARENT_PROTOCOL_SHA256"],
        "corrected_atlas_member_sha256": os.environ["R5_CORRECTED_ATLAS_SHA256"],
        "source_files": {
            "v0_7_4_source": {
                "path": "src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py",
                "sha256": os.environ["R5_V074_SOURCE_SHA256"],
            },
            "v0_9_2_design_reference": {
                "path": "src/response_fibre_centered_mean_value_krawczyk_v0_9_2.py",
                "sha256": os.environ["R5_V092_SOURCE_SHA256"],
                "role": "candidate construction provenance only; not an R5 or R6 certificate",
            },
            "v0_9_3_design_reference": {
                "path": "src/response_fibre_intrinsic_picard_microstep_v0_9_3.py",
                "sha256": os.environ["R5_V093_SOURCE_SHA256"],
                "role": "candidate construction provenance only; not an R5 or R6 certificate",
            },
            "inputs_zip": {
                "path": "inputs/response_fibre_v0_6_2_backend_inputs.zip",
                "sha256": os.environ["R5_INPUTS_ZIP_SHA256"],
            },
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "python_flint": "0.8.0",
            "arb_precision_bits": str(PRECISION_BITS),
        },
        "construction_method": {
            "source": "deterministic replay of the v0.9.3 midpoint SVD frame construction",
            "chart": "9",
            "subdivision": "32",
            "child_index": "15",
            "theta0_local_coordinate": repr(float(center)),
            "svd_rule": (
                "np.linalg.svd(jacobian_midpoint, full_matrices=True), then "
                "for each right singular vector row choose the sign so its "
                "largest-absolute component is positive; row order is NumPy's "
                "nonincreasing singular-value order followed by the returned "
                "null-space rows"
            ),
            "degeneracy_rule": (
                "if a canonicalization pivot is zero, stop; future Arb "
                "certificates must independently validate frame rank and "
                "transversality"
            ),
            "no_search_or_optimization": True,
            "candidate_only_not_theorem": True,
        },
        "object_roles": {
            "W_Pi": "R3 protocol-relative response-cost weight, fixed as I_8; not serialized here as B or P",
            "B": "response-coordinate map in the graph equation B(R3(theta)-c)=0",
            "P": "numerical candidate inverse/preconditioner for B*DR3(theta0)*N",
        },
        "dimensions": {
            "control_dimension": str(CONTROL_DIMENSION),
            "response_dimension": str(RESPONSE_DIMENSION),
            "tangent_dimension": str(CONTROL_DIMENSION - RESPONSE_DIMENSION),
            "normal_dimension": str(RESPONSE_DIMENSION),
            "theta_0": [str(CONTROL_DIMENSION)],
            "T": [str(CONTROL_DIMENSION), str(CONTROL_DIMENSION - RESPONSE_DIMENSION)],
            "N": [str(CONTROL_DIMENSION), str(RESPONSE_DIMENSION)],
            "B": [str(RESPONSE_DIMENSION), str(RESPONSE_DIMENSION)],
            "c": [str(RESPONSE_DIMENSION)],
            "P": [str(RESPONSE_DIMENSION), str(RESPONSE_DIMENSION)],
        },
        "tube": {
            "v": ["1", "0", "0", "0", "0", "0"],
            "t_interval": ["-1e-12", "1e-12"],
            "frozen_epsilons": ["1e-14", "3e-14", "1e-13", "3e-13", "1e-12"],
        },
        "objects": {
            "theta_0": r5_vector_decimal(base_phases),
            "T": r5_float_matrix_strings(tangent_float),
            "N": r5_float_matrix_strings(normal_float),
            "B": r5_float_matrix_strings(b_float),
            "c": r5_vector_decimal(response_c),
            "P": r5_float_matrix_strings(p_float),
            "midpoint_response_singular_values": [
                repr(float(value)) for value in singular_values
            ],
            "midpoint_response_jacobian": r5_float_matrix_strings(jacobian_float),
            "normal_derivative_midpoint": r5_float_matrix_strings(fb0_midpoint),
        },
        "future_arb_validation_required": [
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
        ],
        "forbidden_interpretations": [
            "R5 certificate",
            "R6 search result",
            "normal K=1 residual recovery",
            "theorem-bearing Arb validation",
            "physical time, energy, or action claim",
            "Lorentzian spacetime or GR claim",
            "global flow claim",
        ],
    }
    r5_output.write_text(
        json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


r5_main()
raise SystemExit(0)
'''
    return textwrap.indent(textwrap.dedent(code).strip("\n") + "\n", "    ")


def patch_frozen_source(source: bytes) -> str:
    text = source.decode("utf-8")
    needle = '''    banner(
        "STAGE A FROZEN-SOLVE DESCENT / "
        "STAGE B FROZEN KKT-WITNESS ALIGNMENT"
    )
'''
    if text.count(needle) != 1:
        raise RuntimeError("frozen Stage-A insertion point not unique")
    return text.replace(needle, injection() + needle)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def add_object_hashes(path: Path) -> None:
    data = read_json(path)
    objects = data["objects"]
    data["object_sha256"] = {
        name: sha256_bytes(canonical_json(value))
        for name, value in sorted(objects.items())
    }
    path.write_text(
        canonical_json(data).decode("utf-8") + "\n",
        encoding="utf-8",
    )


def run_once(output: Path) -> str:
    check_inputs()
    with tempfile.TemporaryDirectory(prefix="r5_auxiliary_") as tmp:
        patched = Path(tmp) / "_r5_auxiliary_backend.py"
        patched.write_text(patch_frozen_source(V074_SOURCE.read_bytes()), encoding="utf-8")
        env = dict(os.environ)
        env.update(
            {
                "R5_AUX_OUTPUT": str(output),
                "R5_BASELINE_COMMIT": BASELINE_COMMIT,
                "R5_PARENT_PROTOCOL_SHA256": PARENT_PROTOCOL_SHA256,
                "R5_INPUTS_ZIP_SHA256": INPUTS_ZIP_SHA256,
                "R5_CORRECTED_ATLAS_SHA256": CORRECTED_ATLAS_MEMBER_SHA256,
                "R5_V074_SOURCE_SHA256": V074_SOURCE_SHA256,
                "R5_V092_SOURCE_SHA256": V092_SOURCE_SHA256,
                "R5_V093_SOURCE_SHA256": V093_SOURCE_SHA256,
            }
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(patched),
                "--inputs-zip",
                str(INPUTS_ZIP),
                "--chart",
                "9",
                "--subdivision",
                "32",
                "--output",
                str(Path(tmp) / "unused"),
            ],
            text=True,
            capture_output=True,
            env=env,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "R5 auxiliary candidate extraction failed:\n"
                + completed.stdout
                + completed.stderr
            )
    add_object_hashes(output)
    return sha256_file(output)


def generated_reproducibly() -> tuple[bytes, str, str]:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r5_auxiliary_final_") as tmp:
        first_path = Path(tmp) / "first.json"
        second_path = Path(tmp) / "second.json"
        first = run_once(first_path)
        second = run_once(second_path)
        first_bytes = first_path.read_bytes()
        if second_path.read_bytes() != first_bytes:
            print("R5_AUXILIARY_DATA_INCONCLUSIVE_NONDETERMINISTIC")
            print(json.dumps({"first_sha256": first, "second_sha256": second}, indent=2))
            raise SystemExit(1)
        return first_bytes, first, second


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "deprecated alias for --diagnose-regeneration; this is not a "
            "cross-platform CI or theorem gate"
        ),
    )
    parser.add_argument(
        "--verify-frozen",
        action="store_true",
        help="verify only the committed byte-frozen artifact identity",
    )
    parser.add_argument(
        "--diagnose-regeneration",
        action="store_true",
        help=(
            "rerun the platform-sensitive binary64 SVD construction as a "
            "diagnostic; a platform variant is not an R5/R6 result"
        ),
    )
    args = parser.parse_args()

    if args.verify_frozen:
        if not OUTPUT.is_file():
            print("R5_AUXILIARY_FROZEN_ARTIFACT_MISSING")
            return 1
        frozen_sha = sha256_file(OUTPUT)
        passed = frozen_sha == EXPECTED_FROZEN_AUXILIARY_SHA256
        print(
            json.dumps(
                {
                    "mode": "verify_frozen",
                    "output": str(OUTPUT.relative_to(ROOT)),
                    "sha256": frozen_sha,
                    "expected_sha256": EXPECTED_FROZEN_AUXILIARY_SHA256,
                    "candidate_artifact_byte_frozen": passed,
                    "cross_platform_regeneration_required": False,
                    "r5_certificate_run": False,
                    "r6_search_performed": False,
                    "theorem_certified": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        print("PASS" if passed else "FAIL")
        return 0 if passed else 1

    generated, first, second = generated_reproducibly()
    if args.check or args.diagnose_regeneration:
        if not OUTPUT.is_file():
            print("R5_AUXILIARY_REGENERATION_PLATFORM_VARIANT")
            print(
                json.dumps(
                    {
                        "mode": "diagnose_regeneration",
                        "generated_sha256": first,
                        "frozen_sha256": None,
                        "r5_certificate_run": False,
                        "r6_search_performed": False,
                        "theorem_certified": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
        frozen = OUTPUT.read_bytes()
        frozen_sha = hashlib.sha256(frozen).hexdigest()
        matched = frozen == generated
        status = (
            "R5_AUXILIARY_REGENERATION_MATCHED"
            if matched
            else "R5_AUXILIARY_REGENERATION_PLATFORM_VARIANT"
        )
        print(status)
        print(
            json.dumps(
                {
                    "mode": "diagnose_regeneration",
                    "generated_sha256": first,
                    "repeat_sha256": second,
                    "frozen_sha256": frozen_sha,
                    "known_platform_variant_sha256": KNOWN_PLATFORM_VARIANT_SHA256,
                    "byte_for_byte_matches_frozen": matched,
                    "cross_platform_regeneration_required": False,
                    "candidate_artifact_byte_frozen": (
                        frozen_sha == EXPECTED_FROZEN_AUXILIARY_SHA256
                    ),
                    "diagnostic_only_not_ci_gate": True,
                    "platform_variant_is_not_r5_failure": True,
                    "r5_certificate_run": False,
                    "r6_search_performed": False,
                    "theorem_certified": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    else:
        tmp_output = OUTPUT.with_suffix(".tmp")
        tmp_output.write_bytes(generated)
        tmp_output.replace(OUTPUT)
    print(
        json.dumps(
            {
                "scientific_status": (
                    "R5_AUXILIARY_CANDIDATE_DATA_FROZEN_PENDING_ARB_VALIDATION"
                ),
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": first,
                "repeat_sha256": second,
                "byte_for_byte_reproducible": True,
                "candidate_artifact_byte_frozen": True,
                "cross_platform_regeneration_required": False,
                "diagnostic_only_not_ci_gate": False,
                "r5_certificate_run": False,
                "r6_search_performed": False,
                "theorem_certified": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
