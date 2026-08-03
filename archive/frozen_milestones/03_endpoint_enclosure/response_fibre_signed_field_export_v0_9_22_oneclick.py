#!/usr/bin/env python3
"""Repository-native signed six-component field export audit v0.9.22.

Instruments the frozen v0.9.10 chain at the point where the Arb intrinsic
field has already been constructed. It exports real interval midpoints/radii
for all six components and integrates the uniform signed enclosure for 557
steps. No midpoint is accepted unless the original formal graph/metric/Picard
gates pass.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import importlib
import importlib.util
import json
import platform
import subprocess
import sys
import time
from decimal import Decimal, getcontext
from pathlib import Path

VERSION = "0.9.22"
TITLE = "GEOMETRIC-FLOW REPOSITORY-NATIVE SIGNED SIX-COMPONENT FIELD EXPORT"
V0910_NAME = "archive/frozen_milestones/02_second_chart/response_fibre_second_chart_v0_9_10_oneclick.py"
V0910_SHA = "e83ba04cf823b99ee1ae01d0d3d06c229e8699640950ff41e97730bc01a5e48c"
EMBEDDED_V0910_GZIP_B64 = "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"
getcontext().prec = 80

FIELD_HOOK = '''    field_sup = max((upper_point(value) for value in field), default=arb(0))'''
FIELD_REPLACEMENT = FIELD_HOOK + r'''

    # v0.9.22: signed real-component intervals. The complex-polydisc field
    # encloses its restriction to the real intrinsic domain, so value.real is
    # a valid real-field enclosure on that complete domain.
    v0922_field_midpoints=[]
    v0922_field_radii=[]
    v0922_field_lower=[]
    v0922_field_upper=[]
    for v0922_value in field:
        v0922_mid,v0922_rad=midpoint_radius(v0922_value.real)
        v0922_lo=float(v0922_value.real.lower())
        v0922_hi=float(v0922_value.real.upper())
        v0922_field_midpoints.append(float(v0922_mid))
        v0922_field_radii.append(float(v0922_rad))
        v0922_field_lower.append(v0922_lo)
        v0922_field_upper.append(v0922_hi)
'''

RESULT_HOOK = '''        "intrinsic_field_sup_norm_upper": upper_float(field_sup),'''
RESULT_REPLACEMENT = RESULT_HOOK + r'''
        "v0922_signed_intrinsic_field_component_midpoints": v0922_field_midpoints,
        "v0922_signed_intrinsic_field_component_radii": v0922_field_radii,
        "v0922_signed_intrinsic_field_component_lower": v0922_field_lower,
        "v0922_signed_intrinsic_field_component_upper": v0922_field_upper,
        "v0922_signed_field_export_coordinate_system": "v0.9.10-recentered-second-chart-intrinsic-tangent",
'''

PATCH_GENERATOR_HOOK = ''' source=source.replace(HOOK,HOOK+ARB_CODE,1)
 envneedle='''
PATCH_GENERATOR_REPLACEMENT = ''' source=source.replace(HOOK,HOOK+ARB_CODE,1)
 field_hook=%r
 field_replacement=%r
 result_hook=%r
 result_replacement=%r
 if source.count(field_hook)!=1:raise RuntimeError("v0.9.22 field hook not unique")
 source=source.replace(field_hook,field_replacement,1)
 if source.count(result_hook)!=1:raise RuntimeError("v0.9.22 result hook not unique")
 source=source.replace(result_hook,result_replacement,1)
 envneedle=''' % (FIELD_HOOK, FIELD_REPLACEMENT, RESULT_HOOK, RESULT_REPLACEMENT)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tmp.replace(path)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def locate_v0910(explicit: str | None, embedded_destination: Path) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend([Path.cwd() / V0910_NAME, Path("/content") / V0910_NAME])
    script = globals().get("__file__")
    if script:
        candidates.append(Path(script).resolve().parent / V0910_NAME)
    for path in candidates:
        if path.is_file():
            got = sha(path)
            if got != V0910_SHA:
                raise RuntimeError(f"v0.9.10 hash mismatch: expected {V0910_SHA}, got {got}")
            return path.resolve()
    raw = gzip.decompress(base64.b64decode(EMBEDDED_V0910_GZIP_B64))
    got = hashlib.sha256(raw).hexdigest()
    if got != V0910_SHA:
        raise RuntimeError(f"embedded v0.9.10 hash mismatch: expected {V0910_SHA}, got {got}")
    embedded_destination.parent.mkdir(parents=True, exist_ok=True)
    embedded_destination.write_bytes(raw)
    return embedded_destination.resolve()


def ensure_flint() -> str:
    try:
        import flint
        return getattr(flint, "__version__", "installed")
    except ModuleNotFoundError:
        if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
            raise RuntimeError("Install python-flint==0.8.0")
        print("[setup] installing frozen formal backend python-flint==0.8.0")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "python-flint==0.8.0"])
        importlib.invalidate_caches()
        import flint
        return getattr(flint, "__version__", "0.8.0")


def parse() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(description=TITLE)
    p.add_argument("--outdir", default="response_fibre_signed_field_v0_9_22_results")
    p.add_argument("--v0910")
    p.add_argument("--root-radius", default="2e-18")
    p.add_argument("--steps", type=int, default=557)
    return p.parse_known_args()


def run(args: argparse.Namespace) -> dict:
    started = time.time()
    if args.steps < 1 or args.steps > 557:
        raise ValueError("--steps must lie in [1,557]")
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    flint_version = ensure_flint()

    v0910_path = locate_v0910(
        args.v0910, out / "embedded_sources" / V0910_NAME
    )
    v0910 = load_module("gf_v0910_source", v0910_path)
    v099_source = v0910.locate(None, out / "embedded_sources" / v0910.V099)
    patched_v099 = out / "instrumented_v099_with_v0910_switch.py"
    v0910.patch_v099(v099_source, patched_v099)
    v099 = load_module("gf_v099_switched", patched_v099)
    materialized_v098 = out / "materialized_v098"
    materialized_v098.mkdir(parents=True, exist_ok=True)
    v098_path = v099.materialize_and_patch(materialized_v098)

    text = v098_path.read_text()
    if text.count(PATCH_GENERATOR_HOOK) != 1:
        raise RuntimeError("v0.9.8 patch-generator hook not unique")
    text = text.replace(PATCH_GENERATOR_HOOK, PATCH_GENERATOR_REPLACEMENT, 1)
    patched_v098 = out / "instrumented_v098_signed_field_driver.py"
    patched_v098.write_text(text)

    child = out / "formal_signed_field_chain"
    done = subprocess.run(
        [sys.executable, str(patched_v098), "--outdir", str(child),
         "--root-radius", str(args.root_radius)],
        text=True, capture_output=True,
    )
    (out / "stdout.txt").write_text(done.stdout)
    (out / "stderr.txt").write_text(done.stderr)
    picard = child / "formal_base" / "intrinsic_picard_microstep_certificate.json"
    root = child / "normal_root_arb_certificate.json"
    if not (picard.is_file() and root.is_file()):
        raise RuntimeError(
            f"instrumented formal backend exit={done.returncode}; certificates missing; inspect stdout.txt/stderr.txt"
        )
    p = json.loads(picard.read_text())
    r = json.loads(root.read_text())
    mids = p.get("v0922_signed_intrinsic_field_component_midpoints", [])
    radii = p.get("v0922_signed_intrinsic_field_component_radii", [])
    lower = p.get("v0922_signed_intrinsic_field_component_lower", [])
    upper = p.get("v0922_signed_intrinsic_field_component_upper", [])
    M = Decimal(str(p["intrinsic_field_sup_norm_upper"]))

    T = Decimal(args.steps) * Decimal("1e-14")
    r0 = Decimal("3.187e-15")
    endpoint_centers = [str(T * Decimal(str(x))) for x in mids]
    endpoint_radii = [str(r0 + T * Decimal(str(x))) for x in radii]
    endpoint_lower = [str(-r0 + T * Decimal(str(x))) for x in lower]
    endpoint_upper = [str(r0 + T * Decimal(str(x))) for x in upper]
    max_abs_endpoint = max(
        [abs(Decimal(x)) for x in endpoint_lower + endpoint_upper],
        default=Decimal("Infinity"),
    )

    gates = {
        "instrumented_backend_exit_zero": done.returncode == 0,
        "v0910_source_hash_exact": sha(v0910_path) == V0910_SHA,
        "v098_unique_normal_root": r.get("unique_normal_root_certified") is True,
        "v099_recentered_frame": r.get("v099_all_frame_gates_pass") is True,
        "formal_picard_gates_pass": p.get("all_gates_pass") is True,
        "six_signed_field_intervals_exported": len(mids) == len(radii) == len(lower) == len(upper) == 6,
        "signed_intervals_ordered": len(lower) == 6 and all(Decimal(str(lo)) <= Decimal(str(hi)) for lo, hi in zip(lower, upper)),
        "signed_intervals_inside_formal_sup_bound": len(mids) == 6 and all(abs(Decimal(str(m))) + Decimal(str(rad)) <= M * Decimal("1.000000000001") for m, rad in zip(mids, radii)),
        "at_least_one_component_sign_resolved": len(lower) == 6 and any(Decimal(str(lo)) > 0 or Decimal(str(hi)) < 0 for lo, hi in zip(lower, upper)),
        "signed_557_endpoint_box_inside_inner_domain": max_abs_endpoint < Decimal("1e-11"),
    }
    passed = all(gates.values())
    certificate = {
        "schema": "geometric-flow/signed-field-export/v0.9.22",
        "coordinate_system": p.get("v0922_signed_field_export_coordinate_system"),
        "field_interval_midpoints": mids,
        "field_interval_radii": radii,
        "field_interval_lower": lower,
        "field_interval_upper": upper,
        "endpoint_box": {
            "step_count": args.steps,
            "total_time": str(T),
            "center": endpoint_centers,
            "component_radius": endpoint_radii,
            "lower": endpoint_lower,
            "upper": endpoint_upper,
        },
        "source_hashes": {
            "v0910": V0910_SHA,
            "picard_certificate": sha(picard),
            "normal_root_certificate": sha(root),
        },
    }
    atomic(out / "signed_field_endpoint_certificate.json", certificate)
    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": "VALIDATED_REPOSITORY_NATIVE_SIGNED_FIELD_AND_557_ENDPOINT_BOX_CERTIFIED" if passed else "V0922_SIGNED_FIELD_INCONCLUSIVE_FAIL_CLOSED",
        "formal_backend": f"python-flint/Arb {flint_version}",
        "source_v0910": str(v0910_path),
        "signed_field": {
            "midpoints": mids, "radii": radii, "lower": lower, "upper": upper,
            "uniform_absolute_upper": str(M),
        },
        "signed_endpoint_box": certificate["endpoint_box"],
        "maximum_endpoint_absolute_coordinate": str(max_abs_endpoint),
        "gates": gates,
        "all_scientific_gates_pass": passed,
        "repository_native_signed_field_certified": passed,
        "signed_557_step_endpoint_box_certified": passed and args.steps == 557,
        "taylor_lohner_flowpipe_certified": False,
        "complete_child_certified": False,
        "global_flow_claimed": False,
        "certificate": str(out / "signed_field_endpoint_certificate.json"),
        "next_required_step": "use this signed endpoint box as the target for a third same-chart normal-root/frame/graph/Picard recenter audit",
        "claim_boundary": "uniform signed-field endpoint enclosure in the certified second chart; no Taylor/Lohner flowpipe, complete child, or global theorem",
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
            "scientific_status": "V0922_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
