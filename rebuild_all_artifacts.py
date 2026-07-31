#!/usr/bin/env python3
"""Regenerate the lost formal input and the 80/160-step raw outputs.

This driver is deliberately fail-closed. It only packages results when the
reconstructed v1.3.1 parameterization and both projected-gradient curves have
the previously recorded canonical SHA-256 values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


EXPECTED_PARAMETERIZATION = (
    "e8ad8a6fbcab626b726082b570f59df6854d4a28259177783e1f5e3274b1cb84"
)
EXPECTED_CURVE_80 = (
    "c05e1184d6e8e0b603f6a73323957f300291d02a78fdd950f920f0a1dc383063"
)
EXPECTED_CURVE_160 = (
    "b63827b54311e895a2089610575601a5c79fa43d66ddd40f9cccfb1f37c9d670"
)
SUPPORTED_STATUS = "PROJECTED_GRADIENT_CURVE_RECONSTRUCTION_SUPPORTED"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_json_sha256(path: Path) -> str:
    return hashlib.sha256(canonical_json(json.loads(path.read_text()))).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> None:
    print("\n[run]", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def verify_exact_root(output: Path) -> Path:
    parameterization = output / "global_parameterization.json"
    report_path = output / "report.json"
    required = [
        output / "protocol.json",
        parameterization,
        output / "certificate.json",
        report_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"incomplete v1.3.1 output: {missing}")
    actual = canonical_json_sha256(parameterization)
    if actual != EXPECTED_PARAMETERIZATION:
        raise RuntimeError(
            "v1.3.1 parameterization hash mismatch: "
            f"expected {EXPECTED_PARAMETERIZATION}, got {actual}"
        )
    report = json.loads(report_path.read_text())
    gates = (
        report.get("all_parameter_boxes_pass")
        and report.get("all_shared_endpoints_pass")
        and report.get("all_endpoint_root_boxes_pass")
        and report.get("L6_descent_segments_certified") == 10
    )
    if not gates:
        raise RuntimeError("the formal response-curve/L6 gates did not close")
    return parameterization


def verify_curve(output: Path, expected_curve: str, expected_steps: int) -> None:
    required = [
        output / "protocol.json",
        output / "reconstructed_curve.json",
        output / "report.json",
        output / "step_diagnostics.csv",
        output / "provenance.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"incomplete {expected_steps}-step output: {missing}")
    report = json.loads((output / "report.json").read_text())
    actual_curve = canonical_json_sha256(output / "reconstructed_curve.json")
    if (
        report.get("scientific_status") != SUPPORTED_STATUS
        or not report.get("all_gates_pass")
        or report.get("steps") != expected_steps
        or report.get("source_parameterization_sha256")
        != EXPECTED_PARAMETERIZATION
        or actual_curve != expected_curve
        or report.get("reconstructed_curve_sha256") != expected_curve
    ):
        raise RuntimeError(
            f"{expected_steps}-step validation failed; "
            f"expected curve {expected_curve}, got {actual_curve}"
        )


def copy_repository_payload(package: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in (
        ".github",
        "docs",
        "scripts",
        "tools",
        ".gitignore",
        "MIGRATION_PLAN.md",
        "README.md",
        "README_RECOVERY.md",
        "requirements.txt",
        "rebuild_all_artifacts.py",
    ):
        source = package / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        elif source.is_file():
            shutil.copy2(source, target)


def build_release(
    package: Path,
    workspace: Path,
    exact: Path,
    run80: Path,
    run160: Path,
) -> Path:
    ready = workspace / "Geometric-Flow-ready-v0.2.3"
    if ready.exists():
        shutil.rmtree(ready)
    copy_repository_payload(package, ready)
    (ready / "inputs").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        exact / "global_parameterization.json",
        ready / "inputs" / "global_parameterization.json",
    )
    results = ready / "results"
    shutil.copytree(exact, results / "exact_root_v1_3_1")
    shutil.copytree(run80, results / "projected_gradient_80")
    shutil.copytree(run160, results / "projected_gradient_160")

    manifest = {
        "release": "Geometric-Flow-ready-v0.2.3",
        "known_canonical_hashes": {
            "global_parameterization.json": EXPECTED_PARAMETERIZATION,
            "reconstructed_curve_80.json": EXPECTED_CURVE_80,
            "reconstructed_curve_160.json": EXPECTED_CURVE_160,
        },
        "files": {
            str(path.relative_to(ready)): file_sha256(path)
            for path in sorted(ready.rglob("*"))
            if path.is_file() and path.name != "RECOVERY_MANIFEST.json"
        },
    }
    (ready / "RECOVERY_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    archive = workspace / "Geometric-Flow-ready-v0.2.3.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as stream:
        for path in sorted(ready.rglob("*")):
            if path.is_file():
                stream.write(path, path.relative_to(workspace))
    return archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default="recovered_artifacts")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--force",
        action="store_true",
        help="rerun stages even when complete verified outputs already exist",
    )
    args, ignored = parser.parse_known_args()
    if ignored:
        print(f"[notice] ignored notebook arguments: {ignored}")

    package = Path(__file__).resolve().parent
    scripts = package / "scripts"
    workspace = Path(args.workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    exact = workspace / "exact_root_v1_3_1"
    run80 = workspace / "projected_gradient_80"
    run160 = workspace / "projected_gradient_160"

    if args.force or not (exact / "global_parameterization.json").is_file():
        run(
            [
                args.python,
                str(scripts / "response_fibre_exact_root_descent_v1_3_1.py"),
                "--output",
                str(exact),
            ],
            workspace,
        )
    parameterization = verify_exact_root(exact)

    if args.force or not (run80 / "reconstructed_curve.json").is_file():
        run(
            [
                args.python,
                str(
                    scripts
                    / "response_fibre_projected_gradient_reconstruction_v0_2_2_oneclick.py"
                ),
                "--parameterization",
                str(parameterization),
                "--steps",
                "80",
                "--output",
                str(run80),
            ],
            workspace,
        )
    verify_curve(run80, EXPECTED_CURVE_80, 80)

    if args.force or not (run160 / "reconstructed_curve.json").is_file():
        run(
            [
                args.python,
                str(
                    scripts
                    / "response_fibre_projected_gradient_reconstruction_v0_2_3_steps160_oneclick.py"
                ),
                "--parameterization",
                str(parameterization),
                "--steps",
                "160",
                "--output",
                str(run160),
            ],
            workspace,
        )
    verify_curve(run160, EXPECTED_CURVE_160, 160)

    archive = build_release(package, workspace, exact, run80, run160)
    print("\nRECOVERY COMPLETE")
    print(f"archive = {archive}")
    print(f"archive_sha256 = {file_sha256(archive)}")


if __name__ == "__main__":
    main()
