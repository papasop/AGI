#!/usr/bin/env python3
"""Repository-native Arb normal-root solver attempt for Geometric-Flow v0.9.8.

The script hash-verifies the frozen v0.9.3 generator, instruments its injected
Arb backend at one auditable hook, and computes a Krawczyk enclosure for
B(R(theta0 + T*a_c + N*b) - R(theta0)) = 0.  It fails closed: a numerical
Newton centre is never reported as a theorem unless the outward-rounded
Krawczyk image is a strict subset of the declared normal box.
"""
from __future__ import annotations

import argparse, hashlib, importlib, json, os, platform, subprocess, sys, time, urllib.request
from pathlib import Path
from typing import Any

VERSION="0.9.8"
TITLE="GEOMETRIC-FLOW ARB RECENTERED NORMAL-ROOT SOLVER"
REPO="https://github.com/papasop/Geometric-Flow"
RAW="https://raw.githubusercontent.com/papasop/Geometric-Flow/main"
V093_REL="src/response_fibre_intrinsic_picard_microstep_v0_9_3.py"
V093_SHA="3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c"
V074_REL="src/response_fibre_arb_kkt_witness_alignment_v0_7_4.py"
V074_SHA="1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8"
INPUT_REL="inputs/response_fibre_v0_6_2_backend_inputs.zip"
INPUT_SHA="2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"
A_C=["-4.355219676575712e-16","2.760123667996916e-15","3.970739962875234e-15",
     "4.969572627411907e-15","4.8364932996051435e-15","-5.328901229456864e-15"]

def sha(path:Path)->str:
 h=hashlib.sha256();
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def atomic(path:Path,obj:Any)->None:
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n");tmp.replace(path)

def ensure_flint()->str:
 try:
  import flint;return getattr(flint,"__version__","installed")
 except ModuleNotFoundError:
  if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:
   raise RuntimeError("Install python-flint==0.8.0")
  print("[setup] installing frozen formal backend python-flint==0.8.0")
  subprocess.check_call([sys.executable,"-m","pip","install","-q","python-flint==0.8.0"])
  importlib.invalidate_caches();import flint;return getattr(flint,"__version__","0.8.0")

def acquire(root:Path,rel:str,digest:str)->Path:
 path=root/Path(rel).name;path.parent.mkdir(parents=True,exist_ok=True)
 if not path.is_file():print(f"[repository] downloading {rel}");urllib.request.urlretrieve(f"{RAW}/{rel}",path)
 got=sha(path)
 if got!=digest:raise RuntimeError(f"frozen hash mismatch for {rel}: {got}")
 return path

INJECT_ENV='''v093_output.mkdir(parents=True, exist_ok=True)'''
INJECT_ENV_REPL='''v093_output.mkdir(parents=True, exist_ok=True)
v098_a_c = [ap(x) for x in os.environ["V098_A_C"].split(",")]
v098_root_radius = ap(os.environ["V098_ROOT_RADIUS"])
v098_certificate_path = Path(os.environ["V098_CERTIFICATE"])
'''

HOOK='''    fb_inverse = v093_midpoint_inverse(fb0, "normal derivative")'''

