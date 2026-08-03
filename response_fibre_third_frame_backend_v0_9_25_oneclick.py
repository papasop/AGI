#!/usr/bin/env python3
"""Standalone repository-native Arb third-frame certificate generator v0.9.25.

This dependency-free one-file driver embeds and reruns the frozen v0.9.23 chain, extracts its certified
third-recenter target, instruments the same repository-native v0.9.3 Arb
backend used by v0.9.8--v0.9.22, and at the new tangent midpoint:

* Krawczyk-certifies a unique eight-dimensional normal root;
* evaluates the complete 8x14 response-Jacobian interval box;
* constructs a 14x6 tangent and 14x8 normal midpoint-SVD frame;
* proves uniform row rank, frame completeness, and normal invertibility; and
* outwardly transforms the complete v0.9.23 endpoint box into the new frame.

It emits ``third_frame_arb_certificate.json`` in exactly the schema audited by
v0.9.24.  It does not construct a third fibre graph or Picard microstep.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

VERSION = "0.9.25"
TITLE = "GEOMETRIC-FLOW REPOSITORY-NATIVE ARB THIRD-FRAME CERTIFICATE GENERATOR"
REPOSITORY = "https://github.com/papasop/Geometric-Flow"
FROZEN_COMMIT = "7e4a17e7fa8de859660694fef85ecd0990a9f577"
V0923_NAME = "response_fibre_third_recenter_inclusion_v0_9_23_oneclick.py"
V0923_URL = (
    "https://raw.githubusercontent.com/papasop/Geometric-Flow/"
    f"{FROZEN_COMMIT}/{V0923_NAME}"
)
V0923_SHA256 = "c4099345b0479bc52fffbc9a5e1b376261ec1c49d64d606505d5ac50a3b6db22"
EMBEDDED_V0923_GZIP_B64 = """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"""
INSTRUMENTED_DRIVER_NAME = "instrumented_v098_signed_field_driver.py"
PRECISION_BITS = 192
TANGENT_DIMENSION = 6
RESPONSE_DIMENSION = 8
CONTROL_DIMENSION = 14
getcontext().prec = 80


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def ensure_flint() -> None:
    if importlib.util.find_spec("flint") is not None:
        return
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise RuntimeError("Install python-flint==0.8.0")
    print("[setup] installing frozen formal backend python-flint==0.8.0")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "python-flint==0.8.0"]
    )


def locate_v0923(explicit: str | None, destination: Path) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend([Path.cwd() / V0923_NAME, Path("/content") / V0923_NAME])
    script = globals().get("__file__")
    if script:
        candidates.append(Path(script).resolve().parent / V0923_NAME)
    for candidate in candidates:
        if candidate.is_file():
            digest = sha256_file(candidate)
            if digest != V0923_SHA256:
                raise RuntimeError(
                    f"v0.9.23 source hash mismatch at {candidate}: {digest}"
                )
            return candidate.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"[embedded] materializing frozen {V0923_NAME}")
    destination.write_bytes(gzip.decompress(base64.b64decode(EMBEDDED_V0923_GZIP_B64)))
    digest = sha256_file(destination)
    if digest != V0923_SHA256:
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"embedded v0.9.23 source hash mismatch: {digest}")
    return destination.resolve()


def decimal_vector(value: Any, dimension: int, label: str) -> list[Decimal]:
    if not isinstance(value, list) or len(value) != dimension:
        raise ValueError(f"{label} must have exactly {dimension} entries")
    result = [Decimal(str(x)) for x in value]
    if not all(x.is_finite() for x in result):
        raise ValueError(f"{label} contains non-finite values")
    return result


# This code is inserted inside the frozen v0.9.3 Arb proof routine, immediately
# after the v0.9.10 switch has made base_phases/tangent/normal/whitener refer to
# the certified second chart.  Every theorem gate below is computed with Arb.
THIRD_FRAME_ARB_CODE = r'''

    # v0.9.25: third-centre normal root and tangent/normal frame.
    v0925_a_c=[ap(x) for x in os.environ["V0925_A_C"].split(",")]
    v0925_a_radius=[ap(x) for x in os.environ["V0925_A_RADIUS"].split(",")]
    v0925_root_radius=ap(os.environ["V0925_ROOT_RADIUS"])
    v0925_graph_normal_radius=ap(os.environ["V0925_GRAPH_NORMAL_RADIUS"])
    v0925_new_domain_radius=ap(os.environ["V0925_NEW_DOMAIN_RADIUS"])
    if len(v0925_a_c)!=tangent_dimension or len(v0925_a_radius)!=tangent_dimension:
        raise ArithmeticError("v0.9.25 third target dimension mismatch")

    # Solve B(R(theta_base + T*a_c + N*b)-R(theta_base))=0.
    v0925_response0=v098_response(base_phases)
    v0925_theta_a=[base_phases[r]+sum(
        (tangent[r][j]*v0925_a_c[j] for j in range(tangent_dimension)),acb(0))
        for r in range(CONTROL_DIMENSION)]
    v0925_response_a=v098_response(v0925_theta_a)
    v0925_f_a=v093_matvec(whitener,[
        v0925_response_a[i]-v0925_response0[i] for i in range(RESPONSE_DIMENSION)])
    v0925_jac_a,_=response_jacobian_and_gradient(v0925_theta_a,True)
    v0925_d_a=v093_matmul(v093_matmul(whitener,v0925_jac_a),normal)
    v0925_d_a_mid=np.asarray([[midpoint_radius(v0925_d_a[r][c].real)[0]
        for c in range(RESPONSE_DIMENSION)] for r in range(RESPONSE_DIMENSION)],dtype=float)
    v0925_f_a_mid=np.asarray([midpoint_radius(x.real)[0] for x in v0925_f_a],dtype=float)
    try:
        v0925_b0_float=np.linalg.solve(v0925_d_a_mid,-v0925_f_a_mid)
    except np.linalg.LinAlgError as exc:
        raise ArithmeticError("v0.9.25 midpoint normal Newton solve failed") from exc
    v0925_b0=[acb(ap(float(x))) for x in v0925_b0_float]
    v0925_theta_b=[v0925_theta_a[r]+sum(
        (normal[r][j]*v0925_b0[j] for j in range(RESPONSE_DIMENSION)),acb(0))
        for r in range(CONTROL_DIMENSION)]
    v0925_response_b=v098_response(v0925_theta_b)
    v0925_f_b=v093_matvec(whitener,[
        v0925_response_b[i]-v0925_response0[i] for i in range(RESPONSE_DIMENSION)])
    v0925_jac_b,_=response_jacobian_and_gradient(v0925_theta_b,True)
    v0925_d_b=v093_matmul(v093_matmul(whitener,v0925_jac_b),normal)
    v0925_A=v093_midpoint_inverse(v0925_d_b,"v0.9.25 third normal derivative")
    v0925_correction=v093_matvec(v0925_A,v0925_f_b)
    v0925_image_center=[v0925_b0[i]-v0925_correction[i]
        for i in range(RESPONSE_DIMENSION)]

    # Normal-root box and Krawczyk inclusion.
    v0925_theta_box=[]
    for r in range(CONTROL_DIMENSION):
        v0925_rad=v0925_root_radius*sum(
            (upper_point(normal[r][j]) for j in range(RESPONSE_DIMENSION)),arb(0))
        v0925_theta_box.append(v0925_theta_b[r]+acb(ball(0,v0925_rad),ball(0,v0925_rad)))
    v0925_jac_box,_=response_jacobian_and_gradient(v0925_theta_box,True)
    v0925_d_box=v093_matmul(v093_matmul(whitener,v0925_jac_box),normal)
    v0925_defect=v093_defect(v0925_A,v0925_d_box)
    v0925_defect_upper=v093_inf_matrix(v0925_defect)
    v0925_margins=[];v0925_utils=[]
    for i in range(RESPONSE_DIMENSION):
        v0925_rad=upper_point(v0925_correction[i])+v0925_root_radius*sum(
            (upper_point(v0925_defect[i][j]) for j in range(RESPONSE_DIMENSION)),arb(0))
        v0925_displacement=upper_point(v0925_image_center[i]-v0925_b0[i])+v0925_rad
        v0925_margins.append(v0925_root_radius-v0925_displacement)
        v0925_utils.append(v0925_displacement/v0925_root_radius)
    v0925_root_strict=all(x>arb(0) for x in v0925_margins)
    v0925_root_invertible=bool(v0925_defect_upper<arb(1))
    v0925_unique_root=bool(v0925_root_strict and v0925_root_invertible)

    # New midpoint-SVD frame, certified uniformly over the root box.
    v0925_jc_mid=np.asarray([[midpoint_radius(v0925_jac_b[r][c].real)[0]
        for c in range(CONTROL_DIMENSION)] for r in range(RESPONSE_DIMENSION)],dtype=float)
    v0925_left,v0925_svals,v0925_rt=np.linalg.svd(v0925_jc_mid,full_matrices=True)
    v0925_nf=v0925_rt[:RESPONSE_DIMENSION,:].T
    v0925_tf=v0925_rt[RESPONSE_DIMENSION:,:].T
    v0925_bf=np.diag(1.0/v0925_svals)@v0925_left.T
    v0925_n=[[acb(ap(float(v0925_nf[r,c]))) for c in range(RESPONSE_DIMENSION)]
        for r in range(CONTROL_DIMENSION)]
    v0925_t=[[acb(ap(float(v0925_tf[r,c]))) for c in range(tangent_dimension)]
        for r in range(CONTROL_DIMENSION)]
    v0925_B=[[acb(ap(float(v0925_bf[r,c]))) for c in range(RESPONSE_DIMENSION)]
        for r in range(RESPONSE_DIMENSION)]
    v0925_Q=[v0925_n[r]+v0925_t[r] for r in range(CONTROL_DIMENSION)]
    v0925_qtq=v093_matmul(v093_transpose(v0925_Q),v0925_Q)
    v0925_orth=v093_inf_matrix([[acb(int(r==c))-v0925_qtq[r][c]
        for c in range(CONTROL_DIMENSION)] for r in range(CONTROL_DIMENSION)])
    v0925_bj=v093_matmul(v0925_B,v0925_jac_box)
    v0925_nd=v093_matmul(v0925_bj,v0925_n)
    v0925_td=v093_matmul(v0925_bj,v0925_t)
    v0925_ndef=v093_inf_matrix([[acb(int(r==c))-v0925_nd[r][c]
        for c in range(RESPONSE_DIMENSION)] for r in range(RESPONSE_DIMENSION)])
    v0925_tres=v093_inf_matrix(v0925_td)
    v0925_full_rank=bool(v0925_svals[-1]>0 and v0925_ndef<arb(1))
    v0925_orthogonal=bool(v0925_orth<ap("1e-12"))
    v0925_normal_invertible=bool(v0925_ndef<arb(1))

    # Outward phase-box image of the complete signed endpoint box.  The
    # inherited whole-graph normal radius is deliberately used instead of the
    # much smaller midpoint root radius, so this is a complete-box enclosure.
    v0925_phase_delta=[]
    for r in range(CONTROL_DIMENSION):
        v0925_dr=sum((upper_point(tangent[r][j])*v0925_a_radius[j]
            for j in range(tangent_dimension)),arb(0))
        v0925_dr+=v0925_graph_normal_radius*sum(
            (upper_point(normal[r][j]) for j in range(RESPONSE_DIMENSION)),arb(0))
        v0925_phase_delta.append(acb(ball(0,v0925_dr),ball(0,v0925_dr)))
    v0925_endpoint_new=v093_matvec(v093_transpose(v0925_t),v0925_phase_delta)
    v0925_endpoint_inside=all(upper_point(x)<v0925_new_domain_radius
        for x in v0925_endpoint_new)

    def v0925_lo(x):
        return format(np.nextafter(float(x.real.lower()),-np.inf),".17e")
    def v0925_hi(x):
        return format(np.nextafter(float(x.real.upper()),np.inf),".17e")
    def v0925_matrix_box(mat,side):
        f=v0925_lo if side=="lower" else v0925_hi
        return [[f(x) for x in row] for row in mat]
    def v0925_point_matrix(mat):
        return [[format(float(midpoint_radius(x.real)[0]),".17e") for x in row] for row in mat]

    v0925_frame_pass=bool(v0925_unique_root and v0925_full_rank and
        v0925_orthogonal and v0925_normal_invertible and v0925_endpoint_inside)
    v0925_certificate={
      "schema":"geometric-flow/third-recentered-frame/v0.9.24",
      "generator_version":"0.9.25",
      "formal_backend":"python-flint/Arb","precision_bits":PRECISION_BITS,
      "frozen_v0923_source_sha256":os.environ["V0925_V0923_SHA256"],
      "frozen_target_certificate_sha256":os.environ["V0925_TARGET_SHA256"],
      "frozen_target_semantic_sha256":os.environ["V0925_TARGET_SEMANTIC_SHA256"],
      "coordinate_system_from":os.environ["V0925_COORDINATE_FROM"],
      "coordinate_system_to":"v0.9.25-third-recentered-intrinsic-tangent",
      "third_tangent_target_center":os.environ["V0925_A_C"].split(","),
      "third_tangent_target_component_radius":os.environ["V0925_A_RADIUS"].split(","),
      "normal_root_center":[v098_mid(x) for x in v0925_b0],
      "normal_root_radius":[v098_up(v0925_root_radius) for _ in range(RESPONSE_DIMENSION)],
      "krawczyk_maximum_utilization":v098_up(max(v0925_utils)),
      "krawczyk_minimum_margin":v098_up(min(v0925_margins)),
      "corrected_phase_center_box":{
        "lower":[v0925_lo(x) for x in v0925_theta_box],
        "upper":[v0925_hi(x) for x in v0925_theta_box]},
      "response_jacobian_box":{
        "lower":v0925_matrix_box(v0925_jac_box,"lower"),
        "upper":v0925_matrix_box(v0925_jac_box,"upper")},
      "tangent_frame_midpoint":v0925_point_matrix(v0925_t),
      "normal_frame_midpoint":v0925_point_matrix(v0925_n),
      "response_singular_values_midpoint":[float(x) for x in v0925_svals],
      "minimum_response_singular_value_lower":format(
        np.nextafter(float(v0925_svals[-1])*(1.0-min(0.999999,float(upper_float(v0925_ndef)))),-np.inf),".17e"),
      "frame_orthogonal_completeness_defect_upper":v098_up(v0925_orth),
      "normal_identity_defect_upper":v098_up(v0925_ndef),
      "tangent_response_residual_upper":v098_up(v0925_tres),
      "transformed_endpoint_box":{
        "lower":[v0925_lo(x) for x in v0925_endpoint_new],
        "upper":[v0925_hi(x) for x in v0925_endpoint_new]},
      "new_start_domain_box":{
        "lower":[str(-float(v0925_new_domain_radius)) for _ in range(tangent_dimension)],
        "upper":[str(float(v0925_new_domain_radius)) for _ in range(tangent_dimension)]},
      "unique_normal_root_certified":v0925_unique_root,
      "full_response_row_rank_certified":v0925_full_rank,
      "frame_orthogonal_complete_certified":v0925_orthogonal,
      "normal_derivative_invertible_certified":v0925_normal_invertible,
      "endpoint_overlap_in_new_frame_certified":bool(v0925_endpoint_inside),
      "all_backend_gates_pass":v0925_frame_pass,
      "claim_boundary":"third tangent/normal frame and complete endpoint-box overlap only; no third graph, Picard chart, complete child, or global flow"
    }
    Path(os.environ["V0925_CERTIFICATE"]).write_text(
        json.dumps(v0925_certificate,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
'''


def patch_driver(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")
    hook = "    v098_cert.update({"
    if text.count(hook) != 1:
        raise RuntimeError("repository-native third-frame injection hook is not unique")
    destination.write_text(
        text.replace(hook, THIRD_FRAME_ARB_CODE + "\n" + hook, 1),
        encoding="utf-8",
    )


def parse() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outdir", default="response_fibre_third_frame_backend_v0_9_25_results"
    )
    parser.add_argument("--v0923", help="optional local frozen v0.9.23 source")
    parser.add_argument("--root-radius", default="2e-18")
    parser.add_argument("--new-domain-radius", default="1e-11")
    return parser.parse_known_args()


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    ensure_flint()
    v0923 = locate_v0923(args.v0923, out / "frozen_sources" / V0923_NAME)

    # Reproduce v0.9.23 to obtain both the target certificate and its exact
    # repository-native instrumented backend source.
    chain = out / "v0923_chain"
    completed = subprocess.run(
        [sys.executable, str(v0923), "--outdir", str(chain),
         "--root-radius", str(args.root_radius)],
        text=True, capture_output=True,
    )
    (out / "v0923_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (out / "v0923_stderr.txt").write_text(completed.stderr, encoding="utf-8")
    target_path = chain / "third_recenter_target_certificate.json"
    summary_path = chain / "run_summary.json"
    if not (target_path.is_file() and summary_path.is_file()):
        raise RuntimeError(
            f"frozen v0.9.23 exit={completed.returncode}; target outputs missing; inspect logs"
        )
    target = json.loads(target_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if completed.returncode != 0 or summary.get("all_scientific_gates_pass") is not True:
        raise RuntimeError("frozen v0.9.23 scientific gates did not pass")

    centers = decimal_vector(
        target.get("tangent_target_center"), TANGENT_DIMENSION, "target center"
    )
    radii = decimal_vector(
        target.get("tangent_target_component_radius"),
        TANGENT_DIMENSION,
        "target radii",
    )
    graph_radius = Decimal(str(target.get("normal_root_enclosure_radius")))
    if graph_radius <= 0:
        raise RuntimeError("v0.9.23 normal graph radius is not positive")
    target_semantic_sha = sha256_json({
        "coordinate_system": target.get("coordinate_system"),
        "tangent_target_center": target.get("tangent_target_center"),
        "tangent_target_component_radius": target.get("tangent_target_component_radius"),
        "certified_parametric_domain": target.get("certified_parametric_domain"),
        "normal_root_enclosure_radius": target.get("normal_root_enclosure_radius"),
    })

    drivers = list(chain.rglob(INSTRUMENTED_DRIVER_NAME))
    if len(drivers) != 1:
        raise RuntimeError(
            f"expected one repository-native instrumented driver, found {len(drivers)}"
        )
    source_driver = drivers[0]
    patched_driver = out / "instrumented_repository_backend_v0_9_25.py"
    patch_driver(source_driver, patched_driver)
    certificate_path = (out / "third_frame_arb_certificate.json").resolve()

    env = dict(os.environ)
    env.update({
        "V0925_A_C": ",".join(str(x) for x in centers),
        "V0925_A_RADIUS": ",".join(str(x) for x in radii),
        "V0925_ROOT_RADIUS": str(args.root_radius),
        "V0925_GRAPH_NORMAL_RADIUS": str(graph_radius),
        "V0925_NEW_DOMAIN_RADIUS": str(args.new_domain_radius),
        "V0925_V0923_SHA256": V0923_SHA256,
        "V0925_TARGET_SHA256": sha256_file(target_path),
        "V0925_TARGET_SEMANTIC_SHA256": target_semantic_sha,
        "V0925_COORDINATE_FROM": str(target.get("coordinate_system")),
        "V0925_CERTIFICATE": str(certificate_path),
    })
    backend_dir = out / "formal_third_frame_backend"
    backend = subprocess.run(
        [sys.executable, str(patched_driver), "--outdir", str(backend_dir),
         "--root-radius", str(args.root_radius), "--no-install"],
        text=True, capture_output=True, env=env,
    )
    (out / "backend_stdout.txt").write_text(backend.stdout, encoding="utf-8")
    (out / "backend_stderr.txt").write_text(backend.stderr, encoding="utf-8")
    if not certificate_path.is_file():
        raise RuntimeError(
            f"third-frame Arb backend exit={backend.returncode}; certificate missing; inspect backend logs"
        )
    cert = json.loads(certificate_path.read_text(encoding="utf-8"))
    declared = [
        cert.get("unique_normal_root_certified") is True,
        cert.get("full_response_row_rank_certified") is True,
        cert.get("frame_orthogonal_complete_certified") is True,
        cert.get("normal_derivative_invertible_certified") is True,
        cert.get("endpoint_overlap_in_new_frame_certified") is True,
        cert.get("all_backend_gates_pass") is True,
    ]
    gates = {
        "frozen_v0923_source_hash_exact": sha256_file(v0923) == V0923_SHA256,
        "v0923_reproduction_passed": completed.returncode == 0,
        "v0923_third_target_certified": summary.get("third_recenter_target_certified") is True,
        "repository_native_driver_uniquely_resolved": len(drivers) == 1,
        "instrumented_backend_exit_zero": backend.returncode == 0,
        "certificate_schema_exact": cert.get("schema") == "geometric-flow/third-recentered-frame/v0.9.24",
        "certificate_bound_to_target": cert.get("frozen_target_semantic_sha256") == target_semantic_sha,
        "formal_precision_192_bits": int(cert.get("precision_bits", 0)) >= PRECISION_BITS,
        "unique_third_normal_root": declared[0],
        "third_response_full_row_rank": declared[1],
        "third_frame_orthogonal_complete": declared[2],
        "third_normal_derivative_invertible": declared[3],
        "complete_endpoint_box_overlap": declared[4],
        "all_backend_gates_pass": declared[5],
    }
    passed = all(gates.values())
    result = {
        "title": TITLE,
        "version": VERSION,
        "scientific_status": (
            "VALIDATED_THIRD_RECENTERED_TANGENT_NORMAL_FRAME_CERTIFICATE_GENERATED"
            if passed else "THIRD_FRAME_BACKEND_INCONCLUSIVE_FAIL_CLOSED"
        ),
        "repository": REPOSITORY,
        "frozen_commit": FROZEN_COMMIT,
        "formal_backend": "python-flint/Arb 192-bit",
        "certificate": str(certificate_path),
        "certificate_sha256": sha256_file(certificate_path),
        "certificate_metrics": {
            key: cert.get(key) for key in [
                "normal_root_center",
                "normal_root_radius",
                "krawczyk_maximum_utilization",
                "krawczyk_minimum_margin",
                "response_singular_values_midpoint",
                "minimum_response_singular_value_lower",
                "frame_orthogonal_completeness_defect_upper",
                "normal_identity_defect_upper",
                "tangent_response_residual_upper",
            ]
        },
        "gates": gates,
        "all_scientific_gates_pass": passed,
        "third_tangent_normal_frame_certified": passed,
        "third_local_picard_chart_certified": False,
        "complete_child_certified": False,
        "ten_chart_continuation_certified": False,
        "global_flow_claimed": False,
        "next_command": (
            "python response_fibre_third_frame_v0_9_24_oneclick.py "
            f"--frame-certificate {certificate_path}"
        ),
        "next_required_step": (
            "feed this certificate to v0.9.24; after independent acceptance, construct the third complex fibre graph and Picard microstep"
            if passed else "inspect backend_stdout.txt and backend_stderr.txt; do not claim a third frame"
        ),
        "claim_boundary": (
            "third-centre normal root, tangent/normal frame, and complete endpoint-box overlap only; "
            "no third graph/Picard chart, complete child, or global flow"
        ),
        "elapsed_seconds": time.time() - started,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    result["report_sha256_before_self_field"] = sha256_json(result)
    atomic_json(out / "run_summary.json", result)
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
            "scientific_status": "V0925_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, indent=2))
        return 2


if __name__ == "__main__":
    code = main()
    if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
        raise SystemExit(code)

