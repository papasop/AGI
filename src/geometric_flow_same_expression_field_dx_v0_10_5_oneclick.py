#!/usr/bin/env python3
"""Build the native fourth-chart X and DX from one complex Arb Jet expression."""
from __future__ import annotations

import argparse, hashlib, importlib.util, json, math, subprocess, sys
from pathlib import Path

TITLE = "GEOMETRIC-FLOW SAME-EXPRESSION INTRINSIC FIELD / JACOBIAN"
VERSION = "0.10.5"
EXPECTED_SCALAR_SHA = "16e153347068b9f412fc01e2bb9eadf1aa4091b8dc4e3a62d6c7e691d960e417"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def clean(argv):
    out, ignored, i = [], [], 0
    while i < len(argv):
        if argv[i] == "-f" and i + 1 < len(argv):
            ignored += argv[i:i + 2]; i += 2
        else:
            out.append(argv[i]); i += 1
    if ignored: print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    return out


def locate(explicit, candidates, message):
    for p in ([Path(explicit)] if explicit else []) + [Path(x) for x in candidates]:
        if p.is_file(): return p.resolve()
    raise FileNotFoundError(message)


def ensure_flint():
    try:
        from flint import arb, arb_mat, acb, ctx
    except ModuleNotFoundError:
        print("[setup] installing frozen formal backend python-flint==0.8.0")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "python-flint==0.8.0"])
        from flint import arb, arb_mat, acb, ctx
    return arb, arb_mat, acb, ctx


