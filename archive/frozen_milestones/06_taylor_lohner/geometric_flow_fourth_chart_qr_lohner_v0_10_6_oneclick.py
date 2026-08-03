#!/usr/bin/env python3
"""Ten-step fourth-chart QR/Lohner support-flowpipe audit.

The proof-producing part uses Arb support recurrences driven by the v0.10.5
same-expression X/DX enclosure.  QR records preserve the midpoint shape but
are not promoted to directional tightening when the certified DX midpoint is
zero.  This distinction prevents a valid support tube from being mislabeled
as a fifth-frame inclusion theorem.
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, subprocess, sys, urllib.request
from pathlib import Path

TITLE = "GEOMETRIC-FLOW FOURTH-CHART TEN-STEP QR/LOHNER SUPPORT FLOWPIPE"
VERSION = "0.10.6"
FROZEN_REPOSITORY_COMMIT = "fcabf3622f22582d960b31e94c41f896855cc56c"
V0104_SHA = "20111f4b1f5e53af38b3439608ab472a8fb7c1ee6a79aa403039e031ede7975e"
V0105_SHA = "88d3440d25d1404c536ef71bd3d5606ba222ce7f895408a0e4fa128ccc68ce19"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def clean(argv):
    out, ignored, i = [], [], 0
    while i < len(argv):
        if argv[i] == "-f" and i + 1 < len(argv): ignored += argv[i:i+2]; i += 2
        else: out.append(argv[i]); i += 1
    if ignored: print(f"[notice] ignored notebook/kernel arguments: {ignored}")
    return out


def locate(explicit, candidates, message):
    for p in ([Path(explicit)] if explicit else []) + [Path(x) for x in candidates]:
        if p.is_file(): return p.resolve()
    raise FileNotFoundError(message)


def ensure_deps():
    try:
        import numpy as np
        from flint import arb, acb, ctx
    except ModuleNotFoundError:
        print("[setup] installing numpy and frozen python-flint==0.8.0")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "numpy", "python-flint==0.8.0"])
        import numpy as np
        from flint import arb, acb, ctx
    return np, arb, acb, ctx


def upper(x): return float(x.upper())
def abs_upper(x): return float(abs(x).upper())


def parse_acb(text, arb, acb):
    """Parse python-flint's human-readable `real +/- imag j` enclosure."""
    s = str(text).strip()
    if not s.endswith("j"):
        return acb(arb(s))
    body = s[:-1]
    if " + " in body:
        real, imag = body.rsplit(" + ", 1); sign = 1
    elif " - " in body:
        real, imag = body.rsplit(" - ", 1); sign = -1
    else:
        raise ValueError(f"unrecognized acb enclosure: {s}")
    return acb(arb(real), sign * arb(imag))


def frozen_download(repository_path, destination, expected_sha):
    url = ("https://raw.githubusercontent.com/papasop/Geometric-Flow/" +
           FROZEN_REPOSITORY_COMMIT + "/" + repository_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"[repository] downloading frozen {repository_path}")
    with urllib.request.urlopen(url, timeout=120) as response:
        destination.write_bytes(response.read())
    if sha(destination) != expected_sha:
        raise RuntimeError(f"frozen source hash mismatch for {repository_path}: {sha(destination)}")


