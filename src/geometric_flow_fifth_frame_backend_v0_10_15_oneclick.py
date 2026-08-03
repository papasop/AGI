#!/usr/bin/env python3
"""Proof-producing backend harness for the fifth Geometric-Flow chart.

The harness refuses midpoint-only/SVD-only substitutes.  A native adapter must
evaluate the complete fourth normal graph and nonlinear fourth-to-fifth chart
map with Arb intervals.  A passing certificate is accepted by v0.10.14.1.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import math
import re
import sys
from pathlib import Path

TITLE = "GEOMETRIC-FLOW REPOSITORY-NATIVE FIFTH FRAME / NONLINEAR TRANSITION BACKEND"
VERSION = "0.10.15"
SCHEMA = "geometric-flow/fifth-frame-transition-arb-certificate/v0.10.14.1"
REQUIRED = (
    "lift_fourth_correlated_set_to_phase_box",
    "solve_fifth_parametric_normal_root",
    "construct_fifth_arb_svd_frame",
    "map_phase_box_to_fifth_intrinsic_box",
)
NUM = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


def clean(argv):
    out, ignored, i = [], [], 0
    while i < len(argv):
        if argv[i] == "-f" and i + 1 < len(argv):
            ignored += argv[i:i + 2]; i += 2
        else:
            out.append(argv[i]); i += 1
    if ignored:
        print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    return out


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def locate(explicit, candidates, label):
    for p in ([Path(explicit)] if explicit else []) + [Path(x) for x in candidates]:
        if p.is_file(): return p.resolve()
    raise FileNotFoundError(label)


def scalar_bounds(value):
    if isinstance(value, (int, float)):
        x = float(value); return x, x
    text = str(value).strip()
    if text == "0": return 0.0, 0.0
    vals = [float(x) for x in NUM.findall(text)]
    if not vals: raise ValueError(f"invalid Arb scalar {value!r}")
    if text.startswith("[+/-"):
        return -abs(vals[0]), abs(vals[0])
    mid = vals[0]
    rad = abs(vals[1]) if "+/-" in text and len(vals) > 1 else 0.0
    return mid - rad, mid + rad


def ordered_box(box, n):
    try:
        lo, hi = box["lower"], box["upper"]
        return len(lo) == len(hi) == n and all(scalar_bounds(a)[0] <= scalar_bounds(b)[1]
                                               for a, b in zip(lo, hi))
    except Exception:
        return False


def box_abs_upper(box):
    return max(max(abs(scalar_bounds(a)[0]), abs(scalar_bounds(b)[1]))
               for a, b in zip(box["lower"], box["upper"]))


def finite_matrix(value, rows, cols):
    try:
        return len(value) == rows and all(len(r) == cols and
               all(math.isfinite(x) for v in r for x in scalar_bounds(v)) for r in value)
    except Exception:
        return False


def import_module(path):
    spec = importlib.util.spec_from_file_location("gf_fifth_native", path)
    if spec is None or spec.loader is None: raise ImportError(path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def emit_template(path, frozen_hash):
    body = f'''"""Fill these callbacks with repository-native python-flint/Arb operations.