ARB_CODE=r'''

    # v0.9.8: formal normal-root Krawczyk solve at the frozen v0.9.6 target.
    def v098_response(phases):
        z, _ = projective_jet_and_derivatives(phases, mirror=False)
        zb, _ = projective_jet_and_derivatives(phases, mirror=True)
        vals=[]
        for order in range(RESPONSE_ORDER + 1):
            vals.append((z.c[order] + zb.c[order]) / 2)
        for order in range(RESPONSE_ORDER + 1):
            vals.append((z.c[order] - zb.c[order]) / (2 * I))
        return vals

    if len(v098_a_c) != tangent_dimension:
        raise ArithmeticError("v0.9.8 tangent target dimension mismatch")
    response0 = v098_response(base_phases)
    theta_a = [base_phases[r] + sum((tangent[r][j] * v098_a_c[j]
               for j in range(tangent_dimension)), acb(0))
               for r in range(CONTROL_DIMENSION)]
    response_a = v098_response(theta_a)
    f_a = v093_matvec(whitener,[response_a[i]-response0[i]
                               for i in range(RESPONSE_DIMENSION)])
    jac_a,_ = response_jacobian_and_gradient(theta_a,True)
    d_a = v093_matmul(v093_matmul(whitener,jac_a),normal)
    d_a_mid=np.asarray([[midpoint_radius(d_a[r][c].real)[0]
                         for c in range(RESPONSE_DIMENSION)]
                        for r in range(RESPONSE_DIMENSION)],dtype=float)
    f_a_mid=np.asarray([midpoint_radius(f_a[r].real)[0]
                        for r in range(RESPONSE_DIMENSION)],dtype=float)
    try:
        b0_float=np.linalg.solve(d_a_mid,-f_a_mid)
    except np.linalg.LinAlgError as exc:
        raise ArithmeticError("v0.9.8 midpoint normal Newton solve failed") from exc
    b0=[acb(ap(float(x))) for x in b0_float]
    theta_b=[theta_a[r]+sum((normal[r][j]*b0[j]
             for j in range(RESPONSE_DIMENSION)),acb(0))
             for r in range(CONTROL_DIMENSION)]
    response_b=v098_response(theta_b)
    f_b=v093_matvec(whitener,[response_b[i]-response0[i]
                              for i in range(RESPONSE_DIMENSION)])
    jac_b,_=response_jacobian_and_gradient(theta_b,True)
    d_b=v093_matmul(v093_matmul(whitener,jac_b),normal)
    A=v093_midpoint_inverse(d_b,"v0.9.8 recentered normal derivative")
    correction=v093_matvec(A,f_b)
    image_center=[b0[i]-correction[i] for i in range(RESPONSE_DIMENSION)]

    theta_box=[]
    for r in range(CONTROL_DIMENSION):
        rad=v098_root_radius*sum((upper_point(normal[r][j])
                                 for j in range(RESPONSE_DIMENSION)),arb(0))
        theta_box.append(theta_b[r]+acb(ball(0,rad),ball(0,rad)))
    jac_box,_=response_jacobian_and_gradient(theta_box,True)
    d_box=v093_matmul(v093_matmul(whitener,jac_box),normal)
    defect=v093_defect(A,d_box)
    defect_upper=v093_inf_matrix(defect)
    image_radii=[];margins=[];utils=[]
    for i in range(RESPONSE_DIMENSION):
        rad=upper_point(correction[i])
        rad+=v098_root_radius*sum((upper_point(defect[i][j])
                                  for j in range(RESPONSE_DIMENSION)),arb(0))
        image_radii.append(rad)
        displacement=upper_point(image_center[i]-b0[i])+rad
        margins.append(v098_root_radius-displacement)
        utils.append(displacement/v098_root_radius)
    strict=all(m>arb(0) for m in margins)
    derivative_invertible=bool(defect_upper<arb(1))
    # Krawczyk strict inclusion itself proves a unique zero; direct interval
    # evaluation is recorded only as a diagnostic because dependency may make
    # it wider than the topological certificate.
    response_box=v098_response(theta_box)
    f_box=v093_matvec(whitener,[response_box[i]-response0[i]
                                for i in range(RESPONSE_DIMENSION)])
    direct_contains=all(x.real.contains(0) and x.imag.contains(0) for x in f_box)
    backend_pass=bool(strict and derivative_invertible)
    def v098_mid(x): return format(midpoint_radius(x.real)[0],".40e")
    def v098_up(x): return format(upper_float(x),".40e")
    v098_cert={
      "schema":"geometric-flow/recentered-normal-root-krawczyk/v0.9.8",
      "formal_backend":"python-flint/Arb","precision_bits":PRECISION_BITS,
      "dimension":RESPONSE_DIMENSION,
      "frozen_repository_hashes":{"v093_source":"3be3e07146ff0e505f08bae7bd0ec7f2895955f2540647fea3278fdba51db79c","v074_source":"1f71c4918d1cd1d6c45dc0da4a7358e176baac9116c8f71f4a949a6d657520f8","inputs_zip":"2efd863f5ff26da1067594f068bfe265678e6ebac480574ff0574ccc55f98666"},
      "a_c":[str(x) for x in os.environ["V098_A_C"].split(",")],
      "normal_box_center":[v098_mid(x) for x in b0],
      "normal_box_radius":[v098_up(v098_root_radius) for _ in range(RESPONSE_DIMENSION)],
      "newton_correction_radius":[v098_up(x) for x in correction],
      "normal_derivative_defect_upper":v098_up(defect_upper),
      "krawczyk_image_center":[v098_mid(x) for x in image_center],
      "krawczyk_image_radius":[v098_up(x) for x in image_radii],
      "krawczyk_strict_interior_margin":[v098_up(x) for x in margins],
      "maximum_krawczyk_utilization":v098_up(max(utils)),
      "normal_derivative_invertible":derivative_invertible,
      "krawczyk_strict_inclusion":bool(strict),
      "direct_interval_response_contains_zero":bool(direct_contains),
      "unique_normal_root_certified":backend_pass,
      "all_backend_gates_pass":backend_pass,
      "claim_boundary":"unique normal root at fixed a_c only; no new frame, second Picard chart, or global flow"
    }
    v098_certificate_path.parent.mkdir(parents=True,exist_ok=True)
    v098_certificate_path.write_text(json.dumps(v098_cert,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
'''