def corrected_xdx_if_required(xdx_path, picard_path, frame_path, six_path, outdir):
    current = json.loads(xdx_path.read_text())
    if current.get("picard_certificate_sha256") == sha(picard_path):
        return xdx_path, False
    print("[dependency] v0.10.5 is bound to the smaller preflight domain; rebuilding on the certified 1.5e-11 fourth domain")
    embedded = outdir / "embedded_frozen_sources"
    v104_script = embedded / "geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py"
    v105_script = embedded / "geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py"
    frozen_download("archive/frozen_milestones/06_taylor_lohner/geometric_flow_parametric_normal_graph_jet_v0_10_4_oneclick.py", v104_script, V0104_SHA)
    frozen_download("archive/frozen_milestones/06_taylor_lohner/geometric_flow_same_expression_field_dx_v0_10_5_oneclick.py", v105_script, V0105_SHA)
    corrected104 = outdir / "corrected_v0104_dependency"
    corrected105 = outdir / "corrected_v0105_dependency"
    env = dict(os.environ)
    subprocess.check_call([sys.executable, str(v104_script), "--six-jet", str(six_path),
                           "--frame-certificate", str(frame_path), "--picard-certificate", str(picard_path),
                           "--outdir", str(corrected104)], env=env)
    subprocess.check_call([sys.executable, str(v105_script), "--six-jet", str(six_path),
                           "--v0104-certificate", str(corrected104 / "parametric_normal_graph_jet_arb_certificate.json"),
                           "--frame-certificate", str(frame_path), "--picard-certificate", str(picard_path),
                           "--outdir", str(corrected105)], env=env)
    result = corrected105 / "same_expression_X_DX_arb_certificate.json"
    if not result.is_file(): raise RuntimeError("corrected v0.10.5 certificate was not emitted")
    return result.resolve(), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v0105-certificate"); ap.add_argument("--six-jet"); ap.add_argument("--frame-certificate")
    ap.add_argument("--picard-certificate"); ap.add_argument("--steps", type=int, default=10)
    ap.add_argument("--outdir", default="geometric_flow_qr_lohner_v0_10_6_results")
    args, _ = ap.parse_known_args(clean(sys.argv[1:]))

    xdx_path = locate(args.v0105_certificate, [
        "geometric_flow_same_expression_dx_v0_10_5_results/same_expression_X_DX_arb_certificate.json",
        "/content/geometric_flow_same_expression_dx_v0_10_5_results/same_expression_X_DX_arb_certificate.json"],
        "Run v0.10.5 first or pass --v0105-certificate")
    six_path = locate(args.six_jet, [
        "geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py",
        "/content/geometric_flow_six_variable_jet_v0_10_3_results/geometric_flow_native_six_jet_primitives_v0_10_3.py"],
        "Run v0.10.3 first or pass --six-jet")
    frame_path = locate(args.frame_certificate, [
        "geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json",
        "/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/v0929_formal_base/fourth_frame_arb_certificate.json"],
        "Fourth-frame certificate not found")
    picard_path = locate(args.picard_certificate, [
        "geometric_flow_native_source_v0_10_1_results/v0930_reproduction/formal_fourth_picard_backend/formal_base/intrinsic_picard_microstep_certificate.json",
        "/content/geometric_flow_native_source_v0_10_1_results/v0930_reproduction/formal_fourth_picard_backend/formal_base/intrinsic_picard_microstep_certificate.json"],
        "Fourth Picard certificate not found")

    np, arb, acb, ctx = ensure_deps(); ctx.prec = 192
    out = Path(args.outdir).resolve(); out.mkdir(parents=True, exist_ok=True)
    xdx_path, dependencies_rebuilt = corrected_xdx_if_required(xdx_path, picard_path, frame_path, six_path, out)
    xdx, frame, picard = json.loads(xdx_path.read_text()), json.loads(frame_path.read_text()), json.loads(picard_path.read_text())
    if not xdx.get("all_certificate_gates_pass") or xdx.get("schema") != "geometric-flow/same-expression-intrinsic-X-DX/v0.10.5":
        raise RuntimeError("v0.10.5 X/DX certificate is absent or failed")
    if args.steps != 10: raise ValueError("v0.10.6 freezes exactly ten prospective steps")

    X = [parse_acb(s, arb, acb) for s in xdx["X"]]
    DX = [[parse_acb(s, arb, acb) for s in row] for row in xdx["DX"]]
    if len(X) != 6 or len(DX) != 6 or any(len(row) != 6 for row in DX):
        raise RuntimeError("v0.10.5 field/Jacobian shape mismatch")
    h = arb(str(picard["certified_time_step"]))
    inner = arb(str(picard["inner_real_picard_radius"]))
    outer = arb(str(picard["outer_complex_tangent_radius"]))
    initial = frame["transformed_endpoint_box"]
    initial_radii = []
    initial_centers = []
    for lo, hi in zip(initial["lower"], initial["upper"]):
        l, u = arb(lo), arb(hi)
        initial_centers.append((l + u) / 2)
        initial_radii.append((u - l) / 2)

    x_mid = [arb(str(z.real.mid())) for z in X]
    x_rad = [arb(str(z.real.rad())) for z in X]
    x_abs = [abs(z.real) for z in X]
    dx_mid = [[arb(str(DX[i][j].real.mid())) for j in range(6)] for i in range(6)]
    dx_mid_zero = all(value == arb(0) for row in dx_mid for value in row)
    if not dx_mid_zero:
        raise ArithmeticError("v0.10.6 support protocol requires the frozen DX midpoint matrix to be zero")
    row_bounds = [sum((abs(DX[i][j].real) for j in range(6)), arb(0)) for i in range(6)]
    L = max(row_bounds); M = max(x_abs)
    growth = (L * h).exp()
    local_tail = h * h * L * M * growth / 2

    # Exact initial axis box as a zonotope; QR is recorded without replacing
    # the Arb support recurrence used for proof.
    center = np.array([float(c.mid()) for c in initial_centers], dtype=float)
    shape = np.diag([float(r.upper()) for r in initial_radii])
    remainder = [arb(0) for _ in range(6)]
    support = initial_radii[:]
    records = []
    all_inner, all_outer = True, True
    for step in range(1, 11):
        center = center + float(h.mid()) * np.array([float(v.mid()) for v in x_mid])
        # Midpoint variational matrix is I because the certified DX midpoint is zero.
        q, r = np.linalg.qr(shape)
        shape = q @ r
        for i in range(6):
            remainder[i] = remainder[i] + h * x_rad[i] + local_tail
            support[i] = support[i] + h * x_abs[i] + local_tail
        coordinate_upper = [abs(arb(str(center[i]))) + sum((arb(str(abs(shape[i, j]))) for j in range(6)), arb(0)) + remainder[i] for i in range(6)]
        # The independent Arb recurrence dominates any floating QR bookkeeping.
        proof_upper = [max(coordinate_upper[i], support[i]) for i in range(6)]
        inside_inner = all(value < inner for value in proof_upper)
        inside_outer = all(value < outer for value in proof_upper)
        all_inner &= inside_inner; all_outer &= inside_outer
        records.append({
            "step": step, "time_upper": upper(h * step),
            "center": [float(v) for v in center],
            "shape_matrix": shape.tolist(),
            "qr_Q": q.tolist(), "qr_R": r.tolist(),
            "interval_remainder_upper": [upper(v) for v in remainder],
            "formal_coordinate_support_upper": [upper(v) for v in proof_upper],
            "strictly_inside_real_inner_domain": inside_inner,
            "strictly_inside_complex_outer_domain": inside_outer,
        })

    final_support = [arb(str(v)) for v in records[-1]["formal_coordinate_support_upper"]]
    maximum_final_support = max(final_support)
    gates = {
        "v0105_same_expression_X_DX_certificate": True,
        "v0105_bound_to_selected_full_fourth_picard_domain": xdx.get("picard_certificate_sha256") == sha(picard_path),
        "formal_precision_at_least_192_bits": ctx.prec >= 192,
        "frozen_ten_step_protocol": args.steps == 10,
        "positive_time_step": h > 0,
        "initial_transformed_endpoint_box_present": len(initial_radii) == 6,
        "six_component_field_and_6x6_DX": len(X) == 6,
        "DX_induced_infinity_bound_finite": math.isfinite(upper(L)),
        "DX_midpoint_zero_handled_without_fake_directional_gain": dx_mid_zero,
        "complete_QR_shape_history_emitted": len(records) == 10,
        "all_ten_support_tubes_inside_real_domain": all_inner,
        "all_ten_support_tubes_inside_complex_domain": all_outer,
        "local_Taylor_remainder_finite": math.isfinite(upper(local_tail)),
    }
    passed = all(gates.values())
    history = out / "qr_lohner_step_records.json"
    history.write_text(json.dumps(records, indent=2) + "\n")
    certificate = {
        "schema": "geometric-flow/fourth-chart-qr-lohner-support/v0.10.6",
        "formal_backend": "python-flint/Arb", "precision_bits": ctx.prec,
        "v0105_certificate_sha256": sha(xdx_path), "frame_certificate_sha256": sha(frame_path),
        "picard_certificate_sha256": sha(picard_path), "steps": 10,
        "dependencies_rebuilt_on_full_fourth_domain": dependencies_rebuilt,
        "time_step": str(h), "total_time": str(h * 10),
        "induced_infinity_DX_upper": upper(L), "field_absolute_upper": upper(M),
        "per_step_growth_upper": upper(growth), "per_step_local_tail_upper": upper(local_tail),
        "initial_support_upper": [upper(v) for v in initial_radii],
        "final_support_upper": [upper(v) for v in final_support],
        "maximum_final_support_upper": upper(maximum_final_support),
        "real_inner_domain_radius": upper(inner), "complex_outer_domain_radius": upper(outer),
        "directional_qr_tightening_certified": False,
        "reason_directional_false": "the full-box DX midpoint matrix is zero; QR history is retained but no directional gain is claimed",
        "all_certificate_gates_pass": passed,
    }
    cert = out / "fourth_chart_qr_lohner_support_certificate.json"
    cert.write_text(json.dumps(certificate, indent=2) + "\n")
    report = {
        "title": TITLE, "version": VERSION,
        "scientific_status": "VALIDATED_TEN_STEP_FOURTH_CHART_LOHNER_SUPPORT_FLOWPIPE_CERTIFIED" if passed else "V0106_FAILED_CLOSED",
        "certificate": str(cert), "step_records": str(history),
        "metrics": {k: certificate[k] for k in ["steps", "time_step", "total_time", "induced_infinity_DX_upper", "field_absolute_upper", "per_step_growth_upper", "per_step_local_tail_upper", "maximum_final_support_upper", "real_inner_domain_radius", "complex_outer_domain_radius", "dependencies_rebuilt_on_full_fourth_domain"]},
        "gates": gates, "qr_lohner_support_flowpipe_certified": passed,
        "directional_qr_tightening_certified": False,
        "fifth_recenter_target_box_certified": False, "fifth_frame_certified": False,
        "complete_child_certified": False, "global_flow_claimed": False,
        "all_scientific_gates_pass": False,
        "next_required_step": "evaluate X/DX on step-local subboxes to obtain nonzero directional midpoint Jacobians, then map the correlated terminal set into the actual fifth SVD frame",
        "claim_boundary": "ten-step fourth-chart Arb support flowpipe plus QR shape history only; no directional QR gain, fifth recenter/frame, complete child, or global flow",
    }
    (out / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print("=" * 112); print(f"{TITLE} v{VERSION}"); print("=" * 112); print(json.dumps(report, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "IPython" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)
