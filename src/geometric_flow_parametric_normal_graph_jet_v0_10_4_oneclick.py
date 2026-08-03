#!/usr/bin/env python3
"""Certify the fourth-chart parametric normal-graph derivative with Arb.

This consumes the v0.10.3 native six-variable Jet module and the frozen
fourth-frame/Picard certificates.  It evaluates the *same* repository-native
response Jacobian on the complete (a,b) graph box and certifies

    Dpsi(a) = -(d_b F)^{-1} d_a F,
    F(a,b) = R(theta_c + T a + N b) - R(theta_c).

It does not construct X or DX and therefore intentionally leaves the global
scientific gate false.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

TITLE = "GEOMETRIC-FLOW PARAMETRIC NORMAL-GRAPH ARB JET"
VERSION = "0.10.4"
EXPECTED_SCALAR_SHA = "16e153347068b9f412fc01e2bb9eadf1aa4091b8dc4e3a62d6c7e691d960e417"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def clean_kernel_args(argv):
    out, ignored, i = [], [], 0
    while i < len(argv):
        if argv[i] == "-f" and i + 1 < len(argv):
            ignored += argv[i:i + 2]
            i += 2
        else:
            out.append(argv[i])
            i += 1
    if ignored:
        print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    return out


def first_file(explicit, candidates, message):
    paths = ([Path(explicit)] if explicit else []) + [Path(p) for p in candidates]
    for path in paths:
        if path.is_file():
            return path.resolve()
    raise FileNotFoundError(message)


def ensure_flint():
    try:
        from flint import arb, arb_mat, acb, ctx
        return arb, arb_mat, acb, ctx
    except ModuleNotFoundError:
        print("[setup] installing frozen formal backend python-flint==0.8.0")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "python-flint==0.8.0"])
        from flint import arb, arb_mat, acb, ctx
        return arb, arb_mat, acb, ctx


def arb_abs_upper(x):
    return float(abs(x).upper())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--six-jet")
    parser.add_argument("--frame-certificate")
    parser.add_argument("--picard-certificate")
    parser.add_argument("--outdir", default="geometric_flow_parametric_graph_jet_v0_10_4_results")
    args, _ = parser.parse_known_args(clean_kernel_args(sys.argv[1:]))

    six_jet = first_file(args.six_jet, [
        "geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py",
        "/content/geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py",
    ], "Run v0.10.3 first or pass --six-jet PATH")
    frame_path = first_file(args.frame_certificate, [
        "geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json",
        "/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json",
    ], "Fourth-frame certificate not found")
    picard_path = first_file(args.picard_certificate, [
        "geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/formal_fourth_frame_backend/formal_base/intrinsic_picard_microstep_certificate.json",
        "/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/formal_fourth_frame_backend/formal_base/intrinsic_picard_microstep_certificate.json",
    ], "Fourth Picard certificate not found")

    arb, arb_mat, acb, ctx = ensure_flint()
    ctx.prec = 192
    frame = json.loads(frame_path.read_text())
    picard = json.loads(picard_path.read_text())
    T = frame["tangent_frame_midpoint"]
    N = frame["normal_frame_midpoint"]
    phase_box = frame["corrected_phase_center_box"]
    if len(T) != 14 or any(len(row) != 6 for row in T):
        raise RuntimeError("tangent frame is not 14x6")
    if len(N) != 14 or any(len(row) != 8 for row in N):
        raise RuntimeError("normal frame is not 14x8")

    spec = importlib.util.spec_from_file_location("gf_native_six_jet_v0103", six_jet)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    metadata = module.SIX_JET_METADATA
    if metadata.get("source_scalar_sha256") != EXPECTED_SCALAR_SHA:
        raise RuntimeError("v0.10.3 module is not bound to the frozen v0.10.2 scalar primitives")

    a_radius_text = str(picard["inner_real_picard_radius"])
    b_radius_text = str(picard["refined_normal_graph_radius"])
    a_radius = arb(a_radius_text)
    b_radius = arb(b_radius_text)
    a_box = [module.CJet.variable(arb(f"0 +/- {a_radius_text}"), j) for j in range(6)]
    b_box = [arb(f"0 +/- {b_radius_text}") for _ in range(8)]
    theta = []
    for i in range(14):
        center = (arb(phase_box["lower"][i]) + arb(phase_box["upper"][i])) / 2
        value = module.CJet(acb(center))
        for j in range(6):
            value = value + arb(T[i][j]) * a_box[j]
        for k in range(8):
            value = value + arb(N[i][k]) * b_box[k]
        theta.append(value)

    response_jacobian, _gradient = module.response_jacobian_and_gradient(theta, True)
    A = [[arb(0) for _ in range(8)] for _ in range(8)]
    B = [[arb(0) for _ in range(6)] for _ in range(8)]
    maximum_imaginary_radius = 0.0
    for q in range(8):
        for i in range(14):
            z = response_jacobian[q][i].v
            maximum_imaginary_radius = max(maximum_imaginary_radius, arb_abs_upper(z.imag))
            jr = z.real
            for k in range(8):
                A[q][k] += jr * arb(N[i][k])
            for j in range(6):
                B[q][j] += jr * arb(T[i][j])

    A_mat, B_mat = arb_mat(A), arb_mat(B)
    A_inv = A_mat.inv()  # Arb raises if the interval matrix cannot be certified invertible.
    Dpsi = -(A_inv * B_mat)
    inverse_product = A_mat * A_inv
    inverse_residual_row_sum = 0.0
    for i in range(8):
        row_sum = 0.0
        for j in range(8):
            row_sum += arb_abs_upper(inverse_product[i, j] - (1 if i == j else 0))
        inverse_residual_row_sum = max(inverse_residual_row_sum, row_sum)

    implicit_residual = A_mat * Dpsi + B_mat
    residual_contains_zero = all(implicit_residual[i, j].contains(0) for i in range(8) for j in range(6))
    maximum_implicit_residual = max(arb_abs_upper(implicit_residual[i, j]) for i in range(8) for j in range(6))
    maximum_Dpsi = max(arb_abs_upper(Dpsi[i, j]) for i in range(8) for j in range(6))

    gates = {
        "v0103_frozen_scalar_binding": metadata.get("source_scalar_sha256") == EXPECTED_SCALAR_SHA,
        "six_variable_same_expression_response_jet": bool(metadata.get("same_expression_response_derivative")),
        "formal_precision_at_least_192_bits": ctx.prec >= 192,
        "frame_14_by_6_and_normal_14_by_8": len(T) == 14 and len(N) == 14,
        "inherited_parametric_graph_krawczyk_strict": float(picard["complex_graph_krawczyk_utilization"]) < 1,
        "complete_real_tangent_box_used": a_radius > 0,
        "complete_refined_normal_graph_box_used": b_radius > 0,
        "normal_response_block_arb_invertible": inverse_residual_row_sum < 1,
        "implicit_derivative_residual_contains_zero": residual_contains_zero,
        "no_finite_difference": True,
    }
    passed = all(gates.values())
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    certificate = {
        "schema": "geometric-flow/parametric-normal-graph-jet/v0.10.4",
        "formal_backend": "python-flint/Arb",
        "precision_bits": ctx.prec,
        "six_jet_source_sha256": sha256(six_jet),
        "frame_certificate_sha256": sha256(frame_path),
        "picard_certificate_sha256": sha256(picard_path),
        "tangent_box_radius": str(a_radius),
        "normal_graph_box_radius": str(b_radius),
        "Dpsi_shape": [8, 6],
        "Dpsi_enclosure": [[str(Dpsi[i, j]) for j in range(6)] for i in range(8)],
        "maximum_Dpsi_absolute_upper": maximum_Dpsi,
        "inverse_residual_induced_infinity_upper": inverse_residual_row_sum,
        "maximum_implicit_derivative_residual_upper": maximum_implicit_residual,
        "implicit_derivative_identity": "(d_b F) Dpsi + d_a F contains 0 entrywise",
        "all_certificate_gates_pass": passed,
    }
    cert_path = outdir / "parametric_normal_graph_jet_arb_certificate.json"
    cert_path.write_text(json.dumps(certificate, indent=2) + "\n")
    report = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": "VALIDATED_PARAMETRIC_NORMAL_GRAPH_ARB_JET_CERTIFIED" if passed else "V0104_FAILED_CLOSED",
        "formal_backend": "python-flint/Arb 192-bit",
        "certificate": str(cert_path),
        "metrics": {
            "tangent_box_radius": str(a_radius),
            "normal_graph_box_radius": str(b_radius),
            "Dpsi_shape": [8, 6],
            "maximum_Dpsi_absolute_upper": maximum_Dpsi,
            "inverse_residual_induced_infinity_upper": inverse_residual_row_sum,
            "maximum_implicit_derivative_residual_upper": maximum_implicit_residual,
            "maximum_discarded_imaginary_enclosure_upper": maximum_imaginary_radius,
        },
        "gates": gates,
        "implicit_normal_graph_jet_ready": passed,
        "same_expression_response_derivative_ready": passed,
        "same_expression_X_ready": False,
        "same_expression_DX_ready": False,
        "qr_lohner_flowpipe_certified": False,
        "fifth_frame_certified": False,
        "global_flow_claimed": False,
        "all_scientific_gates_pass": False,
        "next_required_step": "assemble W(a), H(a), normalized X(a), and same-expression DX(a) from the certified psi/Dpsi enclosure",
        "claim_boundary": "parametric implicit normal-graph derivative over the certified fourth-chart (a,b) box only; no X/DX, QR/Lohner flowpipe, fifth frame, complete child, or global flow",
    }
    (outdir / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print("=" * 112)
    print(f"{TITLE} v{VERSION}")
    print("=" * 112)
    print(json.dumps(report, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "IPython" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
