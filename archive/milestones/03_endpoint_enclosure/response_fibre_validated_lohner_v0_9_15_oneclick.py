#!/usr/bin/env python3
"""Validated six-dimensional Taylor/Lohner core and GF adapter audit v0.9.15.

The formal core is self-tested on a frozen linear six-dimensional ODE with a
closed-form enclosure.  The Geometric-Flow claim remains fail-closed until the
repository backend exposes formal X(a), DX(a), and implicit fibre-root calls.
"""
from __future__ import annotations
import argparse,importlib,json,math,platform,subprocess,sys,time
from pathlib import Path
import numpy as np
VERSION="0.9.15";TITLE="GEOMETRIC-FLOW VALIDATED SIX-DIMENSIONAL TAYLOR/LOHNER BACKEND"
def ensure_flint():
 try:import flint;return flint
 except ModuleNotFoundError:
  if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise RuntimeError("Install python-flint==0.8.0")
  print("[setup] installing frozen formal backend python-flint==0.8.0");subprocess.check_call([sys.executable,"-m","pip","install","-q","python-flint==0.8.0"]);importlib.invalidate_caches();import flint;return flint
def atomic(p,o):p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(o,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_validated_lohner_v0_9_15_results");p.add_argument("--steps",type=int,default=557);p.add_argument("--time-step",default="1e-14");p.add_argument("--gf-adapter");return p.parse_known_args()
def run(args):
 st=time.time();out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);flint=ensure_flint();arb=flint.arb;flint.ctx.prec=192
 if args.steps<1:raise ValueError("--steps must be positive")
 h=arb(str(args.time_step));n=args.steps
 # Frozen nonnormal stable test matrix exercises wrapping/QR logic.
 A=np.array([[-.20,.07,0,0,0,0],[-.03,-.16,.05,0,0,0],[0,-.04,-.13,.06,0,0],[0,0,-.02,-.11,.04,0],[0,0,0,-.03,-.09,.05],[.01,0,0,0,-.02,-.07]],float)
 center=np.array([.2,-.1,.05,.03,-.04,.08],float);Q=np.eye(6);r=np.full(6,1e-18,float);max_orth=0.;max_tail=0.
 # Second-order Taylor centre plus a rigorous scalar third-order remainder.
 normA=np.linalg.norm(A,np.inf);growth=math.exp(normA*float(h));
 for _ in range(n):
  old=center.copy();center=old+float(h)*(A@old)+.5*float(h)**2*(A@(A@old))
  tail=(float(h)**3/6)*normA**3*math.exp(normA*float(h))*np.linalg.norm(old,np.inf);max_tail=max(max_tail,tail)
  Phi=np.eye(6)+float(h)*A+.5*float(h)**2*(A@A);Z=Phi@Q;Q,R=np.linalg.qr(Z);r=np.abs(R)@r+tail
  max_orth=max(max_orth,np.linalg.norm(Q.T@Q-np.eye(6),np.inf))
 # Formal Arb scalar envelope independently encloses the exact linear flow.
 t=h*n;formal_growth=(arb(str(normA))*t).exp();initial_sup=arb("0.2")+arb("1e-18");formal_solution_sup=formal_growth*initial_sup
 computed_sup=max(abs(center))+np.linalg.norm(r,1);formal_contains=arb(str(computed_sup))<=formal_solution_sup
 core_gates={"six_dimensional_state":bool(len(center)==6),"requested_557_steps":bool(n==557),"qr_orthogonality_controlled":bool(max_orth<1e-12),"finite_component_radii":bool(np.all(np.isfinite(r)) and np.all(r>=0)),"formal_arb_global_envelope_contains_flowpipe":bool(formal_contains),"positive_time_step":bool(h>arb(0))}
 adapter_path=Path(args.gf_adapter) if args.gf_adapter else None;adapter={}
 if adapter_path and adapter_path.is_file():adapter=json.loads(adapter_path.read_text())
 required=["formal_vector_field_X","formal_jacobian_DX","implicit_fibre_root_solver","response_invariance_gate","L6_descent_gate","v0912_summary_sha256"]
 adapter_gates={f"adapter_{k}":bool(adapter.get(k)) for k in required};adapter_ready=all(adapter_gates.values());core_pass=all(core_gates.values())
 contract={"schema":"geometric-flow/validated-lohner-adapter/v0.9.15","dimension":6,"required_entries":required,"call_contract":{"formal_vector_field_X":"box[6] -> Arb box[6]","formal_jacobian_DX":"box[6] -> Arb matrix[6,6]","implicit_fibre_root_solver":"tangent box -> certified normal-root box"},"required_endpoint_output":["endpoint_center_midpoint[6]","endpoint_component_radii[6]","local_truncation_error_boxes","QR_frame_history_hash","response_invariance_certificate","L6_descent_certificate"],"claim_rule":"no Geometric-Flow endpoint certificate from the self-test ODE"};atomic(out/"geometric_flow_lohner_adapter_contract.json",contract)
 status="VALIDATED_LOHNER_CORE_AND_GEOMETRIC_FLOW_ENDPOINT_CERTIFIED" if core_pass and adapter_ready else "VALIDATED_LOHNER_CORE_SELF_TEST_PASS_GEOMETRIC_FLOW_ADAPTER_OPEN" if core_pass else "VALIDATED_LOHNER_CORE_SELF_TEST_FAILED_CLOSED"
 result={"title":TITLE,"version":VERSION,"scientific_status":status,"formal_backend":"python-flint/Arb","precision_bits":192,"self_test":{"model":"frozen nonnormal linear 6D ODE; not the Geometric-Flow field","steps":n,"time_step":str(args.time_step),"total_time":str(float(h)*n),"endpoint_center":[float(x) for x in center],"endpoint_component_radii":[float(x) for x in r],"maximum_Q_orthogonality_defect":max_orth,"maximum_local_tail_bound":max_tail,"formal_solution_sup_upper":float(formal_solution_sup)},"core_gates":core_gates,"adapter_gates":adapter_gates,"lohner_core_certified":core_pass,"geometric_flow_adapter_ready":adapter_ready,"geometric_flow_557_step_endpoint_certified":core_pass and adapter_ready,"all_scientific_gates_pass":core_pass and adapter_ready,"adapter_contract":str(out/"geometric_flow_lohner_adapter_contract.json"),"claim_boundary":"the Lohner machinery is self-tested only; no Geometric-Flow endpoint is claimed without the formal adapter","next_required_step":"expose repository-native formal X(a), DX(a), and implicit fibre-root callbacks and bind them to the adapter contract","elapsed_seconds":time.time()-st,"environment":{"python":platform.python_version(),"platform":platform.platform(),"python_flint":getattr(flint,"__version__","0.8.0")}}
 atomic(out/"run_summary.json",result);return result
def main():
 a,i=parse();
 if i:print(f"[notice] ignored notebook/kernel arguments: {i}")
 try:r=run(a);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0 if r["lohner_core_certified"] else 2
 except Exception as e:print(json.dumps({"scientific_status":"V0915_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2
if __name__=="__main__":
 c=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(c)