def abs_upper(x): return float(abs(x).upper())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--six-jet"); ap.add_argument("--v0104-certificate")
    ap.add_argument("--frame-certificate"); ap.add_argument("--picard-certificate")
    ap.add_argument("--outdir", default="geometric_flow_same_expression_dx_v0_10_5_results")
    args, _ = ap.parse_known_args(clean(sys.argv[1:]))

    six_path = locate(args.six_jet, [
        "geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py",
        "/content/geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py"],
        "Run v0.10.3 first or pass --six-jet")
    v104_path = locate(args.v0104_certificate, [
        "geometric_flow_parametric_graph_jet_v0_10_4_results/parametric_normal_graph_jet_arb_certificate.json",
        "/content/geometric_flow_parametric_graph_jet_v0_10_4_results/parametric_normal_graph_jet_arb_certificate.json"],
        "Run v0.10.4 first or pass --v0104-certificate")
    frame_path = locate(args.frame_certificate, [
        "geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json",
        "/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json"],
        "Fourth-frame certificate not found")
    picard_path = locate(args.picard_certificate, [
        "geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/formal_fourth_frame_backend/formal_base/intrinsic_picard_microstep_certificate.json",
        "/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/formal_fourth_frame_backend/formal_base/intrinsic_picard_microstep_certificate.json"],
        "Fourth Picard certificate not found")

    arb, arb_mat, acb, ctx = ensure_flint(); ctx.prec = 192
    frame = json.loads(frame_path.read_text()); picard = json.loads(picard_path.read_text())
    v104 = json.loads(v104_path.read_text())
    if not v104.get("all_certificate_gates_pass"):
        raise RuntimeError("v0.10.4 normal-graph Jet certificate did not pass")
    T, N = frame["tangent_frame_midpoint"], frame["normal_frame_midpoint"]
    lo, hi = frame["corrected_phase_center_box"]["lower"], frame["corrected_phase_center_box"]["upper"]
    if len(T) != 14 or any(len(x) != 6 for x in T) or len(N) != 14 or any(len(x) != 8 for x in N):
        raise RuntimeError("fourth frame shape mismatch")
    spec = importlib.util.spec_from_file_location("gf6_v0105", six_path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    if m.SIX_JET_METADATA.get("source_scalar_sha256") != EXPECTED_SCALAR_SHA:
        raise RuntimeError("six-Jet source is not bound to frozen native scalar primitives")

    ar_text = str(picard["inner_real_picard_radius"])
    br_text = str(picard["refined_normal_graph_radius"])
    a_ball = arb(f"0 +/- {ar_text}"); b_ball = arb(f"0 +/- {br_text}")

    # First interval solve: Dpsi value enclosure over the full (a,b) box.
    phase_partial = []
    for i in range(14):
        x = m.CJet(acb((arb(lo[i]) + arb(hi[i])) / 2))
        for j in range(6): x += arb(T[i][j]) * m.CJet.variable(a_ball, j)
        for k in range(8): x += arb(N[i][k]) * b_ball
        phase_partial.append(x)
    J0, _ = m.response_jacobian_and_gradient(phase_partial, True)
    A = [[arb(0) for _ in range(8)] for _ in range(8)]
    B = [[arb(0) for _ in range(6)] for _ in range(8)]
    for q in range(8):
        for i in range(14):
            jr = J0[q][i].v.real
            for k in range(8): A[q][k] += jr * arb(N[i][k])
            for j in range(6): B[q][j] += jr * arb(T[i][j])
    D0 = -(arb_mat(A).inv() * arb_mat(B))

    # Re-evaluate the same native expression with total graph tangent W=T+N*Dpsi.
    phase_total = []
    for i in range(14):
        value = acb((arb(lo[i]) + arb(hi[i])) / 2)
        for j in range(6): value += acb(arb(T[i][j]) * a_ball)
        for k in range(8): value += acb(arb(N[i][k]) * b_ball)
        derivatives = []
        for j in range(6):
            wij = arb(T[i][j])
            for k in range(8): wij += arb(N[i][k]) * D0[k, j]
            derivatives.append(acb(wij))
        phase_total.append(m.CJet(value, derivatives))
    J, gradient = m.response_jacobian_and_gradient(phase_total, True)

    def transpose(X): return [list(row) for row in zip(*X)]
    def matmul(X, Y):
        return [[sum((X[i][k] * Y[k][j] for k in range(len(Y))), m.CJet(0))
                 for j in range(len(Y[0]))] for i in range(len(X))]
    def solve(M, rhs):
        n, q = len(M), len(rhs[0])
        aug = [[m.CJet(M[i][j]) for j in range(n)] + [m.CJet(rhs[i][j]) for j in range(q)] for i in range(n)]
        for col in range(n):
            pivot = max(range(col, n), key=lambda r: abs(complex(aug[r][col].v.mid())))
            aug[col], aug[pivot] = aug[pivot], aug[col]
            if aug[col][col].contains(0): raise ArithmeticError(f"Jet interval pivot {col} contains zero")
            piv = aug[col][col]; aug[col] = [x / piv for x in aug[col]]
            for row in range(n):
                if row == col: continue
                factor = aug[row][col]
                aug[row] = [aug[row][c] - factor * aug[col][c] for c in range(n + q)]
        return [row[n:] for row in aug]

    Ajet = [[m.CJet(0) for _ in range(8)] for _ in range(8)]
    Bjet = [[m.CJet(0) for _ in range(6)] for _ in range(8)]
    for q in range(8):
        for i in range(14):
            for k in range(8): Ajet[q][k] += J[q][i] * arb(N[i][k])
            for j in range(6): Bjet[q][j] += J[q][i] * arb(T[i][j])
    Dpsi = solve(Ajet, [[-x for x in row] for row in Bjet])
    W = [[m.CJet(arb(T[i][j])) + sum((m.CJet(arb(N[i][k])) * Dpsi[k][j] for k in range(8)), m.CJet(0))
          for j in range(6)] for i in range(14)]
    H = matmul(transpose(W), W)
    identity = [[m.CJet(1 if i == j else 0) for j in range(6)] for i in range(6)]
    Hinv = solve(H, identity)
    Hres = matmul(H, Hinv)
    pullback_gradient = [[sum((W[i][j] * gradient[i] for i in range(14)), m.CJet(0))] for j in range(6)]
    metric_gradient = solve(H, pullback_gradient)
    descent_square = sum((pullback_gradient[i][0] * metric_gradient[i][0] for i in range(6)), m.CJet(0))
    if not descent_square.v.real > arb(0) or descent_square.v.contains(0):
        raise ArithmeticError("normalization square is not separated from zero")
    descent_norm = descent_square.sqrt()
    X = [-metric_gradient[i][0] / descent_norm for i in range(6)]
    DX = [[X[i].d[j] for j in range(6)] for i in range(6)]

    graph_residual = matmul(J, W)
    implicit_residual = [[sum((Ajet[i][k] * Dpsi[k][j] for k in range(8)), m.CJet(0)) + Bjet[i][j]
                          for j in range(6)] for i in range(8)]
    graph_zero = all(z.v.contains(0) for row in graph_residual for z in row)
    implicit_zero = all(z.v.contains(0) for row in implicit_residual for z in row)
    metric_identity = all((Hres[i][j].v - (1 if i == j else 0)).contains(0) for i in range(6) for j in range(6))
    dx_finite = all(math.isfinite(abs_upper(z)) for row in DX for z in row)
    dx_nonzero_entry_certified = any(not z.contains(0) for row in DX for z in row)
    imaginary_contains_zero = all(x.v.imag.contains(0) for x in X)
    signed_lo = picard.get("v0922_signed_intrinsic_field_component_lower", [])
    signed_hi = picard.get("v0922_signed_intrinsic_field_component_upper", [])
    signed_overlap = len(signed_lo) == 6 and all(not (X[i].v.real.upper() < arb(str(signed_lo[i])) or
                                                       X[i].v.real.lower() > arb(str(signed_hi[i]))) for i in range(6))

    gates = {
        "v0104_parametric_normal_graph_jet": True,
        "native_scalar_hash_chain_exact": True,
        "complete_fourth_graph_box_used": True,
        "Dpsi_and_second_derivative_same_expression": implicit_zero,
        "graph_tangent_response_preservation": graph_zero,
        "pullback_metric_inverse_certified": metric_identity,
        "analytic_normalization_branch_separated_from_zero": True,
        "six_component_X_cjets": len(X) == 6 and all(isinstance(x, m.CJet) for x in X),
        "six_by_six_DX_from_same_expression": len(DX) == 6 and all(len(row) == 6 for row in DX),
        "DX_enclosure_finite": dx_finite,
        "field_imaginary_enclosures_contain_zero": imaginary_contains_zero,
        "field_overlaps_frozen_repository_picard_enclosure": signed_overlap,
        "no_finite_difference": True,
    }
    passed = all(gates.values())
    out = Path(args.outdir).resolve(); out.mkdir(parents=True, exist_ok=True)
    certificate = {
        "schema": "geometric-flow/same-expression-intrinsic-X-DX/v0.10.5",
        "formal_backend": "python-flint/Arb", "precision_bits": ctx.prec,
        "six_jet_sha256": sha(six_path), "v0104_certificate_sha256": sha(v104_path),
        "frame_certificate_sha256": sha(frame_path), "picard_certificate_sha256": sha(picard_path),
        "X": [str(x.v) for x in X], "DX": [[str(z) for z in row] for row in DX],
        "descent_square": str(descent_square.v),
        "maximum_X_absolute_upper": max(abs_upper(x.v) for x in X),
        "maximum_DX_absolute_upper": max(abs_upper(z) for row in DX for z in row),
        "DX_nonzero_entry_certified": dx_nonzero_entry_certified,
        "maximum_response_tangent_residual_upper": max(abs_upper(z.v) for row in graph_residual for z in row),
        "all_certificate_gates_pass": passed,
    }
    cert = out / "same_expression_X_DX_arb_certificate.json"
    cert.write_text(json.dumps(certificate, indent=2) + "\n")
    report = {
        "title": TITLE, "version": VERSION,
        "scientific_status": "VALIDATED_NATIVE_SAME_EXPRESSION_X_DX_CERTIFIED" if passed else "V0105_FAILED_CLOSED",
        "formal_backend": "python-flint/Arb 192-bit", "certificate": str(cert),
        "metrics": {k: certificate[k] for k in ["descent_square", "maximum_X_absolute_upper", "maximum_DX_absolute_upper", "maximum_response_tangent_residual_upper"]},
        "gates": gates, "implicit_normal_graph_jet_ready": passed,
        "same_expression_X_ready": passed, "same_expression_DX_ready": passed,
        "qr_lohner_flowpipe_certified": False, "fifth_frame_certified": False,
        "complete_child_certified": False, "global_flow_claimed": False,
        "all_scientific_gates_pass": False,
        "next_required_step": "feed the certified same-expression X/DX callback into the ten-step fourth-chart QR/Lohner propagator and prove the flowpipe remains inside the complex domain",
        "claim_boundary": "native same-expression fourth-chart X and DX enclosure only; no QR/Lohner flowpipe, fifth frame, complete child, or global flow",
    }
    (out / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print("=" * 112); print(f"{TITLE} v{VERSION}"); print("=" * 112); print(json.dumps(report, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "IPython" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