Frozen terminal semantic hash: {frozen_hash}
No callback may use sampling, finite differences, or midpoint-only transitions.
"""
ADAPTER_METADATA = {{
    "formal_backend": "python-flint/Arb",
    "precision_bits": 192,
    "frozen_terminal_set_sha256": "{frozen_hash}",
    "nonlinear_transition_with_formal_remainder": False,
    "no_finite_difference": True,
}}

def lift_fourth_correlated_set_to_phase_box(terminal_set, precision_bits):
    """Return a 14-dimensional {{lower, upper}} Arb phase box."""
    raise NotImplementedError("bind the certified fourth normal graph")

def solve_fifth_parametric_normal_root(phase_box, precision_bits):
    """Return normal_root_box plus strict Krawczyk inclusion metadata."""
    raise NotImplementedError("bind the repository-native normal equation")

def construct_fifth_arb_svd_frame(normal_root_result, precision_bits):
    """Return tangent_frame_midpoint (14x6), defects, and singular bound."""
    raise NotImplementedError("construct the fifth-centre Arb SVD frame")

def map_phase_box_to_fifth_intrinsic_box(phase_box, root_result, frame_result, precision_bits):
    """Return complete nonlinear image_box and formal transition remainder."""
    raise NotImplementedError("evaluate the nonlinear chart transition")
'''
    path.write_text(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v01014-summary")
    ap.add_argument("--native-adapter")
    ap.add_argument("--precision-bits", type=int, default=192)
    ap.add_argument("--outdir", default="geometric_flow_fifth_backend_v0_10_15_results")
    args, _ = ap.parse_known_args(clean(sys.argv[1:]))
    out = Path(args.outdir).resolve(); out.mkdir(parents=True, exist_ok=True)
    summary_path = locate(args.v01014_summary, [
        "geometric_flow_fifth_frame_v0_10_14_results/run_summary.json",
        "/content/geometric_flow_fifth_frame_v0_10_14_results/run_summary.json",
    ], "v0.10.14.1 summary missing")
    summary = json.loads(summary_path.read_text())
    terminal_path = Path(summary["frozen_terminal_set"])
    if not terminal_path.is_file():
        raise FileNotFoundError(f"frozen terminal set missing: {terminal_path}")
    terminal_hash = sha256(terminal_path)
    if terminal_hash != summary.get("frozen_terminal_set_sha256"):
        raise RuntimeError("v0.10.14.1 frozen terminal-set hash mismatch")
    terminal = json.loads(terminal_path.read_text())["terminal_set"]

    template = out / "geometric_flow_fifth_native_adapter_v0_10_15.py"
    emit_template(template, terminal_hash)
    adapter_path = Path(args.native_adapter).resolve() if args.native_adapter else None
    adapter = None; errors = []
    if adapter_path:
        try: adapter = import_module(adapter_path)
        except Exception as exc: errors.append(f"adapter import failed: {type(exc).__name__}: {exc}")

    callable_gates = {name: bool(adapter and callable(getattr(adapter, name, None))) for name in REQUIRED}
    metadata = getattr(adapter, "ADAPTER_METADATA", {}) if adapter else {}
    static_gates = {
        "v01014_base_gates_pass": all(summary.get("base_gates", {}).values()),
        "terminal_correlated_set_certified": bool(summary.get("terminal_correlated_set_certified")),
        "terminal_hash_exact": terminal_hash == summary.get("frozen_terminal_set_sha256"),
        "formal_precision_at_least_192_bits": args.precision_bits >= 192,
        "all_native_callbacks_callable": all(callable_gates.values()),
        "adapter_bound_to_terminal_hash": metadata.get("frozen_terminal_set_sha256") == terminal_hash,
        "adapter_declares_no_finite_difference": metadata.get("no_finite_difference") is True,
    }

    phase = root = frame = image = None
    if all(static_gates.values()):
        try:
            print("[fifth] lifting complete correlated set through fourth normal graph")
            phase = adapter.lift_fourth_correlated_set_to_phase_box(terminal, args.precision_bits)
            print("[fifth] solving parametric fifth normal root")
            root = adapter.solve_fifth_parametric_normal_root(phase, args.precision_bits)
            print("[fifth] constructing fifth Arb SVD frame")
            frame = adapter.construct_fifth_arb_svd_frame(root, args.precision_bits)
            print("[fifth] evaluating complete nonlinear transition image")
            image = adapter.map_phase_box_to_fifth_intrinsic_box(
                phase, root, frame, args.precision_bits)
        except Exception as exc:
            errors.append(f"native backend failed: {type(exc).__name__}: {exc}")

    image_box = (image or {}).get("image_box")
    start_radius = (image or {}).get("fifth_start_domain_radius", float("nan"))
    try:
        image_inside = ordered_box(image_box, 6) and box_abs_upper(image_box) < float(start_radius)
        singular = float((frame or {}).get("minimum_singular_value_lower", 0.0))
        orth = float((frame or {}).get("orthogonality_defect_upper", math.inf))
    except Exception:
        image_inside, singular, orth = False, 0.0, math.inf
    backend_gates = {
        "phase_box_14D_complete": ordered_box((phase or {}).get("phase_box", phase), 14),
        "unique_fifth_parametric_normal_root": bool((root or {}).get("unique_parametric_root")),
        "normal_krawczyk_strict_inclusion": bool((root or {}).get("krawczyk_strict_inclusion")),
        "fifth_response_full_row_rank": singular > 0,
        "fifth_frame_orthogonal_complete": finite_matrix(
            (frame or {}).get("tangent_frame_midpoint"), 14, 6) and orth < 1e-10,
        "nonlinear_transition_with_formal_remainder": bool(
            (image or {}).get("nonlinear_transition_with_formal_remainder")) and
            metadata.get("nonlinear_transition_with_formal_remainder") is True,
        "terminal_image_strictly_inside_fifth_start_domain": image_inside,
        "no_finite_difference": metadata.get("no_finite_difference") is True,
    }
    passed = all(static_gates.values()) and all(backend_gates.values()) and not errors

    certificate = None
    if passed:
        certificate = {
            "schema": SCHEMA, "precision_bits": args.precision_bits,
            "formal_backend": metadata.get("formal_backend", "python-flint/Arb"),
            "frozen_terminal_set_sha256": terminal_hash,
            "fifth_normal_root_box": root.get("normal_root_box"),
            "fifth_tangent_frame_midpoint": frame.get("tangent_frame_midpoint"),
            "fifth_frame_orthogonality_defect_upper": orth,
            "fifth_response_minimum_singular_value_lower": singular,
            "nonlinear_transition_image_box": image_box,
            "fifth_start_domain_radius": start_radius,
            "transition_remainder": image.get("transition_remainder"),
            "backend_gates": backend_gates,
        }
        cert_path = out / "fifth_frame_transition_arb_certificate.json"
        cert_path.write_text(json.dumps(certificate, indent=2) + "\n")
    else:
        cert_path = None

    report = {
        "title": TITLE, "version": VERSION,
        "scientific_status": ("VALIDATED_ACTUAL_FIFTH_SVD_FRAME_AND_NONLINEAR_TRANSITION_CERTIFICATE_GENERATED"
                              if passed else "FIFTH_NATIVE_ADAPTER_IMPLEMENTATION_OPEN_FAIL_CLOSED"),
        "frozen_terminal_set_sha256": terminal_hash,
        "native_adapter": str(adapter_path) if adapter_path else None,
        "generated_adapter_template": str(template),
        "required_callbacks": callable_gates,
        "static_gates": static_gates, "backend_gates": backend_gates,
        "errors": errors, "certificate": str(cert_path) if cert_path else None,
        "all_scientific_gates_pass": passed,
        "fifth_frame_certificate_generated": passed,
        "fifth_local_picard_chart_certified": False,
        "complete_child_certified": False, "global_flow_claimed": False,
        "next_command": (f"python geometric_flow_fifth_frame_inclusion_v0_10_14_oneclick.py --backend-certificate {cert_path}"
                         if passed else None),
        "next_required_step": ("feed the generated certificate to v0.10.14.1"
                               if passed else "replace the generated adapter template callbacks with repository-native Arb operations and rerun using --native-adapter"),
        "claim_boundary": "proof-producing fifth root/frame/transition backend only; no fifth Picard chart, complete child, or global flow",
    }
    (out / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print("=" * 112); print(f"{TITLE} v{VERSION}"); print("=" * 112)
    print(json.dumps(report, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "IPython" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