def patch_generator(source:str)->str:
 if source.count(INJECT_ENV)!=1:raise RuntimeError("v0.9.3 environment hook not unique")
 source=source.replace(INJECT_ENV,INJECT_ENV_REPL,1)
 if source.count(HOOK)!=1:raise RuntimeError("v0.9.3 normal-derivative hook not unique")
 source=source.replace(HOOK,HOOK+ARB_CODE,1)
 envneedle='''                "V093_OUTPUT": str(output),'''
 envrepl=envneedle+'''
                "V098_A_C": os.environ["V098_A_C"],
                "V098_ROOT_RADIUS": os.environ["V098_ROOT_RADIUS"],
                "V098_CERTIFICATE": os.environ["V098_CERTIFICATE"],'''
 if source.count(envneedle)!=1:raise RuntimeError("v0.9.3 subprocess environment hook not unique")
 return source.replace(envneedle,envrepl,1)

def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_arb_normal_root_v0_9_8_results")
 p.add_argument("--root-radius",default="2e-18");p.add_argument("--no-install",action="store_true")
 return p.parse_known_args()

def run(args)->dict[str,Any]:
 start=time.time();out=Path(args.outdir);frozen=out/"frozen_repository_inputs";out.mkdir(parents=True,exist_ok=True)
 flint=ensure_flint();v093=acquire(frozen,V093_REL,V093_SHA);v074=acquire(frozen,V074_REL,V074_SHA);inputs=acquire(frozen,INPUT_REL,INPUT_SHA)
 patched=out/"instrumented_v0_9_3_generator_for_v0_9_8.py";patched.write_text(patch_generator(v093.read_text()))
 cert=out/"normal_root_arb_certificate.json";base=out/"formal_base"
 env=dict(os.environ);env.update({"V098_A_C":",".join(A_C),"V098_ROOT_RADIUS":str(args.root_radius),"V098_CERTIFICATE":str(cert.resolve())})
 cmd=[sys.executable,str(patched),"--inputs-zip",str(inputs),"--v074-source",str(v074),"--no-download","--output",str(base)]
 done=subprocess.run(cmd,text=True,capture_output=True,env=env);(out/"stdout.txt").write_text(done.stdout);(out/"stderr.txt").write_text(done.stderr)
 if not cert.is_file():raise RuntimeError(f"instrumented Arb backend exit={done.returncode}; certificate missing; inspect logs")
 c=json.loads(cert.read_text());basecert=base/"intrinsic_picard_microstep_certificate.json"
 baseok=basecert.is_file() and json.loads(basecert.read_text()).get("all_gates_pass") is True
 gates={"repository_hashes_match":True,"instrumented_backend_exit_zero":done.returncode==0,"frozen_v093_base_gates_pass":baseok,
        "normal_derivative_invertible":c.get("normal_derivative_invertible") is True,
        "krawczyk_strict_inclusion":c.get("krawczyk_strict_inclusion") is True,
        "unique_normal_root_certified":c.get("unique_normal_root_certified") is True}
 passed=all(gates.values());status="VALIDATED_RECENTERED_NORMAL_ROOT_KRAWCZYK_CERTIFIED" if passed else "RECENTERED_NORMAL_ROOT_KRAWCZYK_INCONCLUSIVE_FAIL_CLOSED"
 result={"title":TITLE,"version":VERSION,"scientific_status":status,"repository":REPO,"python_flint_version":flint,
   "normal_root_certificate":str(cert),"normal_root_metrics":c,"gates":gates,"all_scientific_gates_pass":passed,
   "recentered_tangent_normal_frame_certified":False,"second_local_picard_chart_certified":False,"global_flow_claimed":False,
   "next_required_step":"construct a new formal tangent/normal frame at the corrected centre" if passed else "adjust only the declared root radius or strengthen Arb dependency bounds; inspect the reported Krawczyk margin",
   "claim_boundary":"At most a unique normal root at the fixed v0.9.6 tangent target; no second chart/global theorem.",
   "elapsed_seconds":time.time()-start,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
 atomic(out/"run_summary.json",result);return result

def main()->int:
 args,ignored=parse();
 if ignored:print(f"[notice] ignored notebook/kernel arguments: {ignored}")
 try:
  r=run(args);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0 if r["all_scientific_gates_pass"] else 2
 except Exception as e:
  print(json.dumps({"scientific_status":"V098_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2

if __name__=="__main__":
 code=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(code)
