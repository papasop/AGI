#!/usr/bin/env python3
"""Third same-chart recenter target / parametric-root inclusion audit v0.9.23.

Runs the embedded hash-locked v0.9.22 chain, then proves that its complete
signed 557-step endpoint box lies inside the v0.9.10 certified parametric
fibre-graph domain. Consequently the existing parametric Krawczyk theorem
already supplies a unique normal root for every tangent point in that box.

This does not yet construct a third tangent/normal frame or third Picard chart.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import time
from decimal import Decimal, getcontext
from pathlib import Path

VERSION = "0.9.23"
TITLE = "GEOMETRIC-FLOW THIRD-RECENTER ENDPOINT-BOX / PARAMETRIC-ROOT INCLUSION"
V0922_NAME = "archive/frozen_milestones/03_endpoint_enclosure/response_fibre_signed_field_export_v0_9_22_oneclick.py"
V0922_SHA = "22c1d0f0f4ae736e22e317fe90371a0b160140176a8c214e18d2f151be2d3cf7"
EMBEDDED_V0922_GZIP_B64 = "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"
getcontext().prec = 80


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tmp.replace(path)


def materialize_v0922(destination: Path) -> Path:
    raw = gzip.decompress(base64.b64decode(EMBEDDED_V0922_GZIP_B64))
    got = hashlib.sha256(raw).hexdigest()
    if got != V0922_SHA:
        raise RuntimeError(f"embedded v0.9.22 hash mismatch: expected {V0922_SHA}, got {got}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    return destination


def parse() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(description=TITLE)
    p.add_argument("--outdir", default="response_fibre_third_recenter_v0_9_23_results")
    p.add_argument("--root-radius", default="2e-18")
    return p.parse_known_args()


def find_picard(root: Path) -> Path:
    matches = list(root.rglob("intrinsic_picard_microstep_certificate.json"))
    valid = []
    for path in matches:
        try:
            data = json.loads(path.read_text())
            if (data.get("gates", {}).get("complex_parametric_fibre_graph") is True
                    and "outer_complex_tangent_radius" in data):
                valid.append(path)
        except Exception:
            pass
    if len(valid) != 1:
        raise RuntimeError(f"expected one formal second-chart Picard certificate, found {len(valid)}")
    return valid[0]


def run(args: argparse.Namespace) -> dict:
    started = time.time()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    v0922 = materialize_v0922(out / "embedded_sources" / V0922_NAME)
    child = out / "v0922_signed_endpoint_chain"
    done = subprocess.run(
        [sys.executable, str(v0922), "--outdir", str(child),
         "--root-radius", str(args.root_radius)],
        text=True, capture_output=True,
    )
    (out / "stdout.txt").write_text(done.stdout)
    (out / "stderr.txt").write_text(done.stderr)
    summary_path = child / "run_summary.json"
    endpoint_cert_path = child / "signed_field_endpoint_certificate.json"
    if not (summary_path.is_file() and endpoint_cert_path.is_file()):
        raise RuntimeError(
            f"embedded v0.9.22 exit={done.returncode}; expected certificates missing; inspect logs"
        )
    s = json.loads(summary_path.read_text())
    e = json.loads(endpoint_cert_path.read_text())
    picard_path = find_picard(child)
    p = json.loads(picard_path.read_text())

    box = e["endpoint_box"]
    centers = [Decimal(str(x)) for x in box["center"]]
    radii = [Decimal(str(x)) for x in box["component_radius"]]
    if len(centers) != 6 or len(radii) != 6:
        raise RuntimeError("signed endpoint box is not six-dimensional")
    abs_component_upper = [abs(c) + r for c, r in zip(centers, radii)]
    max_abs = max(abs_component_upper)
    inner = Decimal(str(p["inner_real_picard_radius"]))
    outer = Decimal(str(p["outer_complex_tangent_radius"]))
    normal_radius = Decimal(str(p["refined_normal_graph_radius"]))
    graph_utilization = Decimal(str(p["complex_graph_krawczyk_utilization"]))
    inner_margin = inner - max_abs
    outer_margin = outer - max_abs

    gates = {
        "embedded_v0922_hash_exact": sha(v0922) == V0922_SHA,
        "embedded_v0922_exit_zero": done.returncode == 0,
        "v0922_all_scientific_gates_pass": s.get("all_scientific_gates_pass") is True,
        "signed_557_endpoint_box_certified": s.get("signed_557_step_endpoint_box_certified") is True,
        "formal_complex_parametric_fibre_graph": p.get("gates", {}).get("complex_parametric_fibre_graph") is True,
        "implicit_graph_derivative_enclosed": p.get("gates", {}).get("implicit_graph_derivative_enclosed") is True,
        "graph_krawczyk_utilization_strictly_below_one": graph_utilization < 1,
        "complete_endpoint_box_inside_real_inner_domain": max_abs < inner,
        "complete_endpoint_box_inside_complex_outer_domain": max_abs < outer,
        "positive_third_recenter_domain_margin": inner_margin > 0,
    }
    passed = all(gates.values())
    third_target = {
        "schema": "geometric-flow/third-recenter-target/v0.9.23",
        "coordinate_system": e.get("coordinate_system"),
        "tangent_target_center": [str(x) for x in centers],
        "tangent_target_component_radius": [str(x) for x in radii],
        "maximum_absolute_tangent_coordinate": str(max_abs),
        "certified_parametric_domain": {
            "inner_real_radius": str(inner),
            "outer_complex_radius": str(outer),
            "inner_margin": str(inner_margin),
            "outer_margin": str(outer_margin),
        },
        "normal_root_enclosure_radius": str(normal_radius),
        "unique_normal_root_for_every_point_in_endpoint_box": passed,
        "source_hashes": {
            "v0922": V0922_SHA,
            "v0922_summary": sha(summary_path),
            "signed_endpoint_certificate": sha(endpoint_cert_path),
            "picard_certificate": sha(picard_path),
        },
        "claim_boundary": "parametric-root existence/uniqueness and target inclusion only; no third frame or third Picard microstep",
    }
    atomic(out / "third_recenter_target_certificate.json", third_target)

    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": "VALIDATED_THIRD_RECENTER_TARGET_AND_UNIQUE_PARAMETRIC_NORMAL_ROOT_CERTIFIED" if passed else "V0923_THIRD_RECENTER_INCONCLUSIVE_FAIL_CLOSED",
        "third_recenter_target": third_target,
        "metrics": {
            "maximum_endpoint_absolute_coordinate": str(max_abs),
            "inner_real_domain_radius": str(inner),
            "outer_complex_domain_radius": str(outer),
            "inner_domain_margin": str(inner_margin),
            "outer_domain_margin": str(outer_margin),
            "refined_normal_graph_radius": str(normal_radius),
            "complex_graph_krawczyk_utilization": str(graph_utilization),
        },
        "gates": gates,
        "all_scientific_gates_pass": passed,
        "third_recenter_target_certified": passed,
        "unique_normal_root_over_complete_endpoint_box_certified": passed,
        "third_tangent_normal_frame_certified": False,
        "third_local_picard_chart_certified": False,
        "complete_child_certified": False,
        "global_flow_claimed": False,
        "certificate": str(out / "third_recenter_target_certificate.json"),
        "next_required_step": "construct and Arb-certify a new tangent/normal frame at the frozen third-recenter centre, then prove endpoint-box overlap in that frame",
        "claim_boundary": "third-recenter target inclusion plus inherited unique parametric normal root; no third frame/Picard chart or global continuation",
        "elapsed_seconds": time.time() - started,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    raw = json.dumps(result, sort_keys=True, allow_nan=False).encode()
    result["report_sha256_before_self_field"] = hashlib.sha256(raw).hexdigest()
    atomic(out / "run_summary.json", result)
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
        return 0 if result["all_scientific_gates_pass"] else 2
    except Exception as exc:
        print(json.dumps({
            "scientific_status": "V0923_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
